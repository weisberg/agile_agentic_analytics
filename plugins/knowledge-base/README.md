# Knowledge Base

Knowledge base workflows for capturing, organizing, retrieving, and maintaining reusable domain knowledge.

## Skills

| Skill | Description |
|-------|-------------|
| **ask-user** | Reusable choice-gate pattern for presenting 2-4 explicit options, including an escape hatch, and stopping until the user responds. |
| **ingest** | Router for ingesting meetings, articles, media, documents, and conversations into the knowledge base with citations, raw source preservation, entity updates, and back-links. |
| **skillify** | Meta-skill for turning raw features into proper, resolvable, tested agent skills with evals, resolver checks, and KB filing guidance. |
| **strategic-reading** | Read a source text through one specific strategic problem and produce an applied do/avoid/watch-for playbook with cited recommendations. |
| **vaultli** | Use the bundled `vaultli` CLI to initialize, scaffold, index, validate, search, and assemble context from file-based knowledge vaults. |

## Bundled Tools

| Tool | Path | Use Cases |
| --- | --- | --- |
| `vaultli` | `vaultli/` via `bin/vaultli` | File-based KB setup, YAML frontmatter, sidecar docs for non-markdown assets, `INDEX.jsonl` rebuilds, validation, metadata search, context assembly, and federated vault lookup. |

## Status

Plugin skeleton with reusable workflow skills and a bundled vault maintenance CLI. Add more skills, agents, references, and scripts under the standard plugin directories:

| Directory | Purpose |
| --- | --- |
| `skills/<name>/SKILL.md` | User-facing knowledge base workflows |
| `agents/*.md` | Specialized knowledge management subagents |
| `references/` | Taxonomies, schemas, templates, and curation guidance |
| `scripts/` | Reusable indexing, validation, import, or export utilities |
| `vaultli/` | Bundled file-based knowledge vault CLI and implementation docs |
| `bin/` | Executable wrappers exposed while the plugin is enabled |

## Installation

```text
/plugin install knowledge-base@agile-agentic-analytics
```

## Local Testing

```bash
claude --plugin-dir ./plugins/knowledge-base
```

Reload after edits with `/reload-plugins`. Validate with `claude plugin validate`.

Try the bundled CLI after loading the plugin:

```bash
vaultli --json root .
vaultli --json validate --root ./kb
```
