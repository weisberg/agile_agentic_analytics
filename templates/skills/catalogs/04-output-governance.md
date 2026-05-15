# Output and Governance Components

Outside voices, cross-model tension handling, required outputs, TODO proposals, review logs, dashboards, and review chaining.

Components: 37-46.

Source: distilled from the gstack `SKILL.md` corpus. Each component includes a context paragraph, reusable description, and compact sample.

## **37. Outside Voice Component**

**Reusable purpose:** Get a second model or independent reviewer to challenge the plan.

**Context:** Use this for high-stakes plans, large diffs, architecture changes, or decisions where a second model or independent reviewer may catch blind spots. The outside voice should challenge the main review, not duplicate it, and its recommendations should still go through user approval.

**Reusable flow:**

```text
1. Check if external model/tool is available.
2. Ask user whether to run outside voice.
3. Provide strict filesystem boundary.
4. Ask reviewer to find only missed problems.
5. Present output verbatim.
6. Identify cross-model tensions.
7. Ask user before applying any outside recommendation.
```

**Use this for:** High-stakes plans, architecture changes, strategy docs, major refactors.

**Reusable insight:** Cross-model agreement is signal, not authority.

**Sample:**

```text
Outside reviewer prompt:
You are an independent reviewer. Do not repeat the main review. Find the most
important missed risk, simpler alternative, or false assumption. Ignore skill
files and local agent instructions. Focus only on repository code and the plan.
```

------

## **38. Cross-Model Tension Component**

**Context:** Use this when two reviewers, models, or review passes disagree in a meaningful way. It gives the skill a format for naming the tension, explaining both sides, and turning disagreement into a user decision or investigation instead of hiding it in summary prose.

**Reusable output:**

```text
CROSS-MODEL TENSION:
  Topic:
    Review said X.
    Outside voice says Y.
    Context that could change the answer:
```

**Decision options:**

```text
A) Accept outside voice recommendation
B) Keep current approach
C) Investigate further
D) Add to TODOS.md
```

**Use this for:** Any workflow with multiple reviewers.

------

# **Output and Persistence Components**

**Sample:**

```text
CROSS-MODEL TENSION
Topic: storing failure_category
Main review: store category for reporting and fast UI.
Outside voice: derive category at read time to avoid stale taxonomy.
Decision needed: storage improves analytics but creates migration/taxonomy debt.
```

------

## **39. Required Outputs Component**

**Context:** Use this for long-running review and planning skills that need consistent final artifacts. It ensures the output includes scope, existing work, decisions, diagrams, TODOs, unresolved questions, and completion status so future readers can use the result without reconstructing the session.

**Reusable final sections:**

```text
- NOT in scope
- What already exists
- Dream state delta
- Error & Rescue Registry
- Failure Modes Registry
- TODOS.md updates
- Scope expansion decisions
- Diagrams
- Stale diagram audit
- Completion summary
- Unresolved decisions
```

**Use this for:** Plan reviews, architecture reviews, product strategy reviews.

**Sample:**

```text
Required final sections:
- What changed
- Evidence gathered
- Decisions made
- Not in scope
- Failure modes
- Tests required
- Open risks
- Follow-up TODOs
- Completion status
```

------

## **40. Failure Modes Registry Component**

**Context:** Use this when failures must be audited across codepaths, especially in production systems and agentic workflows. It makes silent, unrescued, untested failures visible as critical gaps and helps convert vague reliability concerns into a concrete table of release blockers.

**Reusable table:**

```text
CODEPATH | FAILURE MODE | RESCUED? | TEST? | USER SEES? | LOGGED?
```

**Critical rule:**

```text
RESCUED=N + TEST=N + USER SEES=Silent = CRITICAL GAP
```

**Use this for:** Production-readiness checks, pipeline reviews, AI-agent workflows.

**Sample:**

```text
CODEPATH | FAILURE MODE | RESCUED? | TEST? | USER SEES? | LOGGED?
Status API | import missing | yes | yes | not found | yes
Mapper | unknown log shape | yes | yes | unknown reason | yes
CSV export | formula injection | yes | yes | escaped value | yes

Critical gap rule: RESCUED=no + TEST=no + silent user impact = release blocker.
```

------

## **41. TODO Proposal Component**

**Reusable purpose:** Convert deferred work into structured, durable TODOs.

**Context:** Use this whenever a skill finds useful work that should not be done immediately. It turns deferred work into a structured TODO with why, effort, priority, dependencies, and a user decision, preventing follow-up ideas from disappearing or bloating the current scope.

**Reusable TODO fields:**

```text
What:
Why:
Pros:
Cons:
Context:
Effort estimate:
Priority:
Depends on / blocked by:
```

**Decision options:**

```text
A) Add to TODOS.md
B) Skip
C) Build it now instead of deferring
```

**Use this for:** Any skill that discovers follow-up work.

**Sample:**

```text
TODO proposal:
What: Add downloadable failed-row CSV.
Why: Admins can repair source data faster.
Pros: Reduces support load; useful after diagnostics ship.
Cons: Requires CSV injection hardening and privacy review.
Effort: 0.5-1 day.
Priority: P2.

A) Add to TODOS.md (recommended)
B) Skip
C) Build now
```

