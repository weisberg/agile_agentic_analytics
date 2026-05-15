# Review Fix, Security, and Investigation Components

Clean working trees, fix-first classification, scope drift, specialist review armies, security confidence gates, incident response, root cause, and reassessment.

Components: 73-80.

Source: distilled from the gstack `SKILL.md` corpus. Each component includes a context paragraph, reusable description, and compact sample.

## **73. Clean Working Tree and Atomic Commit Component**

**Reusable purpose:** Protect user changes while allowing safe fix loops.

**Context:** Use this before any skill starts editing, fixing, or committing in a repository that may contain user work. It protects unrelated changes, encourages one logical fix per commit, and provides a safe recovery path if the agent's own fix regresses.

**Reusable rules:**

```text
- Check git status before edits.
- Identify unrelated user changes and leave them alone.
- One fix equals one logical commit when the workflow owns commits.
- Stage only intentional files.
- Never use broad destructive cleanup to make the tree look clean.
- Revert only the agent's own failed fix when verification regresses.
```

**Use this for:** QA, design-review, review, ship, release docs.

**Sample:**

```text
Before fixing:
- git status shows user-modified docs/roadmap.md. Do not touch.
- Agent owns app/views/admin/imports/show.html.erb and test/e2e/imports.spec.ts.

Commit rule:
- Stage only owned files.
- Commit exactly one verified fix.
- If verification regresses, revert only the agent's last change.
```

------

## **74. Fix-First Review Classification Component**

**Reusable purpose:** Decide which review findings should be fixed immediately and which require user judgment.

**Context:** Use this in review workflows that can both report and fix findings. It helps the skill decide what can be fixed immediately, what requires a user decision, and what should remain a report-only observation because it is speculative or outside scope.

**Reusable classes:**

```text
auto_fix:
  mechanical correctness, typo, obvious broken test, clear lint, small doc sync

ask_first:
  architecture, product behavior, taste, public API, data migration, security tradeoff

report_only:
  out of scope, speculative, low-confidence, needs stakeholder input
```

**Use this for:** Code review, QA, design review, document-release.

**Sample:**

```text
Finding: typo in empty-state copy.
Class: auto_fix.

Finding: change retry behavior from immediate to queued.
Class: ask_first because it changes product behavior.

Finding: possible future export feature.
Class: report_only because it is outside current scope.
```

------

## **75. Scope Drift Audit Component**

**Reusable purpose:** Compare intended plan scope against actual diff and outputs.

**Context:** Use this when a branch, implementation, or release must be checked against an intended plan. It catches unplanned files, missing planned items, undocumented external deliverables, and surprise user-facing behavior before the work is approved or shipped.

**Reusable checks:**

```text
- Files changed but not explained by plan.
- Planned items not reflected in diff.
- External deliverables claimed but not verifiable.
- Unplanned user-facing behavior.
- Docs, tests, and migrations missing for implemented behavior.
```

**Use this for:** Review, ship, release notes, plan completion dashboards.

**Sample:**

```text
Scope drift audit:
- Planned: import failure reason UI.
- Diff includes: new billing settings route.
- Status: drift detected.
- Recommendation: remove billing route from this branch or ask user to accept
  scope expansion.
```

------

## **76. Specialist Review Army Component**

**Reusable purpose:** Run targeted review passes with distinct lenses instead of one generic code review.

**Context:** Use this for large or high-risk changes where one generic review pass is likely to miss domain-specific issues. It coordinates architecture, test, security, performance, UX, docs, ops, and adversarial lenses, then deduplicates findings into a coherent review.

**Reusable reviewers:**

```text
- architecture
- tests
- security
- performance
- UX/design
- docs
- operations/deploy
- adversarial red team
```

**Rules:**

```text
- Each reviewer gets the same evidence pack.
- Findings are deduplicated.
- P1/P2 findings gate release.
- Cross-review disagreement becomes a decision or investigation.
```

**Use this for:** Large PR review, release gates, high-risk implementation plans.

**Sample:**

```text
Specialist passes:
- Architecture: schema and API shape.
- Tests: failure category coverage and browser regression.
- Security: log redaction and authorization.
- Performance: large import behavior.
- UX: empty/error/partial states.
- Ops: rollout flag and canary.

Deduplicate findings before final report.
```

