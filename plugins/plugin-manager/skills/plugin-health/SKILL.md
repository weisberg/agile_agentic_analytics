---
name: plugin-health
version: 0.1.0
description: |
  Run plugin health, conformance, and packaging audits for one plugin or the
  whole marketplace. Use when checking plugin manifests, marketplace entries,
  skill frontmatter, required skill sections, routing fixtures, references,
  generated artifacts, or CI readiness. Inspired by GBrain skillpack-check and
  GStack health.
triggers:
  - "plugin health"
  - "check plugin health"
  - "skillpack health"
  - "validate all plugins"
  - "check skill conformance"
  - "doctor plugin"
tools:
  - read
  - exec
mutating: false
writes_pages: false
---

# Plugin Health

## Contract

This skill returns a plugin health report with:

- `ok`: true only when no failing checks remain.
- `summary`: one-line human-readable status.
- `actions`: remediation hints that can be executed or assigned.
- `plugins`: per-plugin checks for manifest, marketplace, skills, references,
  routing evals, generated artifacts, and optional strict sections.

It follows the GBrain `skillpack-check` pattern: JSON first for agents and CI,
plain summary for humans, specific remediation hints for every failure.

## Workflow

1. **Preflight**
   - Run `git status --short --branch`.
   - Identify whether the user asked for one plugin or the whole marketplace.
   - Read `plugins/plugin-manager/references/gbrain-gstack-learnings.md` if
     changing the audit shape.

2. **Run the audit**

   ```bash
   python3 plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py \
     --plugin <plugin-name> \
     --json
   ```

   Omit `--plugin` to audit every plugin. Add `--strict-sections` when preparing
   a plugin release or checking newly imported skills.

3. **Add plugin-specific checks**
   - For `plugin-manager`: run the upstream harvest tests and `harvest_check.py`
     against manager skills.
   - For `knowledge-base`: run the upstream ledger checks and KB terminology
     checks through `/plugin-manager:upstream-skill-harvest`.
   - For plugins with bundled CLIs, run their help/validate commands.

4. **Report**
   - Lead with the health verdict.
   - List failing checks by plugin and path.
   - Include remediation commands or file edits.
   - Do not auto-fix unless the user asks for repair.

## Output Format

```text
PLUGIN HEALTH
Scope: <plugin-name|all>
Verdict: healthy|action-needed|unknown
Summary: <one line>
Actions:
- <specific remediation>
Checks:
- <plugin>: <pass/fail counts>
Artifacts:
- JSON: <printed or saved path>
```

## Anti-Patterns

- Treating warnings as release blockers without saying why.
- Printing only prose when CI or another agent needs JSON.
- Hiding which check produced a failure.
- Running destructive cleanup to fix generated artifacts.
- Claiming a plugin is healthy without checking marketplace registration and
  skill frontmatter.

