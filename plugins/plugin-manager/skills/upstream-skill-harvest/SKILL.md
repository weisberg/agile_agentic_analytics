---
name: upstream-skill-harvest
version: 0.1.0
description: |
  Plugin-manager maintenance workflow for importing, adapting, diffing, and
  periodically resyncing skills from upstream GBrain or GStack checkouts into
  plugins in this marketplace. Use when harvesting a skill into
  plugins/<plugin>/skills, refreshing a plugin skill from upstream, auditing
  source drift, or recording source/adaptation notes. This skill ships in the
  plugin-manager plugin because it manages other plugins rather than serving
  one plugin's end users.
triggers:
  - "harvest upstream skill"
  - "sync upstream skill"
  - "update from gbrain"
  - "update from gstack"
  - "diff upstream skill"
  - "record skill source"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: false
writes_to:
  - plugins/

disable-model-invocation: false
---

# Upstream Skill Harvest

## Placement Rule

This is a plugin-manager maintenance skill. Keep it at
`plugins/plugin-manager/skills/upstream-skill-harvest/SKILL.md`, not in
`$CODEX_HOME/skills` and not inside the target plugin it is harvesting into.

Use this skill to maintain plugin skills. The imported runtime capability still
lands in `plugins/<plugin>/skills/<slug>/SKILL.md`.

## Contract

A harvest or sync is complete only when:

- The source path is recorded with a stable alias such as
  `$GBRAIN_ROOT/skills/<slug>/SKILL.md` or `$GSTACK_ROOT/<slug>/SKILL.md`.
- The target path and adaptation notes are recorded in the target plugin's
  upstream ledger, usually `plugins/<plugin>/references/upstream-sources.md`.
- YAML frontmatter is preserved when the user requests preservation. If
  adaptation requires changes, keep all meaningful routing fields and document
  each intentional change.
- Knowledge-base targets use "knowledge base" or "KB" in user-facing text
  instead of "brain". Mentions of GBrain/GStack are allowed only in source
  provenance, audit notes, or commands that truly depend on those tools.
- Privacy and fork-specific path checks run before the change is presented.
  Do not commit absolute personal paths, emails, private channels, or private
  fork names into plugin deliverables.
- A fresh upstream-diff check is captured so future maintainers can tell
  whether the plugin copy is current, intentionally forked, or stale.
- A next-review cadence is recorded. Default to monthly for active upstream
  skills and before each plugin release for quieter skills.

## Inputs

Collect or infer:

- **Source:** upstream skill directory or `SKILL.md`.
  Use `$GBRAIN_ROOT` and `$GSTACK_ROOT` aliases in records. Resolve their
  concrete local values from environment variables or session context, but do
  not commit those absolute paths into plugin deliverables.
- **Target plugin:** for example `knowledge-base`.
- **Target slug:** for example `strategic-reading`.
- **Mode:** `new-import`, `refresh`, `diff-only`, or `ledger-only`.
- **Frontmatter policy:** `preserve-exact`, `preserve-keys`, or
  `adapt-with-notes`.

If the user asks for exact frontmatter preservation, treat that as a hard
constraint. If the upstream frontmatter conflicts with plugin runtime safety or
terminology, stop and ask before changing it.

## Phase 1: Preflight

1. Confirm you are in this repository.
2. Check `git status --short --branch`. Identify unrelated user edits and leave
   them alone.
3. Confirm source roots:
   - `GBRAIN_ROOT` points at the local GBrain checkout.
   - `GSTACK_ROOT` points at the local GStack checkout.
   Record aliases in files, not resolved absolute paths.
4. Resolve the source file and target path. Source may be outside this repo;
   target must be under `plugins/`.
5. Read the source `SKILL.md`, target `SKILL.md` if it exists, and the target
   plugin ledger if present.

## Phase 2: Source Inventory

Create a short inventory before editing:

```text
Source: $GBRAIN_ROOT/skills/<slug>/SKILL.md
Source commit: <short sha or unknown>
Target: plugins/<plugin>/skills/<slug>/SKILL.md
Mode: new-import|refresh|diff-only|ledger-only
Frontmatter policy: preserve-exact|preserve-keys|adapt-with-notes
Sibling files: <routing-eval.jsonl, references/, scripts/, assets/, none>
```

When source and target both exist, diff them before editing:

```bash
diff -u "$SOURCE" "$TARGET" | sed -n '1,220p'
```

For large skills, summarize the diff by section and list any upstream sections
that are intentionally not imported.

## Phase 3: Adaptation

Use the source as input, not as a blind copy, unless the user explicitly asks
for a raw copy.

Required adaptation checks:

