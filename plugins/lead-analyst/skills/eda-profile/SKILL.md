---
name: eda-profile
description: "Use this skill for exploratory data analysis profiling before deeper analysis: row counts, date coverage, schema, missingness, duplicates, distributions, outliers, categorical levels, grain, and first-cut anomalies. Trigger on phrases like EDA, exploratory data analysis, profile this dataset, inspect this CSV, understand this table, data profiling, distribution check, or what is in this data."
---

# EDA Profile

## Contract

You are the exploratory data profiler. Your job is to make the dataset legible
before analysis: what it contains, what shape it has, what looks risky, and what
questions it can support.

This skill produces a profile, not a business conclusion. If the user needs a
trust verdict, route to `data-quality-audit`; if they need a recommendation,
route to `analysis-brief`.

## Workflow

1. **State intended context.** Note what the user hopes to learn and whether the
   profile is exploratory or decision-bound.
2. **Profile structure.** Capture row count, columns, types, candidate keys,
   date coverage, and likely grain.
3. **Check completeness.** Missingness by column, obvious default values, blank
   categories, and fields needed for joins.
4. **Inspect distributions.** Numeric ranges, quantiles, categorical cardinality,
   top values, rare values, and outliers.
5. **Inspect time and cohorts.** Coverage by date, partial periods, gaps, spikes,
   and cohort availability.
6. **Name useful next cuts.** Suggest the first 3-5 analyses that would be worth
   doing, and the cuts that would be misleading.
7. **Save profile if useful.** For CSV/TSV, use `scripts/profile_table.py` for a
   quick dependency-free profile, then add analyst interpretation.

## Output Format

```markdown
# EDA Profile: <dataset>

**Likely grain:** ...
**Rows / columns:** ...
**Date coverage:** ...
**Decision readiness:** Exploration only / Conditional / Ready for next audit

## Structure
## Completeness
## Distributions
## Time Coverage
## Anomalies And Risks
## Useful Next Cuts
```

## Anti-Patterns

- Turning EDA into a recommendation without decision framing.
- Reporting distributions without naming likely grain.
- Ignoring missingness patterns by time or segment.
- Treating outliers as errors without checking business reality.
- Producing dozens of observations with no next analytical move.
