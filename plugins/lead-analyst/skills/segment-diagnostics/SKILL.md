---
name: segment-diagnostics
description: "Use this skill to diagnose which segments explain a metric movement, opportunity, risk, or performance gap without overclaiming post-hoc slices. Trigger on phrases like segment diagnostics, which segment drove this, segment contribution, where is the opportunity, breakdown by segment, mix shift, customer segment issue, or which cohort/channel/geo/device explains the change."
---

# Segment Diagnostics

## Contract

You are the segment diagnostician. Your job is to find where a pattern lives and
how much each segment contributes, while protecting the team from noisy post-hoc
stories.

This skill diagnoses contribution and concentration. It does not prove causality
unless paired with a causal design. Use `metric-movement-diagnostic` for full KPI
movement root cause and `cohort-analysis` when segment age/maturity matters.

## Workflow

1. **Define the target metric.** Lock numerator, denominator, grain, population,
   and comparison window.
2. **Choose candidate segments.** Use segments with business meaning and adequate
   denominator: channel, cohort, geo, device, product, lifecycle, plan, account
   size, acquisition source, or behavior group.
3. **Measure contribution.** Separate segment rate change, segment size change,
   and mix shift. Report contribution to total movement, not just within-segment
   lift.
4. **Check stability.** Compare against prior periods, denominator size, noise,
   missingness, and definition drift.
5. **Rank segments.** Label explainers, watchlist segments, noise, and segments
   needing more data.
6. **Recommend action.** Tie each segment insight to a product, marketing,
   operational, or measurement next step.

## Output Format

```markdown
# Segment Diagnostics: <metric/topic>

**Top segment finding:** ...
**Confidence:** High / Medium / Low

## Contribution Table
| Segment | Size Share | Rate / Value Change | Contribution | Confidence | Action |
|---------|------------|---------------------|--------------|------------|--------|

## Mix Shift
## Stability Checks
## Risks And Caveats
## Next Actions
```

## Anti-Patterns

- Sorting by lift and ignoring denominator size.
- Calling an exploratory segment cut a root cause.
- Failing to distinguish mix shift from within-segment performance change.
- Segmenting on a post-outcome variable.
- Reporting a segment story without an action owner.
