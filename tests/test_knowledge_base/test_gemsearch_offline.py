"""Small, offline tests for archive integrity and extraction boundaries."""

import importlib.util
import io
import json
import sys
import tarfile
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2] / "plugins/knowledge-base/gemsearch"
sys.path.insert(0, str(PACKAGE / "src"))
from gemsearch import embedding

spec = importlib.util.spec_from_file_location("offline_bundle", PACKAGE / "scripts/offline_bundle.py")
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


def test_archive_round_trip_and_deterministic_compression(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    (source / "nested").mkdir()
    (source / "nested/text.txt").write_text("local evidence\n")
    archive = tmp_path / "model.tar.gz"
    bundle.archive_tree(source, archive)
    expected = bundle.sha256(archive)
    bundle.archive_tree(source, tmp_path / "repeat.tar.gz")
    assert bundle.sha256(tmp_path / "repeat.tar.gz") == expected
    parts = tmp_path / "parts"
    parts.mkdir()
    monkeypatch.setattr(bundle, "PART_BYTES", 30)
    meta = bundle.split_archive(archive, parts, bundle.file_inventory(source))
    assert len(meta["parts"]) > 1
    joined = tmp_path / "joined.tar.gz"
    bundle.join_archive(parts, meta, joined)
    assert bundle.sha256(joined) == expected
    output = tmp_path / "extracted"
    output.mkdir()
    bundle.extract_archive(joined, meta, output)
    assert (output / "nested/text.txt").read_text() == "local evidence\n"


def test_modified_missing_and_reordered_parts_are_rejected(tmp_path, monkeypatch):
    archive = tmp_path / "wheels.tar.gz"
    archive.write_bytes(b"abcdef")
    output = tmp_path / "parts"
    output.mkdir()
    monkeypatch.setattr(bundle, "PART_BYTES", 3)
    meta = bundle.split_archive(archive, output)
    reordered = json.loads(json.dumps(meta))
    reordered["parts"].reverse()
    with pytest.raises(ValueError, match="order"):
        bundle.join_archive(output, reordered, tmp_path / "joined")
    first = output / meta["parts"][0]["name"]
    first.write_bytes(b"BAD")
    with pytest.raises(ValueError, match="checksum"):
        bundle.join_archive(output, meta, tmp_path / "joined")
    first.unlink()
    with pytest.raises(FileNotFoundError):
        bundle.join_archive(output, meta, tmp_path / "joined")


@pytest.mark.parametrize("name,kind", [("../escape", "file"), ("/absolute", "file"), ("link", "symlink")])
def test_unsafe_tar_members_are_rejected(tmp_path, name, kind):
    archive = tmp_path / "unsafe.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        info = tarfile.TarInfo(name)
        if kind == "symlink":
            info.type = tarfile.SYMTYPE
            info.linkname = "../../outside"
            stream.addfile(info)
        else:
            info.size = 1
            stream.addfile(info, io.BytesIO(b"x"))
    with pytest.raises(ValueError, match="Unsafe"):
        bundle.extract_archive(archive, {"files": {}}, tmp_path / "extract")
    assert not (tmp_path / "escape").exists()


def test_extracted_inventory_mismatch_is_rejected(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "evidence.txt").write_text("evidence")
    archive = tmp_path / "files.tar.gz"
    bundle.archive_tree(source, archive)
    with pytest.raises(ValueError, match="inventory mismatch"):
        bundle.extract_archive(archive, {"files": {}}, tmp_path / "extract")


@pytest.mark.parametrize("name", ["../bad", "/absolute", "", ".."])
def test_bundle_filenames_cannot_escape_directory(name):
    with pytest.raises(ValueError, match="filename"):
        bundle.safe_name(name)


def test_bundled_model_cache_precedence(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMSEARCH_MODEL_CACHE", raising=False)
    monkeypatch.setattr(sys, "prefix", str(tmp_path))
    local = tmp_path / "share/gemsearch/model-cache"
    local.mkdir(parents=True)
    assert embedding.model_cache() == local
    override = tmp_path / "override"
    monkeypatch.setenv("GEMSEARCH_MODEL_CACHE", str(override))
    assert embedding.model_cache() == override


def test_model_identity_cannot_silently_change():
    manifest = {
        "format": 1,
        "target": "macos-arm64-python3.12",
        "model": {"id": bundle.MODEL_ID, "revision": "different"},
        "archives": {"python": {}, "wheels": {}, "model": {}},
    }
    with pytest.raises(ValueError, match="identity"):
        bundle.validate_manifest(manifest)


@pytest.mark.parametrize("change", ["missing", "stale", "omitted", "extra"])
def test_checksum_inventory_must_exactly_match_manifest(tmp_path, change):
    manifest = {
        "archives": {
            "python": {
                "parts": [
                    {"sha256": "a" * 64, "name": "python.tar.gz.part-000"},
                    {"sha256": "b" * 64, "name": "python.tar.gz.part-001"},
                ]
            }
        }
    }
    expected = bundle.checksum_inventory(manifest)
    path = tmp_path / "SHA256SUMS"
    path.write_text(expected)
    bundle.validate_checksum_inventory(tmp_path, manifest)
    if change == "missing":
        path.unlink()
    elif change == "stale":
        path.write_text(expected.replace("a" * 64, "c" * 64))
    elif change == "omitted":
        path.write_text(expected.splitlines()[0] + "\n")
    else:
        path.write_text(expected + "unexpected inventory entry\n")
    with pytest.raises((OSError, ValueError)):
        bundle.validate_checksum_inventory(tmp_path, manifest)
