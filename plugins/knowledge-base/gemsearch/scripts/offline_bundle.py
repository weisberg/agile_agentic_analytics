#!/usr/bin/env python3
"""Build, verify and install the committed macOS arm64 bundle using the stdlib."""

import argparse
import gzip
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

PART_BYTES = 45 * 1024 * 1024
MODEL_ID = "google/embeddinggemma-2"
MODEL_REVISION = "914f7f89142e33e77833254d9c9b90c3cef7303b"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(arguments, **kwargs):
    subprocess.run(arguments, check=True, **kwargs)


def safe_name(name):
    if not name or Path(name).name != name or name in (".", ".."):
        raise ValueError(f"Invalid bundle filename: {name}")
    return name


def file_inventory(root):
    return {
        p.relative_to(root).as_posix(): {"bytes": p.stat().st_size, "sha256": sha256(p)}
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def archive_tree(root, target):
    # Normalize metadata and gzip timestamps so unchanged assets produce unchanged Git blobs.
    with (
        target.open("wb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=6) as zipped,
    ):
        with tarfile.open(fileobj=zipped, mode="w|", format=tarfile.PAX_FORMAT) as archive:
            for path in sorted(root.rglob("*")):
                info = archive.gettarinfo(str(path), path.relative_to(root).as_posix())
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = ""
                info.pax_headers = {}
                info.mode = 0o755 if info.isdir() else 0o644
                if info.isfile():
                    with path.open("rb") as stream:
                        archive.addfile(info, stream)
                else:
                    archive.addfile(info)


def split_archive(path, output, files=None):
    result = {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path), "parts": []}
    if files is not None:
        result["files"] = files
    with path.open("rb") as stream:
        number = 0
        while data := stream.read(PART_BYTES):
            part = output / f"{path.name}.part-{number:03d}"
            part.write_bytes(data)
            result["parts"].append({"name": part.name, "bytes": len(data), "sha256": sha256(part)})
            number += 1
    return result


def validate_manifest(manifest):
    if manifest.get("format") != 1 or manifest.get("target") != "macos-arm64-python3.12":
        raise ValueError("Unsupported offline bundle format or target")
    if manifest.get("model") != {"id": MODEL_ID, "revision": MODEL_REVISION}:
        raise ValueError("Offline bundle model identity differs from gemsearch")
    if set(manifest.get("archives", {})) != {"python", "wheels", "model"}:
        raise ValueError("Offline bundle must contain Python, wheels and model archives")


def checksum_inventory(manifest):
    return "".join(
        f"{part['sha256']}  {part['name']}\n" for archive in manifest["archives"].values() for part in archive["parts"]
    )


def validate_checksum_inventory(bundle, manifest):
    if (bundle / "SHA256SUMS").read_text() != checksum_inventory(manifest):
        raise ValueError("SHA256SUMS differs from the manifest's exact archive part inventory")


def join_archive(bundle, metadata, target):
    name = safe_name(metadata["name"])
    digest = hashlib.sha256()
    total = 0
    if not metadata["parts"]:
        raise ValueError("Archive has no parts")
    with target.open("wb") as out:
        for number, info in enumerate(metadata["parts"]):
            if safe_name(info["name"]) != f"{name}.part-{number:03d}":
                raise ValueError("Archive parts are out of order or missing")
            path = bundle / info["name"]
            if path.stat().st_size != info["bytes"] or sha256(path) != info["sha256"]:
                raise ValueError(f"Bundle checksum mismatch: {path.name}")
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    out.write(block)
                    digest.update(block)
                    total += len(block)
    if total != metadata["bytes"] or digest.hexdigest() != metadata["sha256"]:
        raise ValueError(f"Combined archive checksum mismatch: {name}")


def extract_archive(archive_path, metadata, destination):
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or not (member.isdir() or member.isfile()):
                raise ValueError(f"Unsafe archive member: {member.name}")
        archive.extractall(destination, members=members, filter="data")
    actual = file_inventory(destination)
    if actual != metadata["files"]:
        raise ValueError(f"Extracted file inventory mismatch: {archive_path.name}")


def verify(source):
    manifest = json.loads((source / "offline/manifest.json").read_text())
    validate_manifest(manifest)
    validate_checksum_inventory(source / "offline", manifest)
    if sha256(source / "requirements-macos.lock") != manifest["lock_sha256"]:
        raise ValueError("Dependency lock differs from the offline bundle")
    for name, expected in manifest["source_sha256"].items():
        if sha256(source / name) != expected:
            raise ValueError(f"Source differs from the bundled gemsearch wheel: {name}")
    for metadata in manifest["archives"].values():
        join_archive(source / "offline", metadata, Path(os.devnull))
    print(
        json.dumps(
            {
                "ok": True,
                "target": manifest["target"],
                "archives": len(manifest["archives"]),
                "parts": sum(len(m["parts"]) for m in manifest["archives"].values()),
            },
            indent=2,
        )
    )


def install(source, install_dir):
    if platform.system() != "Darwin" or platform.machine() != "arm64" or sys.version_info[:2] != (3, 12):
        raise ValueError("Offline installation requires bundled macOS arm64 Python 3.12")
    manifest = json.loads((source / "offline/manifest.json").read_text())
    validate_manifest(manifest)
    validate_checksum_inventory(source / "offline", manifest)
    if sha256(source / "requirements-macos.lock") != manifest["lock_sha256"]:
        raise ValueError("Dependency lock differs from the bundled wheels; rebuild the offline bundle")
    for name, expected in manifest["source_sha256"].items():
        if sha256(source / name) != expected:
            raise ValueError(f"Source differs from the bundled gemsearch wheel: {name}")
    environment = dict(
        os.environ,
        PIP_CONFIG_FILE=os.devnull,
        PIP_NO_INDEX="1",
        PIP_DISABLE_PIP_VERSION_CHECK="1",
        HF_HUB_OFFLINE="1",
        HF_HUB_DISABLE_TELEMETRY="1",
        TRANSFORMERS_OFFLINE="1",
    )
    install_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="offline-install-", dir=install_dir) as temp:
        staging = Path(temp)
        for kind in ("wheels", "model"):
            print(f"Verifying and extracting {kind} archive...", flush=True)
            compressed = staging / f"{kind}.tar.gz"
            join_archive(source / "offline", manifest["archives"][kind], compressed)
            destination = staging / kind
            destination.mkdir()
            extract_archive(compressed, manifest["archives"][kind], destination)
            compressed.unlink()
        run([sys.executable, "-m", "venv", str(install_dir)], env=environment)
        python = install_dir / "bin/python"
        wheels = staging / "wheels"
        run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-index",
                "--no-cache-dir",
                "--find-links",
                str(wheels),
                "--require-hashes",
                "-r",
                str(source / "requirements-macos.lock"),
            ],
            env=environment,
        )
        run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-index",
                "--no-deps",
                "--force-reinstall",
                str(wheels / manifest["tool_wheel"]),
            ],
            env=environment,
        )
        cache = install_dir / "share/gemsearch/model-cache"
        cache.parent.mkdir(parents=True, exist_ok=True)
        old = cache.with_name("model-cache.previous")
        if old.exists():
            raise ValueError(f"Previous model backup exists; inspect before reinstalling: {old}")
        if cache.exists():
            cache.rename(old)
        try:
            (staging / "model/model-cache").rename(cache)
        except OSError:
            if old.exists():
                old.rename(cache)
            raise
        if old.exists():
            shutil.rmtree(old)
    print(
        json.dumps(
            {
                "ok": True,
                "install_dir": str(install_dir),
                "offline": True,
                "model": manifest["model"],
                "tool_version": manifest["tool_version"],
            },
            indent=2,
        )
    )


