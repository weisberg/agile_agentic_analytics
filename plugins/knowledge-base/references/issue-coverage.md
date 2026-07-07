# Knowledge Base Issue Coverage

This map ties the Knowledge Base roadmap issues to the current consolidated
plugin surface. Keep it current when issues are closed, reopened, or absorbed by
another survivor skill.

## Portfolio

- #30 Resolver: `skills/resolver/SKILL.md`, `references/routing-eval.jsonl`,
  and `scripts/kb_ops.py resolver-check`.
- #31 Query skill: `skills/query/SKILL.md`, `references/retrieval.md`,
  `references/retrieval-and-benchmarks.md`,
  `references/benchmarks/retrieval-benchmarks.jsonl`, and
  `scripts/kb_ops.py query`.
- #32 Signal detector and originals: `skills/signal-detector/SKILL.md`.
- #33 Enrich: `skills/enrich/SKILL.md` and
  `skills/conflict-resolution/SKILL.md`.
- #34 Citation fixer: `skills/citation-fixer/SKILL.md`,
  `references/quality.md`, page/source schemas, and
  `scripts/kb_ops.py citation-audit`.
- #35 Frontmatter guard: absorbed by `skills/health/SKILL.md`, the bundled
  `vaultli` validation flow, and `scripts/kb_ops.py frontmatter-audit`.
- #36 Filing rules: `references/kb-filing-rules.md` and
  `references/schemas/page-types.md`.
- #37 Article enrichment: absorbed by `skills/media-ingest/SKILL.md` with
  `references/raw-source-storage.md`.
- #38 Meeting ingestion: `skills/meeting-ingestion/SKILL.md` and the sample
  meeting fixture.
- #39 Media ingest: `skills/media-ingest/SKILL.md`, sidecar guidance, and
  raw-source guidance.
- #40 Voice-note ingest: absorbed by `skills/media-ingest/SKILL.md` with
  exact-phrasing handoff to `skills/signal-detector/SKILL.md`.
- #41 Cold start: absorbed by `skills/setup/SKILL.md` and sample vault paths.
- #42 Migrate: `skills/migrate/SKILL.md` and the vaultli
  import/frontmatter workflow.
- #43 Archive crawler: absorbed by `skills/migrate/SKILL.md` and
  `skills/background-jobs/SKILL.md`.
- #44 Concept synthesis: `skills/concept-synthesis/SKILL.md` and conflict
  handling.
- #45 Book mirror: absorbed by `skills/concept-synthesis/SKILL.md` with
  raw-source and citation rules.
- #46 Academic verify: absorbed by `skills/current-research/SKILL.md`.
- #47 Current research: `skills/current-research/SKILL.md` and freshness
  routing.
- #48 Strategic reading hardening: `skills/strategic-reading/SKILL.md`,
  routing eval, sample strategic reading page, and upstream ledger.
- #49 Briefing: `skills/briefing/SKILL.md` with the `query` /
  `current-research` chain.
- #50 Task manager: `skills/task-manager/SKILL.md` and integration envelope.
- #51 Reports: `skills/reports/SKILL.md`, page schema, and dashboard linkage.
- #52 Publish: `skills/publish/SKILL.md` and privacy/security reference.
- #53 PDF export: absorbed by `skills/publish/SKILL.md`.
- #54 Webhook transforms: absorbed into `skills/ingest/SKILL.md`,
  `references/connector-ingestion.md`,
  `references/schemas/integration-contracts.md`,
  `references/examples/source-event.json`, and
  `scripts/kb_ops.py normalize-event`.
- #55 Cron scheduler: absorbed by `skills/background-jobs/SKILL.md`,
  `references/automation.md`, `references/examples/weekly-kb-health.yaml`, and
  `scripts/kb_ops.py validate-schedule`.
- #56 Background jobs: `skills/background-jobs/SKILL.md`, checkpoints and batch
  rules, and `scripts/kb_ops.py checkpoint`.
- #57 Health: `skills/health/SKILL.md`, `plugin-manager:plugin-health` audit,
  and `scripts/kb_ops.py dashboard`.
