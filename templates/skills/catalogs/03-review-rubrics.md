# Review Rubric Components

Engineering, security, data, code quality, test, performance, observability, deployment, trajectory, and UX rubrics.

Components: 26-36.

Source: distilled from the gstack `SKILL.md` corpus. Each component includes a context paragraph, reusable description, and compact sample.

## **26. Architecture Review Component**

**Context:** Use this for plans or reviews that introduce new services, APIs, state machines, data flows, background jobs, or integrations. It helps the skill reason about boundaries, coupling, scaling, failure points, and rollback posture before code is written or approved.

**Reusable checks:**

```text
- System boundaries
- Data flow
- State machines
- Coupling
- Scaling
- Single points of failure
- Security boundaries
- Production failure scenarios
- Rollback posture
```

**Required output:**

```text
ASCII system architecture diagram
```

**Use this for:** `/plan-eng-review`, PR review, system design review.

**Sample:**

```text
Architecture diagram:

Admin UI -> Import Status API -> ImportRun model -> Worker logs
                       |
                       v
              FailureReason mapper

Checks:
- API does not expose raw secrets from logs.
- Mapper has stable categories.
- UI handles missing worker log references.
```

------

## **27. Error & Rescue Map Component**

**Context:** Use this for production workflows, data pipelines, integrations, and user-facing systems where generic 'handle errors' language is not enough. It forces the skill to name concrete failure modes, exception classes, rescue behavior, logging, and what the user sees when things go wrong.

**Reusable checks:**

```text
For every codepath:
- What can go wrong?
- What exception class?
- Is it rescued?
- What is the rescue action?
- What does the user see?
```

**Reusable registry:**

```text
METHOD/CODEPATH | WHAT CAN GO WRONG | EXCEPTION CLASS
EXCEPTION CLASS | RESCUED? | RESCUE ACTION | USER SEES
```

**Use this for:** Production-critical software, data pipelines, LLM systems, automation jobs.

**Reusable insight:** “Handle errors” is not a plan. Named failures are a plan.

**Sample:**

```text
CODEPATH | WHAT CAN GO WRONG | EXCEPTION | RESCUED | USER SEES
ImportStatusController#show | run id missing | NotFound | yes | "Import not found"
FailureReasonMapper#call | unknown log shape | ParseError | yes | "Unknown failure"
CsvImporter#perform | source file missing | FileMissing | yes | "Source file expired"
```

------

## **28. Security & Threat Model Component**

**Context:** Use this whenever a feature touches user data, credentials, permissions, files, APIs, LLM prompts, CI/CD, or external integrations. It gives the skill a practical threat-model table so security findings are tied to likelihood, impact, and mitigation rather than broad warnings.

**Reusable checks:**

```text
- Attack surface
- Input validation
- Authorization
- Secrets
- Dependency risk
- Data classification
- Injection vectors
- Audit logging
```

**Reusable output:**

```text
Threat | Likelihood | Impact | Mitigation
```

**Use this for:** Any feature touching user data, files, APIs, credentials, LLM inputs, or permissions.

**Sample:**

```text
Threat | Likelihood | Impact | Mitigation
Log secret exposure | Medium | High | redact before mapping and test fixtures
Unauthorized import read | Low | High | policy check on ImportRun account_id
CSV formula injection | Medium | Medium | escape cells starting with =,+,-,@
```

------

## **29. Data Flow & Interaction Edge Cases Component**

**Context:** Use this for UI flows, data transformations, imports, async jobs, dashboards, and automations where edge cases often become user-visible bugs. It makes the skill enumerate empty, nil, stale, partial, large, slow, retry, and navigation cases before approving the plan or implementation.

**Reusable checks:**

```text
Data:
- nil input
- empty input
- wrong type
- invalid value
- upstream error
- stale output
- partial write

Interaction:
- double-click
- navigate away
- retry in flight
- slow network
- zero results
- 10,000 results
- background job partial failure
```

**Use this for:** UI features, analytics workflows, upload flows, async jobs.

**Sample:**

```text
Data edges:
- no failed rows
- 1 failed row
- 10,000 failed rows
- stale source file
- unknown error category

Interaction edges:
- user refreshes during import
- user opens details after retention expiry
- user retries while previous retry is in flight
```

------

## **30. Code Quality Component**

**Context:** Use this in code reviews, implementation plans, and refactor discussions where maintainability matters as much as correctness. It guides the skill to compare proposed code against local patterns, naming, complexity, error style, and abstraction choices instead of only checking whether it works once.

**Reusable checks:**

```text
- Fit with existing patterns
- DRY violations
- Naming
- Error handling style
- Over-engineering
- Under-engineering
- Cyclomatic complexity
```

**Use this for:** PR review, refactor review, implementation plan review.

**Sample:**

```text
Code quality review:
- Does the mapper follow existing service object naming?
- Are categories constants or scattered strings?
- Is controller logic thin?
- Are test fixtures close to the importer tests?
- Is this simpler than adding a new state machine?
```

------

## **31. Test Review Component**

**Context:** Use this when a change adds behavior, data flow, UI, integrations, or failure paths that need confidence after the agent leaves. It helps the skill design tests around real risk: user flows, code paths, rescue behavior, regressions, chaos cases, and the test that would make a Friday-night deploy feel safe.

