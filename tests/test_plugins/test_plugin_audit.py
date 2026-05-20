import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT = REPO_ROOT / "plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py"


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def run_audit(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AUDIT), "--repo-root", str(tmp_path), *args, "--json"],
        check=False,
        capture_output=True,
        text=True,
    )


def make_marketplace(tmp_path: Path, plugin_name: str = "demo") -> None:
    write(
        tmp_path / ".claude-plugin/marketplace.json",
        json.dumps(
            {
                "name": "test-marketplace",
                "plugins": [
                    {
                        "name": plugin_name,
                        "source": f"./plugins/{plugin_name}",
                        "description": "Demo plugin.",
                        "version": "0.1.0",
                        "keywords": ["demo"],
                        "license": "MIT",
                    }
                ],
            }
        ),
    )


def make_plugin(tmp_path: Path, plugin_name: str = "demo") -> Path:
    plugin = tmp_path / "plugins" / plugin_name
    write(
        plugin / ".claude-plugin/plugin.json",
        json.dumps(
            {
                "name": plugin_name,
                "description": "Demo plugin.",
                "version": "0.1.0",
                "author": {"name": "Example"},
                "license": "MIT",
                "keywords": ["demo"],
            }
        ),
    )
    write(
        plugin / "skills/demo/SKILL.md",
        """---
name: demo
description: Demo skill.
---

# Demo

## Contract

Works.

## Workflow

Run it.

## Output Format

Text.

## Anti-Patterns

Do not break it.
""",
    )
    write(
        plugin / "skills/demo/routing-eval.jsonl",
        """// GBrain-style comment
{"intent":"run demo","expected_skill":"demo"}
""",
    )
    return plugin


def test_plugin_audit_passes_clean_plugin(tmp_path: Path) -> None:
    make_marketplace(tmp_path)
    make_plugin(tmp_path)

    result = run_audit(tmp_path, "--plugin", "demo", "--strict-sections")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["plugins"][0]["fail_count"] == 0


def test_plugin_audit_flags_missing_marketplace_entry(tmp_path: Path) -> None:
    make_marketplace(tmp_path, plugin_name="other")
    make_plugin(tmp_path, plugin_name="demo")

    result = run_audit(tmp_path, "--plugin", "demo")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    failures = [
        check["name"]
        for plugin in payload["plugins"]
        for check in plugin["checks"]
        if check["status"] == "fail"
    ]
    assert "marketplace-entry" in failures


def test_plugin_audit_flags_skill_without_frontmatter(tmp_path: Path) -> None:
    make_marketplace(tmp_path)
    plugin = make_plugin(tmp_path)
    write(plugin / "skills/demo/SKILL.md", "# Demo\n\nNo frontmatter.\n")

    result = run_audit(tmp_path, "--plugin", "demo")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    failures = [
        check["name"]
        for plugin_report in payload["plugins"]
        for check in plugin_report["checks"]
        if check["status"] == "fail"
    ]
    assert "skill-frontmatter" in failures


def test_plugin_audit_flags_invalid_routing_eval_jsonl(tmp_path: Path) -> None:
    make_marketplace(tmp_path)
    plugin = make_plugin(tmp_path)
    write(plugin / "skills/demo/routing-eval.jsonl", "// comment ok\nnot json\n")

    result = run_audit(tmp_path, "--plugin", "demo")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    failures = [
        check["name"]
        for plugin_report in payload["plugins"]
        for check in plugin_report["checks"]
        if check["status"] == "fail"
    ]
    assert "routing-eval-jsonl" in failures


def test_plugin_audit_accepts_ignored_generated_artifacts(tmp_path: Path) -> None:
    make_marketplace(tmp_path)
    plugin = make_plugin(tmp_path)
    write(plugin / ".gitignore", "cache/**/__pycache__/\ncache/target/\n")
    write(plugin / "cache/__pycache__/demo.pyc", "")
    write(plugin / "cache/target/output.bin", "")

    result = run_audit(tmp_path, "--plugin", "demo")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["plugins"][0]["warn_count"] == 0
    generated_checks = [
        check
        for check in payload["plugins"][0]["checks"]
        if check["name"] == "generated-artifact"
    ]
    assert generated_checks[0]["status"] == "pass"