- #58 Conformance tests: `tests/test_plugins/`, `tests/test_knowledge_base/`,
  and focused plugin-health strict-section checks.
- #59 Quality gate: absorbed by `skills/skillify/SKILL.md` and
  `plugin-manager:plugin-quality-gate`.
- #60 Vaultli CI parity: `skills/vaultli/SKILL.md`, bundled `vaultli/`,
  `.github/workflows/knowledge-base-vaultli.yml`, sample vault validation, and
  Rust/Python parity checks.
- #61 Generated artifact hygiene: plugin audit generated-artifact check and
  ignored cache/target paths.
- #62 Raw source: `references/raw-source-storage.md`,
  `skills/media-ingest/SKILL.md`, and `scripts/kb_ops.py raw-source-audit`.
- #63 Source router: absorbed by `skills/query/SKILL.md`.
- #64 Search modes: absorbed by `skills/query/SKILL.md`,
  `references/retrieval.md`, and `references/retrieval-and-benchmarks.md`.
- #65 Graph ops: absorbed by `skills/query/SKILL.md` and
  `skills/health/SKILL.md`, with relationship sections in schemas and
  `scripts/kb_ops.py graph-audit`.
- #66 Schemas: `references/schemas/page-types.md`,
  `references/schemas/integration-contracts.md`, and `references/templates/`.
- #67 Privacy/security: `references/privacy-and-security.md`,
  `skills/publish/SKILL.md`, `skills/health/SKILL.md`, and
  `scripts/kb_ops.py privacy-audit`.
- #68 Agents: `agents/kb-curation.md`, `agents/kb-ingestion.md`,
  `agents/kb-ops.md`, and `agents/kb-retrieval.md`.
- #69 Context checkpoint: absorbed by `skills/background-jobs/SKILL.md`,
  `plugin-manager:plugin-work-checkpoint`, and `scripts/kb_ops.py checkpoint`.
- #70 Browser ingest: absorbed by `skills/media-ingest/SKILL.md`.
- #71 Sample vault: `skills/sample-vault/SKILL.md`,
  `references/samples/mini-vault/`, and `references/samples/walkthrough.md`.
- #72 Release upgrade: `references/release-upgrade.md` and
  `plugin-manager:plugin-release`.
- #73 Upstream sync: `plugins/plugin-manager/skills/upstream-skill-harvest/`
  and `references/upstream-sources.md`.
- #74 Dashboard: absorbed by `skills/health/SKILL.md` and
  `scripts/kb_ops.py dashboard`.
- #75 Maintenance: absorbed by `skills/health/SKILL.md`,
  `skills/background-jobs/SKILL.md`, and `scripts/kb_ops.py maintenance-plan`.
- #76 Setup: `skills/setup/SKILL.md` and sample vault quickstart.
- #77 Graph query: absorbed by `skills/query/SKILL.md`,
  `references/retrieval.md`, and `scripts/kb_ops.py graph-audit`.
- #78 Integration contracts: `references/schemas/integration-contracts.md` and
  `references/connector-ingestion.md`.
- #79 Devex review: absorbed by `skills/skillify/SKILL.md` and
  `plugin-manager:plugin-devex-review`.
- #80 KB ops: absorbed by `skills/resolver/SKILL.md`,
  `skills/health/SKILL.md`, and `scripts/kb_ops.py`.
- #81 Conflict resolution: `skills/conflict-resolution/SKILL.md`.
- #82 Originals: absorbed by `skills/signal-detector/SKILL.md`.

## Closeout Gate

Before closing the issue set, run:

```bash
CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(pwd)/plugins/knowledge-base}"
python3 "${CLAUDE_PLUGIN_ROOT}/../plugin-manager/skills/plugin-health/scripts/plugin_audit.py" --plugin knowledge-base --strict-sections --json
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" resolver-check
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" retrieval-benchmark --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" dashboard --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
uv run --no-project --with pytest --with numpy --with pandas --with pyyaml pytest tests/test_plugins tests/test_knowledge_base
```

All commands should pass with zero plugin-health warnings for the
knowledge-base plugin.
