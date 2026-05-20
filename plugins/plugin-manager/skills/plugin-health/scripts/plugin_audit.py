#!/usr/bin/env python3
"""Audit Claude Code plugins in this marketplace.

The audit is intentionally dependency-free so it can run in CI, fresh clones,
and agent sessions before project dependencies are installed.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REQUIRED_MANIFEST_FIELDS = ("name", "description", "version", "author", "license", "keywords")
GENERATED_PATTERNS = ("__pycache__", ".pytest_cache", "target", ".DS_Store")
SECTION_ALIASES = {
    "Contract": ("## Contract",),
    "Process": ("## Workflow", "## Process", "## Phases", "## Phase"),
    "Output Format": ("## Output Format",),
    "Anti-Patterns": ("## Anti-Patterns",),
}


@dataclass
class Check:
    name: str
    status: str
    path: str
    message: str
    action: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "status": self.status,
            "path": self.path,
            "message": self.message,
        }
        if self.action:
            payload["action"] = self.action
        return payload


@dataclass
class PluginReport:
    name: str
    path: str
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(check.status != "fail" for check in self.checks)

    def as_dict(self) -> dict[str, Any]:
        fail_count = sum(1 for check in self.checks if check.status == "fail")
        warn_count = sum(1 for check in self.checks if check.status == "warn")
        return {
            "name": self.name,
            "path": self.path,
            "ok": self.ok,
            "fail_count": fail_count,
            "warn_count": warn_count,
            "checks": [check.as_dict() for check in self.checks],
        }


def read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, "file does not exist"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"


def split_frontmatter(text: str) -> tuple[str | None, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    return None, text


def frontmatter_keys(frontmatter: str | None) -> set[str]:
    if not frontmatter:
        return set()
    keys: set[str] = set()
    for line in frontmatter.splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):", line)
        if match:
            keys.add(match.group(1))
    return keys


def marketplace_entries(repo_root: Path) -> tuple[dict[str, dict[str, Any]], str | None]:
    marketplace_path = repo_root / ".claude-plugin/marketplace.json"
    data, error = read_json(marketplace_path)
    if error:
        return {}, error
    entries = {
        entry.get("name", ""): entry
        for entry in data.get("plugins", [])
        if isinstance(entry, dict) and entry.get("name")
    }
    return entries, None


def plugin_dirs(repo_root: Path, selected: str | None) -> list[Path]:
    plugins_root = repo_root / "plugins"
    if selected:
        return [plugins_root / selected]
    return sorted(path for path in plugins_root.iterdir() if (path / ".claude-plugin/plugin.json").exists())


def add_check(
    report: PluginReport, name: str, status: str, path: Path, message: str, action: str | None = None
) -> None:
    report.checks.append(Check(name=name, status=status, path=str(path), message=message, action=action))


def audit_manifest(plugin_dir: Path, report: PluginReport) -> dict[str, Any] | None:
    manifest_path = plugin_dir / ".claude-plugin/plugin.json"
    manifest, error = read_json(manifest_path)
    if error:
        add_check(report, "manifest-json", "fail", manifest_path, error, "Create a valid .claude-plugin/plugin.json.")
        return None

    add_check(report, "manifest-json", "pass", manifest_path, "Manifest JSON parsed.")

    for field_name in REQUIRED_MANIFEST_FIELDS:
        value = manifest.get(field_name)
        if value in (None, "", []):
            add_check(
                report,
                "manifest-field",
                "fail",
                manifest_path,
                f"Missing or empty manifest field {field_name!r}.",
                f"Add {field_name!r} to {manifest_path}.",
            )

    if manifest.get("name") != plugin_dir.name:
        add_check(
            report,
            "manifest-name",
            "fail",
            manifest_path,
            f"Manifest name {manifest.get('name')!r} does not match directory {plugin_dir.name!r}.",
            "Rename the plugin directory or update manifest name.",
        )
    else:
        add_check(report, "manifest-name", "pass", manifest_path, "Manifest name matches directory.")

    return manifest


def audit_marketplace(
    plugin_dir: Path, report: PluginReport, entries: dict[str, dict[str, Any]], marketplace_error: str | None
) -> None:
    marketplace_path = plugin_dir.parents[1] / ".claude-plugin/marketplace.json"
    if marketplace_error:
        add_check(report, "marketplace-json", "fail", marketplace_path, marketplace_error, "Fix marketplace JSON.")
        return

    entry = entries.get(plugin_dir.name)
    if not entry:
        add_check(
            report,
            "marketplace-entry",
            "fail",
            marketplace_path,
            "Plugin is not registered in the marketplace.",
            f"Add {plugin_dir.name!r} to .claude-plugin/marketplace.json.",
        )
        return

    expected_source = f"./plugins/{plugin_dir.name}"
    if entry.get("source") != expected_source:
        add_check(
            report,
            "marketplace-source",
            "fail",
            marketplace_path,
            f"Marketplace source is {entry.get('source')!r}, expected {expected_source!r}.",
            "Update marketplace source path.",
        )
    else:
        add_check(report, "marketplace-entry", "pass", marketplace_path, "Marketplace entry is present.")


def audit_manifest_dir(plugin_dir: Path, report: PluginReport) -> None:
    manifest_dir = plugin_dir / ".claude-plugin"
    if not manifest_dir.exists():
        add_check(
            report,
            "manifest-dir",
            "fail",
            manifest_dir,
            "Plugin is missing .claude-plugin/ directory.",
            "Create .claude-plugin/plugin.json.",
        )
        return

    forbidden = [path for path in manifest_dir.iterdir() if path.name != "plugin.json"]
    if forbidden:
        for path in forbidden:
            add_check(
                report,
                "manifest-dir-clean",
                "fail",
                path,
                "Only plugin.json belongs inside .claude-plugin/.",
                "Move component directories to the plugin root.",
            )
    else:
        add_check(report, "manifest-dir-clean", "pass", manifest_dir, "No extra files in .claude-plugin/.")


def audit_skill_file(skill_file: Path, report: PluginReport, strict_sections: bool) -> None:
    text = skill_file.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(text)
    keys = frontmatter_keys(frontmatter)

    if not frontmatter:
        add_check(report, "skill-frontmatter", "fail", skill_file, "SKILL.md is missing YAML frontmatter.")
    else:
        add_check(report, "skill-frontmatter", "pass", skill_file, "YAML frontmatter exists.")

    for key in ("name", "description"):
        if key not in keys:
            add_check(
                report,
                "skill-frontmatter-key",
                "fail",
                skill_file,
                f"Frontmatter missing required key {key!r}.",
                f"Add {key!r} to the skill frontmatter.",
            )

    if strict_sections:
        for section_name, aliases in SECTION_ALIASES.items():
            if not any(alias in body for alias in aliases):
                add_check(
                    report,
                    "skill-section",
                    "fail",
                    skill_file,
                    f"Missing required section {section_name!r}.",
                    f"Add a {section_name} section or an accepted alias.",
                )


def audit_skills(plugin_dir: Path, report: PluginReport, strict_sections: bool) -> None:
    skills_dir = plugin_dir / "skills"
    if not skills_dir.exists():
        add_check(report, "skills-dir", "warn", skills_dir, "Plugin has no skills directory.")
        return

    skill_files = sorted(skills_dir.glob("*/SKILL.md"))
    if not skill_files:
        add_check(report, "skills-present", "warn", skills_dir, "No skills found under skills/*/SKILL.md.")
        return

    add_check(report, "skills-present", "pass", skills_dir, f"Found {len(skill_files)} skill(s).")
    for skill_file in skill_files:
        audit_skill_file(skill_file, report, strict_sections)

    for routing_eval in sorted(skills_dir.glob("*/routing-eval.jsonl")):
        for line_number, line in enumerate(routing_eval.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            try:
                json.loads(stripped)
            except json.JSONDecodeError as exc:
                add_check(
                    report,
                    "routing-eval-jsonl",
                    "fail",
                    routing_eval,
                    f"Invalid JSONL at line {line_number}: {exc}",
                    "Fix or remove the invalid routing eval line.",
                )
                break
        else:
            add_check(report, "routing-eval-jsonl", "pass", routing_eval, "Routing eval JSONL parsed.")


def ignore_patterns(plugin_dir: Path) -> list[str]:
    ignore_path = plugin_dir / ".gitignore"
    if not ignore_path.exists():
        return []

    patterns: list[str] = []
    for raw_line in ignore_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        patterns.append(line)
    return patterns


def ignored_by_plugin(path: Path, plugin_dir: Path, patterns: list[str]) -> bool:
    try:
        rel = path.relative_to(plugin_dir).as_posix()
    except ValueError:
        return False

    rel_parts = rel.split("/")
    for raw_pattern in patterns:
        directory_only = raw_pattern.endswith("/")
        pattern = raw_pattern.rstrip("/").lstrip("/")
        if not pattern:
            continue

        if "/" not in pattern and pattern in rel_parts:
            return True

        candidates = [pattern]
        if directory_only:
            candidates.append(f"{pattern}/**")

        for candidate in candidates:
            if fnmatch.fnmatch(rel, candidate):
                return True

        if "/**/" in pattern:
            prefix, suffix = pattern.split("/**/", 1)
            if rel == f"{prefix}/{suffix}" or (rel.startswith(f"{prefix}/") and rel.endswith(f"/{suffix}")):
                return True
            if directory_only and (
                rel.startswith(f"{prefix}/{suffix}/") or (rel.startswith(f"{prefix}/") and f"/{suffix}/" in rel)
            ):
                return True

    return False


def audit_generated_artifacts(plugin_dir: Path, report: PluginReport) -> None:
    candidates: list[Path] = []
    for path in plugin_dir.rglob("*"):
        if any(part in GENERATED_PATTERNS for part in path.parts):
            candidates.append(path)

    generated: list[Path] = []
    for path in sorted(candidates, key=lambda item: (len(item.parts), str(item))):
        if not any(parent in generated for parent in path.parents):
            generated.append(path)

    patterns = ignore_patterns(plugin_dir)
    unignored = [path for path in generated if not ignored_by_plugin(path, plugin_dir, patterns)]

    if unignored:
        for path in unignored:
            add_check(
                report,
                "generated-artifact",
                "warn",
                path,
                "Generated artifact exists inside plugin tree.",
                "Remove it from source or ensure it is ignored and not packaged.",
            )
    elif generated:
        add_check(
            report,
            "generated-artifact",
            "pass",
            plugin_dir,
            f"Generated artifact directories found only in ignored paths ({len(generated)}).",
        )
    else:
        add_check(report, "generated-artifact", "pass", plugin_dir, "No generated artifact directories found.")


def audit_plugin(
    repo_root: Path,
    plugin_dir: Path,
    entries: dict[str, dict[str, Any]],
    marketplace_error: str | None,
    strict_sections: bool,
) -> PluginReport:
    report = PluginReport(name=plugin_dir.name, path=str(plugin_dir))

    if not plugin_dir.exists():
        add_check(report, "plugin-dir", "fail", plugin_dir, "Plugin directory does not exist.")
        return report

    audit_manifest(plugin_dir, report)
    audit_marketplace(plugin_dir, report, entries, marketplace_error)
    audit_manifest_dir(plugin_dir, report)
    audit_skills(plugin_dir, report, strict_sections)
    audit_generated_artifacts(plugin_dir, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--plugin", help="Audit one plugin by directory name.")
    parser.add_argument(
        "--strict-sections",
        action="store_true",
        help="Require Contract, Process, Output Format, and Anti-Patterns sections.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    entries, marketplace_error = marketplace_entries(repo_root)

    reports = [
        audit_plugin(repo_root, plugin_dir, entries, marketplace_error, args.strict_sections)
        for plugin_dir in plugin_dirs(repo_root, args.plugin)
    ]

    failures = [check for report in reports for check in report.checks if check.status == "fail"]
    warnings = [check for report in reports for check in report.checks if check.status == "warn"]
    actions = sorted({check.action for check in failures + warnings if check.action})
    payload = {
        "ok": not failures,
        "summary": f"{len(reports)} plugin(s), {len(failures)} failure(s), {len(warnings)} warning(s)",
        "actions": actions,
        "plugins": [report.as_dict() for report in reports],
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        verdict = "healthy" if payload["ok"] else "action-needed"
        print(f"PLUGIN HEALTH: {verdict}")
        print(payload["summary"])
        for action in actions:
            print(f"- {action}")

    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
