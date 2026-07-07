---
name: vaultli
description: >
  Use when initializing, maintaining, validating, searching, documenting, or
  assembling context from a file-based knowledge base with the bundled vaultli
  CLI. Trigger on knowledge vaults, KB setup, .kbroot, YAML frontmatter,
  sidecar markdown, INDEX.jsonl, documenting SQL/templates/configs/scripts,
  validating stale or broken KB state, searching vault metadata, hydrating
  source assets, assembling retrieval context, or federated lookup across
  multiple vault roots.
triggers:
  - "vaultli"
  - "validate knowledge base vault"
  - "index KB vault"
  - "search vault metadata"
  - "assemble vault context"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
mutating: true

disable-model-invocation: false
---

# vaultli

Use `vaultli` when the task is to make a file tree of knowledge assets
discoverable, auditable, retrievable, and safe for later agents. It is the
Knowledge Base plugin's bundled CLI for vault roots, YAML metadata, sidecar
documentation, JSONL indexes, validation, metadata search, and deterministic
context assembly.

The bundled implementation lives at `../../vaultli/` relative to this skill.
Enabled plugin sessions also expose a wrapper at `bin/vaultli`, so normal use
looks like:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json <command> ...
```

For deeper reference, read only what you need:

- `../../vaultli/README.md` for the tool overview and command surface.
- `../../vaultli/vaultli-spec-v1.0.md` for the storage and metadata spec.
- `../../vaultli/SKILL.md` for the original full tool operating guide.
- `../../references/samples/walkthrough.md` for a synthetic sample vault flow.
- `../../references/schemas/page-types.md` for KB page type conventions.

## Contract

When this skill is used:

- The source of truth is the file tree. `INDEX.jsonl` is a rebuildable cache.
- Markdown pages carry YAML frontmatter inline.
- Non-markdown assets become discoverable only through same-directory sidecar
  markdown files such as `retention.sql.md`.
- Generated metadata is treated as a draft and refined before claiming the KB
  is high quality.
- Bulk writes are previewed with `--dry-run` and narrowed with `--include` or
  `--exclude` when the tree is large.
- Every material edit is followed by `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index` and
  `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate`.
- Retrieval happens in two stages: search metadata first, then hydrate body or
  source content with `resolve`, `cat`, or `context`.
- `search --semantic` is token-overlap matching over indexed metadata, not a
  vector database or full-text search engine.
- Do not edit `INDEX.jsonl` directly.

## When To Use

Use this skill for:

- Creating or finding KB vault roots.
- Adding or repairing markdown frontmatter.
- Creating sidecars for SQL, Jinja, JSON, YAML, TOML, scripts, configs, and
  other non-markdown assets.
- Bulk scaffolding, indexing, validation, search, hydration, context assembly,
  federated lookup, and stale/broken state audits.

## When Not To Use

Do not use `vaultli` as the primary tool for:

- Current web facts. Use `current-research`, then file the result if needed.
- Semantic/vector retrieval expectations. `vaultli` is metadata-first.
- Editing large binary assets. Store or point to them, then document with a
  sidecar.
- Replacing citation, privacy, or filing judgment. Pair with `citation-fixer`
  and `health`, and read `references/privacy-and-security.md` and
  `references/kb-filing-rules.md`, when those concerns matter.
- Automatically fixing validation failures without inspecting what they mean.

## Core Mental Model

vaultli uses markdown to wrap knowledge, YAML frontmatter for metadata, and JSONL for rebuildable indexes.

A typical vault:

```text
kb/
  .kbroot
  INDEX.jsonl
  concepts/decision-quality.md
  queries/retention.sql
  queries/retention.sql.md
  templates/report.j2
  templates/report.j2.md
```

Native markdown files are indexed directly. Non-markdown files are indexed
through sidecars. Sidecars keep the original asset valid in its native format
and put retrievable metadata and prose in markdown.

## Invocation Rules

Prefer the plugin wrapper:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json --help
```

