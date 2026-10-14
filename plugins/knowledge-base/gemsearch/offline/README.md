# Offline gemsearch bundle: macOS arm64, Python 3.12

All payloads are committed as ordinary Git files. No Git LFS client, release-asset
fetch, PyPI connection or Hugging Face connection is needed after obtaining the
full repository. A shallow clone or GitHub source ZIP includes all parts.

Run from the repository root:

```bash
bash plugins/knowledge-base/gemsearch/install-macos.sh --offline
```

The bundle includes portable CPython 3.12.13, 44 locked third-party wheels, the
`aaa-gemsearch` 0.2.0 wheel and Google EmbeddingGemma 2 revision
`914f7f89142e33e77833254d9c9b90c3cef7303b`. Native Apple Silicon macOS 14+ is required.
Intel Macs, Linux, Windows and other Python ABIs need separately built profiles.

| Compressed archive | Bytes | Parts |
| --- | ---: | ---: |
| python | 24,942,229 | 1 |
| wheels | 199,239,435 | 5 |
| model | 839,959,832 | 18 |

Parts are at most 45 MiB each, below GitHub's ordinary Git file limits. They are
segments of a single gzip stream and are not individually extractable. The
installer checks every part against `SHA256SUMS`, restores Python, then verifies
combined archive hashes and extracted file hashes from `manifest.json`. Missing,
changed or reordered parts fail installation. There is no online fallback.

Installed state lives under `GEMSEARCH_INSTALL_DIR` (default documented in the
parent README): `bootstrap/python/`, the virtual environment, and
`share/gemsearch/model-cache/`. Upgrades reuse the same pinned model identity;
existing vaultli data and gemsearch SQLite indexes require no migration.

## Provenance and rebuilding

See [third-party notices](THIRD_PARTY_NOTICES.md). `manifest.json` records upstream
Python provenance/digest, the model revision, all compressed and extracted
checksums, and hashes tying the gemsearch wheel to the committed source.

To rebuild on an online native arm64 Python 3.12 development machine:

1. Download wheels with `python -m pip download --only-binary=:all:
   --require-hashes -r requirements-macos.lock -d <downloads>/wheels`.
2. Download the portable Python archive named by
   `manifest.json`'s `python_upstream`; save its GitHub asset metadata including
   its digest as `<downloads>/python-asset.json` and the archive as `python.tar.gz`.
3. Use `huggingface_hub.snapshot_download` for the pinned revision into
   `<downloads>/model-download`, and save the Apache 2.0 license as
   `<downloads>/MODEL-LICENSE-Apache-2.0.txt`.
4. From `gemsearch/`, run:
   `python scripts/offline_bundle.py build --source . --downloads <downloads>
   --output <empty-output-directory>`.
5. Validate checksums, then test install and real inference with network access
   denied before replacing these committed parts.

The builder normalizes tar metadata and gzip timestamps. Unchanged model assets
produce unchanged parts. Archive updates intentionally increase repository size;
reuse unchanged model/runtime parts across later tool-only releases.
