#!/usr/bin/env bash
set -euo pipefail

if ! command -v claude >/dev/null 2>&1; then
  echo "claude CLI not found; skipping Claude smoke test" >&2
  exit 0
fi

claude plugin validate . --strict

for plugin_dir in plugins/*; do
  if [ -d "$plugin_dir/.claude-plugin" ]; then
    claude plugin validate "$plugin_dir" --strict
  fi
done

echo "Claude smoke validation passed"
