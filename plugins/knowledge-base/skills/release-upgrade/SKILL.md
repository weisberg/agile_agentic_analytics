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

## Output Format

- KB RELEASE
- Version, validation, docs, upgrade notes, approval gate.

## Anti-Patterns

- Changing plugin behavior without version/docs sync.
- Publishing without validating the bundled vaultli surface.
