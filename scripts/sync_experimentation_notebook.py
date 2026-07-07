#!/usr/bin/env python3
"""Render the experimentation plugin notebook mirror from the knowledge corpus.

The source of truth is ``knowledge/experimentation``. The packaged plugin mirror
under ``plugins/experimentation/references/notebook`` is generated from it so
skills can read notebook references after marketplace install without reaching
outside the plugin root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "knowledge/experimentation/notebook-sync.json"
GENERATED_BY = "scripts/sync_experimentation_notebook.py"


class SyncError(Exception):
    """Raised for invalid notebook sync configuration."""


def repo_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return REPO_ROOT / candidate


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SyncError(f"config not found: {repo_relative(path)}") from exc
    except json.JSONDecodeError as exc:
        raise SyncError(f"{repo_relative(path)} is not valid JSON: {exc}") from exc

    if not isinstance(config, dict):
        raise SyncError(f"{repo_relative(path)} must contain a JSON object")

    required = ("source_root", "target_root", "manifest_name", "source_glob")
    missing = [key for key in required if key not in config]
    if missing:
        raise SyncError(f"{repo_relative(path)} missing required key(s): {', '.join(missing)}")
    return config


def strip_yaml_frontmatter(text: str) -> str:
    """Remove a top-of-file YAML frontmatter block from rendered plugin docs."""
    if not text.startswith("---\n"):
        return text

    end = text.find("\n---\n", 4)
    if end == -1:
        return text

    rendered = text[end + len("\n---\n") :]
    if rendered.startswith("\n"):
        rendered = rendered[1:]
    return rendered


def render_source(path: Path, transforms: list[str]) -> str:
    text = path.read_text(encoding="utf-8")
    for transform in transforms:
        if transform == "strip_yaml_frontmatter":
            text = strip_yaml_frontmatter(text)
        else:
            raise SyncError(f"unsupported transform {transform!r}")
    return text


def build_sync_plan(
    config: dict[str, Any],
    config_path: Path,
    source_override: str | None = None,
    target_override: str | None = None,
) -> tuple[Path, Path, Path, list[dict[str, Any]], str]:
    source_root = repo_path(source_override or config["source_root"])
    target_root = repo_path(target_override or config["target_root"])
    manifest_path = target_root / config["manifest_name"]
    source_glob = config["source_glob"]
    transforms = list(config.get("transforms", []))
    renames = dict(config.get("renames", {}))

    if not source_root.is_dir():
        raise SyncError(f"source root not found: {repo_relative(source_root)}")

    records: list[dict[str, Any]] = []
    seen_targets: dict[str, str] = {}

    for source in sorted(source_root.glob(source_glob), key=lambda p: p.name):
        if not source.is_file():
            continue
        target_name = renames.get(source.name, source.name)
        previous_source = seen_targets.get(target_name)
        if previous_source is not None:
            raise SyncError(f"multiple sources map to {target_name!r}: {previous_source!r} and {source.name!r}")
        seen_targets[target_name] = source.name

        rendered = render_source(source, transforms)
        records.append(
            {
                "source": source.name,
                "target": target_name,
                "sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
                "bytes": len(rendered.encode("utf-8")),
                "_target_path": target_root / target_name,
                "_text": rendered,
            }
        )

    if not records:
        raise SyncError(f"no source files matched {source_glob!r} in {repo_relative(source_root)}")

    public_records = [{key: value for key, value in record.items() if not key.startswith("_")} for record in records]
    manifest = {
        "generated_by": GENERATED_BY,
        "config": repo_relative(config_path),
        "source_root": repo_relative(source_root),
        "target_root": repo_relative(target_root),
        "source_glob": source_glob,
        "transforms": transforms,
        "preserve_unmanaged_target_files": bool(config.get("preserve_unmanaged_target_files", True)),
        "managed_files": public_records,
    }
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    return source_root, target_root, manifest_path, records, manifest_text


def old_managed_targets(manifest_path: Path) -> set[str]:
    if not manifest_path.exists():
        return set()
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return {
        record["target"]
        for record in payload.get("managed_files", [])
        if isinstance(record, dict) and isinstance(record.get("target"), str)
    }


def sync(
    config_path: Path = DEFAULT_CONFIG,
    check: bool = False,
    source_override: str | None = None,
    target_override: str | None = None,
) -> int:
    config = load_config(config_path)
    _, target_root, manifest_path, records, manifest_text = build_sync_plan(
        config,
        config_path,
        source_override=source_override,
        target_override=target_override,
    )

    stale: list[str] = []
    written = 0
    deleted = 0

    for record in records:
        target_path: Path = record["_target_path"]
        expected_text: str = record["_text"]
        current = target_path.read_text(encoding="utf-8") if target_path.exists() else None
        if current == expected_text:
            continue
        if check:
            stale.append(f"{repo_relative(target_path)} (missing)" if current is None else repo_relative(target_path))
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(expected_text, encoding="utf-8")
        written += 1

    current_targets = {record["target"] for record in records}
    if config.get("delete_stale_managed_files", True):
        for target_name in sorted(old_managed_targets(manifest_path) - current_targets):
            target_path = target_root / target_name
            if not target_path.exists():
                continue
            if check:
                stale.append(f"{repo_relative(target_path)} (stale managed file)")
                continue
            target_path.unlink()
            deleted += 1

    current_manifest = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else None
    if current_manifest != manifest_text:
        if check:
            manifest_label = repo_relative(manifest_path)
            stale.append(f"{manifest_label} (missing)" if current_manifest is None else manifest_label)
        else:
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(manifest_text, encoding="utf-8")
            written += 1

    if check and stale:
        print("Experimentation notebook mirror is stale:", file=sys.stderr)
        for path in stale:
            print(f"- {path}", file=sys.stderr)
        print(f"Run `python3 {GENERATED_BY}` to refresh it.", file=sys.stderr)
        return 1

    managed_count = len(records)
    if check:
        print(f"experimentation notebook mirror current ({managed_count} managed file(s))")
    else:
        print(
            "synced experimentation notebook mirror: "
            f"{written} written, {deleted} deleted, {managed_count} managed file(s)"
        )
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Notebook sync config JSON.")
    parser.add_argument("--check", action="store_true", help="Check the mirror without writing files.")
    parser.add_argument("--source-root", help="Override source_root from the config, primarily for tests.")
    parser.add_argument("--target-root", help="Override target_root from the config, primarily for tests.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        return sync(
            config_path=repo_path(args.config),
            check=args.check,
            source_override=args.source_root,
            target_override=args.target_root,
        )
    except SyncError as exc:
        print(f"notebook sync failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
