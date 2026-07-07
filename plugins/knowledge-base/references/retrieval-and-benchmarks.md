# Retrieval Modes And Benchmarks

Retrieval-mode selection is owned by the `query` skill; see `retrieval.md` for
the full mode / source-scope / graph-expansion reference. This file focuses on
the benchmark record shape.

## Modes

| Mode | Use For | First Tool |
| --- | --- | --- |
| exact | known slug, id, title, phrase | `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search`, `rg` |
| metadata | tags, category, status, domain | `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search --category --tag` |
| body hydrate | reading the actual page | `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json resolve --body`, `cat` |
| graph | people, companies, relationships | back-link traversal in `query` |
| timeline | dates, meetings, events | `query` page timelines |
| federated | multiple vaults/scopes | `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json federated-search` |
| freshness | current developments | `current-research` |

## Benchmark Record

```json
{
  "query": "what do we know about Acme renewal risk?",
  "mode": "hybrid",
  "expected_ids": ["companies/acme-example", "meetings/2026-05-01-alice-acme"],
  "actual_ids": [],
  "judgment": "miss",
  "fix": "Improve company page description and add renewal-risk tag."
}
```

Store benchmark fixtures beside the relevant skill or in a report when a
retrieval miss teaches the KB something durable.