The wrapper chooses a compatible bundled Rust binary if one has been built,
then falls back to the Python package with `PYTHONPATH` pointed at the plugin
root. In local development, the Python fallback requires `PyYAML`.

Use `--json` in agent workflows unless the user explicitly wants human-only
terminal output. JSON output makes failures parseable and prevents brittle
screen-scraping.

Always pass `--root <vault-root>` for commands that operate on a vault. Do not
depend on the shell's current directory unless root discovery is the task.

## Command Selection

| Need | Command |
| --- | --- |
| Create/find root | `init <path>`, `root <path>` |
| Preview IDs/metadata | `make-id <file> --root <root>`, `infer <file> --root <root>` |
| Add markdown | `add <file> --root <root>` |
| Add non-markdown sidecar | `scaffold <file> --root <root>` |
| Bulk scaffold | `ingest <path> --root <root> --dry-run` |
| Maintain fields | `set`, `unset`, `refresh` |
| Rebuild/audit | `index --root <root>`, `validate --root <root>` |
| Search/hydrate | `search`, `show`, `resolve`, `cat`, `context` |
| Multi-vault/git | `federated-search`, `git-info`, `dump-index` |

## Workflow

For most maintenance work, run this loop:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json root .
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json ingest ./kb --root ./kb --dry-run
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index --root ./kb
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root ./kb
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search "retention query" --root ./kb --limit 5
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json resolve queries/retention --root ./kb --body --source
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json context --root ./kb --id queries/retention --token-budget 2000
```

If `ingest --dry-run` shows too many changes, narrow it:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json ingest ./kb --root ./kb --dry-run --include 'queries/*.sql'
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json ingest ./kb --root ./kb --dry-run --exclude 'tmp/**'
```

After reviewing the dry-run, run the write command intentionally:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json ingest ./kb --root ./kb --index --include 'queries/*.sql'
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root ./kb
```

### Creating A New Vault

Pick a root that belongs to the user or project, initialize only when `.kbroot`
is missing, add or scaffold a few representative files, refine metadata, then
index and validate:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json init ./kb
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json add ./kb/concepts/decision-quality.md --root ./kb
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json scaffold ./kb/queries/open_tasks.sql --root ./kb
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index --root ./kb
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root ./kb
```

`.kbroot` may contain conservative YAML defaults:

```yaml
defaults:
  author: brian
  scope: personal
  domain: knowledge-management
```

Defaults should never be used to hide per-file specificity.

## Metadata Quality

The practical fields for useful retrieval are:

- `id`: stable path-derived identifier, used by links and dependencies.
- `title`: human-readable display name.
- `description`: one precise sentence explaining what the page or asset is for.
- `category`: useful type such as `person`, `company`, `concept`, `meeting`,
  `source`, `query`, `template`, `runbook`, `report`, or `task`.
- `tags`: flat, retrieval-friendly keywords.
- `status`: `draft`, `active`, `review`, `deprecated`, or `archived`.
- `scope`: `personal`, `team`, `org`, or `public`.
- `related` and `depends_on`: soft links and structural prerequisites.
- `source`: required for sidecars and relative to the sidecar.

Treat `description` as the most valuable retrieval field. Replace generic
scaffold text like "Markdown document for..." with specific language that
answers: "When should an agent retrieve this?"

Good:

```yaml
description: >-
  SQL query that finds overdue renewal tasks by account owner and priority for
  weekly customer-success review.
tags: [renewal, tasks, customer-success, sql]
category: query
```

Weak:

```yaml
description: SQL query stored in the vault.
tags: [query]
```

## Sidecar Workflow

