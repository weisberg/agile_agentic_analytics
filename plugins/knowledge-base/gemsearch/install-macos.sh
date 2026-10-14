#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 ]]; then
  echo 'Use native arm64 macOS (Apple Silicon); do not run this installer under Rosetta.' >&2
  exit 1
fi
source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mode="${1:---offline}"
install_dir="${GEMSEARCH_INSTALL_DIR:-$HOME/Library/Application Support/aaa-gemsearch/runtime}"
if [[ "$#" -gt 1 || ( "$mode" != --offline && "$mode" != --online ) ]]; then
  echo 'Usage: install-macos.sh [--offline|--online] (default: --offline)' >&2
  exit 1
fi
if [[ "$mode" == --offline ]]; then
  if [[ ! -f "$source_dir/offline/manifest.json" ]]; then
    echo 'Offline bundle is missing. Download the full repo including offline archive parts.' >&2
    exit 1
  fi
  macos_version="$(/usr/bin/sw_vers -productVersion)"
  if [[ "${macos_version%%.*}" -lt 14 ]]; then
    echo 'macOS 14 or later is required.' >&2
    exit 1
  fi
  umask 077
  unset PYTHONHOME PYTHONPATH
  echo 'Verifying committed offline archive parts...'
  (cd "$source_dir/offline" && /usr/bin/shasum --status -a 256 -c SHA256SUMS)
  mkdir -p "$install_dir"
  bootstrap_dir="$install_dir/bootstrap"
  # Always restore the verified interpreter; executable presence is not an integrity check.
  staging_dir="$(mktemp -d "$install_dir/bootstrap.XXXXXX")"
  trap 'rm -rf "$staging_dir"' EXIT
  /bin/cat "$source_dir"/offline/python.tar.gz.part-* | /usr/bin/tar -xzf - -C "$staging_dir"
  previous_bootstrap="$(mktemp -d "$install_dir/bootstrap-previous.XXXXXX")"
  rmdir "$previous_bootstrap"
  if [[ -e "$bootstrap_dir" ]]; then
    mv "$bootstrap_dir" "$previous_bootstrap"
  fi
  if mv "$staging_dir" "$bootstrap_dir"; then
    rm -rf "$previous_bootstrap"
  else
    if [[ -e "$previous_bootstrap" ]]; then
      mv "$previous_bootstrap" "$bootstrap_dir"
    fi
    exit 1
  fi
  trap - EXIT
  exec "$bootstrap_dir/python/bin/python3.12" -I "$source_dir/scripts/offline_bundle.py" install \
    --source "$source_dir" --install-dir "$install_dir"
fi

python_bin="${PYTHON:-python3.12}"
if ! command -v "$python_bin" >/dev/null 2>&1; then
  echo 'Install native Python 3.12 (e.g. brew install python@3.12), then rerun. Set PYTHON to its path if needed.' >&2
  exit 1
fi
"$python_bin" -c 'import platform,sys; assert platform.machine() == "arm64" and sys.version_info[:2] == (3,12), "Native arm64 Python 3.12 is required by the macOS lockfile"; assert int(platform.mac_ver()[0].split(".")[0]) >= 14, "macOS 14 or later is required"'
umask 077
"$python_bin" -m venv "$install_dir"
"$install_dir/bin/python" -m pip install --require-hashes -r "$source_dir/requirements-macos.lock"
"$install_dir/bin/python" -m pip install --no-deps --no-build-isolation "$source_dir"
printf '\nInstalled. Add this directory to PATH:\n%s/bin\n' "$install_dir"
printf 'Then run: gemsearch download-model && gemsearch doctor\n'
