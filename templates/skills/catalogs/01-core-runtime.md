# Core Runtime Components

Runtime setup, routing, decision gates, style, persistence, and completion contracts.

Components: 1-15.

Source: distilled from the gstack `SKILL.md` corpus. Each component includes a context paragraph, reusable description, and compact sample.

## **1. Skill Metadata / Routing Header**

**Reusable purpose:** Tell the agent when the skill should activate, what tools it may use, and what context it should preload.

**Context:** Use this at the very top of any skill that should be discoverable, routable, and safe to invoke without extra explanation from the user. It is especially important for plugin-shipped skills because the frontmatter is the first contract Claude Code sees: it describes when the skill should load, which tools it may use, which related skills it composes with, and what prior artifacts should be preloaded.

**Reusable fields:**

```yaml
name: <skill-name>
preamble-tier: <number>
interactive: true|false
version: <semver>
description: |
  What this skill does, when to use it, and what modes it supports.
benefits-from:
  - <related-skill>
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
  - WebSearch
triggers:
  - <phrase>
  - <phrase>
gbrain:
  schema: 1
  context_queries:
    - id: <query-id>
      kind: filesystem|list|...
      glob: <path>
      sort: mtime_desc
      limit: 5
      render_as: "## Context section title"
```

**Use this for:** Any Claude Code skill that should be invoked automatically or semi-automatically.

**Reusable insight:** The header acts like a **routing contract**. It tells the model, “Use this when the user says these things, and preload these artifacts first.”

**Sample:**

```yaml
---
name: sample-feature-review
version: 0.1.0
preamble-tier: 2
interactive: true
description: |
  Review a feature plan before implementation. Use when the user asks whether a
  plan is complete, safe, shippable, or worth building.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
triggers:
  - review this plan
  - is this ready to build
benefits-from:
  - office-hours
gbrain:
  schema: 1
  context_queries:
    - id: recent-plans
      kind: filesystem
      glob: "~/.gstack/projects/*/ceo-plans/*.md"
      sort: mtime_desc
      limit: 3
      render_as: "## Recent related plans"
---
```

------

## **2. Runtime Preamble Component**

**Reusable purpose:** Establish the execution environment before the actual skill starts.

**Context:** Use this at the beginning of long-running or stateful skills where branch, repo, telemetry, checkpoint, and artifact state can change the right behavior. The preamble gives the agent a reliable starting snapshot before it reviews, edits, tests, ships, or writes memory, so later decisions can cite concrete environment facts instead of assumptions.

**Responsibilities:**

```text
- Check tool/version updates
- Create session marker
- Detect branch
- Detect repo mode
- Load config flags
- Detect telemetry mode
- Detect checkpoint mode
- Detect proactive mode
- Detect routing setup
- Detect vendored skill install
- Load project learnings
- Write start event to local timeline
```

**Reusable interface:**

```bash
echo "BRANCH: $_BRANCH"
echo "PROACTIVE: $_PROACTIVE"
echo "REPO_MODE: $REPO_MODE"
echo "TELEMETRY: ${_TEL:-off}"
echo "CHECKPOINT_MODE: $_CHECKPOINT_MODE"
echo "MODEL_OVERLAY: claude"
```

**Use this for:** Any long-running skill where you want reproducibility, local state, and recoverability.

**Reusable insight:** A good skill starts by making hidden state explicit. Branch, mode, telemetry, routing, and checkpoint settings should be surfaced before decisions are made.

**Sample:**

```bash
set -euo pipefail
_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
_SESSION_ID="$(date -u +%Y%m%dT%H%M%SZ)-sample-feature-review"
_PROJECT_DIR="$HOME/.gstack/projects/$(basename "$_ROOT")"
mkdir -p "$_PROJECT_DIR/sessions"
printf '%s\n' "$_SESSION_ID" > "$_PROJECT_DIR/sessions/active"
echo "BRANCH: $_BRANCH"
echo "PROJECT_DIR: $_PROJECT_DIR"
echo "SESSION_ID: $_SESSION_ID"
```

------

## **3. Plan Mode Safety Component**

**Reusable purpose:** Define what the agent may do while in planning mode.

**Context:** Use this for skills that run during planning or review phases where reading and writing the plan is allowed but product-code mutation is not. It prevents a planning skill from drifting into implementation while still allowing useful operations such as reading files, writing plan notes, recording local skill metadata, and asking explicit decision questions.

