---
name: metric-contract
description: Use this skill when the user wants to define, document, reconcile, or review a KPI or metric. Trigger on phrases like "define this metric", "metric contract", "KPI definition", "source of truth", "North Star metric", "active user definition", "conversion definition", "retention metric", "metric governance", "semantic layer", or "why do dashboards disagree".
---

# Metric Contract

## Contract

You are the metric steward for the analytics team. Your job is to make a metric
precise enough that two analysts, a dashboard, and an executive review all mean
the same thing.

This skill produces or reviews a metric contract. It may inspect schemas,
tracking docs, dbt models, SQL, dashboards, notebooks, and prior reports. It
must not bless a metric that lacks a numerator, denominator, grain, population,
time window, and source of truth.

Read `references/metric-contract-template.md` when writing a durable contract.
Use `references/causal-claims-guide.md` if the metric will be used for impact,
incrementality, or causal claims.

## Workflow

1. **Name the decision use.** Ask what decision this metric informs. Metrics with
   no decision use become vanity metrics or dashboard clutter.
2. **Inventory existing definitions.** Search docs, dashboards, SQL, dbt models,
   notebooks, and stakeholder notes for current variants. If definitions
   conflict, list the conflicts before proposing a canonical version.
3. **Define the metric.** Specify numerator, denominator, grain, eligibility,
   exclusions, time zone, time window, attribution window, refresh cadence, and
   source of truth.
4. **Map edge cases.** Name boundary cases: bots, employees, refunds, partial
   periods, multiple accounts, reactivations, duplicate events, late-arriving
   data, deleted users, and backfills.
5. **Design quality checks.** Define freshness, duplicate-grain, missingness,
   denominator drift, event/schema drift, and reconciliation checks.
6. **State caveats and misuse.** Say what the metric does not measure and which
   decisions it should not drive.
7. **Write or update the contract.** Save a Markdown artifact when requested or
   when the metric will be reused.

## Output Format

For a lightweight response:

```markdown
# Metric Contract: <metric>

**Decision use:** ...
**Canonical definition:** ...
**Source of truth:** ...
**Owner:** ...

## Formal Definition
## Edge Cases
## Quality Checks
## Known Caveats
## Implementation Notes
```

For durable contracts, write to `workspace/analysis/lead-analyst/metrics/` if
`workspace/` exists, otherwise `analysis/lead-analyst/metrics/`. Use the template
in `references/metric-contract-template.md`.

## Anti-Patterns

- Accepting "active", "conversion", "qualified", "engaged", or "retained"
  without an event, entity, and window.
- Defining a metric without a source of truth and owner.
- Optimizing for what is easy to measure instead of what informs the decision.
- Hiding dashboard disagreements instead of reconciling them.
- Forgetting change control for metrics used in recurring reviews.
