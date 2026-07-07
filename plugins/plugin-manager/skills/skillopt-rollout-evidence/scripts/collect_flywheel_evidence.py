#!/usr/bin/env python3
"""Collect standing SkillOpt flywheel evidence for a release cycle.

The collector turns the repository's existing quality gates into a compact
SkillOpt evidence bundle:

* strict-section plugin audit;
* portfolio routing accuracy;
* pytest coverage, when run or already available;
* a recommended next skill-improve target based on weakest routing evidence.

It intentionally does not edit skills. It creates durable artifacts that the
SkillOpt skills can use as rollout evidence for the next improvement pass.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def utc_run_id() -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d-%H%M")
    return f"{stamp}-portfolio-flywheel"


def tail(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:]


def run_command(command: list[str], repo_root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "stdout_tail": tail(completed.stdout),
        "stderr_tail": tail(completed.stderr),
    }


def parse_json_output(result: dict[str, Any]) -> dict[str, Any] | None:
    try:
        parsed = json.loads(str(result.get("stdout", result.get("stdout_tail", ""))))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def command_receipt(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "command": result["command"],
        "returncode": result["returncode"],
        "stdout_tail": result.get("stdout_tail", ""),
        "stderr_tail": result.get("stderr_tail", ""),
    }


def parse_coverage_xml(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    root = ET.parse(path).getroot()
    line_rate = root.attrib.get("line-rate")
    branch_rate = root.attrib.get("branch-rate")
    return {
        "path": str(path),
        "line_rate": float(line_rate) if line_rate is not None else None,
        "branch_rate": float(branch_rate) if branch_rate is not None else None,
        "lines_valid": int(root.attrib.get("lines-valid", "0")),
        "lines_covered": int(root.attrib.get("lines-covered", "0")),
    }


def recommended_skill_improve_target(routing: dict[str, Any] | None) -> dict[str, Any]:
    if not routing:
        return {
            "target": None,
            "reason": "Routing evidence was unavailable or unparsable.",
            "failure_count": 0,
        }

    failures = routing.get("failures", [])
    expected_counts: Counter[str] = Counter()
    for failure in failures:
        expected = failure.get("expected", [])
        if isinstance(expected, list) and expected:
            expected_counts[str(expected[0])] += 1

    if expected_counts:
        target, count = expected_counts.most_common(1)[0]
        return {
            "target": target,
            "reason": "Most frequent expected skill among routing top-1 failures.",
            "failure_count": count,
        }

    per_plugin = routing.get("per_plugin", {})
    if isinstance(per_plugin, dict) and per_plugin:
        ranked = sorted(
            (
                (plugin, float(stats.get("top1_accuracy", 1.0)), int(stats.get("cases", 0)))
                for plugin, stats in per_plugin.items()
                if isinstance(stats, dict)
            ),
            key=lambda item: (item[1], -item[2], item[0]),
        )
        plugin, accuracy, cases = ranked[0]
        return {
            "target": f"{plugin}:<lowest-routing-skill>",
            "reason": "No hard routing failures; plugin has the lowest top-1 accuracy.",
            "failure_count": 0,
            "plugin_top1_accuracy": accuracy,
            "plugin_cases": cases,
        }

    return {
        "target": None,
        "reason": "Routing evidence had no failures or per-plugin summary.",
        "failure_count": 0,
    }


def weakest_plugins(routing: dict[str, Any] | None, limit: int = 5) -> list[dict[str, Any]]:
    if not routing or not isinstance(routing.get("per_plugin"), dict):
        return []
    rows = []
    for plugin, stats in routing["per_plugin"].items():
        if not isinstance(stats, dict):
            continue
        rows.append(
            {
                "plugin": plugin,
                "cases": int(stats.get("cases", 0)),
                "top1_accuracy": float(stats.get("top1_accuracy", 0.0)),
                "top3_accuracy": float(stats.get("top3_accuracy", 0.0)),
            }
        )
    return sorted(rows, key=lambda row: (row["top1_accuracy"], row["plugin"]))[:limit]


def render_markdown(evidence: dict[str, Any]) -> str:
    routing = evidence.get("routing", {})
    routing_summary = routing.get("summary") or {}
    portfolio = routing_summary.get("portfolio") or {}
    coverage = evidence.get("coverage") or {}
    target = evidence.get("recommended_skill_improve_target") or {}

    lines = [
        "# SkillOpt Flywheel Evidence",
        "",
        f"Run: `{evidence['run_id']}`",
        f"Generated: `{evidence['generated_at']}`",
        "",
        "## Standing Gates",
        "",
        f"- Strict-section audit: `{evidence['strict_audit']['status']}`",
        (
            "- Routing eval: "
            f"`{routing.get('status', 'unknown')}` "
            f"({portfolio.get('top1_accuracy', 0.0):.1%} top-1 over "
            f"{portfolio.get('cases', 0)} cases)"
        ),
        f"- Test coverage: `{coverage.get('status', 'unknown')}`",
    ]

    if coverage.get("line_rate") is not None:
        lines.append(f"  - Line coverage: {coverage['line_rate']:.1%}")

    lines.extend(
        [
            "",
            "## Weakest Routing Surfaces",
            "",
            "| Plugin | Cases | Top-1 | Top-3 |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in evidence.get("weakest_plugins", []):
        lines.append(f"| {row['plugin']} | {row['cases']} | {row['top1_accuracy']:.1%} | {row['top3_accuracy']:.1%} |")

    lines.extend(
        [
            "",
            "## Recommended Release-Cycle Action",
            "",
            f"- Target: `{target.get('target') or 'none'}`",
            f"- Reason: {target.get('reason', 'No recommendation available.')}",
            "",
            "Run `skill-improve` on the target before the next release cycle, then "
            "run this collector again and record the before/after delta with "
            "`skillopt-rollout-evidence`.",
            "",
            "## Commands",
            "",
        ]
    )

    for command in evidence.get("commands", []):
        command_text = " ".join(command["command"])
        lines.append(f"- `{command_text}` -> `{command['returncode']}`")

    lines.append("")
    return "\n".join(lines)


def build_evidence(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    run_id = args.run_id or utc_run_id()

    audit_cmd = [
        sys.executable,
        "plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py",
        "--strict-sections",
        "--json",
    ]
    routing_cmd = [
        sys.executable,
        "scripts/routing_eval.py",
        "--format",
        "json",
        "--threshold",
        f"{args.routing_threshold:.2f}",
    ]

    commands = []
    audit_result = run_command(audit_cmd, repo_root)
    commands.append(audit_result)
    routing_result = run_command(routing_cmd, repo_root)
    commands.append(routing_result)

    if args.skip_pytest:
        pytest_result = {
            "command": [sys.executable, "-m", "pytest", "--cov=plugins", "--cov-report=xml"],
            "returncode": None,
            "stdout": "skipped by --skip-pytest",
            "stderr": "",
            "stdout_tail": "skipped by --skip-pytest",
            "stderr_tail": "",
        }
    else:
        pytest_result = run_command([sys.executable, "-m", "pytest", "--cov=plugins", "--cov-report=xml"], repo_root)
    commands.append(pytest_result)

    audit_json = parse_json_output(audit_result)
    routing_json = parse_json_output(routing_result)
    coverage_xml = parse_coverage_xml(repo_root / "coverage.xml")

    if args.skip_pytest:
        coverage_status = "existing-coverage" if coverage_xml is not None else "skipped-no-coverage-xml"
    else:
        coverage_status = "pass" if pytest_result["returncode"] == 0 else "fail"

    routing_portfolio = (routing_json or {}).get("portfolio", {})
    routing_status = "pass" if routing_result["returncode"] == 0 else "fail"

    evidence = {
        "run_id": run_id,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "strict_audit": {
            "status": "pass" if audit_result["returncode"] == 0 and (audit_json or {}).get("ok") is True else "fail",
            "summary": (audit_json or {}).get("summary"),
        },
        "routing": {
            "status": routing_status,
            "summary": routing_json,
            "portfolio_status": routing_status,
            "portfolio": routing_portfolio,
        },
        "coverage": {
            "status": coverage_status,
            **(coverage_xml or {}),
        },
        "weakest_plugins": weakest_plugins(routing_json),
        "recommended_skill_improve_target": recommended_skill_improve_target(routing_json),
        "commands": [command_receipt(command) for command in commands],
    }
    return evidence


def write_artifacts(evidence: dict[str, Any], repo_root: Path, output_dir: str | None) -> tuple[Path, Path]:
    run_root = repo_root / (output_dir or f".plugin-manager/skillopt/{evidence['run_id']}/standing-evidence")
    run_root.mkdir(parents=True, exist_ok=True)
    json_path = run_root / "standing-evidence.json"
    md_path = run_root / "standing-evidence.md"
    json_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(evidence), encoding="utf-8")
    return json_path, md_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(default_repo_root()))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--routing-threshold", type=float, default=0.90)
    parser.add_argument(
        "--skip-pytest",
        action="store_true",
        help="Skip pytest execution and parse an existing coverage.xml if present.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    evidence = build_evidence(args)
    json_path, md_path = write_artifacts(evidence, repo_root, args.output_dir)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")

    failed = [
        evidence["strict_audit"]["status"] != "pass",
        evidence["routing"]["status"] != "pass",
        (not args.skip_pytest and evidence["coverage"]["status"] != "pass"),
    ]
    return 1 if any(failed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
