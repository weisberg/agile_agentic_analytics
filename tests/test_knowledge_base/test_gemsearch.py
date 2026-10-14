"""Offline regression tests; real model/device checks are separate doctor commands."""

import hashlib
import io
import json
import os
import sqlite3
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2] / "plugins/knowledge-base/gemsearch"
sys.path.insert(0, str(PACKAGE / "src"))

from gemsearch import embedding
from gemsearch import index as module
from gemsearch.cli import main
from gemsearch.embedding import PythonEmbedder, SearchError, normalize
from gemsearch.files import CHUNK_CHARS, chunks, extract
from gemsearch.index import build_index, database_path, search, status


class FakeEmbedder:
    batch_size = 2

    def __init__(self):
        self.calls = []
        self.fail = False

    def identity(self):
        return {"model": "fake", "revision": "1", "dimensions": 3}

    def documents(self, title, texts):
        self.calls.extend(texts)
        if self.fail:
            raise SearchError("inference failed")
        return [self.query(text) for text in texts]

    def query(self, text):
        text = text.lower()
        return normalize(
            [
                1.0 if "renewal" in text or "churn" in text else 0.0,
                1.0 if "recipe" in text or "cooking" in text else 0.0,
                0.1,
            ]
        )


@pytest.fixture
def corpus(tmp_path):
    root = tmp_path / "files"
    root.mkdir()
    (root / "business.md").write_text("# Customer retention\nRenewal warning indicators.\n", encoding="utf-8")
    (root / "food.txt").write_text("A recipe for cooking lentils.\n", encoding="utf-8")
    return root, tmp_path / "cache/index.sqlite3", FakeEmbedder()


def test_semantic_synonyms_citations_and_source_preservation(corpus):
    root, db, backend = corpus
    before = {p.name: p.read_bytes() for p in root.iterdir()}
    result = build_index(root, db, backend)
    assert result["indexed"] == 2
    hit = search(root, db, "churn", backend, "semantic")["hits"][0]
    assert hit["path"] == "business.md"
    assert hit["line_start"] == 1 and hit["line_end"] == 2
    assert hit["citation"] == f"{root}/business.md:1"
    assert hit["cosine"] == pytest.approx(1)
    assert "vector" not in hit
    assert hit["sha256"] == hashlib.sha256(before["business.md"]).hexdigest()
    assert before == {p.name: p.read_bytes() for p in root.iterdir()}
    assert db.stat().st_mode & 0o777 == 0o600


def test_incremental_change_delete_and_stale_hits(corpus):
    root, db, backend = corpus
    build_index(root, db, backend)
    calls = len(backend.calls)
    assert build_index(root, db, backend)["unchanged"] == 2
    assert len(backend.calls) == calls
    (root / "business.md").write_text("New renewal decision\n")
    (root / "food.txt").unlink()
    found = search(root, db, "churn", backend, "semantic")
    assert found["hits"] == [] and found["stale_files_skipped"] == 2
    changed = build_index(root, db, backend)
    assert (changed["indexed"], changed["removed"]) == (1, 1)
    assert search(root, db, "churn", backend)["hits"][0]["text"] == "New renewal decision\n"


def test_inference_failure_rolls_back_update_and_pruning(corpus):
    root, db, backend = corpus
    build_index(root, db, backend)
    before = status(root, db)
    (root / "business.md").write_text("Changed renewal\n")
    (root / "food.txt").unlink()
    backend.fail = True
    with pytest.raises(SearchError, match="inference failed"):
        build_index(root, db, backend)
    assert status(root, db) == before
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT text FROM chunks WHERE path='business.md'").fetchone()[0].startswith("# Customer")


def test_walk_failure_does_not_prune(corpus, monkeypatch):
    root, db, backend = corpus
    build_index(root, db, backend)
    before = status(root, db)

    def failed_walk(*args):
        yield root / "business.md"
        raise SearchError("permission denied")

    monkeypatch.setattr(module, "walk", failed_walk)
    with pytest.raises(SearchError, match="permission denied"):
        build_index(root, db, backend)
    assert status(root, db) == before


def test_scope_model_and_policy_guards(corpus, tmp_path):
    root, db, backend = corpus
    build_index(root, db, backend)
    other = tmp_path / "other"
    other.mkdir()
    with pytest.raises(SearchError, match="another root"):
        build_index(other, db, backend, rebuild=True)
    with pytest.raises(SearchError, match="policy changed"):
        build_index(root, db, backend, excludes=["food*"])
    build_index(root, db, backend, excludes=["food*"], rebuild=True)
    assert status(root, db)["files"] == 1
    backend.identity = lambda: {"model": "fake", "revision": "2", "dimensions": 3}
    with pytest.raises(SearchError, match="differs"):
        search(root, db, "churn", backend)
    assert search(root, db, "renewal", backend, "lexical")["hits"]
    with pytest.raises(SearchError, match="outside"):
        database_path(root, root / "cache.sqlite3")


