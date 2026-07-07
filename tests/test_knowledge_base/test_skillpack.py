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


# Canonical Claude Code tool names (see docs/TOOLS_REFERENCE.md). Skill
# `allowed-tools` and agent `tools` frontmatter must draw only from this set —
# no lowercase pseudo-tools (read/write/exec/search) and no fictional KB tools
# (get_page, put_page, sync_kb, ...).
CANONICAL_TOOLS = {
    "Read",
    "Write",
    "Edit",
    "MultiEdit",
    "Bash",
    "Grep",
    "Glob",
    "Agent",
    "WebFetch",
    "WebSearch",
    "NotebookEdit",
    "TodoWrite",
}


def read_frontmatter(text: str) -> dict:
    """Minimal frontmatter reader: handles inline `key: a, b` and YAML `- item` lists."""
    if not text.startswith("---\n"):
        return {}
    end = text.index("\n---", 4)
    block = text[4:end].splitlines()
    data: dict = {}
    i = 0
    while i < len(block):
        line = block[i]
        if line and not line.startswith((" ", "\t")) and ":" in line:
            key, _, rest = line.partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest:
                data[key] = rest
            else:
                items = []
                j = i + 1
                while j < len(block) and block[j].lstrip().startswith("- "):
                    items.append(block[j].lstrip()[2:].strip().strip('"').strip("'"))
                    j += 1
                data[key] = items
                i = j - 1
        i += 1
    return data


def tool_values(raw) -> list[str]:
    if isinstance(raw, list):
        return [v.strip().strip('"').strip("'") for v in raw if v.strip()]
    return [v.strip() for v in str(raw).split(",") if v.strip()]


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

    # Phase 2.2 consolidation: 19 generated skills + 5 hand-authored = 24 total.
    assert len(generated_slugs) == 19
    assert len(skill_files) == 24

    for slug in generated_slugs:
        text = (KB_ROOT / f"skills/{slug}/SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert f"name: {slug}\n" in text
        assert "description: >-\n" in text
        assert "## Contract\n" in text
        assert "## Workflow\n" in text
        assert "## Operating System Backing\n" in text
        assert '"${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py"' in text
        assert "plugins/knowledge-base/scripts/kb_ops.py" not in text
        assert "## Output Format\n" in text
        assert "## Anti-Patterns\n" in text


def test_all_kb_frontmatter_uses_canonical_tool_names() -> None:
    """Every KB skill (`allowed-tools`) and agent (`tools`) frontmatter must use
    only canonical Claude Code tool names, and no skill may use the agent-only
    `tools:` key."""
    offenders: list[str] = []

    for skill_file in sorted((KB_ROOT / "skills").glob("*/SKILL.md")):
        fm = read_frontmatter(skill_file.read_text(encoding="utf-8"))
        rel = skill_file.relative_to(KB_ROOT)
        if "tools" in fm:
            offenders.append(f"{rel}: uses agent-only `tools:` key (should be `allowed-tools:`)")
        for value in tool_values(fm.get("allowed-tools", [])):
            if value not in CANONICAL_TOOLS:
                offenders.append(f"{rel}: non-canonical allowed-tools value {value!r}")

    for agent_file in sorted((KB_ROOT / "agents").glob("*.md")):
        fm = read_frontmatter(agent_file.read_text(encoding="utf-8"))
        rel = agent_file.relative_to(KB_ROOT)
        for value in tool_values(fm.get("tools", [])):
            if value not in CANONICAL_TOOLS:
                offenders.append(f"{rel}: non-canonical tools value {value!r}")

    assert not offenders, "\n".join(offenders)


def test_no_skill_body_hardcodes_repo_plugin_path() -> None:
    """No SKILL.md may hardcode the repo-relative `plugins/knowledge-base/` path;
    cache-safe skills use `${CLAUDE_PLUGIN_ROOT}` instead."""
    offenders: list[str] = []
    for skill_file in sorted((KB_ROOT / "skills").glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        if "plugins/knowledge-base/" in text:
            offenders.append(str(skill_file.relative_to(KB_ROOT)))
    assert not offenders, "hardcoded repo path in: " + ", ".join(offenders)


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