- **Frontmatter:** keep `name`, `version`, `description`, `triggers`, tool
  declarations, mutability, write targets, and routing metadata unless there is
  a documented reason to alter them.
- **Terminology:** for knowledge-base plugin targets, replace user-facing
  "brain" wording with "knowledge base" or "KB". Convert GBrain-only commands
  to the plugin's available surfaces, such as `kb`, `vaultli`, or generic page
  tools, unless the command is intentionally an upstream eval/check command.
- **Paths:** replace local absolute roots with `$GBRAIN_ROOT`, `$GSTACK_ROOT`,
  or repo-relative paths. Do not write absolute home-directory paths into
  deliverables.
- **Privacy:** scrub real names, emails, private channels, fork names, internal
  project names, client names, and screenshots or examples that identify a real
  private workspace.
- **Sibling files:** import only files that are needed by the target skill.
  Keep `routing-eval.jsonl`, references, scripts, and assets beside the skill
  when they are part of the behavior.
- **Plugin fit:** if the workflow is for maintaining plugin sources rather than
  for end users of one plugin, keep it in `plugins/plugin-manager/skills/`.

## Phase 4: Record The Ledger

Every imported or refreshed skill gets a durable entry in the target plugin
ledger. Use `references/harvest-record-template.md` for the shape.

At minimum, record:

- target skill path
- source alias path
- upstream repository and commit, when available
- import or refresh date
- frontmatter policy and intentional frontmatter changes
- terminology changes
- privacy/path scrub result
- files imported or intentionally skipped
- validation commands and outcomes
- next upstream review date or cadence

If a skill was adapted from user-provided text rather than directly copied from
a checkout, record the probable upstream file and say that the source was the
user-provided version for this repository.

## Phase 5: Validate

Run the bundled checker on the target. For a knowledge-base plugin skill:

```bash
python3 plugins/plugin-manager/skills/upstream-skill-harvest/scripts/harvest_check.py \
  --source "$GBRAIN_ROOT/skills/<slug>/SKILL.md" \
  --target "plugins/knowledge-base/skills/<slug>/SKILL.md" \
  --ledger "plugins/knowledge-base/references/upstream-sources.md" \
  --target-name "plugins/knowledge-base/skills/<slug>/SKILL.md" \
  --require-source-frontmatter-keys \
  --kb-terminology \
  --json
```

Use `--preserve-frontmatter` only when exact YAML preservation was requested.
If the checker flags GBrain/GStack terms, decide whether each occurrence is
provenance or runtime wording. Runtime wording must be converted; provenance
may remain when it is clearly labeled.

Also run repo-native validation that matches the change:

- Skill-only change: `python3 -m pytest tests/test_plugins/test_upstream_skill_harvest.py`
- Plugin package change: `claude plugin validate plugins/<plugin>` when
  available
- KB file-vault artifact change: `vaultli --json validate --root <kb-root>`

Do not claim completion without fresh validation output.

## Phase 6: Periodic Review

For each ledger entry, review upstream drift monthly or before a plugin release:

1. Resolve the source alias to the local checkout.
2. Capture the upstream short SHA.
3. Diff source against target.
4. Classify drift:
   - `current` - no material upstream change
   - `intentional-fork` - target differs for documented plugin reasons
   - `needs-refresh` - upstream added behavior that should be adapted
   - `blocked` - privacy, path, or dependency issue needs user input
5. Update the ledger with review date, upstream SHA, classification, and next
   review cadence.

## Output Format

```text
UPSTREAM SKILL HARVEST
Source: $GBRAIN_ROOT/skills/<slug>/SKILL.md @ <sha>
Target: plugins/<plugin>/skills/<slug>/SKILL.md
Mode: new-import|refresh|diff-only|ledger-only
Frontmatter: preserved-exact|preserved-keys|adapted-with-notes
Terminology: converted|not-applicable|needs-review
Privacy/path check: pass|fail
Ledger: plugins/<plugin>/references/upstream-sources.md
Validation:
- <command>: pass|fail
Next review: <cadence/date>
Files changed:
- <path>
```

## Anti-Patterns

- Putting this maintainer workflow inside a shipped plugin when it is not for
  that plugin's end users.
- Copying upstream files without reading them.
- Dropping YAML frontmatter because the target plugin has simpler examples.
- Leaving "brain" or `gbrain` runtime wording in a KB plugin skill.
- Committing absolute local paths in plugin deliverables.
- Treating privacy lint as enough. Humans must still read examples, triggers,
  comments, and routing evals.
- Importing multiple large skills at once without separate ledger entries.
- Updating a skill without recording the upstream source SHA and adaptation
  notes.
