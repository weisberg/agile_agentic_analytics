from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "behavioral_skill_eval.py"


def run_eval(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_repository_behavioral_scenarios_pass() -> None:
    result = run_eval()

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Scenarios: 10" in result.stdout
    assert "Failed: 0" in result.stdout


def test_json_output_reports_scenario_count() -> None:
    result = run_eval("--format", "json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["scenarios"] == 10
    assert payload["failed"] == 0


def test_missing_fixture_fails(tmp_path: Path) -> None:
    scenarios = tmp_path / "scenarios.jsonl"
    scenarios.write_text(
        json.dumps(
            {
                "id": "missing-fixture",
                "skill": "lead-analyst:analysis-planning",
                "fixture_paths": ["missing.csv"],
                "required_skill_terms": ["decision"],
                "expected_artifact": {"path_pattern": "workspace/analysis/lead-analyst/plans"},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_eval("--scenarios", str(scenarios))

    assert result.returncode == 1
    assert "missing fixture" in result.stdout