**Pattern:**

```text
In plan mode, allowed operations include:
- Reads and searches
- Writing to the plan file
- Writing to local skill metadata/config directories
- Opening generated artifacts
- Running review-only commands
```

**Hard rules:**

```text
- Skill instructions beat generic plan-mode behavior.
- Treat the skill as executable instructions, not reference material.
- Stop at STOP points.
- Do not implement unless the workflow explicitly allows it.
- AskUserQuestion satisfies plan mode's end-of-turn requirement.
```

**Use this for:** Any skill that runs inside Claude Code plan mode.

**Reusable insight:** Planning skills need their own “safe operations” policy so the model does not accidentally mutate product code.

**Sample:**

```text
Plan mode rules for this skill:
- You may read files, inspect git state, and write the plan file.
- You may write local skill artifacts under ~/.gstack/.
- You may not edit product code.
- You may not run migrations, deploys, pushes, deletes, or package upgrades.
- At STOP points, ask the user and wait.
- If a decision tool is unavailable, write the decision brief into the plan and stop.
```

------

## **4. AskUserQuestion Decision Brief Component**

**Reusable purpose:** Convert every major ambiguity into a structured, auditable decision.

**Context:** Use this whenever the skill reaches a meaningful fork: scope, architecture, taste, cost, privacy, security, deployment, or any one-way operation. The component turns ambiguity into an auditable user decision by giving context, stakes, a recommendation, tradeoffs, and a clear default instead of letting the model silently choose.

**Core format:**

```text
D<N> — <one-line question title>
Project/branch/task: <short grounding sentence>
ELI10: <plain-English explanation>
Stakes if we pick wrong: <what breaks or what is lost>
Recommendation: <choice> because <reason>
Completeness: A=X/10, B=Y/10
or
Note: options differ in kind, not coverage — no completeness score.

Pros / cons:
A) <option label> (recommended)
  ✅ <specific pro>
  ✅ <specific pro>
  ❌ <specific con>
B) <option label>
  ✅ <specific pro>
  ✅ <specific pro>
  ❌ <specific con>

Net: <tradeoff summary>
```

**Reusable rules:**

```text
- One decision per question.
- Always include recommendation.
- Always label one option as recommended.
- Use completeness scores only when options differ in coverage.
- Use “options differ in kind” when comparing postures or categories.
- Never silently auto-decide unless user preferences explicitly allow it.
```

**Use this for:** Scope choices, architecture choices, destructive operations, tradeoff-heavy implementation decisions, review findings.

**Reusable insight:** The decision brief is one of the strongest reusable components. It converts agentic work from “model decides” into “model recommends, user governs.”

**Sample:**

```text
D1: Choose rollout posture
Project/branch/task: checkout-redesign on branch feature/checkout-v2.
ELI10: We can launch this to everyone at once or hide it behind a flag first.
Stakes if we pick wrong: A broken checkout could block purchases.
Recommendation: B because checkout is revenue-critical and flags make rollback fast.
Completeness: A=7/10, B=10/10.

A) Direct launch
  Pro: simplest release.
  Pro: no flag cleanup later.
  Con: rollback requires reverting or hotfixing.

B) Feature-flagged launch (recommended)
  Pro: quick rollback.
  Pro: supports gradual rollout.
  Con: adds one small cleanup task.

Net: B costs a little more now and buys much safer operations.
```

------

## **5. First-Run Configuration Prompt Component**

**Reusable purpose:** Ask once for persistent preferences without repeatedly nagging the user.

**Context:** Use this for plugin or skill ecosystems that need persistent preferences such as telemetry, proactive suggestions, checkpointing, artifact sync, or routing installation. It belongs near setup or preamble logic so users are asked once, the answer is recorded, and future runs do not repeatedly interrupt the workflow for the same configuration choice.

**Reusable gates:**

```text
- Feature prompt seen?
- Telemetry prompted?
- Proactive suggestions prompted?
- Skill routing installed?
- Writing style preference prompted?
- Artifact sync prompted?
- Vendoring warning shown?
```

**Reusable pattern:**

```bash
if marker_missing; then
  AskUserQuestion(...)
  apply_choice
  touch marker_file
fi
```

**Use this for:** Any developer tool or skill framework that needs durable preferences.