For a non-markdown asset, keep the source file untouched and create a sidecar:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json scaffold ./kb/queries/open_tasks.sql --root ./kb
```

Expected files:

```text
kb/queries/open_tasks.sql
kb/queries/open_tasks.sql.md
```

The sidecar frontmatter must include:

```yaml
source: ./open_tasks.sql
```

Fill the body with purpose, parameters, assumptions, usage, sample output, and
downstream consumers. `search` finds the sidecar metadata; `resolve --source`
or `cat --source` retrieves the executable SQL/template/config.

Sidecar rules:

- The sidecar lives beside the source asset and is named `<source>.<ext>.md`.
- A broken `source` field makes validation fail.
- Sidecar-backed hashes are based on source asset bytes.

## Bulk Ingestion

Use bulk ingestion when a directory already contains useful files but lacks KB
metadata.

Start with a preview, slice large trees, then write in batches:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json ingest ./kb --root ./kb --dry-run
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json ingest ./kb --root ./kb --dry-run --include 'queries/*.sql'
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json ingest ./kb --root ./kb --dry-run --exclude 'archive/**'
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json ingest ./kb --root ./kb --index --include 'queries/*.sql'
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root ./kb
```

After writing, manually improve generated metadata. The scaffold is allowed to
be mechanical; the curated KB should not stay mechanical.

## Metadata Maintenance

Use `set`, `unset`, and `refresh` for simple frontmatter changes:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json set queries/open-tasks status active --root ./kb --index
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json set queries/open-tasks scope team --root ./kb --index
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json unset queries/open-tasks priority --root ./kb --index
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json refresh queries/open-tasks --root ./kb --field tags --index
```

Use manual editing when changing prose, multi-line descriptions, relationship
lists, or citations. After manual editing:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index --root ./kb
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root ./kb
```

Avoid ID churn. If an ID changes because a file moved or was renamed, inspect
`related`, `depends_on`, backlinks, citations, and external references.

## Validation And Repair

Run validation after every material batch:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root ./kb
```

Common validation failures:

| Code or symptom | Meaning | Usual fix |
| --- | --- | --- |
| Missing index | Index has not been built | `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index --root <root>` |
| Duplicate IDs | Two pages resolve to the same ID | Rename/move one file or set a distinct ID if supported |
| Broken source | Sidecar `source` target is missing | Fix path or restore the source asset |
| Dangling related/depends_on | Relationship points to a missing ID | Correct the ID or remove the stale link |
| Stale index | Source files differ from index cache | Rebuild with `index` |
| Invalid frontmatter | YAML is malformed or not a mapping | Repair the YAML delimiters and values |

`validate` reports; it does not repair. Inspect failures before changing files,
and sample 3-5 files before a broad repair.

## Retrieval Workflow

Search first:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search "renewal risk" --root ./kb --limit 10
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search --root ./kb --category company --tag renewal-risk
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search "open tasks" --root ./kb --sort priority --order asc
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search "decision quality" --root ./kb --semantic --explain
```

Then hydrate:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json show companies/acme-example --root ./kb
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json resolve companies/acme-example --root ./kb --body
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json resolve queries/open-tasks --root ./kb --body --source
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" cat queries/open-tasks --root ./kb --source
```

Use `search` to shortlist, `show` for metadata, `resolve` for paths/body/source
JSON, `cat` for raw text, and `context` for answer-ready bundles.

Do not answer from `search` metadata alone when the body or source content
matters. Search results are pointers, not full evidence.

## Context Assembly

Use `context` when the next step is synthesis or answering:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json context "renewal risk" --root ./kb --limit 5 --token-budget 3000
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json context --root ./kb --id companies/acme-example --related --token-budget 4000
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json context --root ./kb --id queries/open-tasks --no-dependencies
```

`context` is deterministic and useful for reproducible prompts. Still inspect
whether the bundle includes enough source evidence; add explicit IDs if search
missed important records.

## Federated Search

Use federated search when the question crosses source scopes:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json federated-search "renewal risk" \
  --vault ./personal-kb \
  --vault ./team-kb \
  --per-vault-limit 5 \
  --limit 10
```

In outputs and answers, preserve vault origin and privacy scope. Do not merge
personal and team facts without labeling their source.

## Git And Change Awareness

Use `git-info` when you need to know whether a vault or item is dirty before
writing, committing, migrating, or publishing:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json git-info --root ./kb
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json git-info queries/open-tasks --root ./kb
```

