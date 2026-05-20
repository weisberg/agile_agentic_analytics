import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
KB_ROOT = REPO_ROOT / "plugins/knowledge-base"
AUDIT = REPO_ROOT / "plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py"
GENERATOR = KB_ROOT / "scripts/generate_kb_roadmap_skills.py"
SAMPLE_VAULT = KB_ROOT / "references/samples/mini-vault"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_kb_roadmap_skills", GENERATOR)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_json(command: list[str], **kwargs) -> tuple[int, dict]:
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        **kwargs,
    )
    stream = result.stdout or result.stderr
    return result.returncode, json.loads(stream)


def test_knowledge_base_plugin_audit_is_clean() -> None:
    returncode, payload = run_json(
        [sys.executable, str(AUDIT), "--plugin", "knowledge-base", "--json"],
        cwd=REPO_ROOT,
    )

    assert returncode == 0
    assert payload["ok"] is True
    assert payload["plugins"][0]["fail_count"] == 0
    assert payload["plugins"][0]["warn_count"] == 0


def test_generated_skill_portfolio_has_required_shape() -> None:
    module = load_generator()
    generated_slugs = {spec["slug"] for spec in module.SKILL_SPECS}
    skill_files = sorted((KB_ROOT / "skills").glob("*/SKILL.md"))

    assert len(generated_slugs) == 45
    assert len(skill_files) >= 50

    for slug in generated_slugs:
        text = (KB_ROOT / f"skills/{slug}/SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert f"name: {slug}\n" in text
        assert "description: >-\n" in text
        assert "## Contract\n" in text
        assert "## Workflow\n" in text
        assert "## Output Format\n" in text
        assert "## Anti-Patterns\n" in text


def test_issue_coverage_maps_all_kb_roadmap_issues() -> None:
    coverage = (KB_ROOT / "references/issue-coverage.md").read_text(encoding="utf-8")

    for issue_number in range(30, 83):
        assert f"#{issue_number} " in coverage or f"#{issue_number}:" in coverage

    for required in [
        "plugin-manager",
        "upstream-skill-harvest",
        "knowledge-base-vaultli.yml",
        "references/samples/mini-vault/",
    ]:
        assert required in coverage


def test_sample_vault_builds_first_index_and_validates(tmp_path: Path) -> None:
    vault = tmp_path / "mini-vault"
    shutil.copytree(SAMPLE_VAULT, vault)
    (vault / "INDEX.jsonl").unlink(missing_ok=True)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(KB_ROOT)

    returncode, index_payload = run_json(
        [sys.executable, "-m", "vaultli", "--json", "index", "--root", str(vault)],
        cwd=REPO_ROOT,
        env=env,
    )
    assert returncode == 0, index_payload
    assert index_payload["ok"] is True
    assert index_payload["result"]["indexed"] >= 7

    returncode, validation_payload = run_json(
        [sys.executable, "-m", "vaultli", "--json", "validate", "--root", str(vault)],
        cwd=REPO_ROOT,
        env=env,
    )
    assert returncode == 0, validation_payload
    assert validation_payload["ok"] is True

    returncode, search_payload = run_json(
        [
            sys.executable,
            "-m",
            "vaultli",
            "--json",
            "search",
            "--root",
            str(vault),
            "--tag",
            "renewal-risk",
            "--limit",
            "3",
        ],
        cwd=REPO_ROOT,
        env=env,
    )
    assert returncode == 0, search_payload
    result_ids = {record["id"] for record in search_payload["result"]["results"]}
    assert "companies/acme-example" in result_ids
