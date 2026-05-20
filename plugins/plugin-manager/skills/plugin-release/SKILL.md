---
name: plugin-release
version: 0.1.0
description: |
  Release and upgrade workflow for marketplace plugins. Use when validating,
  versioning, documenting, publishing, creating a PR for, or preparing upgrade
  notes for plugin changes. Borrows GStack ship/document-release discipline and
  GBrain upgrade hygiene.
triggers:
  - "release plugin"
  - "ship plugin"
  - "publish plugin"
  - "upgrade plugin"
  - "prepare plugin release"
  - "bump plugin version"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: false
writes_to:
  - plugins/
  - .claude-plugin/marketplace.json
---

# Plugin Release

## Contract

A plugin release is ready only when:

- The intended plugin and changed files are identified from git status/diff.
- Validation passes for manifests, marketplace entry, skills, tests, and any
  bundled tools.
- Version bumps are applied consistently to plugin manifest and marketplace
  entry when the release changes installable behavior.
- README, root catalog docs, and upgrade notes reflect the shipped behavior.
- One-way operations such as push, merge, tag, publish, and marketplace release
  happen only after explicit user approval.

## Workflow

1. **Preflight**
   - Run `git status --short --branch`.
   - Identify target plugin(s) from changed paths.
   - Read `plugins/plugin-manager/references/gbrain-gstack-learnings.md`.

2. **Diff and scope check**
   - Inspect `git diff --stat` and relevant file diffs.
   - Classify changes: `docs-only`, `skill`, `script/tool`, `manifest`,
     `marketplace`, or `breaking`.
   - Flag unrelated edits; do not stage them by accident.

3. **Version policy**
   - Patch: docs, examples, small skill wording, validation fixes.
   - Minor: new skills, new bundled tools, new workflow behavior.
   - Major: breaking command, path, schema, or install behavior changes.
   - Update `plugins/<plugin>/.claude-plugin/plugin.json`.
   - Update `.claude-plugin/marketplace.json` for listed plugins.

4. **Documentation sync**
   - Plugin `README.md` lists all user-facing skills and tools.
   - Root `README.md`, `CLAUDE.md`, and `PLUGINS_AND_SKILLS.md` reflect new
     installable plugins or skill families.
   - Add upgrade notes when existing users need to change commands, vaults,
     settings, or paths.

5. **Validation bundle**
   - `python3 -m json.tool .claude-plugin/marketplace.json`
   - `python3 -m json.tool plugins/<plugin>/.claude-plugin/plugin.json`
   - `claude plugin validate plugins/<plugin>`
   - `python3 plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py --plugin <plugin> --json`
   - Focused tests for changed scripts.
   - Plugin-specific checks such as `vaultli --json validate` or
     `harvest_check.py` when applicable.

6. **Release gate**
   - Summarize changed files, validation evidence, version change, and upgrade
     notes.
   - Ask before push, PR, tag, publish, or merge.

## Output Format

```text
PLUGIN RELEASE
Plugin: <name>
Change class: docs-only|skill|script-tool|manifest|marketplace|breaking
Version: <old> -> <new|unchanged>
Validation:
- <command>: pass|fail|not-run
Docs updated:
- <path>
Upgrade notes:
- <note or none>
Release gate: ready|blocked|needs-user-approval
```

## Anti-Patterns

- Bumping only the manifest or only the marketplace entry.
- Publishing after tests but before docs reflect the new behavior.
- Treating ignored/generated artifacts as source files.
- Pushing, merging, tagging, or publishing without explicit approval.
- Hiding upgrade impact from users with existing plugin state.

