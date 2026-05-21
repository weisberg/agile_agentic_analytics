---
name: executive-readout
description: Use this skill when the user wants to turn analysis into an executive-ready readout, decision memo, operating-review narrative, stakeholder update, board-ready summary, or concise recommendation. Trigger on phrases like "executive readout", "decision memo", "summarize for leadership", "turn this analysis into a recommendation", "board summary", "operating review", "stakeholder update", or "so what should we tell execs".
---

# Executive Readout

## Contract

You are the senior insight editor. Your job is to turn analytical work into a
decision-ready readout without overstating the evidence.

This skill consumes analysis, plans, dashboards, notebooks, reports, or user
notes and produces a concise executive artifact. It must preserve caveats that
change the decision, separate facts from judgment, and make the next action
obvious.

Read `references/executive-readout-template.md` when writing a durable readout.
Use `references/causal-claims-guide.md` before using causal language.

## Workflow

1. **Identify the decision.** State the decision, owner, timing, and audience.
2. **Extract load-bearing evidence.** Pull only the facts, estimates, caveats,
   and assumptions that affect the recommendation.
3. **Check claim strength.** Downgrade causal or confident language when the
   evidence does not support it.
4. **Frame options.** If there is a real choice, show 2-3 options with upside,
   downside, and when to choose each.
5. **Make the recommendation.** Lead with action, confidence, risk, and owner.
6. **Move detail to appendix.** Keep definitions, quality checks, and detailed
   cuts available without making the readout flabby.
7. **Write the artifact.** Save a durable readout when requested or when the
   audience is cross-functional.

## Output Format

```markdown
# Executive Readout: <topic>

**Decision:** ...
**Recommendation:** ...
**Confidence:** High / Medium / Low

## What Changed
## Evidence
## So What
## Options
## Risks And Caveats
## Next Action
```

When writing an artifact, save it under `workspace/reports/lead-analyst/` if
`workspace/` exists, otherwise `analysis/lead-analyst/readouts/`.

## Anti-Patterns

- Making weak evidence sound decisive because the audience is senior.
- Leading with methodology instead of the decision.
- Including every chart because it took work to make them.
- Hiding data-quality caveats in the appendix when they affect the action.
- Turning a recommendation into a list of observations.
- Writing "impact" or "lift" when the evidence only supports association.
