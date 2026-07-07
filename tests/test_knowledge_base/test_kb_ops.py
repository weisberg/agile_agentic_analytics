import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
KB_ROOT = REPO_ROOT / "plugins/knowledge-base"
KB_OPS = KB_ROOT / "scripts/kb_ops.py"
SAMPLE_VAULT = KB_ROOT / "references/samples/mini-vault"
ROUTING_EVAL = KB_ROOT / "references/routing-eval.jsonl"
RETRIEVAL_BENCHMARK = KB_ROOT / "references/benchmarks/retrieval-benchmarks.jsonl"
SOURCE_EVENT = KB_ROOT / "references/examples/source-event.json"
WEEKLY_HEALTH = KB_ROOT / "references/examples/weekly-kb-health.yaml"


def run_kb_ops(*args: str, check: bool = True) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(KB_OPS), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    payload = json.loads(result.stdout or result.stderr)
    if check:
        assert result.returncode == 0, payload
    return result.returncode, payload


def test_resolver_check_has_fixture_for_every_skill() -> None:
    _, payload = run_kb_ops("resolver-check")

    assert payload["ok"] is True
    # Phase 2.2 consolidation: the KB portfolio is 24 skills (down from 50).
    assert payload["skills"] == 24
    assert payload["fixtures"] >= payload["skills"]
    assert all(count >= 1 for count in payload["fixture_counts"].values())
    assert not [issue for issue in payload["issues"] if issue["severity"] == "error"]


def test_query_and_retrieval_benchmark_hit_sample_vault() -> None:
    _, query_payload = run_kb_ops(
        "query",
        "Acme renewal risk owner dashboard",
        "--root",
        str(SAMPLE_VAULT),
        "--limit",
        "3",
    )

    result_ids = [record["id"] for record in query_payload["results"]]
    assert "companies/acme-example" in result_ids
    assert query_payload["confidence"] in {"high", "medium"}

    _, benchmark_payload = run_kb_ops(
        "retrieval-benchmark",
        "--root",
        str(SAMPLE_VAULT),
        "--benchmark-file",
        str(RETRIEVAL_BENCHMARK),
    )
    assert benchmark_payload["ok"] is True
    assert benchmark_payload["passed"] == benchmark_payload["total"]
    assert benchmark_payload["recall"] == 1.0


def test_dashboard_and_maintenance_plan_are_machine_actionable() -> None:
    _, dashboard_payload = run_kb_ops("dashboard", "--root", str(SAMPLE_VAULT))
    assert dashboard_payload["ok"] is True
    assert set(dashboard_payload["scorecard"]) == {
        "frontmatter",
        "citations",
        "graph",
        "raw_sources",
        "privacy",
        "resolver",
    }

    _, maintenance_payload = run_kb_ops("maintenance-plan", "--root", str(SAMPLE_VAULT))
    assert maintenance_payload["ok"] is True
    assert isinstance(maintenance_payload["actions"], list)
    for action in maintenance_payload["actions"]:
        assert {"area", "status", "action"} <= set(action)


def test_audits_detect_broken_frontmatter_and_raw_sources(tmp_path: Path) -> None:
    vault = tmp_path / "broken-vault"
    (vault / "pages").mkdir(parents=True)
    (vault / "pages/broken.md").write_text(
        """---
id: pages/broken
title: Broken Page
source: ../../outside.txt
related: [missing/page]
---

# Broken Page

This page claims 42 things and requires a source.
""",
        encoding="utf-8",
    )

    returncode, frontmatter_payload = run_kb_ops("frontmatter-audit", "--root", str(vault), check=False)
    assert returncode == 1
    codes = {issue["code"] for issue in frontmatter_payload["issues"]}
    assert "MISSING_REQUIRED_FIELD" in codes
    assert "SOURCE_ESCAPES_ROOT" in codes

    returncode, raw_payload = run_kb_ops("raw-source-audit", "--root", str(vault), check=False)
    assert returncode == 1
    assert {issue["code"] for issue in raw_payload["issues"]} == {"RAW_SOURCE_MISSING"}


def test_checkpoint_event_normalization_and_schedule_validation(tmp_path: Path) -> None:
    _, checkpoint_payload = run_kb_ops(
        "checkpoint",
        "--root",
        str(tmp_path),
        "--job",
        "Acme Backfill",
        "--completed",
        "sample,index",
        "--remaining",
        "bulk,validate",
        "--validation",
        "sample-pass",
    )
    assert Path(checkpoint_payload["path"]).exists()
    assert checkpoint_payload["checkpoint"]["completed"] == ["sample", "index"]

    _, event_payload = run_kb_ops(
        "normalize-event",
        "--input",
        str(SOURCE_EVENT),
        "--provider",
        "fixture",
        "--event-type",
        "meeting-follow-up",
    )
    envelope = event_payload["envelope"]
    assert envelope["schema_version"] == "kb-source-envelope/v1"
    assert envelope["idempotency_key"].startswith("fixture:meeting-follow-up:")
    assert envelope["content"]["title"] == "Acme Renewal Review Follow-Up"

    _, schedule_payload = run_kb_ops("validate-schedule", "--file", str(WEEKLY_HEALTH))
    assert schedule_payload["ok"] is True
    assert schedule_payload["schedule"]["name"] == "weekly-kb-health"


def test_page_templates_keep_required_frontmatter_and_source_placeholders() -> None:
    for template in sorted((KB_ROOT / "references/templates").glob("*.md")):
        text = template.read_text(encoding="utf-8")
        assert text.startswith("---\n"), template
        assert "\nid:" in text, template
        assert "\ntitle:" in text, template
        assert "\ndescription:" in text, template
        assert "[Source:" in text, template


def test_routing_eval_rows_are_unique_and_jsonl_objects() -> None:
    seen: set[str] = set()
    rows = []
    for raw_line in ROUTING_EVAL.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("//"):
            continue
        payload = json.loads(line)
        rows.append(payload)
        assert {"intent", "expected_skill"} <= set(payload)
        assert payload["intent"].casefold() not in seen
        seen.add(payload["intent"].casefold())

    skill_dirs = {path.parent.name for path in (KB_ROOT / "skills").glob("*/SKILL.md")}
    assert {row["expected_skill"] for row in rows} == skill_dirs