If the target file is dirty and the changes are not yours, read them and work
with them. Do not overwrite user edits to frontmatter or source assets.

## Sample Vault Smoke Test

The Knowledge Base plugin ships a synthetic mini vault:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search --tag renewal-risk --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json context --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault" --id companies/acme-example --related
```

Use this fixture when checking whether the plugin wrapper, Python fallback,
indexing, validation, sidecars, and retrieval flow are functioning.

## Integration With Other KB Skills

- `setup`: create or verify the first vault.
- `health`: repair metadata and index/graph state with `validate`, `set`,
  `unset`, `refresh`, and `index` (health absorbed frontmatter-guard and
  maintenance).
- `ingest`, `media-ingest`, `meeting-ingestion`: make filed source assets
  discoverable with sidecars.
- `query`: use `search`, `resolve`, and `context` as the local retrieval
  substrate (query absorbed search-modes, source-router, and graph-ops; see
  `references/retrieval.md`).
- `references/raw-source-storage.md` and `references/privacy-and-security.md`:
  check source pointers, large assets, `scope`, and sensitivity before broad
  indexing or publishing.
- `citation-fixer`: hydrate pages with `resolve --body` before repairing gaps.
- `sample-vault`: keep fixtures, parity, and plugin-health checks current.

## Output Format

For maintenance tasks:

```text
VAULTLI RESULT
Root: <vault root>
Operation: <init/add/scaffold/ingest/index/validate/search/context/...>
Files changed: <count and paths, or none>
Index: <rebuilt/skipped/missing>
Validation: <pass/fail and issue count>
Results: <key IDs or records>
Next action: <none / inspect failures / refine metadata / rerun command>
```

For retrieval tasks:

```text
VAULTLI RETRIEVAL
Root: <vault root>
Query: <query or IDs>
Mode: <metadata/filter/semantic/context/federated>
Matches: <IDs with titles>
Hydrated: <IDs opened with body/source>
Confidence: <high/medium/low>
Gaps: <missing body/source/stale index/privacy constraint>
```

## Troubleshooting

- `vaultli: no bundled binary found and python3 is unavailable`: expose
  `python3` or build the Rust binary.
- `ModuleNotFoundError: yaml`: install `PyYAML` for the Python fallback.
- `No .kbroot found`: run from inside a vault or pass the correct root path.
- `INDEX_MISSING`: run `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index --root <root>`.
- Search misses obvious content: metadata may be too generic, the file may lack
  frontmatter/sidecar, or the index may be stale.
- Missing source content: check the sidecar `source` field and run `validate`.
- `--jq` fails: the external `jq` binary is not installed; use first-class
  filters when possible.
- Rust and Python disagree: rerun Rust parity tests and inspect the Python
  reference under `../../vaultli/py/`.

## Release And CI Checks

Before claiming vaultli-related changes are ready:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/../plugin-manager/skills/plugin-health/scripts/plugin_audit.py" --plugin knowledge-base --json
uv run --no-project --with pytest --with numpy --with pandas --with pyyaml pytest tests/test_knowledge_base tests/test_plugins
cargo test --locked
```

Run `cargo test --locked` from `${CLAUDE_PLUGIN_ROOT}/vaultli/rs`.

The repository also includes `.github/workflows/knowledge-base-vaultli.yml` for
CI coverage of the Python fallback, sample vault validation, plugin audits, and
Rust vaultli tests.

## Anti-Patterns

- Editing `INDEX.jsonl` by hand.
- Treating metadata search as if it loaded document bodies.
- Creating sidecars without a valid `source` field.
- Leaving scaffolded descriptions generic.
- Running broad bulk ingestion without `--dry-run`.
- Changing IDs casually.
- Mixing personal/team/org/public vaults without scope labels.
- Trusting `search --semantic` as vector retrieval.
- Skipping `validate` after metadata or source changes.
- Committing generated caches or Rust `target/` artifacts.
