from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "plugins/plugin-manager/skills/skillopt-rollout-evidence/scripts/collect_flywheel_evidence.py"


def load_module():
    spec = importlib.util.spec_from_file_location("skillopt_flywheel", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


flywheel = load_module()


def test_recommended_target_uses_most_frequent_expected_skill() -> None:
    routing = {
        "failures": [
            {"expected": ["plugin-manager:manage-plugins"]},
            {"expected": ["plugin-manager:manage-plugins", "plugin-manager:skill-improve"]},
            {"expected": ["lead-analyst:analysis-planning"]},
        ],
        "per_plugin": {},
    }

    target = flywheel.recommended_skill_improve_target(routing)

    assert target["target"] == "plugin-manager:manage-plugins"
    assert target["failure_count"] == 2


def test_recommended_target_falls_back_to_weakest_plugin() -> None:
    routing = {
        "failures": [],
        "per_plugin": {
            "strong": {"cases": 10, "top1_accuracy": 1.0, "top3_accuracy": 1.0},
            "weak": {"cases": 20, "top1_accuracy": 0.75, "top3_accuracy": 0.9},
        },
    }

    target = flywheel.recommended_skill_improve_target(routing)

    assert target["target"] == "weak:<lowest-routing-skill>"
    assert target["plugin_top1_accuracy"] == 0.75


def test_parse_coverage_xml_reads_rates(tmp_path: Path) -> None:
    coverage = tmp_path / "coverage.xml"
    coverage.write_text(
        '<coverage line-rate="0.8123" branch-rate="0.4567" lines-valid="100" lines-covered="81" />',
        encoding="utf-8",
    )

    parsed = flywheel.parse_coverage_xml(coverage)

    assert parsed == {
        "path": str(coverage),
        "line_rate": 0.8123,
        "branch_rate": 0.4567,
        "lines_valid": 100,
        "lines_covered": 81,
    }
