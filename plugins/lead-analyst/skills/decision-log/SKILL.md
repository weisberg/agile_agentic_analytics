---
name: decision-log
description: "Use this skill to capture, update, or review analytical decisions and follow-through: recommendation, evidence, confidence, owner decision, action taken, follow-up date, and outcome. Trigger on phrases like decision log, record this decision, analytics decision record, what did we decide, follow up on this recommendation, track analysis outcome, or log the recommendation."

disable-model-invocation: false
---

# Decision Log

## Contract

You are the analytics decision recorder. Your job is to make analytical
recommendations durable enough that the team can learn whether they were right.

This skill records decisions, not just findings. It can create a new log entry,
update an existing one with outcomes, or review whether prior recommendations
were followed.

## Workflow

1. **Identify the source analysis.** Link or summarize the brief, dashboard,
   review, metric movement diagnostic, forecast, or stakeholder discussion.
2. **Capture the recommendation.** State the recommended action, confidence,
   evidence, caveats, and alternatives considered.
3. **Capture the decision.** Decision owner, chosen action, date, rationale, and
   whether it followed the recommendation.
4. **Define follow-up.** Owner, date, success metric, leading indicator, and what
   would count as reversal or learning.
5. **Write/update the log.** Prefer `workspace/analysis/lead-analyst/decision-log.md`
   when `workspace/` exists, otherwise `analysis/lead-analyst/decision-log.md`.
6. **Review outcomes.** When updating, separate outcome evidence from hindsight
   storytelling.

## Output Format

```markdown
# Analytics Decision Log Entry

**Decision:** ...
**Date:** ...
**Owner:** ...
**Recommendation:** ...
**Decision taken:** ...
**Confidence at decision time:** High / Medium / Low

## Evidence
## Caveats
## Alternatives Considered
## Follow-Up Plan
## Outcome Update
```

## Anti-Patterns

- Logging an analysis finding without the decision it informed.
- Rewriting confidence after the outcome is known.
- Omitting the decision owner.
- Failing to define follow-up metrics and date.
- Treating "no decision" as no record; deferrals are decisions too.
