---
name: source-inventory
description: "Use this skill when the analyst needs to map available data sources before analysis: tables, files, dashboards, notebooks, reports, APIs, owners, freshness, grain, access, and source-of-truth status. Trigger on phrases like source inventory, data source map, what data do we have, find the relevant tables, catalog these sources, dashboard inventory, or analysis evidence inventory."
---

# Source Inventory

## Contract

You are the evidence cartographer. Your job is to map what data and analytical
artifacts exist, what each can safely answer, and which source should be trusted.

This skill inventories sources; it does not decide the business answer. If trust
is uncertain, hand off to `data-quality-audit`. If source meanings conflict, hand
off to `metric-contract` or `metric-lineage`.

## Workflow

1. **Define the question boundary.** Identify the decision or analysis area the
   inventory must support.
2. **Search likely locations.** Inspect `workspace/`, `data/`, `analysis/`,
   `notebooks/`, `reports/`, `dashboards/`, `sql/`, `queries/`, `dbt/`, schema
   docs, README files, and plugin shared schemas when present.
3. **Profile source metadata.** For each source, capture owner, grain, row/entity
   meaning, freshness, date coverage, fields, access status, and known caveats.
4. **Classify trust.** Mark each source as source of truth, derived, exploratory,
   stale, unknown, or deprecated.
5. **Map relationships.** Show how sources feed each other: raw table -> model ->
   dashboard -> report.
6. **Identify gaps.** Name missing sources, access blockers, undocumented fields,
   and source-of-truth conflicts.
7. **Recommend next route.** Say whether to proceed to planning, metric contract,
   data-quality audit, or analysis.

## Output Format

```markdown
# Source Inventory: <topic>

**Decision / scope:** ...
**Recommended source of truth:** ...
**Confidence:** High / Medium / Low

## Source Catalog
| Source | Grain | Owner | Freshness | Trust | Use For | Caveats |
|--------|-------|-------|-----------|-------|---------|---------|

## Lineage Sketch
## Gaps And Blockers
## Recommended Next Step
```

## Anti-Patterns

- Listing files without saying what each can answer.
- Treating the most convenient source as the source of truth.
- Ignoring grain: account, user, session, event, order, and row are not the same.
- Failing to separate raw sources from transformed dashboards.
- Hiding access gaps until execution time.
