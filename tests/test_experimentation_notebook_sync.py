from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "sync_experimentation_notebook.py"


def run_sync(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def write_config(tmp_path: Path, source_root: Path, target_root: Path) -> Path:
    config = {
        "source_root": str(source_root),
        "target_root": str(target_root),
        "manifest_name": "NOTEBOOK_SYNC_MANIFEST.json",
        "source_glob": "*.md",
        "transforms": ["strip_yaml_frontmatter"],
        "preserve_unmanaged_target_files": True,
        "delete_stale_managed_files": True,
        "renames": {"source.md": "rendered.md"},
    }
    path = tmp_path / "notebook-sync.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def test_sync_renders_source_docs_and_preserves_unmanaged_files(tmp_path: Path) -> None:
    source_root = tmp_path / "knowledge"
    target_root = tmp_path / "plugin/notebook"
    source_root.mkdir(parents=True)
    target_root.mkdir(parents=True)
    (source_root / "source.md").write_text("---\ntitle: Source\n---\n\n# Body\n", encoding="utf-8")
    (target_root / "extra.md").write_text("plugin-only reference\n", encoding="utf-8")
    config = write_config(tmp_path, source_root, target_root)

    result = run_sync("--config", str(config))

    assert result.returncode == 0, result.stderr
    assert (target_root / "rendered.md").read_text(encoding="utf-8") == "# Body\n"
    assert (target_root / "extra.md").read_text(encoding="utf-8") == "plugin-only reference\n"

    manifest = json.loads((target_root / "NOTEBOOK_SYNC_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["source_root"] == str(source_root)
    assert manifest["target_root"] == str(target_root)
    assert manifest["managed_files"][0]["source"] == "source.md"
    assert manifest["managed_files"][0]["target"] == "rendered.md"

    check = run_sync("--config", str(config), "--check")
    assert check.returncode == 0, check.stderr


def test_check_fails_when_rendered_mirror_drifts(tmp_path: Path) -> None:
    source_root = tmp_path / "knowledge"
    target_root = tmp_path / "plugin/notebook"
    source_root.mkdir(parents=True)
    target_root.mkdir(parents=True)
    (source_root / "source.md").write_text("---\ntitle: Source\n---\n\n# Body\n", encoding="utf-8")
    config = write_config(tmp_path, source_root, target_root)

    assert run_sync("--config", str(config)).returncode == 0
    (target_root / "rendered.md").write_text("# Drifted\n", encoding="utf-8")

    result = run_sync("--config", str(config), "--check")

    assert result.returncode == 1
    assert "rendered.md" in result.stderr


def test_repository_experimentation_notebook_mirror_is_current() -> None:
    result = run_sync("--check")

    assert result.returncode == 0, result.stdout + result.stderr