------

## **77. Security Confidence Gate Component**

**Reusable purpose:** Keep security reports from becoming noisy lists of guesses.

**Context:** Use this in security audits where noise can be worse than silence. It forces each finding to include confidence, exploit scenario, code/config evidence, false-positive filtering, severity, remediation, and verification so the output is actionable rather than speculative.

**Reusable requirements:**

```text
- Assign confidence to each finding.
- Include exploit scenario or realistic abuse path.
- Trace code or config evidence.
- Apply false-positive exclusions.
- Classify severity separately from confidence.
- Include remediation and verification steps.
```

**Modes:**

```text
daily:
  high-confidence findings only

comprehensive:
  broader scan with clearly labeled lower-confidence items
```

**Use this for:** Security audit, dependency review, CI/CD review, LLM prompt/tool security.

**Sample:**

```text
Finding: Import failure details may expose raw source values.
Severity: High.
Confidence: 8/10.
Evidence: FailureReasonPresenter renders `raw_error` into admin page.
Exploit scenario: user uploads a CSV containing a secret in a failing row; another
admin can view it in logs.
Mitigation: redact raw values and test redaction.
```

------

## **78. Incident Response Playbook Component**

**Reusable purpose:** Provide concrete response steps for confirmed high-severity findings.

**Context:** Use this when a security finding could require immediate containment or coordinated response. It gives the skill a concrete playbook for preserving evidence, rotating credentials, assessing impact, patching, verifying, communicating, and hardening after the incident.

**Reusable shape:**

```text
Trigger:
Immediate containment:
Evidence to preserve:
Credential rotation:
User/data impact assessment:
Patch path:
Verification:
Communication:
Follow-up hardening:
```

**Use this for:** Leaked secret handling, auth bypass, data exposure, production compromise.

**Sample:**

```text
Trigger: raw import data exposed in admin failure logs.
Immediate containment: disable import diagnostics flag.
Evidence: preserve request logs and affected import IDs.
Credential rotation: rotate any exposed tokens found in rows.
Impact: identify accounts with viewed failure details.
Patch: redact raw values and backfill sanitized records.
Verification: replay affected imports in staging.
Communication: notify support and affected account owners if required.
```

------

## **79. Root-Cause Investigation Component**

**Reusable purpose:** Prevent premature fixes.

**Context:** Use this for bug reports, failing tests, production incidents, data discrepancies, and flaky behavior. It prevents the agent from patching symptoms by requiring reproduction or equivalent evidence, code-path tracing, hypothesis testing, minimal fix, regression coverage, and final verification.

**Reusable law:**

```text
No fix without a root cause.
```

**Reusable flow:**

```text
1. Capture symptoms.
2. Reproduce or gather equivalent evidence.
3. Trace the relevant code path.
4. Check recent changes.
5. Form hypotheses.
6. Test hypotheses before editing.
7. Apply minimal fix.
8. Add regression coverage.
9. Verify the original symptom is gone.
```

**Use this for:** Bugs, flaky tests, production issues, failed deploys, data discrepancies.

**Sample:**

```text
Investigation:
Symptom: retry button returns 500.
Reproduction: POST /admin/imports/123/retry in staging fixture.
Trace: RetryController -> ImportRetryJob -> ImportRun#source_file.
Root cause: expired source_file attachment is not handled.
Fix: guard missing file and show "source expired" state.
Regression: request spec for expired source file.
```

------

## **80. Three-Strike Reassessment Component**

**Reusable purpose:** Stop repeated failed debugging attempts.

**Context:** Use this when debugging loops begin to repeat without progress. After three failed hypotheses, the skill must stop, summarize what was tried and disproven, revisit assumptions, and choose a new diagnostic path or ask for missing context.

**Reusable rule:**

```text
After three failed hypotheses, STOP.
Summarize attempts, evidence, and why they failed.
Re-open assumptions.
Ask for missing context or choose a new diagnostic path.
```

**Use this for:** Investigation, QA fix loops, CI failures, deployment debugging.

**Sample:**

```text
Three failed hypotheses:
1. Auth token expired: false, request authenticated.
2. Worker queue down: false, job never enqueued.
3. Bad import id: false, ImportRun exists.

Reassess: stop editing. Trace controller params and attachment state next.
```