def test_exclusions_symlinks_hidden_binary_and_size(corpus, tmp_path):
    root, db, backend = corpus
    for name in (".env", "credentials.json", "secret.py", "INDEX.jsonl", "skip.txt"):
        (root / name).write_text("renewal secret")
    (root / ".hidden").mkdir()
    (root / ".hidden/leak.md").write_text("renewal")
    (root / "node_modules").mkdir()
    (root / "node_modules/leak.js").write_text("renewal")
    (root / "binary.txt").write_bytes(b"bad\0data")
    (root / "large.txt").write_bytes(b"a" * 101)
    outside = tmp_path / "outside.txt"
    outside.write_text("renewal")
    (root / "link.txt").symlink_to(outside)
    preview = build_index(root, db, backend, excludes=["skip.txt"], dry_run=True)
    assert not db.exists() and not backend.calls
    assert set(preview["files"]) == {"business.md", "food.txt", "binary.txt", "large.txt"}
    report = build_index(root, db, backend, excludes=["skip.txt"], max_bytes=100)
    assert report["indexed"] == 2
    assert {r["path"] for r in report["issues"]} == {"binary.txt", "large.txt"}


def test_symlink_replacement_after_index_is_not_returned(corpus, tmp_path):
    root, db, backend = corpus
    build_index(root, db, backend)
    original = root / "business.md"
    outside = tmp_path / "outside.md"
    outside.write_bytes(original.read_bytes())
    original.unlink()
    original.symlink_to(outside)
    assert all(h["path"] != "business.md" for h in search(root, db, "churn", backend)["hits"])


def test_lexical_hybrid_filter_and_safe_fts_query(corpus):
    root, db, backend = corpus
    build_index(root, db, backend)
    assert search(root, db, "churn", backend, "lexical")["hits"] == []
    hit = search(root, db, '"recipe" OR (!!!)', backend, "lexical")["hits"][0]
    assert hit["path"] == "food.txt"
    assert search(root, db, "cooking", backend, "hybrid")["hits"][0]["path"] == "food.txt"
    assert search(root, db, "churn", backend, path_glob="*.txt")["hits"][0]["path"] == "food.txt"
    with pytest.raises(SearchError, match="blank"):
        search(root, db, " ", backend)


def test_chunk_bounds_long_lines_and_page_provenance():
    text = "a" * 10000
    pieces = list(chunks([(7, text), (8, "last page\n")]))
    assert all(len(p["text"]) <= CHUNK_CHARS for p in pieces)
    assert all(p["line_start"] == p["line_end"] == 1 for p in pieces)
    assert pieces[-1]["page"] == 8
    assert len(pieces) < 20


def test_docx_extraction_and_invalid_utf8():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Renewal</w:t></w:r></w:p></w:body></w:document>',
        )
    assert extract(Path("test.docx"), stream.getvalue()) == [(None, "Renewal")]
    with pytest.raises(SearchError, match="UnicodeDecodeError"):
        extract(Path("test.txt"), b"\xff")


def test_pdf_page_citations_and_encryption(corpus):
    pypdf = pytest.importorskip("pypdf")
    root, db, backend = corpus
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(612, 792)
    font = pypdf.generic.DictionaryObject(
        {
            pypdf.generic.NameObject("/Type"): pypdf.generic.NameObject("/Font"),
            pypdf.generic.NameObject("/Subtype"): pypdf.generic.NameObject("/Type1"),
            pypdf.generic.NameObject("/BaseFont"): pypdf.generic.NameObject("/Helvetica"),
        }
    )
    page[pypdf.generic.NameObject("/Resources")] = pypdf.generic.DictionaryObject(
        {
            pypdf.generic.NameObject("/Font"): pypdf.generic.DictionaryObject(
                {
                    pypdf.generic.NameObject("/F1"): font,
                }
            ),
        }
    )
    content = pypdf.generic.DecodedStreamObject()
    content.set_data(b"BT /F1 12 Tf 72 720 Td (Renewal PDF evidence) Tj ET")
    page[pypdf.generic.NameObject("/Contents")] = writer._add_object(content)
    with (root / "evidence.pdf").open("wb") as stream:
        writer.write(stream)
    build_index(root, db, backend)
    hit = search(root, db, "evidence", backend, "lexical")["hits"][0]
    assert hit["page"] == 1 and hit["citation"].endswith(":page 1")
    writer.encrypt("password")
    stream = io.BytesIO()
    writer.write(stream)
    with pytest.raises(SearchError, match="Encrypted"):
        extract(Path("encrypted.pdf"), stream.getvalue())


@pytest.mark.parametrize("values", [[], [0, 0], [float("nan")], [float("inf")], [True], ["bad"]])
def test_invalid_vectors(values):
    with pytest.raises(SearchError):
        normalize(values)


def test_python_adapter_prompts_and_no_silent_truncation():
    backend = PythonEmbedder()
    seen = []
    backend.embed = lambda texts: seen.extend(texts) or [[1.0]] * len(texts)
    backend.documents("notes.md", ["content"])
    backend.query("find this")
    assert seen == ["title: notes.md | text: content", "task: search result | query: find this"]


