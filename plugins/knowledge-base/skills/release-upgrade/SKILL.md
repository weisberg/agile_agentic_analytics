---
name: release-upgrade
version: 0.1.0
description: >-
  Release and upgrade workflow for the knowledge-base plugin: versioning, docs, validation bundle, local testing, and user upgrade notes.
triggers:
  - "release kb plugin"
  - "upgrade kb plugin"
  - "ship knowledge base"
  - "kb release"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Release Upgrade

## Contract

- Version bumps, marketplace entries, docs, tests, and upgrade notes stay in sync.
- Local plugin validation runs before release.
- User-impacting changes include migration/upgrade notes.

## Workflow

- Use `/plugin-manager:plugin-release` with plugin `knowledge-base`.
- Classify change severity and version bump.
- Run plugin health, vaultli tests/parity, KB skill checks, and README sync.
- Document upgrade notes for existing vaults and commands.
- Ask before push, PR, tag, or publish.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py dashboard`
- `python3 plugins/knowledge-base/scripts/kb_ops.py resolver-check`
- `python3 plugins/knowledge-base/scripts/kb_ops.py retrieval-benchmark`


## Output Format

- KB RELEASE
- Version, validation, docs, upgrade notes, approval gate.

## Anti-Patterns

- Changing plugin behavior without version/docs sync.
- Publishing without validating the bundled vaultli surface.
