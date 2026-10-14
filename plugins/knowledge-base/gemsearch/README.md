# gemsearch

Search local file contents with Google's **EmbeddingGemma 2**, running directly
in Python. No Ollama, inference server, hosted embedding API, or cloud fallback.
The default device is PyTorch MPS on Apple Silicon; `--device cpu` is explicit fallback.

## Install on an M3 Mac

The full repository includes compressed **Python 3.12.13**, all runtime dependency
wheels, the gemsearch wheel, and the pinned model weights under `offline/`.
Requires native arm64 macOS 14+ and approximately 8 GiB free for installation and
staging. No preinstalled Python, pip, Homebrew, PyPI access, Hugging Face access,
Git LFS, or inference server is needed for the default installation.

From the full checkout or GitHub source archive:

```bash
bash plugins/knowledge-base/gemsearch/install-macos.sh
export PATH="$HOME/Library/Application Support/aaa-gemsearch/runtime/bin:$PATH"
gemsearch doctor --device mps
```

The default is `--offline`: verify committed archive checksums, unpack the
portable interpreter, create a virtual environment, install local wheels with
`--no-index` and dependency hashes, then restore the model into the installed
runtime. **Do not run `download-model` for an offline installation.** Archive
parts are normal Git files, so a shallow clone or source ZIP includes them.
A sparse/filtered download must include every `offline/*.part-*` file.
See [offline bundle inventory and provenance](offline/README.md).

Set `GEMSEARCH_INSTALL_DIR` to change the installation location; the plugin's
`bin/gemsearch` respects it too. To update, rerun the installer from the new
plugin version. Start with batch size 4; use 1 on memory-constrained machines.
The bundled profile supports macOS arm64 and Python 3.12 only.

An explicit online installation remains available:

```bash
# Requires an existing native Python 3.12 and access to PyPI/Hugging Face.
bash plugins/knowledge-base/gemsearch/install-macos.sh --online
export PATH="$HOME/Library/Application Support/aaa-gemsearch/runtime/bin:$PATH"
gemsearch download-model
```

For other Python development environments: `python -m pip install .` from this
directory. The bundled macOS profile is the supported M3 installation path.

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

Offline model cache: `<install-dir>/share/gemsearch/model-cache`.
Online fallback: `~/.cache/gemsearch/models`. `GEMSEARCH_MODEL_CACHE` overrides
both when set. Indexing/search load the installed snapshot without contacting
Hugging Face.
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

Original runtime validation on 2026-10-13: the locked installer, real MPS semantic/hybrid
retrieval smoke test and CPU inference passed on an arm64 M5 Max. CPU inference
also passed with socket connections blocked. M3 uses the same native arm64/MPS
installation path; a physical M3 was not available for hardware validation.

Offline bundle validation on 2026-10-14: fresh installation and real MPS search
passed with networking, the previous model cache and Homebrew access denied on
an M5 Max. No physical M3 was available. Bundle verification also runs in CI.

To regenerate dependency hashes with uv: `MACOSX_DEPLOYMENT_TARGET=14.0 uv pip compile pyproject.toml
--python-version 3.12 --python-platform aarch64-apple-darwin --generate-hashes
-o requirements-macos.lock`.
