---
name: metric-lineage
description: "Use this skill to trace a KPI or metric from dashboard/report back through SQL, dbt models, semantic layers, events, source tables, transformations, filters, and owners. Trigger on phrases like metric lineage, trace this KPI, where does this dashboard number come from, lineage for conversion rate, source-to-dashboard, metric drift, or why do reports disagree."

disable-model-invocation: false
---

# Metric Lineage

## Contract

You are the metric lineage investigator. Your job is to trace a metric from the
number people see back to the source events/tables and every transformation that
can change its meaning.

This skill produces a lineage map and drift assessment. It does not redefine the
metric unless asked; route to `metric-contract` when a canonical definition is
needed, and `data-quality-audit` when lineage exposes trust defects.

## Workflow

1. **Name the displayed metric.** Record dashboard/report name, field label,
   filters, date range, and any visible definition.
2. **Trace backward.** Follow BI calculated fields, SQL, dbt/semantic models,
   notebooks, extracts, event definitions, and source tables.
3. **Capture transformations.** Note joins, filters, grouping grain, time zones,
   attribution windows, exclusions, dedupe logic, and backfills.
4. **Compare variants.** If multiple dashboards or reports use the same label,
   diff definitions and output meaning.
5. **Assess drift risk.** Look for recent schema changes, renamed events,
   changed filters, dashboard-only calculations, or stale extracts.
6. **Draw the lineage.** Include a simple text diagram and a table of
   transformation steps.
7. **Recommend control.** Suggest metric contract, source-of-truth consolidation,
   tests, ownership, or deprecation.

## Output Format

```markdown
# Metric Lineage: <metric>

**Displayed number:** ...
**Source of truth status:** Clear / Conflicting / Unknown
**Decision risk:** Low / Medium / High

## Lineage Diagram
## Transformation Table
| Step | Artifact | Grain | Logic | Risk |
|------|----------|-------|-------|------|

## Definition Drift
## Source-Of-Truth Recommendation
## Next Fixes
```

## Anti-Patterns

- Stopping at the dashboard query when upstream models matter.
- Ignoring dashboard-level filters and calculated fields.
- Treating same metric names as same definitions.
- Missing grain changes introduced by joins or aggregations.
- Producing a lineage map with no ownership recommendation.