**Reusable insight:** Put first-run prompts behind marker files. Make them one-time, explicit, and reversible.

**Sample:**

```bash
_MARKER="$HOME/.gstack/.sample-feature-review-prompted"
if [ ! -f "$_MARKER" ]; then
  echo "Ask once: should this skill suggest follow-up reviews automatically?"
  echo "A) Yes, suggest next review when evidence points to one (recommended)"
  echo "B) No, only do exactly what I requested"
  touch "$_MARKER"
fi
```

------

## **6. Skill Routing Injection Component**

**Reusable purpose:** Add project-level routing guidance to `CLAUDE.md`.

**Context:** Use this when a project has multiple skills and needs local guidance that tells future agents which skill to invoke for which intent. It is most useful in `CLAUDE.md` or another project instruction file, where it reduces missed skill activation and makes skill routing consistent across sessions and contributors.

**Reusable structure:**

```markdown
## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool.
When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Bugs/errors → invoke /investigate
- QA/testing → invoke /qa
- Code review/diff check → invoke /review
- Ship/deploy/PR → invoke /ship
```

**Use this for:** Any multi-skill ecosystem.

**Reusable insight:** A project needs a local routing table. Without it, skill invocation depends too much on model memory.

**Sample:**

```markdown
## Skill routing

When the user's request matches a known skill, invoke the skill instead of
answering from memory.

- Product idea or problem framing: `/office-hours`
- Scope or strategy review: `/plan-ceo-review`
- Architecture and test plan: `/plan-eng-review`
- UI plan or visual direction: `/plan-design-review`
- Browser QA: `/qa`
- Pre-landing review: `/review`
- Ship or PR creation: `/ship`
```

------

## **7. Artifact Sync / Knowledge Sync Component**

**Reusable purpose:** Keep generated artifacts, plans, reviews, and learnings available across sessions and machines.

**Context:** Use this for skills that produce durable artifacts such as plans, reviews, screenshots, reports, decisions, or learnings that should survive beyond the current chat. It is most relevant in multi-session work or multi-machine setups, where the skill should sync artifacts at the start and end without treating generated files as disposable side effects.

**Responsibilities:**

```text
- Detect artifact sync mode
- Detect local vs remote brain mode
- Pull/push artifact repo when configured
- Report queue depth and last sync
- Ask privacy-gated sync question once
- Sync at skill start and skill end
```

**Reusable modes:**

```text
- off
- artifacts-only
- full
- remote-http managed mode
```

**Use this for:** Any skill ecosystem that creates persistent artifacts.

**Reusable insight:** Artifacts are not side effects. They are reusable memory. Treat them as first-class outputs.

**Sample:**

```bash
_SYNC_MODE=$(gstack-config get artifacts_sync_mode 2>/dev/null || echo off)
case "$_SYNC_MODE" in
  full|artifacts-only)
    gstack-artifacts-sync pull --quiet || echo "ARTIFACT_SYNC: pull failed"
    ;;
  off|"")
    echo "ARTIFACT_SYNC: off"
    ;;
esac

# At skill end:
[ "$_SYNC_MODE" = "full" ] || [ "$_SYNC_MODE" = "artifacts-only" ] && \
  gstack-artifacts-sync push --quiet || true
```

------

## **8. Context Recovery Component**

**Reusable purpose:** Reconstruct the project state after session start or context compaction.

**Context:** Use this when a skill may resume after context compaction, a new session, or a handoff from another agent. It should run early, read the newest relevant checkpoints and reports, and give a short reconstruction of what happened so the agent can continue from durable evidence instead of restarting from memory.

**Reusable inputs:**

```text
- Recent artifacts
- Recent checkpoints
- Timeline entries
- Last completed session
- Recent skills used
- Latest checkpoint
```

**Reusable output:**

```text
- 2-sentence welcome-back summary
- Suggested next skill if recent pattern is obvious
```

**Use this for:** Long-running agent workflows, codebase work, multi-session projects.

**Reusable insight:** Skills should be resumable. Context recovery should be automatic and artifact-backed.

**Sample:**

```bash
_PROJECT_DIR="$HOME/.gstack/projects/$(basename "$(pwd)")"
find "$_PROJECT_DIR/checkpoints" "$_PROJECT_DIR/ceo-plans" \
  -type f -name "*.md" 2>/dev/null | sort | tail -3

echo "If useful artifacts are found, read the newest one and summarize:"
echo "Welcome back: last time we decided X, and Y remains unresolved."
```