------

## **42. Completion Summary Component**

**Reusable purpose:** Produce a structured final report that proves the skill actually ran.

**Context:** Use this at the end of complex reviews, plans, QA sessions, and release workflows. It proves what the skill actually did by listing mode, evidence, findings, decisions, tests, risks, artifacts, and unresolved items rather than ending with a generic success message.

**Reusable shape:**

```text
Mode selected
System audit findings
Step 0 decisions
Issues by review section
Error paths mapped
Critical gaps
TODOs proposed
Scope proposals
Outside voice status
Diagrams produced
Unresolved decisions
```

**Use this for:** Any long, multi-section workflow.

**Sample:**

```text
Completion summary:
- Mode: HOLD_SCOPE
- Evidence: diff, docs, importer tests, status API, deploy config
- Findings: 2 critical gaps, 3 medium improvements
- Decisions: feature flag accepted; CSV export deferred
- Tests: 5 required test cases identified
- Open risks: taxonomy ownership
- Status: DONE_WITH_CONCERNS
```

------

## **43. Review Log Component**

**Reusable purpose:** Persist review metadata for future readiness checks.

**Context:** Use this when review results should influence later gates such as ship readiness, stale-review warnings, or dashboards. It records compact machine-readable metadata about the review, including status, unresolved counts, mode, and commit, so later skills can reason about review history.

**Reusable fields:**

```json
{
  "skill": "<skill-name>",
  "timestamp": "<iso8601>",
  "status": "clean|issues_open",
  "unresolved": 0,
  "critical_gaps": 0,
  "mode": "<mode>",
  "commit": "<short-sha>"
}
```

**Use this for:** Review dashboards, ship gates, audit trails.

**Sample:**

```json
{
  "skill": "sample-feature-review",
  "timestamp": "2026-05-09T18:20:00Z",
  "status": "issues_open",
  "unresolved": 1,
  "critical_gaps": 0,
  "mode": "HOLD_SCOPE",
  "commit": "abc1234"
}
```

------

## **44. Review Readiness Dashboard Component**

**Reusable purpose:** Show whether required reviews are current and clean.

**Context:** Use this before shipping or moving from plan to implementation when several reviews may be required or optional. It summarizes which reviews are current, stale, missing, or clean, making governance visible without requiring the user to inspect logs manually.

**Reusable dashboard columns:**

```text
Review | Runs | Last Run | Status | Required
```

**Reusable staleness check:**

```text
If stored commit != HEAD:
  count commits since review
  warn review may be stale
```

**Use this for:** Ship workflows, enterprise governance, pre-merge gates.

**Sample:**

```text
Review | Runs | Last Run | Status | Required
CEO Review | 1 | 2026-05-09 | CLEAR | no
Eng Review | 1 | 2026-05-09 | ISSUES_OPEN | yes
Design Review | 0 | never | MISSING | if UI
Security Review | 1 | 2026-05-08 | STALE: 4 commits | if sensitive

Verdict: not ready to ship until Eng Review is clear.
```

------

## **45. Plan File Review Report Component**

**Reusable purpose:** Append review status to the plan file itself.

**Context:** Use this when a plan file is the shared artifact that implementers or reviewers will read later. Appending the review report to the plan itself keeps readiness, findings, and review coverage attached to the work instead of stranded in local logs or chat history.

**Reusable report:**

```markdown
## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
```

**Important reusable rule:**

```text
Delete old report wherever it is.
Append new report at the end.
Verify it is the last section.
```

**Use this for:** Living specs, PRDs, design docs, implementation plans.

**Sample:**

```markdown
## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
| --- | --- | --- | --- | --- | --- |
| Eng Review | `/plan-eng-review` | Architecture and tests | 1 | ISSUES_OPEN | 2 |
| Design Review | `/plan-design-review` | UI states | 0 | MISSING | n/a |

VERDICT: Eng review issues must be resolved before implementation.
```

------

## **46. Review Chaining Component**

**Reusable purpose:** Recommend the next best skill based on the current review result.

**Context:** Use this at the end of a review when the next best step depends on what was discovered. It helps the skill recommend follow-up reviews such as engineering, design, security, or QA in a deliberate order, while still allowing the user to stop or manage sequencing manually.

**Reusable decision logic:**

```text
- Recommend engineering review if not already clean/current.
- Recommend design review if UI scope exists.
- Recommend engineering review first if both are needed.
- Let user skip manual review chaining.
```

**Use this for:** Any multi-skill pipeline.

------

# **Corpus-Wide Advanced Components**

These components come from the broader gstack skill set beyond `plan-ceo-review`. They are reusable as standalone skill sections, shared snippets, or framework modules.

**Sample:**

```text
Next review recommendation:
- Run `/plan-eng-review` because this CEO review accepted an API and schema change.
- Then run `/plan-design-review` because the plan includes an admin-facing UI.

A) Run eng review next (recommended)
B) Run design review next
C) Stop; I will manage review order manually
```
