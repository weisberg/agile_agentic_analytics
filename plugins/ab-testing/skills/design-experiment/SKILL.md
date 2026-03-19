---
name: design-experiment
description: Design a rigorous A/B experiment with hypothesis, metrics, guardrails, and a full experiment plan. Use when starting a new experiment or formalizing an existing idea.
---

Help the user design a rigorous A/B experiment. If they provide a description of what they want to test as `$ARGUMENTS`, use that as the starting point. Otherwise, ask what product change or feature they want to test.

## Process

1. **Clarify the change** — Understand what is being changed and why. Ask follow-up questions if the change is ambiguous.

2. **Produce a structured experiment design document** in Markdown with these sections:

### Experiment Design Document

**Experiment Name:** A short descriptive name

**Hypothesis:** Format as: "If [change], then [metric] will [direction] by [expected magnitude] because [mechanism]."

**Primary Metric:** The single metric that will decide ship/no-ship. Define it precisely (numerator, denominator, time window).

**Secondary Metrics:** Additional metrics to monitor for deeper understanding. List 2-5.

**Guardrail Metrics:** Metrics that must NOT degrade. Typical guardrails include:
- Page load time / latency
- Error rate / crash rate
- Revenue (if not the primary metric)
- User retention

**Randomization Unit:** User, session, device, etc. Explain why this unit is appropriate.

**Target Population:** Who is included/excluded from the experiment and why.

**Traffic Allocation:** Recommend a split (e.g., 50/50) or ramped rollout schedule. Justify the choice.

**Expected Duration:** Estimate based on the primary metric's baseline rate and the minimum detectable effect. If the user hasn't provided baseline numbers, ask for them or note what assumptions you're making.

**Interaction Risks:** Flag potential conflicts with other experiments or features.

**Decision Criteria:**
- **Ship** if: [condition]
- **Iterate** if: [condition]
- **Kill** if: [condition]

3. **Offer next steps:**
   - Generate tracking/logging code skeleton in the user's preferred language
   - Run a sample size calculation (suggest using `/ab-testing:sample-size`)
   - Draft a pre-registration document

## Guidelines

- Be opinionated about best practices. If the user's idea has issues (e.g., testing too many things at once, using a bad metric), flag it constructively.
- Keep the document concise but complete. Aim for something a team could review in 10 minutes.
- If the experiment is a multivariate test (more than 2 variants), address the implications for sample size and multiple comparisons.
