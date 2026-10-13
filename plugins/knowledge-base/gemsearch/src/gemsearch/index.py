"""Transactional, root-scoped SQLite search cache, independent of vaultli."""

import fnmatch
import hashlib
import json
import os
import re
import sqlite3
import struct
from datetime import datetime, timezone
from pathlib import Path

from .embedding import SearchError, normalize
from .files import CHUNK_CHARS, EXTRACT_VERSION, OVERLAP, chunks, extract, read_bytes, walk

MAX_BYTES = 20 * 1024 * 1024
SCHEMA = 1


def root_path(value):
    root = Path(value).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise SearchError("Root must be an existing directory")
    return root


def default_db(root):
    base = os.environ.get("GEMSEARCH_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    base = Path(base).expanduser() if base else Path.home() / "Library/Application Support/aaa-gemsearch"
    digest = hashlib.sha256(str(root).encode()).hexdigest()[:24]
    return base / "gemsearch" / digest / "index.sqlite3"


def database_path(root, value=None):
    path = Path(value).expanduser().resolve() if value else default_db(root).resolve()
    if path == root or root in path.parents:
        raise SearchError("Keep the search database outside the indexed root")
    return path


def connect(path, create=False):
    if create:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        # A private file before sqlite creates journals alongside it.
        fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        os.close(fd)
        os.chmod(path, 0o600)
    elif not path.is_file():
        raise SearchError("Search index is missing; run gemsearch index --root <directory>")
    conn = sqlite3.connect(str(path) if create else path.as_uri() + "?mode=ro", uri=not create, timeout=5)
    conn.row_factory = sqlite3.Row
    if create:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, sha256 TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY, path TEXT NOT NULL REFERENCES files(path) ON DELETE CASCADE,
                page INTEGER, line_start INTEGER NOT NULL, line_end INTEGER NOT NULL,
                text TEXT NOT NULL, vector BLOB NOT NULL
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(text, path UNINDEXED);
            CREATE TRIGGER IF NOT EXISTS chunks_insert AFTER INSERT ON chunks BEGIN
                INSERT INTO chunks_fts(rowid, text, path) VALUES (new.id, new.text, new.path);
            END;
            CREATE TRIGGER IF NOT EXISTS chunks_delete AFTER DELETE ON chunks BEGIN
                DELETE FROM chunks_fts WHERE rowid=old.id;
            END;
        """)
    return conn


def metadata(conn):
    return {row["key"]: json.loads(row["value"]) for row in conn.execute("SELECT * FROM metadata")}


def pack(vector):
    return struct.pack(f"<{len(vector)}f", *normalize(vector))


def unpack(blob):
    return struct.unpack(f"<{len(blob) // 4}f", blob)


def check_scope(meta, root, embedder=None):
    if meta.get("root") != str(root) or meta.get("schema") != SCHEMA:
        raise SearchError("Index root/schema differs; choose a different --db or rebuild with --rebuild")
    if embedder is not None and meta.get("identity") != embedder.identity():
        raise SearchError("Embedding model/revision/prompt differs; rebuild with --rebuild")


def build_index(root, db, embedder, excludes=(), max_bytes=MAX_BYTES, dry_run=False, rebuild=False):
    # Complete traversal before opening a write transaction: walk failures never cause pruning.
    paths = list(walk(root, excludes))
    if dry_run:
        return {"dry_run": True, "root": str(root), "db": str(db), "files": [str(p.relative_to(root)) for p in paths]}
    conn = connect(db, create=True)
    try:
        # Serialize writers before reading previous state; rollback includes pruning and all embeddings.
        conn.execute("BEGIN IMMEDIATE")
        old = metadata(conn)
        if old and old.get("root") != str(root):
            raise SearchError("Database belongs to another root; choose a separate --db")
        policy = {
            "excludes": sorted(excludes),
            "max_bytes": max_bytes,
            "extract": EXTRACT_VERSION,
            "chunk_chars": CHUNK_CHARS,
            "overlap": OVERLAP,
        }
        if old and not rebuild:
            check_scope(old, root, embedder)
            if old.get("policy") != policy:
                raise SearchError("Indexing policy changed; use --rebuild to apply it")
        if rebuild:
            conn.execute("DELETE FROM files")
        previous = {row["path"]: row["sha256"] for row in conn.execute("SELECT * FROM files")}
        seen = set()
        report = {"root": str(root), "db": str(db), "indexed": 0, "unchanged": 0, "removed": 0, "issues": []}
        for path in paths:
            relative = path.relative_to(root).as_posix()
            seen.add(relative)
            try:
                data = read_bytes(path, max_bytes)
                sha = hashlib.sha256(data).hexdigest()
                if previous.get(relative) == sha:
                    report["unchanged"] += 1
                    continue
                pieces = list(chunks(extract(path, data)))
                if not pieces:
                    raise SearchError("No extractable text (scanned PDFs need OCR first)")
            except (SearchError, OSError, ValueError, KeyError, UnicodeError) as exc:
                # Remove any cached version of files which can no longer be read.
                conn.execute("DELETE FROM files WHERE path=?", (relative,))
                report["issues"].append({"path": relative, "error": str(exc)})
                continue
            conn.execute("DELETE FROM files WHERE path=?", (relative,))
            conn.execute("INSERT INTO files VALUES (?, ?)", (relative, sha))
            # Bound peak inference memory even for long documents. A backend failure rolls back the entire run.
            for offset in range(0, len(pieces), embedder.batch_size):
                batch = pieces[offset : offset + embedder.batch_size]
                vectors = embedder.documents(path.name, [p["text"] for p in batch])
                if len(vectors) != len(batch):
                    raise SearchError("Embedding count does not match chunks")
                for piece, vector in zip(batch, vectors):
                    if len(vector) != embedder.identity()["dimensions"]:
                        raise SearchError("Embedding dimensions differ from index identity")
                    conn.execute(
                        "INSERT INTO chunks(path,page,line_start,line_end,text,vector) VALUES(?,?,?,?,?,?)",
                        (relative, piece["page"], piece["line_start"], piece["line_end"], piece["text"], pack(vector)),
                    )
            report["indexed"] += 1
        for removed in previous.keys() - seen:
            conn.execute("DELETE FROM files WHERE path=?", (removed,))
            report["removed"] += 1
        state = {
            "schema": SCHEMA,
            "root": str(root),
            "identity": embedder.identity(),
            "policy": policy,
            "indexed_at": datetime.now(timezone.utc).isoformat(),
            "issues": report["issues"],
        }
        for key, value in state.items():
            conn.execute("INSERT OR REPLACE INTO metadata VALUES (?,?)", (key, json.dumps(value)))
        conn.commit()
        report["chunks"] = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        return report
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def status(root, db):
    conn = connect(db)
    try:
        meta = metadata(conn)
        check_scope(meta, root)
        return {
            **meta,
            "db": str(db),
            "files": conn.execute("SELECT COUNT(*) FROM files").fetchone()[0],
            "chunks": conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0],
        }
    finally:
        conn.close()


def search(root, db, query, embedder, mode="hybrid", limit=10, path_glob="*"):
    if not query.strip():
        raise SearchError("Query cannot be blank")
    conn = connect(db)
    try:
        meta = metadata(conn)
        check_scope(meta, root, None if mode == "lexical" else embedder)
        rows = {
            r["id"]: dict(r) for r in conn.execute("SELECT * FROM chunks") if fnmatch.fnmatchcase(r["path"], path_glob)
        }
        semantic = []
        cosine = {}
        if mode != "lexical" and rows:
            import numpy as np

            vector = embedder.query(query)
            if len(vector) != meta["identity"]["dimensions"]:
                raise SearchError("Query and index embedding dimensions differ; rebuild the index")
            # Matrix blocks bound temporary vector memory; SQLite remains the only persisted index.
            ids = list(rows)
            for offset in range(0, len(ids), 1024):
                batch = ids[offset : offset + 1024]
                matrix = np.stack([np.frombuffer(rows[i]["vector"], dtype="<f4") for i in batch])
                scores = matrix @ np.asarray(normalize(vector), dtype=np.float32)
                cosine.update(zip(batch, map(float, scores)))
            semantic = sorted(cosine, key=lambda i: (-cosine[i], rows[i]["path"], i))
        lexical = []
        if mode != "semantic":
            tokens = re.findall(r"\w+", query, re.UNICODE)[:64]
            expression = " OR ".join('"' + t + '"' for t in tokens)
            if expression:
                lexical = [
                    r[0]
                    for r in conn.execute(
                        "SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY bm25(chunks_fts), rowid",
                        (expression,),
                    )
                    if r[0] in rows
                ]
        ranks = {}
        for ranking in (semantic, lexical):
            for rank, item in enumerate(ranking, 1):
                ranks[item] = ranks.get(item, 0) + 1 / (60 + rank)
        ordered = sorted(ranks, key=lambda i: (-ranks[i], rows[i]["path"], i))
        hashes = dict(conn.execute("SELECT path,sha256 FROM files"))
        checked = {}
        hits = []
        matched_paths = set()
        for item in ordered:
            row = rows[item]
            relative = row["path"]
            if relative in matched_paths:
                continue
            path = root / relative
            if relative not in checked:
                try:
                    # Replaced directories/symlinks must not escape the explicitly indexed root.
                    safe = path.resolve(strict=True) == path and root in path.parents
                    checked[relative] = (
                        safe
                        and hashlib.sha256(read_bytes(path, meta["policy"]["max_bytes"])).hexdigest()
                        == hashes[relative]
                    )
                except (OSError, SearchError):
                    checked[relative] = False
            if not checked[relative]:
                continue
            matched_paths.add(relative)
            row.pop("vector")
            row["absolute_path"] = str(path)
            row["sha256"] = hashes[relative]
            row["cosine"] = cosine.get(item)
            row["score"] = cosine[item] if mode == "semantic" else ranks[item]
            row["citation"] = f"{path}:page {row['page']}" if row["page"] else f"{path}:{row['line_start']}"
            hits.append(row)
            if len(hits) == limit:
                break
        return {
            "query": query,
            "mode": mode,
            "root": str(root),
            "indexed_at": meta["indexed_at"],
            "score_type": "cosine" if mode == "semantic" else "reciprocal_rank_fusion",
            "stale_files_skipped": sum(not valid for valid in checked.values()),
            "hits": hits,
            "index_issues": meta.get("issues", []),
        }
    finally:
        conn.close()
