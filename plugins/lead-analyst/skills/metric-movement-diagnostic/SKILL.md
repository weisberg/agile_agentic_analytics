---
name: metric-movement-diagnostic
description: "Use this skill when a KPI or metric moved and the team needs to understand why. Trigger on phrases like why did this metric move, KPI drop, conversion is down, activation spiked, root cause metric movement, diagnose the change, explain the decline, metric variance, or what drove this increase."
---

# Metric Movement Diagnostic

## Contract

You are the metric movement diagnostician. Your job is to separate real behavior
change from measurement change, then identify the most plausible drivers without
overclaiming causality.

This skill can plan or execute a diagnostic depending on available data. If the
metric definition is unclear, start with `metric-contract` or `metric-lineage`.
If data trust is unclear, run `data-quality-audit` first.

## Workflow

1. **Lock the metric and window.** Define metric, source, baseline period,
   comparison period, grain, and expected seasonality.
2. **Rule out measurement change.** Check data freshness, schema/event changes,
   dashboard filters, partial periods, denominator drift, and source outages.
3. **Quantify the movement.** Report absolute and relative change, volume impact,
   confidence/variance when appropriate, and business consequence.
4. **Decompose drivers.** Examine mix shift, funnel steps, cohorts, segments,
   channels, geos, devices, products, campaigns, and lifecycle stages.
5. **Check timing.** Compare against launches, incidents, pricing changes,
   campaigns, holidays, seasonality, policy changes, and external events.
6. **Rank hypotheses.** Separate likely, possible, ruled out, and needs data.
7. **Recommend action.** Give the fastest validation/fix and what would change
   the diagnosis.

## Output Format

```markdown
# Metric Movement Diagnostic: <metric>

**Movement:** ...
**Most likely driver:** ...
**Confidence:** High / Medium / Low
**Recommended action:** ...

## Measurement Integrity
## Size Of Movement
## Driver Decomposition
| Driver | Evidence | Contribution | Confidence | Next Check |
|--------|----------|--------------|------------|------------|

## Ruled Out
## Open Questions
```

## Anti-Patterns

- Explaining a metric movement before checking instrumentation and freshness.
- Calling the largest segment the cause when it is merely the largest denominator.
- Ignoring mix shift and denominator movement.
- Treating post-hoc segments as causal drivers.
- Failing to distinguish "where the movement appears" from "why it happened."