def test_adapter_rejects_overlong_inputs_and_nonfinite_model_output():
    class Tokenizer:
        def encode(self, text, **kwargs):
            return list(range(len(text)))

    class Model:
        tokenizer = Tokenizer()
        max_seq_length = 10

        def encode(self, texts, **kwargs):
            import numpy as np

            return np.array([[float("nan")] * 768])

    backend = PythonEmbedder()
    backend._model = Model()
    with pytest.raises(SearchError, match="token limit"):
        backend.embed(["a" * 11])
    with pytest.raises(SearchError, match="nonfinite"):
        backend.embed(["short"])


def test_local_loader_uses_matching_snapshot_filter_and_safe_settings(monkeypatch):
    from types import SimpleNamespace

    downloads = []
    loads = []

    def snapshot(**kwargs):
        downloads.append(kwargs)
        return "/cached/model"

    def model(path, **kwargs):
        loads.append((path, kwargs))
        return object()

    dtype = object()
    monkeypatch.setenv("HF_HUB_OFFLINE", "")
    monkeypatch.setenv("HF_HUB_DISABLE_TELEMETRY", "")
    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(snapshot_download=snapshot))
    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(SentenceTransformer=model))
    monkeypatch.setitem(
        sys.modules,
        "torch",
        SimpleNamespace(float32=dtype, backends=SimpleNamespace(mps=SimpleNamespace(is_available=lambda: True))),
    )
    embedding.download_model()
    backend = PythonEmbedder()
    assert backend.load() is backend.load()
    assert len(downloads) == 2 and len(loads) == 1
    assert downloads[0]["allow_patterns"] == downloads[1]["allow_patterns"] == embedding.MODEL_FILES
    assert downloads[1]["local_files_only"] is True
    assert downloads[1]["revision"] == embedding.MODEL_REVISION
    assert loads[0][1]["config_kwargs"] == {"vision_config": None, "audio_config": None}
    assert loads[0][1]["model_kwargs"]["torch_dtype"] is dtype
    assert loads[0][1]["device"] == "mps"
    assert loads[0][1]["trust_remote_code"] is False
    assert loads[0][1]["local_files_only"] is True


def test_download_failure_is_actionable(monkeypatch):
    from types import SimpleNamespace

    def failed(**kwargs):
        raise OSError("offline")

    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(snapshot_download=failed))
    with pytest.raises(SearchError, match="connectivity"):
        embedding.download_model()


def test_corrupt_document_does_not_abort_valid_files(corpus):
    root, db, backend = corpus
    (root / "broken.docx").write_bytes(b"not a zip archive")
    report = build_index(root, db, backend)
    assert report["indexed"] == 2
    assert report["issues"][0]["path"] == "broken.docx"
    assert "BadZipFile" in report["issues"][0]["error"]


def test_file_that_becomes_unreadable_loses_cached_content(corpus):
    root, db, backend = corpus
    build_index(root, db, backend)
    (root / "business.md").write_bytes(b"bad\0binary")
    report = build_index(root, db, backend)
    assert report["issues"][0]["path"] == "business.md"
    assert status(root, db)["files"] == 1
    assert search(root, db, "renewal", backend, "lexical")["hits"] == []


def test_dimension_mismatch_rolls_back(corpus):
    root, db, backend = corpus
    build_index(root, db, backend)
    before = status(root, db)
    (root / "business.md").write_text("changed")
    backend.documents = lambda title, texts: [[1.0, 0.0] for _ in texts]
    with pytest.raises(SearchError, match="dimensions differ"):
        build_index(root, db, backend)
    assert status(root, db) == before


def test_cli_dry_run_and_missing_index(corpus, capsys):
    root, db, _backend = corpus
    assert main(["index", "--root", str(root), "--db", str(db), "--dry-run"]) == 0
    assert json.loads(capsys.readouterr().out)["dry_run"]
    assert main(["search", "churn", "--root", str(root), "--db", str(db)]) == 1
    assert "missing" in json.loads(capsys.readouterr().err)["error"]


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["search", "churn"],
        ["search", "churn", "--root", ".", "--limit", "0"],
        ["search", "churn", "--root", ".", "--limit", "invalid"],
        ["search", "churn", "--root", ".", "--mode", "invalid"],
    ],
)
def test_argument_errors_use_json_and_command_error_exit_code(arguments, capsys):
    assert main(arguments) == 1
    captured = capsys.readouterr()
    assert not captured.out
    payload = json.loads(captured.err)
    assert payload["ok"] is False and payload["error"]


def test_installed_plugin_wrapper_works_without_repository_parent(tmp_path):
    import shutil

    plugin = tmp_path / "cached-plugin"
    shutil.copytree(PACKAGE, plugin / "gemsearch")
    (plugin / "bin").mkdir()
    shutil.copy2(PACKAGE.parent / "bin/gemsearch", plugin / "bin/gemsearch")
    runtime = tmp_path / "runtime"
    (runtime / "bin").mkdir(parents=True)
    (runtime / "bin/python").symlink_to(sys.executable)
    env = {**os.environ, "GEMSEARCH_INSTALL_DIR": str(runtime)}
    result = subprocess.run(
        [str(plugin / "bin/gemsearch"), "--version"], check=False, cwd=tmp_path, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0 and result.stdout.strip() == "0.2.0"