def build(source, downloads, output):
    if list(output.glob("*.part-*")):
        raise ValueError("Output already contains archive parts; choose an empty output directory")
    output.mkdir(parents=True, exist_ok=True)
    python_asset = json.loads((downloads / "python-asset.json").read_text())
    if sha256(downloads / "python.tar.gz") != python_asset["digest"].removeprefix("sha256:"):
        raise ValueError("Portable Python archive differs from the upstream GitHub asset digest")
    # Build only our own wheel. Dependencies must already be downloaded with pip's hash verification.
    environment = dict(os.environ, PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1", SOURCE_DATE_EPOCH="1791936000")
    wheels = downloads / "wheels"
    run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--no-index",
            "--wheel-dir",
            str(wheels),
            str(source),
        ],
        env=environment,
    )
    tool_wheels = list(wheels.glob("aaa_gemsearch-*.whl"))
    if len(tool_wheels) != 1:
        raise ValueError("Expected exactly one gemsearch wheel")
    tool_version = tool_wheels[0].name.split("-")[1]
    manifest = {
        "format": 1,
        "target": "macos-arm64-python3.12",
        "python_version": "3.12.13",
        "minimum_macos": "14",
        "tool_version": tool_version,
        "tool_wheel": tool_wheels[0].name,
        "model": {"id": MODEL_ID, "revision": MODEL_REVISION},
        "lock_sha256": sha256(source / "requirements-macos.lock"),
        "source_sha256": {p.relative_to(source).as_posix(): sha256(p) for p in sorted((source / "src").rglob("*.py"))},
        "python_upstream": python_asset,
        "archives": {},
    }
    manifest["archives"]["python"] = split_archive(downloads / "python.tar.gz", output)
    model_repo = "models--google--embeddinggemma-2"
    snapshot = downloads / "model-download" / model_repo / "snapshots" / MODEL_REVISION
    tree = json.loads((downloads / "model-download" / model_repo / "trees" / f"{MODEL_REVISION}.json").read_text())
    for name, info in tree["files"].items():
        path = snapshot / name
        if not path.is_file() or path.stat().st_size != info["size"]:
            raise ValueError(f"Incomplete upstream model snapshot: {name}")
        if info.get("lfs_sha256") and sha256(path) != info["lfs_sha256"]:
            raise ValueError(f"Upstream model LFS checksum mismatch: {name}")
    with tempfile.TemporaryDirectory(prefix="offline-build-", dir=downloads) as temp:
        root = Path(temp)
        model = root / "model"
        cache = model / "model-cache" / model_repo
        shutil.copytree(snapshot, cache / "snapshots" / MODEL_REVISION, symlinks=False)
        (cache / "trees").mkdir(parents=True)
        shutil.copy2(downloads / "model-download" / model_repo / "trees" / f"{MODEL_REVISION}.json", cache / "trees")
        shutil.copy2(downloads / "MODEL-LICENSE-Apache-2.0.txt", cache / "snapshots" / MODEL_REVISION / "LICENSE")
        for kind, directory in (("wheels", wheels), ("model", model)):
            print(f"Compressing {kind}...", flush=True)
            archive = root / f"{kind}.tar.gz"
            archive_tree(directory, archive)
            manifest["archives"][kind] = split_archive(archive, output, file_inventory(directory))
    validate_manifest(manifest)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "SHA256SUMS").write_text(checksum_inventory(manifest))
    print(
        json.dumps(
            {
                "ok": True,
                "archives": {
                    name: {"bytes": a["bytes"], "parts": len(a["parts"])} for name, a in manifest["archives"].items()
                },
            },
            indent=2,
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    builder = commands.add_parser("build")
    builder.add_argument("--source", type=Path, required=True)
    builder.add_argument("--downloads", type=Path, required=True)
    builder.add_argument("--output", type=Path, required=True)
    installer = commands.add_parser("install")
    installer.add_argument("--source", type=Path, required=True)
    installer.add_argument("--install-dir", type=Path, required=True)
    verifier = commands.add_parser("verify")
    verifier.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        build(args.source.resolve(), args.downloads.resolve(), args.output.resolve())
    elif args.command == "verify":
        verify(args.source.resolve())
    else:
        install(args.source.resolve(), args.install_dir.expanduser().resolve())


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1) from exc
