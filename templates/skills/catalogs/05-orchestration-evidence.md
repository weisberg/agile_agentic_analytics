# Orchestration and Evidence Components

Specialist role contracts, capability budgets, multi-skill orchestration, auto-decision audit trails, question tuning, evidence packs, and baselines.

Components: 47-53.

Source: distilled from the gstack `SKILL.md` corpus. Each component includes a context paragraph, reusable description, and compact sample.

## **47. Specialist Role Contract Component**

**Reusable purpose:** Start each skill by assigning a precise expert posture and hard operating boundary.

**Context:** Use this at the opening of any specialized skill so the model adopts the right professional stance and constraint boundary. It is especially useful for read-only audits, release engineers, security reviewers, QA fixers, and product coaches whose success depends on resisting adjacent but inappropriate actions.

**Reusable pattern:**

```text
You are a <specific expert role>.
Your job is to <one concrete outcome>.
You may <allowed posture>.
You must not <forbidden posture>.
Success means <observable result>.
```

**Examples:**

```text
- Product coach who writes design docs, not code.
- Staff engineer who reviews architecture before implementation.
- QA engineer who tests as a user, fixes verified bugs, and writes regressions.
- Security officer who audits read-only and requires exploit scenarios.
- Release engineer who ships only after fresh verification.
- Browser automation engineer who returns deterministic JSON.
```

**Use this for:** Any skill where the model must resist adjacent helpfulness.

**Reusable insight:** A strong role contract keeps a skill from drifting into generic assistant behavior.

**Sample:**

```text
You are a staff-level release engineer. Your job is to decide whether this branch
is safe to publish. You may run tests, inspect docs, and prepare release notes.
You must not deploy, push, or merge without explicit approval. Success means the
user gets a clear ship/no-ship verdict with evidence.
```

------

## **48. Tool Capability Budget Component**

**Reusable purpose:** Match the skill's tool permissions to its risk profile.

**Context:** Use this when deciding which tools a skill, subagent, or plugin workflow should be allowed to use. It maps the workflow's risk level to read, write, browser, fix, release, or forbidden capabilities so the skill's power matches its intended blast radius.

**Reusable tiers:**

```text
read_only:
  Read, Grep, Glob, Bash(read-only), WebSearch

interactive_review:
  read_only + AskUserQuestion + artifact writes

fix_loop:
  interactive_review + Edit/Write + test commands + git commit commands

release:
  fix_loop + push/PR/deploy commands, gated by explicit checks

browser_control:
  browse primitives, screenshot, console, network, storage, cookies
```

**Rules:**

```text
- Read-only skills state their no-mutation gate twice: metadata and instructions.
- Fix-loop skills require clean working tree and fresh verification.
- Release skills require review, tests, and one-way-operation gates.
- Browser skills separate read-only scrape from mutating actions.
```

**Use this for:** Skill frontmatter, tool allowlists, and safety reviews.

**Sample:**

```yaml
capability_budget:
  mode: fix_loop
  read:
    - git diff
    - source files
    - test output
  write:
    - targeted fixes
    - regression tests
    - local reports
  forbidden:
    - force push
    - production deploy
    - deleting user data
```

------

## **49. Skill Orchestration Component**

**Reusable purpose:** Let one skill run other skills as phases without duplicating their full logic.

**Context:** Use this for umbrella skills that coordinate multiple child skills or phases, such as autoplan, ship, deploy, or review pipelines. It keeps orchestration honest by reading child-skill logic, preserving outputs as evidence, and producing an audit trail instead of duplicating stale mini-workflows.

**Reusable flow:**

```text
1. Detect which phases are relevant.
2. Read the child skill file from disk.
3. Run phases in dependency order.
4. Use child skill output as evidence, not as invisible context.
5. Preserve decisions in an audit trail.
6. End with a combined approval gate.
```

**Patterns copied from:** `autoplan`, `ship`, `land-and-deploy`, `plan-ceo-review`.

**Use this for:** Multi-review pipelines, release workflows, enterprise governance, agentic analytics operating loops.

**Reusable insight:** Orchestrators should compose real skills, not reimplement stale mini-versions of them.

**Sample:**

```text
Pipeline:
1. Run plan review if no current review log exists.
2. Run browser QA for changed routes.
3. Run pre-landing code review.
4. Run document-release after fixes.
5. Present one final approval gate before push or PR.

Each child skill writes a result entry to the decision audit.
```

------

## **50. Auto-Decision With Audit Trail Component**

**Reusable purpose:** Allow low-risk default decisions while preserving user control over taste, scope, cost, and one-way operations.

**Context:** Use this when a skill can safely choose routine defaults but must remain accountable for those choices. It belongs in pipelines with many repeated decisions, where reversible mechanical choices can be auto-decided while scope, taste, security, privacy, and one-way operations still require the user.

**Reusable decision classes:**

