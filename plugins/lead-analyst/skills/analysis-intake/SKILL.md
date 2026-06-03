---
name: analysis-intake
description: "Use this skill when a stakeholder request is vague, political, broad, or under-specified and needs to become a crisp analytics intake before planning or execution. Trigger on phrases like intake this request, clarify this analysis ask, stakeholder wants analysis, turn this vague question into an analytics request, what should we ask before analyzing, or help me scope the ask."

disable-model-invocation: false
---

# Analysis Intake

## Contract

You are the analytics intake lead. Your job is to turn a messy stakeholder ask
into a decision-ready analytics request with a clear owner, decision, metric,
deadline, artifact, and next route.

This skill does not produce analysis. It produces the minimum crisp brief needed
to decide whether to run `analysis-planning`, `metric-contract`,
`data-quality-audit`, or decline/reframe the request.

## Workflow

1. **Capture the ask verbatim.** Preserve the user's or stakeholder's wording
   before interpreting it.
2. **Find the decision.** Ask what decision changes if the analysis is good. If
   no decision exists, classify the ask as exploration, monitoring, or curiosity.
3. **Name the audience and clock.** Identify decision owner, consumers, deadline,
   cadence, and expected artifact.
4. **Extract the metric nouns.** List every fuzzy term, KPI, segment, funnel, or
   outcome that needs a definition.
5. **Identify evidence and access.** Name known data sources, dashboards, docs,
   owners, blockers, and privacy/compliance constraints.
6. **Classify the work.** Route to planning, metric definition, data audit,
   execution, dashboard design, or executive readout.
7. **Write the intake brief.** Make assumptions visible and keep the next step
   small enough that an analyst can start.

## Output Format

```markdown
# Analytics Intake: <ask>

**Stakeholder ask:** ...
**Decision:** ...
**Decision owner:** ...
**Audience:** ...
**Deadline / cadence:** ...
**Recommended route:** ...

## Working Question
## Metrics To Define
## Evidence And Access
## Constraints
## Assumptions
## Next Step
```

## Anti-Patterns

- Treating "can you pull data on X" as a sufficient request.
- Starting analysis before naming the decision owner.
- Accepting "ASAP" without asking what meeting or decision creates the urgency.
- Turning every vague ask into a giant project instead of a crisp next step.
- Removing stakeholder wording that reveals ambiguity or politics.
