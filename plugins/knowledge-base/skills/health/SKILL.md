---
name: health
version: 0.2.0
description: >-
  Audit and repair KB decision-readiness in one pass — plugin and vault health checks, YAML frontmatter and sidecar/index validation, stale pages, orphan pages, dead links and missing back-links, citation gaps, and a scored dashboard with prioritized remediation. Trigger on 'KB health', 'knowledge base doctor', 'validate/fix frontmatter', 'lint the vault', 'stale or orphan pages', 'fix backlinks', 'KB dashboard'. Absorbs maintenance, frontmatter-guard, and dashboard. For repairing citations specifically use citation-fixer; for routing-coverage checks use resolver.
triggers:
  - "kb health"
  - "knowledge base doctor"
  - "validate and fix frontmatter"
  - "fix orphan pages and backlinks"
  - "kb dashboard"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
disable-model-invocation: false
mutating: true
---

# Health

## Contract

- Health output is both human-readable and machine-actionable, and every red/yellow status links to a concrete fix.
- Frontmatter/index issues are fixed first, then citations, then graph/back-links, then stale state; derived files are never hand-edited.
- Bulk remediation is sampled before large writes; vault, skill, manifest, and generated-artifact checks are all visible.
- Mutating skill: repair mode may edit KB pages, but audit mode is read-only and must not alter files.

## Intake And Modes

- Treat `$ARGUMENTS` as vault root plus optional audit-only/fix mode, dimensions, and output path.
- Quick mode: run validate/dashboard and return a prioritized health verdict.
- Standard mode: fix a bounded set of frontmatter, sidecar, citation, or graph issues after sampling.
- Deep mode: produce a remediation plan for stale pages, duplicate entities, and recurring health failures.
- Use `ask-user` before deleting pages, merging entities, or applying broad repair batches.

## Evidence Requirements

- Inspect plugin audit output, vault validation, dashboard JSON, and changed-file state before claiming health.
- For stale-page repairs, load the latest timeline/source evidence first; route disputed facts to `conflict-resolution`.

## Workflow

- Run `/plugin-manager:plugin-health` or `plugin_audit.py` for packaging, and `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root <kb-root>` for the vault.
- Run `frontmatter-audit`, then `dashboard` to score frontmatter, citations, graph, raw sources, privacy, and resolver dimensions.
- Repair frontmatter/index issues, scaffold missing sidecars, fix dead links and missing back-links, and refresh stale State sections.
- Merge duplicate entities and route contradictions to `conflict-resolution`.
- Rebuild indexes, rerun `dashboard`, and record the health delta and remaining manual decisions.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" dashboard`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" frontmatter-audit`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" maintenance-plan`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" resolver-check`


## Output Format

- KB HEALTH
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Verdict, scorecard, failures, warnings, fixes applied, remaining actions, JSON evidence.
- Artifact path: inline for quick checks; saved report at `reports/<YYYYMMDD>-kb-health.md` when requested.

## Anti-Patterns

- Treating ignored generated files as invisible packaging risk, or returning only prose when CI needs JSON.
- Fixing stale pages without checking the latest timeline/source evidence.
- Deleting orphans without first checking whether links are merely missing.
