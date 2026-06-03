#!/usr/bin/env bash
set -euo pipefail

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI not found; skipping Codex smoke test" >&2
  exit 0
fi

npm run validate

echo "Codex structural smoke validation passed"
