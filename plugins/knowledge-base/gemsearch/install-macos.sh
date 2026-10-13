#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 ]]; then
  echo 'Use native arm64 macOS (Apple Silicon); do not run this installer under Rosetta.' >&2
  exit 1
fi
source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python_bin="${PYTHON:-python3.12}"
if ! command -v "$python_bin" >/dev/null 2>&1; then
  echo 'Install native Python 3.12 (e.g. brew install python@3.12), then rerun. Set PYTHON to its path if needed.' >&2
  exit 1
fi
"$python_bin" -c 'import platform,sys; assert platform.machine() == "arm64" and sys.version_info[:2] == (3,12), "Native arm64 Python 3.12 is required by the macOS lockfile"; assert int(platform.mac_ver()[0].split(".")[0]) >= 14, "macOS 14 or later is required"'
install_dir="${GEMSEARCH_INSTALL_DIR:-$HOME/Library/Application Support/aaa-gemsearch/runtime}"
umask 077
"$python_bin" -m venv "$install_dir"
"$install_dir/bin/python" -m pip install --require-hashes -r "$source_dir/requirements-macos.lock"
"$install_dir/bin/python" -m pip install --no-deps --no-build-isolation "$source_dir"
printf '\nInstalled. Add this directory to PATH:\n%s/bin\n' "$install_dir"
printf 'Then run: gemsearch download-model && gemsearch doctor\n'