------

## **9. Voice and Writing Style Component**

**Reusable purpose:** Keep skill output consistent.

**Context:** Use this in any skill where output quality and user trust depend on a consistent voice. It belongs in the global behavior section of a skill so findings, decisions, and summaries stay concrete, evidence-led, and user-impact oriented rather than drifting into generic assistant prose.

**Reusable voice rules:**

```text
- Lead with the point.
- Be concrete.
- Tie technical choices to user outcomes.
- Be direct about quality.
- Avoid hype, corporate language, and filler.
- Use short sentences and active voice.
- Gloss jargon on first use unless terse mode is active.
```

**Use this for:** Any skill where answer quality depends on style consistency.

**Reusable insight:** Voice belongs in the skill file. Otherwise every run slowly drifts.

**Sample:**

```text
Voice rules:
- Lead with the finding.
- Name files, commands, routes, screenshots, and numbers.
- Explain user impact, not just implementation detail.
- Avoid filler and generic praise.
- Say "not verified" when evidence is missing.
- In terse mode, remove glossary-style explanations.
```

------

## **10. Completeness Principle Component**

**Reusable purpose:** Bias the agent toward complete, edge-case-aware solutions when AI compresses implementation cost.

**Context:** Use this in planning, review, QA, release, and test-design skills when the agent must decide whether to finish the complete useful scope or defer work. It helps distinguish a valuable complete 'lake' from an unrealistic 'ocean' and makes completeness an explicit tradeoff instead of an accidental shortcut.

**Core principle:**

```text
AI makes completeness cheap.
Recommend complete lakes:
- tests
- edge cases
- error paths
- observability
- rollback

Flag oceans:
- rewrites
- multi-quarter migrations
- unrelated scope explosions
```

**Reusable scoring:**

```text
Completeness: 10/10 = edge cases included
Completeness: 7/10 = happy path plus common failures
Completeness: 3/10 = shortcut
```

**Use this for:** Plan reviews, implementation planning, testing strategy, architecture decisions.

**Reusable insight:** The skill reframes “engineering effort” around AI-assisted marginal cost. That is very reusable for agentic analytics work.

**Sample:**

```text
Completeness check:
- Complete lake: add tests, error states, docs, rollback, and observability because
  the marginal cost is small.
- Ocean: rewrite auth, change storage engines, replace the design system, or expand
  into unrelated roadmap work.

Score:
- 10/10: success, edge cases, failure paths, and verification.
- 7/10: happy path plus common failure handling.
- 3/10: demo path only.
```

------

## **11. Confusion Protocol Component**

**Reusable purpose:** Stop the agent when ambiguity is high-stakes.

**Context:** Use this at high-stakes ambiguity points where guessing would create architectural, data, security, or destructive-scope risk. It tells the skill to stop, name the ambiguity, present a small set of options, and ask the user rather than burying a consequential assumption inside the implementation.

**Trigger conditions:**

```text
- Architecture ambiguity
- Data model ambiguity
- Destructive scope
- Missing context
- Security-sensitive uncertainty
```

**Behavior:**

```text
STOP.
Name the ambiguity.
Present 2-3 options with tradeoffs.
Ask the user.
Do not auto-decide.
```

**Use this for:** Data architecture, production changes, analytics definitions, security-sensitive workflows.

**Reusable insight:** Not all ambiguity is equal. Routine ambiguity can be resolved by judgment. High-stakes ambiguity needs a formal stop gate.

**Sample:**

```text
STOP: high-stakes ambiguity detected.

Ambiguity: The plan does not define whether "active users" means daily active
users, monthly active users, or billable seats.

Options:
A) Define active users as daily active users for engagement reporting.
B) Define active users as billable seats for revenue reporting.
C) Pause until the stakeholder confirms the metric.

Recommendation: C because the wrong metric changes product and business decisions.
```

------

## **12. Continuous Checkpoint Component**

**Reusable purpose:** Persist progress during long-running work.

**Context:** Use this in long implementation, review, or release workflows where losing context would be costly. It creates recoverable progress by committing or recording logical units with decisions, remaining work, and failed approaches, while keeping staging narrow so checkpointing does not sweep in unrelated user changes.

**Reusable policy:**

