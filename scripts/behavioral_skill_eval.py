#!/usr/bin/env python3
"""Run deterministic behavioral scenario checks for high-traffic skills.

This is the CI-cheap tier for AAA_PLAN Phase 5 behavioral evals. It does not
invoke a model. Instead, each scenario binds a realistic fixture input to a skill
and asserts that the skill still exposes the operational contract needed for a
headless/model tier: evidence requirements, hard gates, artifact outputs, and
completion statuses.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIOS = REPO_ROOT / "tests/behavioral_skill_evals/scenarios.jsonl"
SKILL_RE = re.compile(r"^[a-z0-9-]+:[a-z0-9-]+$")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.S)


@dataclass(frozen=True)
class ScenarioResult:
    scenario_id: str
    skill: str
    ok: bool
    failures: list[str]


def repo_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else REPO_ROOT / candidate


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("#"):
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_number}: scenario must be a JSON object")
        record["_line"] = line_number
        records.append(record)
    return records


def split_skill_ref(skill: str) -> tuple[str, str]:
    if not SKILL_RE.match(skill):
        raise ValueError(f"skill reference must be plugin:skill, got {skill!r}")
    plugin, skill_name = skill.split(":", 1)
    return plugin, skill_name


def skill_path(skill: str) -> Path:
    plugin, skill_name = split_skill_ref(skill)
    return REPO_ROOT / "plugins" / plugin / "skills" / skill_name / "SKILL.md"


def read_frontmatter(text: str) -> str:
    match = FRONTMATTER_RE.match(text)
    return match.group(1) if match else ""


def contains_all(text: str, needles: list[str]) -> list[str]:
    haystack = text.lower()
    return [needle for needle in needles if needle.lower() not in haystack]


def evaluate_scenario(record: dict[str, Any]) -> ScenarioResult:
    scenario_id = str(record.get("id") or f"line-{record.get('_line', '?')}")
    skill = str(record.get("skill", ""))
    failures: list[str] = []

    try:
        path = skill_path(skill)
    except ValueError as exc:
        return ScenarioResult(scenario_id, skill, False, [str(exc)])

    if not path.exists():
        return ScenarioResult(scenario_id, skill, False, [f"missing skill file: {path.relative_to(REPO_ROOT)}"])

    text = path.read_text(encoding="utf-8")
    frontmatter = read_frontmatter(text)
    if not frontmatter:
        failures.append("missing YAML frontmatter")
    if "description:" not in frontmatter:
        failures.append("frontmatter.description is required")

    for heading in ("## Contract", "## Workflow", "## Output Format", "## Anti-Patterns"):
        if heading.lower() not in text.lower():
            failures.append(f"missing strict heading {heading}")

    for fixture in record.get("fixture_paths", []):
        fixture_path = repo_path(str(fixture))
        if not fixture_path.exists():
            failures.append(f"missing fixture: {fixture}")

    missing_terms = contains_all(text, [str(term) for term in record.get("required_skill_terms", [])])
    for term in missing_terms:
        failures.append(f"skill missing required scenario term: {term}")

    expected_artifact = record.get("expected_artifact", {})
    if not isinstance(expected_artifact, dict):
        failures.append("expected_artifact must be an object")
    else:
        artifact_terms = [str(term) for term in expected_artifact.get("required_terms", [])]
        missing_artifact_terms = contains_all(text, artifact_terms)
        for term in missing_artifact_terms:
            failures.append(f"skill missing expected artifact term: {term}")
        path_pattern = str(expected_artifact.get("path_pattern", ""))
        if path_pattern and path_pattern.lower() not in text.lower():
            failures.append(f"skill missing expected artifact path pattern: {path_pattern}")

    statuses = [str(status) for status in record.get("required_statuses", [])]
    missing_statuses = contains_all(text, statuses)
    for status in missing_statuses:
        failures.append(f"skill missing completion status: {status}")

    return ScenarioResult(scenario_id, skill, not failures, failures)


def render_text(results: list[ScenarioResult]) -> str:
    passed = sum(1 for result in results if result.ok)
    lines = [
        "Behavioral skill evaluation (deterministic contract tier)",
        "=" * 60,
        f"Scenarios: {len(results)}  Passed: {passed}  Failed: {len(results) - passed}",
    ]
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        lines.append(f"- {status} {result.scenario_id} ({result.skill})")
        for failure in result.failures:
            lines.append(f"  - {failure}")
    return "\n".join(lines)


def render_json(results: list[ScenarioResult]) -> str:
    return json.dumps(
        {
            "scenarios": len(results),
            "passed": sum(1 for result in results if result.ok),
            "failed": sum(1 for result in results if not result.ok),
            "results": [
                {
                    "id": result.scenario_id,
                    "skill": result.skill,
                    "ok": result.ok,
                    "failures": result.failures,
                }
                for result in results
            ],
        },
        indent=2,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenarios", default=str(DEFAULT_SCENARIOS))
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        records = load_jsonl(repo_path(args.scenarios))
    except ValueError as exc:
        print(f"behavioral skill eval failed: {exc}", file=sys.stderr)
        return 2

    results = [evaluate_scenario(record) for record in records]
    output = render_json(results) if args.format == "json" else render_text(results)
    print(output)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
