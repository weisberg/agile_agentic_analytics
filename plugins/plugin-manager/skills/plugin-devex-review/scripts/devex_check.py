#!/usr/bin/env python3
"""Fresh-clone onboarding checker for a marketplace plugin.

Dependency-free (stdlib only) so it runs in CI, fresh clones, and agent
sessions before project dependencies are installed. Given a plugin name it
verifies the mechanical onboarding contract a new contributor relies on:

1. README exists and names every skill directory that exists (and names no
   phantom skills that do not exist on disk).
2. A local-test command using ``--plugin-dir`` is documented.
3. Every ``.py`` script referenced from a SKILL.md resolves on disk and compiles
   (``py_compile``); executable bit is reported as a hint.
4. Each skill's frontmatter ``name`` matches its directory name.

Exit status is 0 when there are no failures, 1 otherwise. Warnings never fail.
"""

from __future__ import annotations

import argparse
import os
import py_compile
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


# Match path-like tokens ending in .py (bare filenames, relative paths,
# repo-relative paths, and ${CLAUDE_PLUGIN_ROOT}/... forms).
PY_TOKEN_RE = re.compile(r"[A-Za-z0-9_./${}-]+\.py")
# Kebab / snake identifiers emphasised in a markdown table row: candidate skills.
BOLD_TOKEN_RE = re.compile(r"\*\*([a-z0-9]+(?:[-_][a-z0-9]+)+)\*\*")
SKILL_PATH_RE = re.compile(r"skills/([a-z0-9]+(?:[-_][a-z0-9]+)*)/")


@dataclass
class Result:
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def note(self, message: str) -> None:
        self.notes.append(message)


def skill_dirs(plugin_dir: Path) -> list[Path]:
    skills_root = plugin_dir / "skills"
    if not skills_root.is_dir():
        return []
    return sorted(p.parent for p in skills_root.glob("*/SKILL.md"))


def frontmatter_name(skill_file: Path) -> str | None:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^name:\s*(.+?)\s*$", line)
        if match:
            return match.group(1).strip().strip("'\"")
    return None


def resolve_script(token: str, skill_dir: Path, plugin_dir: Path, repo_root: Path) -> Path | None:
    """Resolve a .py reference the way a reader would, trying the natural roots."""
    token = token.strip()
    if token.startswith("${CLAUDE_PLUGIN_ROOT}/"):
        rel = token[len("${CLAUDE_PLUGIN_ROOT}/") :]
        bases = [plugin_dir]
    elif token.startswith("./"):
        rel = token[2:]
        bases = [skill_dir, plugin_dir, repo_root]
    elif "/" in token:
        rel = token
        bases = [repo_root, plugin_dir, skill_dir]
    else:  # bare filename
        rel = token
        bases = [skill_dir / "scripts", skill_dir, plugin_dir]
    for base in bases:
        candidate = base / rel
        if candidate.is_file():
            return candidate
    # A bare filename may name a script owned by a sibling skill (cross-skill
    # prose reference). Fall back to a plugin-wide search by name.
    if "/" not in token:
        for match in plugin_dir.rglob(rel):
            if match.is_file() and "__pycache__" not in match.parts:
                return match
    return None


def check_readme(plugin_dir: Path, skills: list[Path], result: Result) -> None:
    readme = plugin_dir / "README.md"
    if not readme.is_file():
        result.fail(f"README.md is missing at {readme}")
        return
    text = readme.read_text(encoding="utf-8")

    actual = {p.name for p in skills}

    # (a) Every real skill dir is named somewhere in the README.
    for name in sorted(actual):
        if name not in text:
            result.fail(f"README.md does not mention existing skill '{name}'")

    # (b) No phantom skills: names presented as skills in the README that are not
    # real skill directories. Draw candidates from table-row bold tokens and
    # skills/<name>/ path references, which are the reliable skill signals.
    candidates: set[str] = set()
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            candidates.update(BOLD_TOKEN_RE.findall(line))
    candidates.update(SKILL_PATH_RE.findall(text))
    # Ignore obvious placeholders like skills/<name>.
    candidates = {c for c in candidates if "<" not in c and ">" not in c}
    for name in sorted(candidates - actual):
        result.fail(f"README.md references phantom skill '{name}' with no skills/{name}/ directory")

    # (c) Local-test command with --plugin-dir is documented.
    if "--plugin-dir" not in text:
        result.fail("README.md does not document the local-test command (--plugin-dir)")


def check_scripts(plugin_dir: Path, skills: list[Path], repo_root: Path, result: Result) -> None:
    seen: set[Path] = set()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_cfile = os.path.join(tmp, "compiled.pyc")
        for skill_dir in skills:
            skill_file = skill_dir / "SKILL.md"
            text = skill_file.read_text(encoding="utf-8")
            for token in dict.fromkeys(PY_TOKEN_RE.findall(text)):
                resolved = resolve_script(token, skill_dir, plugin_dir, repo_root)
                if resolved is None:
                    result.fail(f"{skill_dir.name}/SKILL.md references '{token}' which does not resolve on disk")
                    continue
                if resolved in seen:
                    continue
                seen.add(resolved)
                try:
                    py_compile.compile(str(resolved), cfile=tmp_cfile, doraise=True)
                except py_compile.PyCompileError as exc:
                    result.fail(f"referenced script fails to compile: {resolved} ({exc.msg.strip()})")
                    continue
                if not os.access(resolved, os.X_OK):
                    result.note(f"referenced script is not executable (chmod +x optional): {resolved}")


def check_frontmatter(skills: list[Path], result: Result) -> None:
    for skill_dir in skills:
        name = frontmatter_name(skill_dir / "SKILL.md")
        if name is None:
            result.fail(f"{skill_dir.name}/SKILL.md is missing a frontmatter 'name'")
        elif name != skill_dir.name:
            result.fail(
                f"{skill_dir.name}/SKILL.md frontmatter name '{name}' does not match directory '{skill_dir.name}'"
            )


def run(plugin: str, repo_root: Path) -> Result:
    result = Result()
    plugin_dir = repo_root / "plugins" / plugin
    if not plugin_dir.is_dir():
        result.fail(f"plugin directory does not exist: {plugin_dir}")
        return result

    skills = skill_dirs(plugin_dir)
    if not skills:
        result.warn(f"plugin '{plugin}' has no skills under skills/*/SKILL.md")

    check_readme(plugin_dir, skills, result)
    check_scripts(plugin_dir, skills, repo_root, result)
    check_frontmatter(skills, result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin", required=True, help="Plugin directory name under plugins/.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root (default: cwd).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    result = run(args.plugin, repo_root)

    verdict = "action-needed" if result.failures else "ok"
    print(f"DEVEX CHECK: {args.plugin} -> {verdict}")
    print(f"{len(result.failures)} failure(s), {len(result.warnings)} warning(s), {len(result.notes)} note(s)")
    for message in result.failures:
        print(f"FAIL: {message}")
    for message in result.warnings:
        print(f"WARN: {message}")
    for message in result.notes:
        print(f"NOTE: {message}")

    return 1 if result.failures else 0


if __name__ == "__main__":
    sys.exit(main())
