# Knowledge Base Issue Coverage

This map ties the open Knowledge Base roadmap issues to shipped plugin
artifacts. Keep it current when issues are closed or reopened.

## Portfolio

- #30 Resolver: `skills/resolver/SKILL.md`, `plugin-manager` routing JSONL audit.
- #31 Query skill: `skills/query/SKILL.md`, `references/retrieval-and-benchmarks.md`.
- #32 Signal detector: `skills/signal-detector/SKILL.md`, `skills/originals/SKILL.md`.
- #33 Enrich: `skills/enrich/SKILL.md`, `skills/conflict-resolution/SKILL.md`.
- #34 Citation fixer: `skills/citation-fixer/SKILL.md`, page/source schemas.
- #35 Frontmatter guard: `skills/frontmatter-guard/SKILL.md`, `vaultli` validation.
- #36 Filing rules: `skills/filing-rules/SKILL.md`, `references/schemas/page-types.md`.
- #37 Article enrichment: `skills/article-enrichment/SKILL.md`, raw source reference.
- #38 Meeting ingestion: `skills/meeting-ingestion/SKILL.md`, sample meeting fixture.
- #39 Media ingest: `skills/media-ingest/SKILL.md`, sidecar and raw-source guidance.
- #40 Voice-note ingest: `skills/voice-note-ingest/SKILL.md`, `skills/originals/SKILL.md`.
- #41 Cold start: `skills/cold-start/SKILL.md`, setup and sample vault paths.
- #42 Migrate: `skills/migrate/SKILL.md`, vaultli import/frontmatter workflow.
- #43 Archive crawler: `skills/archive-crawler/SKILL.md`, checkpoint/batch rules.
- #44 Concept synthesis: `skills/concept-synthesis/SKILL.md`, conflict handling.
- #45 Book mirror: `skills/book-mirror/SKILL.md`, raw-source and citation rules.
- #46 Academic verify: `skills/academic-verify/SKILL.md`, current research handoff.
- #47 Current research: `skills/current-research/SKILL.md`, freshness routing.
- #48 Strategic reading hardening: `skills/strategic-reading/SKILL.md`, routing eval,
  sample strategic reading page, and upstream ledger.
- #49 Briefing: `skills/briefing/SKILL.md`, query/current-research chain.
- #50 Task manager: `skills/task-manager/SKILL.md`, integration envelope.
- #51 Reports: `skills/reports/SKILL.md`, page schema and dashboard linkage.
- #52 Publish: `skills/publish/SKILL.md`, privacy/security reference.
- #53 PDF export: `skills/pdf-export/SKILL.md`, publish/privacy gate.
- #54 Webhook transforms: `skills/webhook-transforms/SKILL.md`,
  `references/schemas/integration-contracts.md`.
- #55 Cron scheduler: `skills/cron-scheduler/SKILL.md`, `references/automation.md`.
- #56 Background jobs: `skills/background-jobs/SKILL.md`, checkpoints and batch rules.
- #57 Health: `skills/health/SKILL.md`, `plugin-manager:plugin-health` audit.
- #58 Conformance tests: `tests/test_plugins/`, `tests/test_knowledge_base/`.
- #59 Quality gate: `skills/quality-gate/SKILL.md`,
  `plugin-manager:plugin-quality-gate`.
- #60 Vaultli CI parity: `.github/workflows/knowledge-base-vaultli.yml`,
  Python first-index fix, sample vault validation.
- #61 Generated artifact hygiene: `plugins/knowledge-base/.gitignore`,
  plugin audit generated-artifact check, removed ignored caches/targets.
- #62 Raw source: `skills/raw-source/SKILL.md`,
  `references/raw-source-storage.md`.
- #63 Source router: `skills/source-router/SKILL.md`.
- #64 Search modes: `skills/search-modes/SKILL.md`,
  `references/retrieval-and-benchmarks.md`.
- #65 Graph ops: `skills/graph-ops/SKILL.md`, relationship sections in schemas.
- #66 Schemas: `references/schemas/page-types.md`,
  `references/schemas/integration-contracts.md`.
- #67 Privacy/security: `skills/privacy-security/SKILL.md`,
  `references/privacy-and-security.md`.
- #68 Agents: `agents/kb-curator.md`, `agents/kb-researcher.md`,
  `agents/kb-ops-auditor.md`.
- #69 Context checkpoint: `skills/context-checkpoint/SKILL.md`,
  `plugin-manager:plugin-work-checkpoint`.
- #70 Browser ingest: `skills/browser-ingest/SKILL.md`.
- #71 Sample vault: `references/samples/mini-vault/`,
  `references/samples/walkthrough.md`.
- #72 Release upgrade: `skills/release-upgrade/SKILL.md`,
  `references/release-upgrade.md`, `plugin-manager:plugin-release`.
- #73 Upstream sync: `plugins/plugin-manager/skills/upstream-skill-harvest/`,
  `references/upstream-sources.md`.
- #74 Dashboard: `skills/dashboard/SKILL.md`.
- #75 Maintenance: `skills/maintenance/SKILL.md`.
- #76 Setup: `skills/setup/SKILL.md`, sample vault quickstart.
- #77 Graph query: `skills/graph-ops/SKILL.md`, retrieval benchmark reference.
- #78 Integration contracts: `skills/integration-contracts/SKILL.md`,
  integration schema reference.
- #79 Devex review: `skills/devex-review/SKILL.md`,
  `plugin-manager:plugin-devex-review`.
- #80 KB ops: `skills/kb-ops/SKILL.md`.
- #81 Conflict resolution: `skills/conflict-resolution/SKILL.md`.
- #82 Originals: `skills/originals/SKILL.md`, signal detector and voice-note routes.

## Closeout Gate

Before closing the issue set, run:

```bash
python3 plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py --plugin knowledge-base --json
python3 plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py --plugin plugin-manager --strict-sections --json
uv run --no-project --with pytest --with numpy --with pandas pytest tests/test_plugins tests/test_knowledge_base
```

All three commands should pass with zero plugin-health warnings for the
knowledge-base plugin.
