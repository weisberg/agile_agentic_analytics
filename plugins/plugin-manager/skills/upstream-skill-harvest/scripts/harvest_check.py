#!/usr/bin/env python3
"""Validate an upstream skill harvest or refresh.

The checker is intentionally small and dependency-free. It catches the mistakes
that are easy to make during manual skill adaptation: missing frontmatter,
dropped metadata keys, KB terminology drift, private paths, and missing ledger
records.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    path: str
    line: int | None = None

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }
        if self.line is not None:
            payload["line"] = self.line
        return payload


PRIVACY_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "absolute_user_path",
        re.compile(r"/Users/[^\s)>\]\"']+"),
        "Use $GBRAIN_ROOT, $GSTACK_ROOT, or a repo-relative path instead of an absolute local path.",
    ),
    (
        "email_address",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "Replace private email addresses with placeholders or remove them.",
    ),
    (
        "private_fork_name",
        re.compile(r"\b(Wintermute|Neuromancer|Zion)\b"),
        "Replace private fork names with generic plugin, host repo, or deployment wording.",
    ),
)

KB_TERM_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "gbrain_runtime_term",
        re.compile(r"\bgbrain\b", re.IGNORECASE),
        "Use KB, knowledge base, vaultli, or generic page-tool wording unless this is source provenance.",
    ),
    (
        "brain_runtime_term",
        re.compile(r"\bbrain\b", re.IGNORECASE),
        "Use knowledge base or KB in user-facing plugin text.",
    ),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            frontmatter = "\n".join(lines[1:index]).strip()
            body = "\n".join(lines[index + 1 :])
            return frontmatter, body
    return None, text


def frontmatter_keys(frontmatter: str | None) -> list[str]:
    if frontmatter is None:
        return []
    keys: list[str] = []
    for line in frontmatter.splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):", line)
        if match:
            keys.append(match.group(1))
    return keys


def normalized_frontmatter(frontmatter: str | None) -> str:
    if frontmatter is None:
        return ""
    return "\n".join(line.rstrip() for line in frontmatter.strip().splitlines())


def line_number(text: str, start_index: int) -> int:
    return text.count("\n", 0, start_index) + 1


def scan_patterns(
    *,
    text: str,
    path: Path,
    patterns: Iterable[tuple[str, re.Pattern[str], str]],
) -> list[Finding]:
    findings: list[Finding] = []
    for code, pattern, message in patterns:
        for match in pattern.finditer(text):
            findings.append(
                Finding(
                    code=code,
                    message=message,
                    path=str(path),
                    line=line_number(text, match.start()),
                )
            )
    return findings


def relative_to_repo(path: Path, repo_root: Path) -> Path | None:
    try:
        return path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return None


def check_plugins_target(target: Path, repo_root: Path) -> list[Finding]:
    rel = relative_to_repo(target, repo_root)
    if rel is None:
        return [
            Finding(
                "target_outside_repo",
                "Target must be inside this repository.",
                str(target),
            )
        ]
    if not rel.parts or rel.parts[0] != "plugins":
        return [
            Finding(
                "target_outside_plugins",
                "Target must be under plugins/ for this plugin-manager harvest workflow.",
                str(target),
            )
        ]
    if ".claude-plugin" in rel.parts:
        return [
            Finding(
                "target_inside_manifest_dir",
                "Do not place skills or references inside .claude-plugin/.",
                str(target),
            )
        ]
    return []


def check_ledger(ledger: Path, target_name: str) -> list[Finding]:
    if not ledger.exists():
        return [
            Finding(
                "ledger_missing",
                "Ledger file is required when --ledger is provided.",
                str(ledger),
            )
        ]
    text = read_text(ledger)
    findings = scan_patterns(text=text, path=ledger, patterns=PRIVACY_PATTERNS)
    if target_name not in text:
        findings.append(
            Finding(
                "ledger_target_missing",
                f"Ledger does not mention target {target_name!r}.",
                str(ledger),
            )
        )
    for required_phrase in ("Source", "Adaptation notes", "Privacy/path check"):
        if required_phrase not in text:
            findings.append(
                Finding(
                    "ledger_field_missing",
                    f"Ledger is missing required field phrase {required_phrase!r}.",
                    str(ledger),
                )
            )
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Upstream source SKILL.md.")
    parser.add_argument("--target", type=Path, required=True, help="Target plugin SKILL.md or file.")
    parser.add_argument("--ledger", type=Path, help="Target plugin upstream-source ledger.")
    parser.add_argument(
        "--target-name",
        help="Target string that must appear in the ledger. Defaults to target path relative to repo root.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--preserve-frontmatter",
        action="store_true",
        help="Require exact source and target YAML frontmatter match.",
    )
    parser.add_argument(
        "--require-source-frontmatter-keys",
        action="store_true",
        help="Require every top-level source frontmatter key to appear in target.",
    )
    parser.add_argument(
        "--kb-terminology",
        action="store_true",
        help="Flag raw brain/GBrain terminology in the target.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    target = args.target.resolve()
    source = args.source.resolve() if args.source else None

    failures: list[Finding] = []
    warnings: list[Finding] = []

    if not target.exists():
        failures.append(Finding("target_missing", "Target file does not exist.", str(target)))
        target_text = ""
        target_fm = None
    else:
        target_text = read_text(target)
        target_fm, _target_body = split_frontmatter(target_text)

    failures.extend(check_plugins_target(target, repo_root))

    if target.exists() and target_fm is None:
        failures.append(Finding("target_frontmatter_missing", "Target is missing YAML frontmatter.", str(target)))

    source_fm: str | None = None
    source_keys: list[str] = []
    if source:
        if not source.exists():
            failures.append(Finding("source_missing", "Source file does not exist.", str(source)))
        else:
            source_text = read_text(source)
            source_fm, _source_body = split_frontmatter(source_text)
            source_keys = frontmatter_keys(source_fm)
            if source_fm is None:
                warnings.append(
                    Finding("source_frontmatter_missing", "Source is missing YAML frontmatter.", str(source))
                )

    target_keys = frontmatter_keys(target_fm)

    if args.preserve_frontmatter:
        if not source:
            failures.append(
                Finding(
                    "source_required",
                    "--preserve-frontmatter requires --source.",
                    str(target),
                )
            )
        elif normalized_frontmatter(source_fm) != normalized_frontmatter(target_fm):
            failures.append(
                Finding(
                    "frontmatter_exact_mismatch",
                    "Target YAML frontmatter does not exactly match source frontmatter.",
                    str(target),
                )
            )

    if args.require_source_frontmatter_keys and source:
        missing = sorted(set(source_keys) - set(target_keys))
        for key in missing:
            failures.append(
                Finding(
                    "frontmatter_key_missing",
                    f"Target frontmatter is missing source key {key!r}.",
                    str(target),
                )
            )

    if target.exists():
        failures.extend(scan_patterns(text=target_text, path=target, patterns=PRIVACY_PATTERNS))
        if args.kb_terminology:
            failures.extend(scan_patterns(text=target_text, path=target, patterns=KB_TERM_PATTERNS))

    if args.ledger:
        target_name = args.target_name
        if target_name is None:
            rel = relative_to_repo(target, repo_root)
            target_name = str(rel if rel is not None else target)
        failures.extend(check_ledger(args.ledger.resolve(), target_name))

    payload = {
        "ok": not failures,
        "failures": [finding.as_dict() for finding in failures],
        "warnings": [finding.as_dict() for finding in warnings],
        "source_frontmatter_keys": source_keys,
        "target_frontmatter_keys": target_keys,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if failures:
            print("FAIL")
            for finding in failures:
                location = f"{finding.path}:{finding.line}" if finding.line else finding.path
                print(f"- {finding.code}: {location}: {finding.message}")
        else:
            print("PASS")
        if warnings:
            print("WARNINGS")
            for finding in warnings:
                location = f"{finding.path}:{finding.line}" if finding.line else finding.path
                print(f"- {finding.code}: {location}: {finding.message}")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
