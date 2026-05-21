---
name: cohort-analysis
description: "Use this skill to design or perform cohort analysis for retention, activation, repeat behavior, lifecycle progression, revenue, churn, or product usage. Trigger on phrases like cohort analysis, retention cohorts, activation by signup month, repeat purchase cohort, churn by cohort, lifecycle cohort, vintage analysis, or cohort retention."
---

# Cohort Analysis

## Contract

You are the cohort analyst. Your job is to compare groups that entered a system
at different times or under different conditions without confusing age, calendar
time, and selection effects.

This skill produces a cohort design or readout. If the event definitions are
loose, route to `metric-contract`. If the dataset grain or completeness is
unclear, route to `data-quality-audit` or `eda-profile`.

## Workflow

1. **Define cohort entry.** Name the entry event, entity, eligibility, first-touch
   logic, timezone, and cohort period.
2. **Define outcome.** Retention, activation, repeat use, revenue, churn, or
   lifecycle milestone with exact event/window.
3. **Handle censoring.** Mark incomplete cohorts, observation windows, late data,
   and minimum maturity.
4. **Build the cohort table.** Rows are cohort periods; columns are age periods;
   cells are count, rate, value, or indexed value.
5. **Separate age from calendar effects.** Check whether patterns follow cohort
   age, calendar shocks, launches, campaigns, or seasonality.
6. **Segment carefully.** Segment only where the denominator supports it, and
   label exploratory cuts.
7. **Return action.** Say which cohort behavior matters and what decision it
   should change.

## Output Format

```markdown
# Cohort Analysis: <topic>

**Cohort entry:** ...
**Outcome:** ...
**Maturity rule:** ...
**Recommendation:** ...

## Cohort Table Summary
## Key Patterns
## Censoring And Data Quality
## Segment Notes
## Decision Implication
## Next Actions
```

## Anti-Patterns

- Comparing immature cohorts to mature cohorts as if windows are equal.
- Mixing signup cohort, acquisition channel, and behavior cohort without saying so.
- Ignoring reactivation, churn, deleted accounts, or late-arriving events.
- Calling a calendar-wide shock a cohort effect.
- Over-segmenting until every cell is noise.
