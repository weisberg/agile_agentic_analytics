---
name: manage-plugins
version: 0.1.0
description: |
  Top-level workflow for maintaining plugins in this marketplace. Use when
  creating a plugin, adding or moving plugin skills, checking plugin manifests,
  updating marketplace entries, validating packaging, preparing a plugin release,
  or deciding whether work belongs in a plugin, a plugin-manager workflow, or a
  shared template. Trigger here for "create a new plugin entry", "generated
  Claude and Codex manifests stay in sync", "move this maintainer workflow into
  plugin-manager", "marketplace source of truth", "plugin maintenance request",
  or "add a new skill folder to an existing plugin and update the plugin docs".
  Use plugin-health for audit-only conformance checks, plugin-release for final
  version bump / publish handoff, skill-improve for a bounded edit to one
  existing skill, and upstream-skill-harvest only for importing or refreshing a
  skill from an external upstream checkout.
triggers:
  - "manage plugins"
  - "create plugin"
  - "update plugin"
  - "plugin manager"
  - "validate plugin"
  - "publish plugin"
  - "move skill into plugin"
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

# Manage Plugins

## Contract

Plugin maintenance is complete only when:

- Plugin components live in valid Claude Code plugin locations.
- `marketplace.yaml` is the source of truth for marketplace metadata.
- Generated `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` files
  have stable metadata: `name`, `description`, `version`, `author`, `license`,
  and useful `keywords`.
- Generated marketplace registration exists in both
  `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` when
  the plugin should be installable.
- Skills keep YAML frontmatter and have descriptions that explain real trigger
  situations.
- Cross-plugin maintenance workflows live in the `plugin-manager` plugin unless
  they are meant for end users of one specific plugin.
- Intent is routed to the narrowest workflow that can complete it; broad
  management does not absorb release, health, harvest, skill-improvement, or
  full SkillOpt requests after those are identified.
- Validation is run, or any unavailable validation command is called out.
- Existing user edits are left untouched unless the task requires integrating
  them.

## Routing

Use this skill as the first stop for plugin work, then route:

- **Harvest or refresh upstream skills from GBrain/GStack:** read
  `../upstream-skill-harvest/SKILL.md` and follow that workflow.
- **Audit plugin health or skill conformance:** read
  `../plugin-health/SKILL.md` and run the bundled audit script.
- **Prepare a plugin release:** read `../plugin-release/SKILL.md` and follow
  its version, docs, validation, and approval gates.
- **Review onboarding or contributor experience:** read
  `../plugin-devex-review/SKILL.md` and run the fresh-user path checks.
- **Save or restore long-running plugin work:** read
  `../plugin-work-checkpoint/SKILL.md` and write/read a checkpoint.
- **Run a high-impact quality gate:** read
  `../plugin-quality-gate/SKILL.md` before tests or release lock in behavior.
- **Improve one skill without a full training loop:** read
  `../skill-improve/SKILL.md` and keep edits bounded and evidence-backed.
- **Run a full SkillOpt-style training loop:** read
  `../skillopt-training-run/SKILL.md` and follow its rollout, reflection, gate,
  slow/meta, and release phases.
- **Create a new plugin:** create `plugins/<plugin-name>/README.md`, any needed
  `skills/`, `agents/`, `references/`, `scripts/`, or `bin/` directories, and a
  new `plugins[]` entry in `marketplace.yaml`.
- **Add a skill to a plugin:** put it at
  `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` with optional sibling
  `scripts/`, `references/`, or `assets/`.
- **Move a maintainer skill:** if it manages plugins or the marketplace itself,
  put it under this plugin's `skills/<skill-name>/` directory.
- **Validate or publish:** inspect manifests, marketplace entry, skill
  frontmatter, docs, tests, and git status before committing or pushing.

## Workflow

1. **Preflight**
   - Run `git status --short --branch`.
   - Identify unrelated changes and do not overwrite them.
   - Read `CLAUDE.md`, `PLUGIN_ARCHITECTURE.md`, and the target plugin
     `README.md` or manifest if relevant.

