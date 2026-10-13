"""Bounded file extraction and line/page-aware chunks. Sources are never written."""

import bisect
import fnmatch
import os
import stat
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from .embedding import SearchError

TEXT_SUFFIXES = {
    ".md",
    ".markdown",
    ".txt",
    ".rst",
    ".csv",
    ".tsv",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".toml",
    ".sql",
    ".py",
    ".r",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".sh",
    ".bash",
    ".zsh",
    ".rs",
    ".go",
    ".swift",
    ".java",
    ".c",
    ".h",
    ".cpp",
    ".xml",
    ".log",
    ".j2",
}
SUFFIXES = TEXT_SUFFIXES | {".pdf", ".docx"}
SKIP_DIRS = {"node_modules", "venv", "env", "__pycache__", "target", "dist", "build"}
SKIP_NAMES = {"index.jsonl", "package-lock.json", "uv.lock", "poetry.lock"}
CHUNK_CHARS = 1600
OVERLAP = 200
EXTRACT_VERSION = 1


def allowed(relative, excludes):
    parts = relative.parts
    name = relative.name.lower()
    return (
        not any(p.startswith(".") or p in SKIP_DIRS for p in parts)
        and name not in SKIP_NAMES
        and not any(s in name for s in ("credential", "secret", "private-key"))
        and relative.suffix.lower() in SUFFIXES
        and not any(fnmatch.fnmatchcase(relative.as_posix(), pattern) for pattern in excludes)
    )


def walk(root, excludes):
    def fail(error):
        raise SearchError(f"Cannot traverse {error.filename}; index unchanged") from error

    for directory, dirs, names in os.walk(root, followlinks=False, onerror=fail):
        dirs[:] = sorted(
            d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS and not (Path(directory) / d).is_symlink()
        )
        for name in sorted(names):
            path = Path(directory) / name
            if allowed(path.relative_to(root), excludes) and not path.is_symlink():
                yield path


def read_bytes(path, maximum):
    # O_NOFOLLOW closes the common scan-to-open symlink race on macOS/Linux.
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise SearchError("Not a regular file")
        if info.st_size > maximum:
            raise SearchError(f"File exceeds {maximum} bytes")
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise SearchError(f"File exceeds {maximum} bytes")
    return data


def extract(path, data):
    try:
        return _extract(path, data)
    except SearchError:
        raise
    except Exception as exc:
        # Parser-specific failures must not abort a batch of otherwise valid files.
        raise SearchError(f"Cannot extract {path.suffix.lower()} file ({type(exc).__name__})") from exc


def _extract(path, data):
    import io

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise SearchError("PDF support needs pypdf; run install-macos.sh or pip install this package") from exc
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise SearchError("Encrypted PDF is not supported")
        return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
    if suffix == ".docx":
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            item = archive.getinfo("word/document.xml")
            if item.file_size > 50 * 1024 * 1024:
                raise SearchError("DOCX expanded XML exceeds 50 MiB")
            xml = archive.read(item)
        tree = ElementTree.fromstring(xml)
        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        return [(None, "\n".join("".join(p.itertext()) for p in tree.iter(ns + "p")))]
    if b"\0" in data:
        raise SearchError("Binary or UTF-16 content is not supported")
    return [(None, data.decode("utf-8-sig"))]


def chunks(sections):
    for page, text in sections:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        newlines = [i for i, char in enumerate(text) if char == "\n"]
        start = 0
        while start < len(text):
            end = min(start + CHUNK_CHARS, len(text))
            # Prefer a line boundary while guaranteeing progress for very long lines.
            boundary = text.rfind("\n", start + CHUNK_CHARS // 2, end)
            if end < len(text) and boundary >= 0:
                end = boundary + 1
            snippet = text[start:end]
            if snippet.strip():
                yield {
                    "page": page,
                    "line_start": bisect.bisect_left(newlines, start) + 1,
                    "line_end": bisect.bisect_left(newlines, end - 1) + 1,
                    "text": snippet,
                }
            if end == len(text):
                break
            start = max(start + 1, end - OVERLAP)
