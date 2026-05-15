# Thinking in Bets — Decision Quality for Regulated Marketing & Experimentation

This is the canonical reference for the decision-quality principles that the
experimentation, ab-testing, campaign-analysis, and marketing-analytics
plugins should apply when they design, run, read out, or govern any test or
campaign that influences customers in a regulated, high-trust environment
(financial services, healthcare, regulated insurance, advised products).

The framework comes from Annie Duke's *Thinking in Bets*. The translation
below is opinionated and specific: it tells skills *what to do differently*,
not just what to believe.

---

## Core thesis

> Good decisions do not guarantee good outcomes, and bad outcomes do not
> automatically mean the decision was bad.

For regulated marketing and experimentation, this is not a philosophical
point — it is operational. In a high-trust environment, the cost of a wrong
decision is not bounded by a failed web test. It can include customer
confusion, compliance exposure, stale or misleading claims, brand erosion,
and loss of trust. So the discipline is:

- Treat decisions as probabilistic bets.
- Make uncertainty explicit.
- Judge the *quality of the decision process*, not just the *result*.

A pilot that reduces attrition can still have been a poorly governed
decision. A pilot that shows no lift can still be a successful decision if
it protected trust, clarified a compliance boundary, or exposed a weak
hypothesis cheaply.

---

## The seven principles (with operational behavior)

### 1. Embrace uncertainty — frame decisions as bets

**Principle.** Replace "will this work?" with "given what we know now, how
likely is this to work, and what would change our mind?"

**What skills should do.**

- In design artifacts, write probability/confidence language explicitly. Not "this pilot will reduce attrition", but "we estimate a ~X% chance of detecting a Y pp lift in retention given baseline traffic and the chosen MDE."
- Separate confidence from certainty in stakeholder-facing summaries.
- Surface the assumptions that the probability estimate depends on (baseline rate, traffic, segment definitions, time horizon).

### 2. Avoid "resulting" — don't judge a decision by the outcome alone

**Principle.** A lucky win is not proof of a good decision. A flat result is
not proof of a bad one. Judge the *decision process* separately from the
*outcome*.

**What skills should do.**

- Every readout includes a **Decision Quality** section, distinct from the **Results** section: was the hypothesis pre-registered, were guardrails defined in advance, was the test powered honestly, was the result interpreted within the pre-committed decision rule?
- A "win" on the primary metric is not sufficient to ship. The readout must also clear the guardrails, the trust/compliance check, and the process review.
- A null result is not automatically a failure. The readout asks: did we learn something that improves the next bet?

### 3. Truth-seeking — invite disconfirming evidence

**Principle.** Most pilots have a politically attractive story. That story
should be challenged before it becomes launch logic.

**What skills should do.**

- Design and review skills explicitly prompt: "what would make us update against this idea?" and "who has permission to challenge the preferred narrative before launch?"
- Review boards or specialist roles (analytics, risk, legal, content) are named, not implied.
- Skills produce a short list of disconfirming evidence the team commits to look for.

### 4. Combat cognitive bias — pre-register the hypothesis and the decision rule

**Principle.** Confirmation bias, motivated reasoning, and hindsight bias
are most dangerous *after* data starts flowing. The antidote is to lock the
hypothesis, primary metric, guardrails, sample-size logic, and the
ship/hold/kill rule *before* launch.

**What skills should do.**

- Design skills produce a pre-registration artifact with these fields *before* the test goes live: hypothesis, single primary metric, leading indicators, guardrails, minimum detectable effect, decision rule, duration / sample-size logic.
- Analysis skills refuse to declare a win on a metric that was not pre-registered as primary. Post-hoc segment cuts are labeled exploratory.
- Decision-review skills check the readout against the pre-registered decision rule, not against whatever rule would make the result look best.

### 5. Create accountability — make reasoning visible

**Principle.** Decisions improve when reasoning is shared and reviewed.

**What skills should do.**

- Decision logs, pre-registration files, and readouts are written to a reproducible artifact directory, not just chat output.
- Each artifact records: what was decided, who reviewed it, what evidence was available, what uncertainty remained, and what trade-offs were accepted.
- For regulated workspaces, advocates (marketing, product) are separated from judges (analytics, risk, legal). The same person should not own both the campaign and the decision on whether it shipped.

### 6. Pre-mortem and backcasting

**Principle.** Before launch, ask "six months from now, this is considered a
mistake. What happened?" Then work backward from the desired *end state*,
not forward from the desired *launch*.

**What skills should do.**

- Design and decision-review skills include a pre-mortem step. The deliverable is a short list of failure modes — including reputational, compliance, content-staleness, segment-asymmetry, and amplification-of-bad-behavior failure modes — and a mitigation per mode.
- Backcasting reframes the goal. The deliverable is not "launch the comparison content" but "we can confidently decide whether the content helps retain customers while preserving trust, compliance integrity, and content accuracy."
- Maintenance is a first-class deliverable: content owners, refresh cadence, and takedown triggers are specified at design time, not after launch.

