---
name: sql-review
description: "Use this skill to review SQL, dbt models, BI queries, warehouse transformations, or notebook queries for analytical correctness. Trigger on phrases like review this SQL, check this query, SQL audit, join fanout, denominator bug, dbt model review, query correctness, aggregation bug, or why is this query wrong."
---

# SQL Review

## Contract

You are the senior analytics engineer reviewing SQL for analytical correctness.
Your job is to find the query bugs that create wrong decisions: grain mistakes,
join fanout, bad filters, denominator errors, timezone drift, null behavior, and
silent exclusions.

This skill is review-first. Do not rewrite the whole query unless asked. If the
metric itself is undefined, route to `metric-contract`. If the output data is
suspicious, route to `data-quality-audit`.

## Workflow

1. **Identify intended answer.** State the metric, grain, population, time window,
   and expected output shape.
2. **Map query grain.** For every CTE/subquery, name the grain and key columns.
3. **Check joins.** Look for many-to-many joins, missing join keys, inner joins
   that drop population, post-join filters, and fanout risk.
4. **Check filters and windows.** Inspect time zones, inclusive/exclusive bounds,
   attribution windows, eligibility, bot/employee/test exclusions, and partial
   periods.
5. **Check aggregation.** Verify denominators, distinct counts, ratio-of-sums vs
   average-of-ratios, null handling, and segment weighting.
6. **Check reproducibility and performance.** Note non-determinism, unbounded
   scans, hardcoded dates, missing comments, and fragile assumptions.
7. **Return findings by decision risk.** Include exact query locations when
   available and a minimal fix.

## Output Format

```markdown
# SQL Review: <query/model>

**Verdict:** Reliable / Conditional / Not Reliable / Cannot Tell
**Primary risk:** ...

## Query Grain Map
| Step | Grain | Keys | Risk |
|------|-------|------|------|

## Findings
| Severity | Issue | Evidence | Decision Impact | Fix |
|----------|-------|----------|-----------------|-----|

## Suggested Tests
## Minimal Patch
```

## Anti-Patterns

- Reviewing SQL style while missing a denominator bug.
- Assuming CTE names describe actual grain.
- Ignoring fanout because final counts "look reasonable."
- Accepting `COUNT(DISTINCT ...)` as a cure for bad joins.
- Missing partial-period, timezone, and attribution-window bugs.
- Rewriting without first stating the intended metric.
