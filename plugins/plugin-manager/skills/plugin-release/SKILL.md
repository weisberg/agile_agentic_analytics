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
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
mutating: true
writes_pages: false
writes_to:
  - plugins/
  - marketplace.yaml
  - .claude-plugin/marketplace.json
  - .agents/plugins/marketplace.json

disable-model-invocation: false
---

# Plugin Release

## Contract

A plugin release is ready only when:

- The intended plugin and changed files are identified from git status/diff.
- Validation passes for manifests, marketplace entry, skills, tests, and any
  bundled tools.
- Version bumps are applied in `marketplace.yaml`, then rendered consistently
  into Claude Code and Codex manifests when the release changes installable
  behavior.
- README, root catalog docs, and upgrade notes reflect the shipped behavior.
- One-way operations such as push, merge, tag, publish, and marketplace release
  happen only after explicit user approval.
- Generated files are treated as outputs. If generated manifests or marketplace
  files are stale, identify the source change in `marketplace.yaml` or
  `scripts/`, rerender, and validate before release approval.

## Workflow

1. **Preflight**
   - Run `git status --short --branch`.
   - Identify target plugin(s) from changed paths.
   - Read `${CLAUDE_PLUGIN_ROOT}/references/gbrain-gstack-learnings.md`.

2. **Diff and scope check**
   - Inspect `git diff --stat` and relevant file diffs.
   - Classify changes: `docs-only`, `skill`, `script/tool`, `manifest`,
     `marketplace`, or `breaking`.
   - Separate source files from generated files. Generated JSON should be
     explainable by `marketplace.yaml` or renderer changes.
   - Flag unrelated edits; do not stage them by accident.

3. **Version policy**
   - No bump: internal-only validation, routing fixture, or docs changes that
     do not alter installable behavior.
   - Patch: user-visible docs, examples, small skill wording, or validation
     fixes.
   - Minor: new skills, new bundled tools, new workflow behavior, or new user
     commands.
   - Major: breaking command, path, schema, or install behavior changes.
   - Update `plugins[].version` in `marketplace.yaml`.
   - Run `npm run render` to refresh generated marketplace and manifest files.

4. **Documentation sync**
   - Plugin `README.md` lists all user-facing skills and tools.
   - Root `README.md`, `CLAUDE.md`, and `PLUGINS_AND_SKILLS.md` reflect new
     installable plugins or skill families.
   - Add upgrade notes when existing users need to change commands, vaults,
     settings, or paths.

5. **Validation bundle**
   - `npm run render:check`
   - `npm run validate`
   - `python3 -m json.tool .claude-plugin/marketplace.json`
   - `python3 -m json.tool .agents/plugins/marketplace.json`
   - `python3 -m json.tool plugins/<plugin>/.claude-plugin/plugin.json`
   - `python3 -m json.tool plugins/<plugin>/.codex-plugin/plugin.json`
   - `claude plugin validate plugins/<plugin>`
   - `python3 "${CLAUDE_PLUGIN_ROOT}/skills/plugin-health/scripts/plugin_audit.py" --plugin <plugin> --json`
   - Focused tests for changed scripts.
   - Plugin-specific checks such as `vaultli --json validate` or
     `harvest_check.py` when applicable.

6. **Release gate**
   - Summarize changed files, validation evidence, version change, and upgrade
     notes.
   - Include whether generated files are current and whether the release changes
     Claude, Codex, or both harnesses.
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
Harness impact: Claude|Codex|both|none
Release gate: ready|blocked|needs-user-approval
```

## Anti-Patterns

- Bumping generated manifests by hand instead of bumping `marketplace.yaml`.
- Publishing after tests but before docs reflect the new behavior.
- Treating ignored/generated artifacts as source files.
- Bumping a version for internal-only changes without saying why users need an
  update.
- Pushing, merging, tagging, or publishing without explicit approval.
- Hiding upgrade impact from users with existing plugin state.
