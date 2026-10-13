# gemsearch

Search local file contents with Google's **EmbeddingGemma 2**, running directly
in Python. No Ollama, inference server, hosted embedding API, or cloud fallback.
The default device is PyTorch MPS on Apple Silicon; `--device cpu` is explicit fallback.

## Install on an M3 Mac

Requires native arm64 macOS 14+ and Python 3.12, disk space for the Python runtime
and model weights, and internet access during installation and model download.
Start with batch size 4; use 1 on memory-constrained machines. Model weights are
downloaded, rather than committed to this repository.

From this repository:

```bash
brew install python@3.12  # only if Python 3.12 is missing
bash plugins/knowledge-base/gemsearch/install-macos.sh
export PATH="$HOME/Library/Application Support/aaa-gemsearch/runtime/bin:$PATH"
gemsearch download-model
gemsearch doctor --device mps
```

The installer uses `requirements-macos.lock` (Python 3.12, macOS arm64, hashes),
then installs this self-contained package. It needs no files outside `gemsearch/`.
Set `GEMSEARCH_INSTALL_DIR` to change the installation location; the plugin's
`bin/gemsearch` respects it too. A cached marketplace plugin can use this same
installer without writing into the plugin cache. To update, rerun the installer
from the new plugin version.

For other Python development environments: `python -m pip install .` from this
directory. The macOS installer and lockfile are the supported M3 installation path.

## Index and search

Always choose an explicit root. It need not be a vault or have frontmatter.

```bash
gemsearch index --root "$HOME/Documents/Meetings" --dry-run
gemsearch index --root "$HOME/Documents/Meetings" --exclude 'archive/**'
gemsearch search 'decisions about retention experiments' --root "$HOME/Documents/Meetings"
gemsearch search 'renewal_risk' --root "$HOME/Documents/Meetings" --mode lexical
gemsearch search 'customer churn warning signs' --root "$HOME/Documents/Meetings" --mode semantic --limit 5
gemsearch status --root "$HOME/Documents/Meetings"
```

Commands emit JSON. Exit codes: 0 success, 1 command/inference error, 2 partial
index with per-file extraction issues (valid files are committed).
Invalid arguments also return JSON and exit 1; `--help` and `--version` use
conventional terminal output. Repeat the same index command after edits.
Files are hashed, unchanged files are not
re-embedded, deleted files are pruned, and unreadable/oversized files lose cached
content. An inference error rolls back the entire update. A traversal failure
prevents pruning. Search verifies current file hashes before returning hits and
reports stale files it encounters; rerun indexing to include changed content.

Default hybrid mode fuses cosine and SQLite FTS5/BM25 rankings using reciprocal
rank fusion, with one best chunk per file. Scores are rankings, not probabilities.
`--path 'concepts/*.md'` restricts results by root-relative glob. Semantic search
scans vectors in blocks; it targets personal collections, not million-document
ANN workloads. Model startup occurs for each CLI invocation. Lexical search and
status do not load the model.

## Files and citations

- UTF-8 text: Markdown, plain text, CSV/TSV, JSON/JSONL, YAML, TOML, SQL, common
  code formats, HTML/XML, logs and Jinja. HTML is indexed as source text.
- PDF: extracted text, with physical page numbers and page-local extracted lines.
  Scanned PDFs require prior OCR; encrypted PDFs are rejected.
- DOCX: paragraph/table text; lines refer to extracted text, not Word pagination.
- Images, audio, video, XLSX, PPTX and legacy Office formats are unsupported.

Results include absolute and relative paths, SHA-256, line ranges, PDF page where
applicable, matching text, cosine score (semantic/hybrid), and a citation pointer.
Open the source before drawing conclusions. No source file or vaultli index is
modified. Long lines are split into overlapping bounded chunks.

## Complements vaultli

Use **vaultli first** for authoritative KB IDs, metadata filters, scope, sidecars,
relationships, validation, and context assembly. Use **gemsearch additionally**
for semantic matches inside file bodies or files outside a managed vault.
Search the same root in each tool; join by source path, then hydrate with vaultli
for managed pages, or read the original file. gemsearch does not infer KB IDs,
scope, tags, or sidecar relationships and does not replace vaultli commands.

## Local state and privacy

The pinned model revision is in `embedding.py`. `download-model` fetches only
model assets from Hugging Face; index/search/doctor load cached assets with
`local_files_only=True`, telemetry disabled, and no remote code execution.
The text-only backbone loads in float32, with vision/audio encoders disabled.
The model card documents these inference settings and task prompts:
[Google's model card](https://huggingface.co/google/embeddinggemma-2).

Model cache: `~/.cache/gemsearch/models` (`GEMSEARCH_MODEL_CACHE` overrides).
Index: `~/Library/Application Support/aaa-gemsearch/gemsearch/<root-hash>/index.sqlite3`.
`GEMSEARCH_DATA`, or `CLAUDE_PLUGIN_DATA` when set, overrides its base directory.
`--db` selects a separate cache path, which must be outside the indexed root.
The index contains plaintext snippets; newly created directories/files are private
(0700/0600). Removing an index directory removes cached content, not source files.
Each database belongs to exactly one root. Model/revision/prompt/policy changes
require `index --rebuild`; a different root always needs a separate database.

Hidden paths, symlinks, common build/dependency directories, credential/secret
filenames, lockfiles and vaultli's `INDEX.jsonl` are skipped. This is a conservative
filename policy, not secret detection. `.gitignore` is not interpreted. Use
`--dry-run` and repeatable `--exclude` globs to review scope. Reuse exclusions on
every index run; changing them requires `--rebuild`. macOS may require granting
the terminal access to Documents. Cloud placeholders must be downloaded first.

## Validation and troubleshooting

```bash
python -m pytest tests/test_knowledge_base/test_gemsearch.py
gemsearch doctor --device mps
gemsearch doctor --device cpu
python plugins/knowledge-base/gemsearch/scripts/smoke.py --device mps
```

Run pytest from the repository root with the package installed (or the test file's
source-path bootstrap). The test suite uses fake vectors to test transactions,
staleness, citations, extraction and ranking without model downloads. `doctor`
performs real inference and verifies finite, normalized 768-dimensional output.
On an MPS error, retry with `--device cpu`; fallback is never silent after an
inference failure. Run `download-model` again if the cache is incomplete.

Local validation on 2026-10-13: the locked installer, real MPS semantic/hybrid
retrieval smoke test and CPU inference passed on an arm64 M5 Max. CPU inference
also passed with socket connections blocked. M3 uses the same native arm64/MPS
installation path; a physical M3 was not available for hardware validation.

To regenerate dependency hashes with uv: `MACOSX_DEPLOYMENT_TARGET=14.0 uv pip compile pyproject.toml
--python-version 3.12 --python-platform aarch64-apple-darwin --generate-hashes
-o requirements-macos.lock`.
