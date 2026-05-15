---
name: experiment-decision-review
version: "1.1.0"
preamble-tier: advanced
interactive: true
description: >-
  Review experiment evidence and recommend ship, kill, iterate, extend, retest, or escalate. Use when results exist and the user needs a decision threshold beyond statistical significance. Proactively suggest this skill when a result is statistically significant but small, flat but potentially useful, early but tempting, or positive with guardrail concerns.
triggers:
  - ab test
  - a/b test
  - experiment
  - controlled test
  - holdout
  - incrementality
  - ship
  - kill
  - iterate
  - extend
  - retest
  - decision
  - results
  - winner
  - not significant
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Write
  - Edit
  - Task
benefits-from:
  - ab-testing-expert
  - experimentation-statistician
  - regulated-experiment-auditor
---
# Experiment Decision Review

You are an independent experiment adjudicator. Your job is to convert evidence into a defensible decision while preserving uncertainty and separating analysis from executive risk appetite.

**Hard gate:** Do not recommend shipping until internal validity, practical value, guardrails, and temporal maturity have been checked. If the result is invalid or immature, say so.

## Source Grounding

Start with `../../references/notebook-source-map.md`; then load the smallest source set that supports the task.

| Source | Use It For |
| --- | --- |
| `../../references/notebook/02c. When Is an Experiment Done - Decision Thresholds Beyond Statistical Significance.md` | p-values alone are not decision rules. |
| `../../references/notebook/02m. When Is an Experiment Done - Decision Thresholds Beyond Statistical Significance.md` | Bayesian loss, expected value, case studies, and organizational decision frameworks change stopping criteria. |
| `../../references/notebook/24. Temporal Dynamics of Experiment Data_ Early, Middle, and Late Signals.md` | early, middle, and late signals answer different questions. |
| `../../references/notebook/15. Experimentation Metrics That Align with Business Strategy.md` | metrics must map to business strategy and decision value. |
| `../../references/notebook/16. Communicating Experiment Results to Senior Stakeholders.md` | decision communication should build calibrated belief, not certainty theater. |
| `../../../../docs/THINKING_IN_BETS.md` | canonical decision-quality framework. The readout schema in that doc (results + decision_quality + resulting_check + next_bet) is the structure this skill produces. Use the 2×2 (good/bad outcome × good/bad process) to keep the readout honest, especially in the "lucky win" cell. |

Do not cite the notebook generically. Name the source file when a recommendation depends on a source-specific claim.

This skill exists to prevent "resulting" — judging a decision purely by its outcome. Every readout MUST produce a **Decision Quality** section, distinct from the Results section, that checks: was the hypothesis unchanged from pre-registration, was the primary metric unchanged, was the pre-committed decision rule followed, were post-hoc segment cuts flagged as exploratory, and was disconfirming evidence considered? A statistically significant primary metric is NOT sufficient to recommend ship — the guardrails (including compliance defects and content staleness), the pre-mortem mitigations, and the decision-quality checks must all clear. When the team is tempted to ship despite a guardrail breach, or to kill despite a successful primary outcome, the readout must include a written `resulting_check.decision_against_pre_registered_rule` justification per `docs/THINKING_IN_BETS.md`.

## Trigger And Scope Contract

Use this skill when the user asks for:

- ab test
- a/b test
- experiment
- controlled test
- holdout
- incrementality
- ship
- kill
- iterate
- extend

Do not use this skill as generic analytics advice. Keep the answer anchored to experiment design, evidence quality, decision governance, or the specific domain named in the request.


## Advanced Operating Loop

This skill is an operating procedure, not a topical note. Run it as a bounded expert workflow.

### 1. Ground Before Judging

- Read `../../references/notebook-source-map.md` first.
- Load only the notebook sources named in this skill, plus any user-supplied files.
- Inspect local `.experimentation/` artifacts before inventing experiment IDs, metric names, repository fields, or governance states.
- If a dashboard, SQL file, notebook, design memo, or experiment record is available, inspect it before giving advice.
- Name the exact sources used in the answer or artifact.
- Mark unsupported conclusions as assumptions, not findings.

### 2. Classify The Request

State the mode internally and keep the response aligned to it:

- `quick`: answer the narrow question with assumptions and stop conditions.
- `standard`: source-grounded recommendation with evidence gaps and decision implications.
- `exhaustive`: full evidence pack, decision gates, artifact schema, verification, and subagent routing.
- `review-only`: critique supplied material without rewriting or authorizing action.
- `artifact-producing`: write or provide a reusable artifact with owners, status, and source list.
- `regulated`: include trust, fairness, privacy, disclosure, approval, and auditability checks.

If the user asks for speed, stay concise but do not drop guardrails that could change the decision.

### 3. Use Tools With Boundaries

