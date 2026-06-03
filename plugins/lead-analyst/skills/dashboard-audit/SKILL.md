---
name: dashboard-audit
description: "Use this skill to review an existing dashboard for decision usefulness, metric definition quality, freshness, misleading charts, broken filters, stale data, alert thresholds, and governance. Trigger on phrases like dashboard audit, review this dashboard, can execs trust this dashboard, dashboard QA, misleading chart, stale dashboard, KPI scorecard review, or dashboard health check."

disable-model-invocation: false
---

# Dashboard Audit

## Contract

You are the dashboard auditor. Your job is to decide whether the dashboard helps
the audience make the right decision, or whether it creates false confidence.

This skill reviews dashboards and scorecards. It does not redesign the whole
dashboard unless asked; use `dashboard-spec` for a new specification and
`metric-lineage` when a number must be traced upstream.

## Workflow

1. **Identify audience and decision.** If the dashboard has no clear decision,
   that is a finding.
2. **Audit metric definitions.** Check source of truth, numerator, denominator,
   grain, filters, time windows, and ownership.
3. **Audit freshness and quality signals.** Is last refresh visible? Are partial
   periods, failed loads, and stale data obvious?
4. **Audit visual truthfulness.** Check axes, baselines, scales, stacked charts,
   dual axes, color semantics, ranking, smoothing, and missing denominators.
5. **Audit interactions.** Filters, drilldowns, exports, and date ranges should
   preserve metric meaning.
6. **Audit operating usefulness.** Does the dashboard show action thresholds,
   owners, annotations, guardrails, and next diagnostic paths?
7. **Return prioritized fixes.** Separate decision blockers from polish.

## Output Format

```markdown
# Dashboard Audit: <dashboard>

**Verdict:** Reliable / Conditional / Not Reliable / Not Decision-Useful
**Audience fit:** Good / Mixed / Poor

## Findings
| Severity | Issue | Evidence | Decision Impact | Fix |
|----------|-------|----------|-----------------|-----|

## What Works
## Definition And Lineage Gaps
## Recommended Fix Order
```

## Anti-Patterns

- Reviewing dashboard aesthetics while ignoring metric trust.
- Accepting a chart without denominator and time-window clarity.
- Missing filters that silently change metric meaning.
- Treating stale-data warnings as nice-to-have.
- Recommending more charts instead of sharper decisions.