**Reusable inventory:**

```text
NEW UX FLOWS
NEW DATA FLOWS
NEW CODEPATHS
NEW BACKGROUND JOBS
NEW INTEGRATIONS
NEW ERROR/RESCUE PATHS
```

**Reusable test questions:**

```text
- What test gives 2am Friday confidence?
- What would hostile QA write?
- What is the chaos test?
- Is the test pyramid healthy?
- What tests are flaky by design?
```

**Use this for:** Engineering review, analytics validation, agent eval design.

**Sample:**

```text
Required tests:
- Unit: maps known worker failures to stable categories.
- Unit: unknown errors return fallback category.
- Request: unauthorized user cannot read another account's import.
- Browser: admin sees failure reason and next action.
- Regression: CSV formula-looking values are escaped.
```

------

## **32. Performance Review Component**

**Context:** Use this for backend, frontend, data, and dashboard work where performance can regress silently. It should be applied during design review, PR review, QA, or benchmarking to catch N+1 queries, missing indexes, large bundles, memory growth, p99 latency, and expensive rendering.

**Reusable checks:**

```text
- N+1 queries
- Memory growth
- Missing indexes
- Cache candidates
- Background job sizing
- p99 latency
- Connection pool pressure
```

**Use this for:** Backend systems, data tools, dashboards, APIs.

**Sample:**

```text
Performance checks:
- Status endpoint does not scan all failed rows on page load.
- Error counts use indexed columns.
- Large imports paginate failed row details.
- Browser page avoids rendering 10,000 rows at once.
- p95 target: status endpoint under 300ms for a large import.
```

------

## **33. Observability Review Component**

**Context:** Use this for systems that will run in production or generate operational decisions after release. It asks whether future maintainers can reconstruct what happened from logs, metrics, traces, dashboards, alerts, and runbooks, which is essential for debugging user reports weeks later.

**Reusable checks:**

```text
- Logs
- Metrics
- Traces
- Alerts
- Dashboards
- Runbooks
- Debuggability
- Admin tools
```

**Reusable question:**

```text
If a bug is reported 3 weeks post-ship, can we reconstruct what happened?
```

**Use this for:** Production systems, agentic workflows, pipelines, analytics automation.

**Sample:**

```text
Observability plan:
- Log import_id, account_id, failure_category, and retry_id.
- Metric: import.failure.category.count.
- Alert: failure rate exceeds baseline for 15 minutes.
- Dashboard: top failure categories by account and source.
- Runbook: "Import failures spike after deploy."
```

------

## **34. Deployment & Rollout Component**

**Context:** Use this for features that require migrations, flags, deploy order, background jobs, external services, or production verification. It turns release safety into explicit rollout and rollback steps so a plan is not considered complete just because the code path is described.

**Reusable checks:**

```text
- Migration safety
- Feature flags
- Rollout order
- Rollback plan
- Mixed old/new code risk
- Environment parity
- Post-deploy verification
- Smoke tests
```

**Use this for:** Ship workflows, release planning, data model migrations.

**Sample:**

```text
Rollout plan:
- Add nullable failure_category column.
- Backfill only recent imports in background.
- Ship UI behind `import_diagnostics` flag.
- Enable for internal accounts first.
- Canary status page and import details page.
- Rollback: disable flag; column is additive.
```

------

## **35. Long-Term Trajectory Component**

**Context:** Use this in strategic, architectural, and platform reviews where today's shortcut can create tomorrow's path dependency. It helps the skill evaluate reversibility, debt, knowledge concentration, operational load, and whether the design will still be understandable months later.

**Reusable checks:**

```text
- Technical debt
- Operational debt
- Testing debt
- Documentation debt
- Path dependency
- Knowledge concentration
- Reversibility
- 12-month readability
```

**Reusable metric:**

```text
Reversibility: 1-5
1 = one-way door
5 = easily reversible
```

**Use this for:** Strategic reviews, architecture reviews, operating model changes.

**Sample:**

```text
12-month check:
- Reversibility: 4/5 because schema is additive and UI is flagged.
- Debt risk: category taxonomy could grow without ownership.
- Documentation need: add category owner and review cadence.
- Future path: recovery center if diagnostics reduce support tickets.
```

------

## **36. Design & UX Review Component**

**Context:** Use this for UI plans, dashboards, workflow tools, internal apps, and any feature with user-visible states. It makes the skill inspect information architecture, loading/empty/error/success states, responsive behavior, accessibility, emotional arc, and design-system alignment before implementation or ship.

**Reusable checks:**

```text
- Information architecture
- Loading / empty / error / success / partial states
- Emotional arc
- Generic AI slop risk
- Design system alignment
- Responsive behavior
- Accessibility basics
```

**Reusable state map:**

```text
FEATURE | LOADING | EMPTY | ERROR | SUCCESS | PARTIAL
```

**Use this for:** UI plans, dashboards, internal tools, AI control planes.

------

# **Cross-Model / Outside Voice Components**

**Sample:**

```text
UX state matrix:
STATE | USER COPY | PRIMARY ACTION
Loading | "Checking import status..." | none
Empty | "No failed rows." | Back to imports
Error | "We could not load failure details." | Retry
Partial | "Some details expired." | Download available details
Success | "42 rows failed validation." | View failed rows
```