```text
If checkpoint_mode = continuous:
- Commit completed logical units
- Use WIP prefix
- Stage only intentional files
- Never git add -A
- Do not commit broken tests
- Push only if checkpoint_push = true
```

**Reusable commit body:**

```text
WIP: <description>

[gstack-context]
Decisions: <key choices made>
Remaining: <what is left>
Tried: <failed approaches worth remembering>
Skill: </skill-name>
[/gstack-context]
```

**Use this for:** Long coding sessions, multi-step refactors, generated artifacts.

**Reusable insight:** Checkpoints make agent sessions recoverable, reviewable, and resumable.

**Sample:**

```bash
if [ "$(gstack-config get checkpoint_mode 2>/dev/null)" = "continuous" ]; then
  git add path/to/intentional-file.md
  git commit -m "WIP: record feature review checkpoint

[gstack-context]
Skill: /sample-feature-review
Decisions: rollout must be feature-flagged
Remaining: verify migration rollback and add QA route list
Tried: direct launch rejected as too risky
[/gstack-context]"
fi
```

------

## **13. Repo Ownership Component**

**Reusable purpose:** Decide how proactive the agent should be when it notices unrelated issues.

**Context:** Use this when a skill might notice adjacent issues outside the user's explicit request. It calibrates autonomy based on whether the repository is solo-owned or collaborative, so the agent can proactively help in personal repos while avoiding surprise edits in shared workspaces.

**Modes:**

```text
solo:
  You own everything. Investigate and offer fixes proactively.

collaborative / unknown:
  Flag the issue, but do not fix without permission.
```

**Use this for:** Enterprise repos, shared team projects, open-source work.

**Reusable insight:** Agent autonomy should depend on repo ownership context.

**Sample:**

```text
Repo mode:
- solo: You may propose and, when safe, fix adjacent obvious issues.
- collaborative: Flag adjacent issues, but ask before editing outside the stated
  scope.
- unknown: Behave like collaborative until the user says otherwise.
```

------

## **14. Search Before Building Component**

**Reusable purpose:** Prevent reinventing existing solutions.

**Context:** Use this before designing custom mechanisms, selecting tools, or approving architecture that may already exist in the repo or ecosystem. It gives the skill a disciplined pattern: search local code and proven approaches first, then use first-principles reasoning only when there is a concrete reason to diverge.

**Three-layer model:**

```text
Layer 1: Tried-and-true approach
Layer 2: Current landscape / popular alternatives
Layer 3: First-principles reasoning
```

**Reusable behavior:**

```text
- Search before building unfamiliar systems.
- Prefer proven approaches unless first principles contradict them.
- If a first-principles insight contradicts convention, log it as a eureka.
```

**Use this for:** New features, platform decisions, vendor/tool selection, architecture.

**Reusable insight:** The component balances external precedent with internal reasoning.

**Sample:**

```text
Before designing a custom job scheduler:
1. Search the repo for existing schedulers, queues, cron helpers, and worker APIs.
2. Check ecosystem-standard options already installed.
3. Use first principles only after explaining why built-ins do not fit.
4. Log any surprising "use the simple built-in" or "custom is justified" insight.
```

------

## **15. Completion Status Protocol Component**

**Reusable purpose:** Standardize how a skill ends.

**Context:** Use this at the end of every non-trivial skill so the result is not vague. It is especially important when the work partially succeeded, found risks, or needs more context: the user should see whether the skill is done, done with concerns, blocked, or waiting on specific information.

**Statuses:**

```text
DONE
DONE_WITH_CONCERNS
BLOCKED
NEEDS_CONTEXT
```

**Escalation format:**

```text
STATUS:
REASON:
ATTEMPTED:
RECOMMENDATION:
```

**Use this for:** Any workflow that can partially complete.

**Reusable insight:** Good agent workflows should never end vaguely. They should end with a status and evidence.

------

# **Plan Review Specific Components**

These are reusable, but they are more specific to strategy, architecture, or plan review workflows.

**Sample:**

```text
STATUS: DONE_WITH_CONCERNS
REASON: Plan review completed, but rollout monitoring is underspecified.
EVIDENCE: Read design doc, git diff, CI config, and deployment docs.
ATTEMPTED: Mapped data flow, failure modes, tests, and rollout.
RECOMMENDATION: Add canary metrics before implementation starts.
```