2. **Classify the work**
   - `new-plugin`
   - `plugin-update`
   - `skill-add-or-move`
   - `upstream-harvest`
   - `skill-improve`
   - `skillopt-training-run`
   - `marketplace-entry`
   - `validation-or-release`
   - If the request matches a narrower workflow, route there before editing.
     Continue only for cross-cutting coordination or when the target workflow
     returns with an explicit handoff.

3. **Apply the repo convention**
   - Distributable plugins live under `plugins/<plugin-name>/`.
   - Plugin manifests are generated at
     `plugins/<plugin-name>/.claude-plugin/plugin.json` and
     `plugins/<plugin-name>/.codex-plugin/plugin.json`.
   - Plugin skills live under `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`.
   - Shared skill frontmatter must include `name`, `description`, and
     `disable-model-invocation`.
   - To restrict a skill's capabilities, use `allowed-tools` (never `tools`,
     which is an agent-only field the skill loader ignores) with canonical
     Claude Code tool names from `docs/TOOLS_REFERENCE.md` (e.g. `Read`,
     `Write`, `Edit`, `Bash`, `Grep`, `Glob`, `Agent`). Give read-only audit
     skills `Read`/`Bash`/`Grep`/`Glob` and withhold `Write`/`Edit`.
   - `triggers`, `mutating`, and `version` are repo-convention metadata only;
     the Claude Code loader does not read them, so routing rides entirely on the
     `description`. Keep them for human/tooling use, but never rely on them for
     invocation or capability behavior.
   - Marketplace-wide maintainer workflows live in this plugin.
   - Health, release, devex, checkpoint, quality-gate, and upstream sync
     workflows should be shared from `plugin-manager` instead of copied into
     every plugin.
   - Do not put component directories inside `.claude-plugin/`.

4. **Update docs and marketplace**
   - Update plugin `README.md` when user-facing skills or tools change.
   - Update root `README.md` for installable plugin additions.
   - Update `marketplace.yaml` when marketplace metadata, versions, or plugin
     entries change.
   - Run `npm run render` to refresh generated Claude Code and Codex files.
   - Do not hand-edit `.claude-plugin/marketplace.json`,
     `.agents/plugins/marketplace.json`, `.claude-plugin/plugin.json`, or
     `.codex-plugin/plugin.json` to fix metadata drift; fix the source file or
     renderer and rerun.
   - When skill trigger text or routing intent changes, add or update
     `routing-eval.jsonl` beside that skill.
   - Update `CLAUDE.md` or `PLUGIN_ARCHITECTURE.md` only for repo-wide
     conventions, not every small plugin change.

5. **Validate**
   - Run focused tests for any scripts changed.
   - Run `npm run render:check`.
   - Run `npm run validate`.
   - Run `python3 -m json.tool` on generated marketplace files or changed JSON
     when debugging schema errors.
   - Run `claude plugin validate plugins/<plugin-name>` when available.
   - Run `python3 "${CLAUDE_PLUGIN_ROOT}/skills/plugin-health/scripts/plugin_audit.py" --plugin <plugin-name> --json`.
   - Run plugin-specific checks such as `harvest_check.py` or `vaultli validate`
     when the plugin provides them.

## Output Format

```text
PLUGIN MANAGER RESULT
Mode: new-plugin|plugin-update|skill-add-or-move|upstream-harvest|skill-improve|skillopt-training-run|marketplace-entry|validation-or-release
Plugin: <plugin-name>
Files changed:
- <path>
Validation:
- <command>: pass|fail|not-run
Notes:
- <important decision or follow-up>
```

## Anti-Patterns

- Creating plugin skills inside `.claude-plugin/`.
- Leaving a new plugin out of the marketplace when the user expects it to be
  installable.
- Hand-editing generated marketplace or manifest JSON instead of updating
  `marketplace.yaml` and rerendering.
- Continuing as the router after the request clearly belongs to a narrower
  workflow.
- Duplicating the same maintainer workflow inside every plugin.
- Dropping YAML frontmatter while moving skills.
- Editing unrelated plugin files to make the diff look tidy.
- Claiming a plugin is ready without checking JSON, skill paths, and validation.