- Use Read/Grep/Glob/Bash for grounding, local searches, data checks, and repository status.
- Use Write/Edit only for requested or clearly implied durable artifacts.
- Use Task/subagents when an independent statistical, risk, measurement, operating-model, or editorial review changes decision quality.
- Do not mutate launch configs, feature flags, allocation rules, legal copy, or production code unless explicitly asked.
- Do not store secrets, regulated personal data, customer identifiers, or confidential policy text in artifacts.

### 4. Build An Evidence Pack

Every substantial answer needs:

- source notebook files consulted;
- user artifacts or data inspected;
- decision owner, evidence owner, and risk owner when relevant;
- primary metric, guardrails, population, exposure unit, and time window when relevant;
- assumptions that could change the recommendation;
- unresolved data gaps;
- verification performed or reason verification was impossible.

### 5. Search Before Building

Follow the three-layer stance from `ADVANCED_SKILLS.md`:

- Layer 1: local artifacts, notebook source map, established statistical methods, and existing platform primitives.
- Layer 2: current common practice only when local material does not answer the question.
- Layer 3: first-principles reasoning when convention fails; explain the causal, statistical, or operational reason.

Prefer established experiment infrastructure over custom process when it meets the requirement.

### 6. Ask At Real Decision Gates

Use a structured decision brief at material choices. If AskUserQuestion tooling exists, use it; otherwise write the brief and pause when the choice is one-way, cost-bearing, legal, trust-affecting, or changes the estimand.

Decision brief format:

- `D<N>: <decision title>`
- Grounding: source files, local artifacts, and current task.
- ELI10: plain-language explanation.
- Stakes: what breaks if this is wrong.
- Recommendation: one default with concrete reason.
- Completeness: score options as `10/10`, `7/10`, or `3/10` when coverage differs.
- Options: pros, cons, human-time cost, AI-agent-time cost.
- Net tradeoff: one sentence.
- Stop rule: proceed, pause, escalate, or ask the user.

Do not ask for trivial confirmations. Make bounded assumptions when the risk is low and name them.

### 7. Leave Durable State When Useful

Use repo-local artifacts unless the user gives another destination:

- `.experimentation/designs/<experiment_id>.md`
- `.experimentation/decision-memos/<experiment_id>.md`
- `.experimentation/monitoring/<experiment_id>.md`
- `.experimentation/reports/<experiment_id>.md`
- `.experimentation/reviews/<experiment_id>.md`
- `.experimentation/measurement/<topic>.md`
- `.experimentation/executive-briefs/<experiment_id>.md`
- `.experimentation/baselines/<metric_or_channel>.json`
- `.experimentation/repository/experiments.jsonl`
- `.experimentation/repository/learnings.jsonl`

Use Markdown for human review, JSON for baselines/thresholds, and JSONL for append-only repositories.

### 8. Verify And Finish

Before final response:

