---
name: vaultli
description: >
  Use when initializing, maintaining, validating, or searching a file-based
  knowledge base with the bundled vaultli CLI. Trigger on knowledge vaults,
  KB setup, YAML frontmatter, sidecar markdown, INDEX.jsonl, documenting SQL or
  template assets, validating stale or broken KB state, searching vault
  metadata, assembling retrieval context, or federated lookup across vaults.
---

# vaultli

Use `vaultli` when the task is to make knowledge assets discoverable,
auditable, and agent-friendly in a file-based KB.

The bundled implementation lives at `vaultli/` in this plugin. The plugin also
ships a `bin/vaultli` wrapper so enabled plugin sessions can call:

```bash
vaultli --json <command> ...
```

For the full tool guide, read `../../vaultli/SKILL.md`. For the storage and
metadata schema, read `../../vaultli/vaultli-spec-v1.0.md`.

## Use Cases

- Initialize a new file-based KB root with `.kbroot` and `INDEX.jsonl`.
- Add YAML frontmatter to markdown knowledge pages.
- Create sidecar markdown for non-markdown assets such as SQL, Jinja templates,
  configs, scripts, and runbooks.
- Bulk scaffold missing metadata with a dry-run before writing.
- Rebuild `INDEX.jsonl` after page or metadata edits.
- Validate duplicate IDs, broken sources, dangling refs, and stale index state.
- Search indexed metadata, then hydrate matched records with `resolve`, `cat`, or
  `context`.
- Assemble deterministic context bundles for later answers.
- Federate search across multiple KB vault roots.

## Default Loop

Prefer JSON output in agent workflows:

```bash
vaultli --json root .
vaultli --json ingest ./kb --root ./kb --dry-run
vaultli --json index --root ./kb
vaultli --json validate --root ./kb
vaultli --json search "retention query" --root ./kb --limit 5
vaultli --json resolve queries/retention --root ./kb --body --source
vaultli --json context --root ./kb --id queries/retention --token-budget 2000
```

Use `ingest --dry-run` before bulk writes. Add `--include` and `--exclude`
globs when the tree is large.

## Command Selection

| Need | Command |
| --- | --- |
| Create a vault root | `vaultli --json init <path>` |
| Find the nearest vault root | `vaultli --json root <path>` |
| Add markdown frontmatter and index | `vaultli --json add <file> --root <root>` |
| Create sidecar metadata for a non-markdown asset | `vaultli --json scaffold <file> --root <root>` |
| Bulk scaffold missing metadata | `vaultli --json ingest <path> --root <root> --dry-run` |
| Rebuild the derived index | `vaultli --json index --root <root>` |
| Audit vault consistency | `vaultli --json validate --root <root>` |
| Search metadata | `vaultli --json search <query> --root <root>` |
| Hydrate a result | `vaultli --json resolve <id> --root <root> --body --source` |
| Print raw content | `vaultli cat <id> --root <root> --source` |
| Build a context bundle | `vaultli --json context --root <root> --id <id>` |
| Search across vaults | `vaultli --json federated-search <query> --vault <root> --vault <other>` |

## Rules

- Never edit `INDEX.jsonl` directly; rebuild it with `vaultli index`.
- Treat `INDEX.jsonl` as a cache. The source of truth is the file tree.
- Non-markdown assets are not discoverable until they have sidecar `.md` files.
- Refine generated metadata after scaffolding, especially `description`, `tags`,
  `category`, and relationships.
- Run `validate` after material metadata changes.
- Use `search` to shortlist and `resolve`, `cat`, or `context` to hydrate. Do not
  assume metadata search has loaded the document body.
- Treat `search --semantic` as experimental token-overlap matching, not vector retrieval.
