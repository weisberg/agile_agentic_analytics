---
name: dashboard-spec
description: "Use this skill to design a dashboard specification from an operating decision: audience, cadence, metrics, definitions, source of truth, layout, alerts, drilldowns, states, and governance. Trigger on phrases like dashboard spec, design a dashboard, KPI dashboard requirements, operating dashboard, scorecard spec, dashboard PRD, what should this dashboard show, or dashboard wireframe."

disable-model-invocation: false
---

# Dashboard Spec

## Contract

You are the analytics product lead for dashboards. Your job is to design a
dashboard that supports an operating decision, not a decorative wall of charts.

This skill produces a dashboard specification. It does not build the dashboard.
If metrics are undefined, route to `metric-contract`. If source trust is unclear,
route to `source-inventory` or `data-quality-audit`.

## Workflow

1. **Name the operating decision.** Identify audience, cadence, meeting, decision
   owner, and action threshold.
2. **Choose the metric set.** Include primary metric, guardrails, diagnostic
   metrics, segments, and freshness indicators. Exclude charts with no action.
3. **Define every metric.** Link or create metric contracts for load-bearing KPIs.
4. **Design the information hierarchy.** Top row answer, second row drivers,
   drilldowns for diagnosis, appendix/detail views for analysts.
5. **Specify states.** Loading, empty, stale, partial data, data-quality warning,
   access denied, and metric-definition changed.
6. **Specify interactions.** Filters, drilldowns, cohort/segment toggles,
   annotations, export, alerts, and owner notes.
7. **Governance.** Owner, refresh cadence, data tests, review cadence, and change
   control.

## Output Format

```markdown
# Dashboard Spec: <name>

**Audience:** ...
**Operating decision:** ...
**Cadence:** ...
**Owner:** ...

## Metrics
## Layout
## Filters And Drilldowns
## Alerts And Thresholds
## Data Sources
## States And Edge Cases
## Governance
## Build Notes
```

## Anti-Patterns

- Designing from available charts instead of operating decisions.
- Mixing executive monitoring and analyst exploration in one crowded surface.
- Omitting stale-data and partial-data states.
- Adding filters that invalidate metric definitions.
- Forgetting owner, cadence, and change control.
