# Retrieval Modes And Benchmarks

Use `search-modes` when choosing retrieval strategy.

## Modes

| Mode | Use For | First Tool |
| --- | --- | --- |
| exact | known slug, id, title, phrase | `vaultli search`, `rg` |
| metadata | tags, category, status, domain | `vaultli search --category --tag` |
| body hydrate | reading the actual page | `vaultli resolve`, `cat`, `get_page` |
| graph | people, companies, relationships | `graph-ops` |
| timeline | dates, meetings, events | `query`, `graph-ops` |
| federated | multiple vaults/scopes | `vaultli federated-search` |
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