### 7. Long-term thinking — update beliefs, keep learning

**Principle.** The goal is not a short-term click, conversion, or ship date.
It is a durable learning capability and a trustworthy customer relationship.

**What skills should do.**

- Null results are recorded and indexed (see the `null-results-knowledge-base` skill in the experimentation plugin) — they reduce the cost of the next bet.
- Decision rules and guardrails are versioned over time so the team can see how its risk appetite and standards evolved.
- Readouts include "what would update our belief next time" — a learning hook, not just a retrospective.

---

## Pre-registration template (use this in design artifacts)

Every test or material campaign that goes through one of this repository's
design or review skills should produce a pre-registration block matching
the schema below. The exact field names matter — downstream readout and
decision-review skills check for them by name.

```yaml
pre_registration:
  hypothesis: >
    Plain-language statement of what we believe and the mechanism we think
    is at work. One paragraph. Should be falsifiable.
  primary_metric:
    name: <metric_name>
    direction: increase | decrease
    minimum_detectable_effect: <absolute or relative, with units>
  leading_indicators:
    - <metric_name>: <why we expect this to move first>
  guardrails:
    - <metric_name>: <threshold that would block ship even if primary moves>
    - complaints: <threshold>
    - compliance_defects: 0   # any non-zero is a kill condition
    - content_staleness_days: <max days a sourced claim may go unrefreshed>
  audience:
    eligibility: <who is in, who is out>
    randomization_unit: <user | session | visitor | account>
    holdout_size: <% of eligible>
  duration_logic:
    expected_baseline_rate: <p>
    sample_size_per_arm: <n>
    expected_duration_days: <d>
    interim_look_policy: <none | pre-specified peeks with alpha-spend>
  decision_rule:
    ship_if: <criteria>
    iterate_if: <criteria>
    hold_if: <criteria>
    kill_if: <criteria>
  accountability:
    advocate: <role / team>
    judge: <role / team — must be different from advocate>
    reviewers: [<role>, <role>]
    review_board: <name of governance body if applicable>
  pre_mortem:
    failure_modes:
      - mode: <one-line failure description>
        likelihood: low | medium | high
        impact: low | medium | high
        mitigation: <what we'll do to prevent or detect>
  maintenance:
    content_owner: <role>
    refresh_cadence_days: <n>
    takedown_triggers:
      - <condition that triggers immediate revision or removal>
```

---

## Readout template (use this in analysis / decision-review skills)

```yaml
readout:
  pre_registration_reference: <path or URL to the pre-reg artifact>
  results:
    primary_metric_observed: <value, CI, p or posterior>
    leading_indicators_observed: { ... }
    guardrail_status:
      - metric: <name>
        threshold: <value>
        observed: <value>
        breached: true | false
  decision_quality:
    pre_registered_hypothesis_unchanged: true | false
    primary_metric_unchanged: true | false
    decision_rule_followed: true | false
    post_hoc_segments_flagged_as_exploratory: true | false
    disconfirming_evidence_considered: <one paragraph>
  resulting_check:
    # If the team is tempted to ship despite guardrail breach, or to kill
    # despite a successful primary outcome, this section forces a written
    # justification. Empty if not applicable.
    decision_against_pre_registered_rule: <none | brief reason>
  next_bet:
    what_changed_our_belief: <one paragraph>
    what_we_will_test_next: <next hypothesis or "nothing — retire">
```

---

## When the result and the process disagree

Use this 2x2 to keep the conversation honest. Most skills should reference
it when producing a readout in a high-trust workspace.

|                          | Good outcome                                    | Bad outcome                                     |
|--------------------------|-------------------------------------------------|-------------------------------------------------|
| **Good decision process**| Ship and document why. Capture the learning for next bet. | Honest miss. Update the prior, record what changed our belief. |
| **Bad decision process** | Lucky win — do **not** treat as license to ship more like this. Fix the process before the next bet. | Predictable loss. The lesson is process, not the idea. |

The "lucky win" cell is the most dangerous one. A skill operating in a
regulated workspace must explicitly call it out rather than letting the
team celebrate.

---

## When to apply this framework

The framework is non-optional for:

- Any experiment touching customer-facing content in a regulated workspace (financial services, advised products, healthcare, regulated insurance).
- Any campaign producing performance claims, comparison content, or material that would require compliance review.
- Any decision where rollback is costly, slow, or visible.

For low-risk, easily reversible decisions (internal-only dashboards, copy
tweaks to non-customer-facing pages), the framework can be applied in a
lightweight form: a one-line pre-registration and a brief decision-rule
note are enough.

---

## How individual skills should reference this doc

Skills should not paste this document into their own SKILL.md. Instead they
should:

1. Include a short "Decision Quality" section that names the principles relevant to that skill's stage of the lifecycle (design / readout / governance / campaign post-hoc).
2. Link here for the full framework and the templates.
3. Encode the pre-registration / readout schema field names so downstream automation can check across skills.

This keeps the framework consistent across plugins without duplicating
prose that has to be maintained in many places.