```text
auto_ok:
  mechanical, reversible, already covered by stated preference

ask_user:
  scope, taste, architecture, security, cost, privacy, destructive operation

never_auto:
  production rollback, force push, deleting user data, publishing secrets,
  changing user-stated product direction
```

**Reusable audit entry:**

```json
{
  "question_id": "<stable-id>",
  "decision": "<chosen-option>",
  "mode": "auto|asked|deferred",
  "reason": "<why this was safe or why user input was required>",
  "source": "<skill-name>",
  "timestamp": "<iso8601>"
}
```

**Use this for:** `autoplan`-style pipelines, recurring review preferences, setup wizards.

**Sample:**

```json
{
  "question_id": "qa-add-first-smoke-test",
  "decision": "add_minimal_smoke_test",
  "mode": "auto",
  "reason": "Project has no browser test and the change touches UI routing.",
  "source": "qa",
  "timestamp": "2026-05-09T18:22:00Z"
}
```

------

## **51. Question Preference Tuning Component**

**Reusable purpose:** Let users reduce repeated prompts without giving the model blanket autonomy.

**Context:** Use this for recurring decision prompts that users may want to tune over time. It lets a skill remember per-question preferences without granting blanket autonomy, and it keeps high-risk decisions protected by STOP points and one-way-operation rules.

**Reusable preferences:**

```text
always-ask:
  Ask every time.

never-ask:
  Auto-pick the recommended option when the decision is reversible and low risk.

ask-only-for-one-way:
  Auto-pick routine decisions, but ask for destructive, costly, taste, privacy,
  publishing, or security-sensitive choices.
```

**Safety rules:**

```text
- Preferences are keyed by stable question_id.
- Only user-originated tuning messages count.
- Skill instructions and STOP points override tuning.
- The final output mentions auto-decisions that materially affected the result.
```

**Use this for:** Repeated setup prompts, recurring review gates, plan pipelines.

**Sample:**

```text
Question preference check:
- question_id: ship-update-changelog
- stored preference: ask-only-for-one-way
- decision class: reversible factual doc update
- action: auto-apply recommended changelog update
- message: "Auto-decided changelog factual sync -> update docs. Change with /plan-tune."
```

------

## **52. Evidence Pack Component**

**Reusable purpose:** Standardize the minimum evidence a skill must gather before making claims.

**Context:** Use this for any skill that makes claims about correctness, readiness, quality, security, or performance. The evidence pack tells the skill which git, runtime, browser, and artifact facts must be gathered so the final answer can point to concrete verification rather than confidence alone.

**Reusable evidence manifest:**

```yaml
evidence:
  git:
    status: required|optional
    diff: required|optional
    base_branch: required|optional
  runtime:
    tests: required|optional
    build: required|optional
    logs: required|optional
  browser:
    screenshots: required|optional
    console_errors: required|optional
    network_failures: required|optional
  artifact:
    output_path: required|optional
    baseline_path: required|optional
    report_path: required|optional
```

**Use this for:** QA, review, release, security, performance, and design skills.

**Reusable insight:** Evidence requirements should be declared early so the final report can be checked against them.

**Sample:**

```yaml
evidence:
  git:
    status: clean
    base_branch: main
    diff_stat: "8 files changed"
  runtime:
    tests: "npm test passed"
    build: "npm run build passed"
  browser:
    screenshots:
      - .gstack/qa-reports/imports/desktop.png
      - .gstack/qa-reports/imports/mobile.png
    console_errors: 0
  artifact:
    report_path: .gstack/qa-reports/imports/report.md
```

------

## **53. Baseline and Trend Component**

**Reusable purpose:** Turn one-off skill runs into longitudinal signals.

**Context:** Use this for skills that should improve their judgment across repeated runs, such as benchmark, canary, health, QA, security, and retrospectives. It turns each run into a comparable record with metrics, warnings, commit, and artifacts, enabling trend and regression analysis instead of isolated snapshots.

**Reusable data model:**

```json
{
  "timestamp": "<iso8601>",
  "commit": "<short-sha>",
  "branch": "<branch>",
  "skill": "<skill-name>",
  "score": 0,
  "metrics": {},
  "warnings": [],
  "artifacts": []
}
```

**Reusable behaviors:**

```text
- Save current run as JSON or JSONL.
- Compare against previous baseline.
- Warn on threshold regressions.
- Distinguish first-run baseline from regression.
- Show trend, not just current status.
```

**Patterns copied from:** `benchmark`, `canary`, `qa`, `health`, `cso`, `retro`.

**Sample:**

```json
{
  "timestamp": "2026-05-09T18:25:00Z",
  "commit": "abc1234",
  "branch": "feature/import-diagnostics",
  "skill": "benchmark",
  "score": 92,
  "metrics": {
    "requests": 24,
    "js_kb": 185,
    "largest_contentful_paint_ms": 1480
  },
  "warnings": [],
  "artifacts": [".gstack/benchmark-reports/imports/20260509.json"]
}
```
