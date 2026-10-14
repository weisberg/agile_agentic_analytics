# Bundled third-party resources

These archives redistribute the unmodified upstream wheels and portable Python archive.
The model snapshot retains its upstream README and includes the Apache 2.0 license.

## Python

CPython 3.12.13 from [python-build-standalone](https://github.com/astral-sh/python-build-standalone/releases/download/20260510/cpython-3.12.13%2B20260510-aarch64-apple-darwin-install_only_stripped.tar.gz).
Upstream SHA-256: `55bc1a5edbc8ac4da0081f4f5731ed2d1ed10c57cb37a820b2a0dbc7cad742e9`.
The portable archive retains its Python and bundled pip license files.

## EmbeddingGemma 2

Google DeepMind, `google/embeddinggemma-2`, Apache-2.0.
[Pinned upstream snapshot](https://huggingface.co/google/embeddinggemma-2/tree/914f7f89142e33e77833254d9c9b90c3cef7303b).
Original weights are unchanged; the license text is added alongside the upstream README.

## Python wheels

Original `.dist-info` metadata, license files and notices remain inside each wheel.
Checksums for every wheel are recorded in `manifest.json`; upstream dependency hashes
are also pinned in `../requirements-macos.lock`.

| Distribution | Version | Declared license |
| --- | --- | --- |
| aaa-gemsearch | 0.2.0 | MIT |
| annotated-doc | 0.0.5 | MIT |
| anyio | 4.15.1 | MIT |
| certifi | 2026.7.22 | MPL-2.0 |
| click | 8.5.0 | BSD-3-Clause |
| cloudpickle | 3.1.2 | BSD-3-Clause |
| filelock | 4.1.1 | MIT |
| fsspec | 2026.9.0 | BSD-3-Clause |
| h11 | 0.16.0 | MIT |
| hf-xet | 1.7.0 | Apache-2.0 |
| httpcore | 1.0.9 | BSD-3-Clause |
| httpx | 0.28.1 | BSD-3-Clause |
| huggingface_hub | 1.33.0 | Apache-2.0 |
| idna | 3.20 | BSD-3-Clause |
| Jinja2 | 3.1.6 | See included license files/metadata |
| joblib | 1.6.0 | BSD-3-Clause |
| markdown-it-py | 4.2.0 | See included license files/metadata |
| MarkupSafe | 3.0.4 | BSD-3-Clause |
| mdurl | 0.1.2 | See included license files/metadata |
| mpmath | 1.3.0 | BSD |
| narwhals | 2.27.1 | MIT |
| networkx | 3.7 | BSD-3-Clause |
| numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pillow | 12.3.0 | MIT-CMU |
| Pygments | 2.21.0 | BSD-2-Clause |
| pypdf | 6.20.1 | BSD-3-Clause |
| PyYAML | 6.0.3 | MIT |
| regex | 2026.9.29 | Apache-2.0 AND CNRI-Python |
| rich | 15.0.0 | MIT |
| safetensors | 0.8.0 | See included license files/metadata |
| scikit-learn | 1.9.1 | BSD-3-Clause |
| scipy | 1.18.1 | Copyright (c) 2001-2002 Enthought, Inc. 2003, SciPy Developers. All rights reserved. Redistribution  |
| sentence-transformers | 6.1.0 | Apache-2.0 |
| setuptools | 84.0.0 | MIT |
| shellingham | 1.5.4 | ISC License |
| sympy | 1.14.0 | BSD |
| threadpoolctl | 3.7.0 | BSD-3-Clause |
| tokenizers | 0.23.3 | See included license files/metadata |
| torch | 2.14.1 | Apache-2.0 AND Apache-2.0 WITH LLVM-exception AND BSD-2-Clause AND BSD-3-Clause AND BSL-1.0 AND MIT |
| torchvision | 0.29.1 | BSD |
| tqdm | 4.70.1 | MPL-2.0 AND MIT |
| transformers | 5.19.0 | Apache 2.0 License |
| typer | 0.27.3 | MIT |
| typing_extensions | 4.16.0 | PSF-2.0 |