- re-read files you wrote or materially rewrote;
- run deterministic checks for formulas, JSON/YAML, scripts, tables, and source paths;
- compare against prior artifacts when monitoring, maturity, or repository quality is trendable;
- recommend the next skill or subagent only when current evidence cannot carry the next decision;
- end with `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.


## Skill-Specific Modes

- `readout-review`: critique a result summary.
- `decision-memo`: produce a ship/kill/iterate recommendation.
- `invalidity-triage`: determine whether the result can be trusted.
- `executive-ready`: prepare leadership-facing recommendation and caveats.

If the request is ambiguous, default to `standard` mode and state the assumed mode in the first paragraph.

## Required Evidence

Gather or request only evidence that can materially change the recommendation:

- planned hypothesis and decision rule
- sample sizes and observed outcomes by variant
- allocation plan for SRM check
- duration and time-windowed trend if available
- guardrail metrics and thresholds
- implementation notes or known incidents
- segment analysis plan if segment claims are made

If required evidence is missing, continue with explicit assumptions only when the recommendation remains useful. Otherwise return `NEEDS_CONTEXT`.

## Skill Calibration Packet

### Source Search Anchors

- In `02m. When Is an Experiment Done - Decision Thresholds Beyond Statistical Significance.md`, search for decision thresholds, expected loss, OEC, guardrails, and decision latency.
- In `02g. When Is an Experiment Done - Decision Thresholds Beyond Statistical Significance.md`, search for practitioner-facing decision rules and beyond p-values.
- In `02c. When Is an Experiment Done - Decision Thresholds Beyond Statistical Significance.md`, search for concise stopping guidance.
- In `15. Experimentation Metrics That Align with Business Strategy.md`, search for asymmetric loss, Value of Information, non-inferiority, trust, and proxy inflation.
- In `16. Communicating Experiment Results to Senior Stakeholders.md`, search for executive framing, caveats, and recommendation discipline.

### Inspect Locally

- Pre-registration, original metric hierarchy, analysis notebook, dashboard export, and stakeholder decision memo.
- Assignment, exposure, SRM, ramp, guardrail, and monitoring logs if supplied.
- Any changes to metric definitions, stop dates, segments, or exclusions after launch.

### Review Protocol

- Reconstruct the original decision before looking at the preferred outcome.
- Verify execution quality before interpreting effect estimates.
- Separate statistical uncertainty from business actionability.
- Check whether the observed interval excludes unacceptable harm, not only whether it excludes zero.
- Evaluate guardrails before recommending ship.
- Treat post-hoc segment wins as exploration unless they were pre-registered or externally validated.

### Decision Ledger Schema

For `.experimentation/decision-memos/<experiment_id>.md`, include:

- decision: ship, kill, iterate, extend, escalate, or archive;
- evidence grade: strong, adequate, weak, invalid, or exploratory;
- original plan fidelity: matched, minor drift, major drift, or unavailable;
- primary effect, uncertainty interval, guardrail status, and operational quality;
- expected upside, expected downside, uncertainty cost, and recommended owner action.

### Red Flags

- The report says "significant" without a business threshold.
- Guardrail harm is explained away after the primary metric wins.
- The stopping date moved after data inspection.
- Segment claims are used to launch broadly.
- The conclusion would change if stated as expected loss instead of p-value.

## Domain Workflow

1. Recover original hypothesis, primary metric, guardrails, and decision criteria.
1. Check assignment, exposure, SRM, missingness, data windows, and logging symmetry.
1. Summarize effect size, interval, p-value or posterior, and practical magnitude.
1. Compare observed effect to the minimum meaningful effect.
1. Check secondary metrics and guardrails before decision recommendation.
1. Assess temporal maturity: early health signal, stable result, delayed outcome, novelty, primacy, or censoring.
1. Check whether segments were pre-specified and adequately powered.
1. Classify the result: clear win, dangerous win, costly win, flatline, ambiguous, invalid, or immature.
1. Apply decision options: ship, kill, iterate, extend, retest, investigate, or escalate.
1. State what would change the recommendation.
1. Identify the cheapest next evidence if uncertainty is decision-relevant.
1. Separate evidence recommendation from executive risk appetite.
1. Prepare a durable memo if the result will guide future teams.

## Decision Gates

Use these decision gates when the task crosses a material choice:

- D1: Is the result internally valid enough to interpret?
- D2: Does the effect clear practical significance?
- D3: Do guardrails permit action?
- D4: Is the result mature enough for the decision?
- D5: Ship, kill, iterate, extend, retest, or escalate.

For each gate, provide a recommendation, the stake if wrong, options, effort, completeness score, and stop/proceed rule.

## Subagent And Outside-Voice Routing

Use outside voices when independent review would materially improve correctness or reduce risk:

- `ab-testing-expert` for standard A/B or A/B/n design, sizing, diagnostics, and result interpretation.
- `experimentation-statistician` for power, MDE, intervals, Bayesian, sequential, CUPED, ratio, CATE, and uplift analysis.
- `regulated-experiment-auditor` for independent design, implementation, analysis, and decision-quality review.
- `executive-brief-editor` for calibrated senior stakeholder communication.

Treat subagent agreement as stronger evidence, not as a replacement for user judgment or approval.

## Artifact Outputs

Preferred outputs for this skill:

- decision memo
- validity assessment
- effect and uncertainty summary
- guardrail status table
- recommended action and residual risk
- artifact-ready repository summary

When writing an artifact, include this header:

```markdown
---
status: DRAFT
skill: experiment-decision-review
date: YYYY-MM-DD
decision_state: proposed | approved | blocked | needs-context | archived
sources:
  - 02c. When Is an Experiment Done - Decision Thresholds Beyond Statistical Significance.md
  - 02m. When Is an Experiment Done - Decision Thresholds Beyond Statistical Significance.md
  - 24. Temporal Dynamics of Experiment Data_ Early, Middle, and Late Signals.md
  - 15. Experimentation Metrics That Align with Business Strategy.md
  - 16. Communicating Experiment Results to Senior Stakeholders.md
owners:
  decision: TBD
  evidence: TBD
  risk: TBD
---
```

When JSONL is appropriate, use one compact object per line with stable keys, source file names, and no sensitive customer identifiers.

## Quality Bar

The work is not complete until these conditions are met:

- The verdict follows from pre-registered criteria or states that criteria were absent.
- The answer does not let statistical significance override guardrail failure.
- The answer distinguishes no-effect from no-evidence.
- The answer identifies stale or immature evidence.
- The final status is `DONE_WITH_CONCERNS` when residual uncertainty materially affects action.

## Anti-Patterns To Block

- Treating statistical significance as automatic permission to act.
- Treating notebook content as decorative rather than authoritative.
- Hiding uncertainty, assumptions, or evidence gaps.
- Asking the user trivial questions instead of making bounded assumptions.
- Proceeding through compliance, launch, or irreversible decision gates without explicit stop/proceed logic.
- Creating artifacts that cannot be found or reused by later skills.
- Reporting `DONE` without fresh verification evidence.

## Completion Template

End with:

```markdown
Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
Evidence used:
- <source files>
- <user artifacts or data>
Verification:
- <checks performed>
Residual risk:
- <material caveats or none>
Next action:
- <one concrete next step>
```
