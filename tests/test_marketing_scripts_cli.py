from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = REPO_ROOT / "plugins" / "marketing-analytics" / "skills"
DOCUMENTED_CLI_SCRIPTS = {
    "email-analytics/scripts/deliverability_check.py",
    "email-analytics/scripts/engagement_analysis.py",
    "email-analytics/scripts/list_health.py",
    "email-analytics/scripts/send_time_optimizer.py",
    "funnel-analysis/scripts/build_funnel.py",
    "funnel-analysis/scripts/funnel_stats.py",
    "funnel-analysis/scripts/revenue_impact.py",
}


def marketing_scripts() -> list[Path]:
    return sorted(path for path in SCRIPT_ROOT.rglob("scripts/*.py") if not path.name.startswith("_"))


@pytest.mark.parametrize("script_path", marketing_scripts(), ids=lambda p: str(p.relative_to(SCRIPT_ROOT)))
def test_marketing_scripts_accept_help_flag(script_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("relative_path", sorted(DOCUMENTED_CLI_SCRIPTS))
def test_documented_marketing_clis_show_usage(relative_path: str) -> None:
    script_path = SCRIPT_ROOT / relative_path

    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "usage:" in result.stdout.lower()
