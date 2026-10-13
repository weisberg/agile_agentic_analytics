"""Agent-friendly CLI. Search results are source pointers, never KB metadata writes."""

import argparse
import json
import os
import platform
import sqlite3
import sys

from . import __version__
from .embedding import MODEL_ID, MODEL_REVISION, PythonEmbedder, SearchError, download_model
from .index import MAX_BYTES, build_index, database_path, root_path, search, status


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def parser():
    result = argparse.ArgumentParser(description="Local EmbeddingGemma 2 file search; complements vaultli")
    result.add_argument("--version", action="version", version=__version__)
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("download-model", help="Download the pinned model once; only command requiring network")
    for name in ("doctor", "index", "search", "status"):
        sub = commands.add_parser(name)
        sub.add_argument("--json", action="store_true", help="Machine-readable output (also the default)")
        if name in ("doctor", "index", "search"):
            sub.add_argument("--device", choices=("auto", "mps", "cpu"), default="auto")
            sub.add_argument("--batch-size", type=positive, default=4)
        if name != "doctor":
            sub.add_argument("--root", required=True, help="Explicit directory scope")
            sub.add_argument("--db", help="SQLite cache outside the indexed directory")
        if name == "index":
            sub.add_argument("--exclude", action="append", default=[], help="Root-relative glob; repeatable")
            sub.add_argument("--max-bytes", type=positive, default=MAX_BYTES)
            sub.add_argument("--dry-run", action="store_true")
            sub.add_argument("--rebuild", action="store_true", help="Re-embed when model or indexing policy changes")
        if name == "search":
            sub.add_argument("query")
            sub.add_argument("--mode", choices=("semantic", "lexical", "hybrid"), default="hybrid")
            sub.add_argument("--limit", type=positive, default=10)
            sub.add_argument("--path", default="*", help="Root-relative glob filter")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    os.umask(0o077)
    try:
        if args.command == "download-model":
            output = {"model": MODEL_ID, "revision": MODEL_REVISION, "snapshot": download_model()}
        elif args.command == "doctor":
            backend = PythonEmbedder(args.device, args.batch_size)
            vector = backend.query("local file search health check")
            output = {
                "ok": True,
                "version": __version__,
                "python": platform.python_version(),
                "machine": platform.machine(),
                "device": backend.device,
                "dimensions": len(vector),
                "identity": backend.identity(),
            }
        else:
            root = root_path(args.root)
            db = database_path(root, args.db)
            if args.command == "status":
                output = status(root, db)
            else:
                backend = PythonEmbedder(args.device, args.batch_size)
                if args.command == "index":
                    output = build_index(root, db, backend, args.exclude, args.max_bytes, args.dry_run, args.rebuild)
                else:
                    output = search(root, db, args.query, backend, args.mode, args.limit, args.path)
        print(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False))
        # Partial extraction failures remain visible to callers; valid files are still searchable.
        return 2 if output.get("issues") else 0
    except (SearchError, OSError, sqlite3.Error, ValueError, ImportError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
