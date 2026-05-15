# Planning and Strategy Components

Base-branch detection, pre-review audits, review mode selection, premise challenge, expansion control, and strategy artifacts.

Components: 16-25.

Source: distilled from the gstack `SKILL.md` corpus. Each component includes a context paragraph, reusable description, and compact sample.

## **16. Platform and Base Branch Detection Component**

**Reusable purpose:** Establish the correct comparison base before reviewing a branch.

**Context:** Use this before any diff, branch, PR, or release review where the comparison base determines what is in scope. It prevents the skill from reviewing against the wrong branch by detecting PR metadata, default branch, origin head, or safe fallbacks before interpreting changed files.

**Detection sequence:**

```text
1. Inspect git remote URL.
2. Detect GitHub or GitLab.
3. Try PR/MR target branch.
4. Fall back to repo default branch.
5. Fall back to origin/HEAD.
6. Fall back to main or master.
7. Last fallback: main.
```

**Use this for:** Diff reviews, PR prep, release checks, ship workflows.

**Sample:**

```bash
_REMOTE=$(git remote get-url origin 2>/dev/null || true)
_DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's#refs/remotes/origin/##')
_BASE="${_DEFAULT:-main}"
if command -v gh >/dev/null 2>&1; then
  _PR_BASE=$(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || true)
  [ -n "$_PR_BASE" ] && _BASE="$_PR_BASE"
fi
echo "BASE_BRANCH: $_BASE"
git diff --stat "$_BASE"...HEAD
```

------

## **17. Pre-Review System Audit Component**

**Reusable purpose:** Understand the system before judging the plan.

**Context:** Use this at the start of serious plan, architecture, or code reviews. It gathers the system context that makes the review fair: recent commits, current diff, existing TODOs, hotspots, docs, and prior artifacts, so the agent evaluates the plan against reality rather than just the prose.

**Audit commands:**

```bash
git log --oneline -30
git diff <base> --stat
git stash list
grep -r "TODO\|FIXME\|HACK\|XXX" -l --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=.git . | head -30
git log --since=30.days --name-only --format="" | sort | uniq -c | sort -rn | head -20
```

**Also read:**

```text
- CLAUDE.md
- TODOS.md
- Architecture docs
- Existing design docs
- Prior handoff notes
```

**Use this for:** Any serious codebase review.

**Reusable insight:** Review quality depends on system context, not just the plan text.

**Sample:**

```bash
git status --short
git log --oneline -20
git diff "$BASE_BRANCH"...HEAD --stat
rg -n "TODO|FIXME|HACK|XXX" --glob '!node_modules' --glob '!vendor' .
find docs -maxdepth 3 -type f 2>/dev/null | sort | head -50
```

------

## **18. Prerequisite Skill Offer Component**

**Reusable purpose:** Detect when a downstream skill needs an upstream artifact.

**Context:** Use this when a skill would produce a better result if an upstream artifact existed, such as a design doc, plan, or architecture sketch. It should offer the prerequisite skill as an optional step, then continue if declined, so composition improves quality without blocking the user's current path.

**Pattern:**

```text
If no design doc exists:
  Offer /office-hours before proceeding.
If user accepts:
  Run prerequisite skill inline.
  Re-check for design doc.
If user declines:
  Proceed with standard review.
```

**Use this for:** Skill chains where one skill improves another.



**Reusable examples:**

```text
- No design doc before CEO review → offer office-hours
- No architecture plan before eng review → offer plan-eng-review
- No QA surface before visual review → offer qa
```

**Reusable insight:** Skills can compose. They should offer upstream context generation without forcing it.

**Sample:**

```text
No design doc was found for this feature.

Recommendation: Run `/office-hours` first to produce a short design doc, then
resume this review against the artifact.

Options:
A) Run prerequisite skill now (recommended)
B) Continue review with current context
C) Stop and let me provide a design doc
```

------

## **19. Mode Selection Component**

**Reusable purpose:** Let the user choose the review posture.

**Context:** Use this when the same review workflow can validly take different postures, such as expanding scope, holding scope, or reducing scope. It belongs near the start of strategy and planning skills because the user's chosen mode changes what counts as a finding, a recommendation, or an overreach.

**Modes:**

```text
SCOPE EXPANSION:
  Push ambition up. Propose 10x version. Every addition requires opt-in.

SELECTIVE EXPANSION:
  Hold baseline scope but surface optional upgrades. User cherry-picks.

HOLD SCOPE:
  Do not expand or reduce. Make the existing plan bulletproof.

SCOPE REDUCTION:
  Strip to the minimum viable version.
```

**Use this for:** Product reviews, analytics roadmap reviews, AI-agent design reviews, operating model plans.

**Reusable insight:** Review posture should be explicit. Otherwise the agent silently mixes “dream bigger,” “cut scope,” and “make it safe.”

**Sample:**

```text
Choose review mode:

A) Scope expansion: find the highest-leverage bigger version.
B) Selective expansion: keep the plan, but offer optional upgrades.
C) Hold scope: make the existing plan safe and complete. (recommended)
D) Scope reduction: cut to the smallest useful version.
```

------

## **20. Premise Challenge Component**

**Reusable purpose:** Challenge whether the plan is solving the right problem.

**Context:** Use this before evaluating implementation details for a product, analytics, or platform plan. It asks whether the plan is solving the right problem, for the right user, with the right success measure, which prevents a polished implementation plan from hiding a weak or misdirected premise.

**Reusable questions:**

```text
- Is this the right problem?
- What user or business outcome matters?
- Is this solving a proxy problem?
- What happens if we do nothing?
- What existing code or process already solves part of this?
- What is the 12-month ideal state?
```

**Use this for:** Strategy plans, analytics initiatives, product ideas, AI agent designs.

**Reusable insight:** Before reviewing implementation, review the premise.

**Sample:**

```text
Premise check:
- User problem: Admins cannot tell why imports failed.
- Current plan: Add retry controls.
- Challenge: Retry controls may not solve the real problem if failures are caused
  by invalid source data.
- Better question: Should the first version explain failures before it adds retry?
```

------

## **21. Implementation Alternatives Component**

**Reusable purpose:** Force the plan to consider multiple paths.

**Context:** Use this when a plan presents only one implementation path or when a decision has meaningful architectural alternatives. It forces the skill to lay out at least two options with effort, risk, reuse, pros, and cons before recommending a path, so the user can choose with real tradeoff visibility.

**Required approaches:**

```text
- Minimal viable approach
- Ideal architecture approach
- Optional third path if meaningfully distinct
```

**Reusable template:**

```text
APPROACH A: <Name>
  Summary:
  Effort:
  Risk:
  Pros:
  Cons:
  Reuses:

APPROACH B: <Name>
  ...
```

**Rules:**

```text
- At least 2 approaches required.
- Do not proceed without user approval.
- Recommend one, but user decides.
```

**Use this for:** Architecture, analytics pipelines, product changes, refactors.

**Reusable insight:** A plan with only one approach is usually under-reviewed.

**Sample:**

```text
APPROACH A: Minimal diagnostic banner
Effort: 1 day
Risk: Low
Reuses: existing import status API
Tradeoff: explains failures but does not add self-serve repair

APPROACH B: Full import recovery center
Effort: 1 week
Risk: Medium
Reuses: status API plus new retry endpoint
Tradeoff: more complete, but larger operational surface

Recommendation: A first, then B if support volume remains high.
```

------

## **22. Expansion / Cherry-Pick Ceremony Component**

**Reusable purpose:** Make scope expansion explicit and user-controlled.

**Context:** Use this when the agent discovers valuable scope beyond the original plan but should not silently add it. It is useful in product, design, and engineering reviews because it lets the agent be ambitious while giving the user explicit control to accept, defer, or reject each expansion.

**Options per expansion:**

```text
A) Add to this plan's scope
B) Defer to TODOS.md
C) Skip
```

**Reusable behavior:**

```text
- Present one expansion at a time.
- Explain felt user impact.
- Include effort and risk.
- Accepted items become scope.
- Deferred items become TODO candidates.
- Skipped items go to NOT in scope.
```

**Use this for:** Product polish, UX improvements, platformization opportunities, operating model improvements.

**Reusable insight:** The agent can dream big, but scope belongs to the user.

**Sample:**

```text
Expansion candidate: Add a downloadable error CSV for failed imports.
User impact: Admins can fix rows offline instead of guessing.
Effort: 2-4 hours.
Risk: Low if exported fields avoid secrets.

A) Add to this plan
B) Defer to TODOS.md (recommended)
C) Skip and mark out of scope
```

------

## **23. CEO Plan Artifact Component**

**Reusable purpose:** Persist strategic decisions from the review.

**Context:** Use this when strategic plan decisions need to survive beyond the chat transcript. It creates a durable artifact for vision, scope decisions, accepted work, and deferred work, which later reviews, implementation sessions, or release steps can read as the source of truth.

**Reusable artifact path:**

```text
~/.gstack/projects/<slug>/ceo-plans/<date>-<feature-slug>.md
```

**Reusable structure:**

```markdown
---
status: ACTIVE
---

# CEO Plan: <Feature Name>

Generated by /plan-ceo-review on <date>
Branch: <branch> | Mode: <mode>
Repo: <owner/repo>

## Vision

## Scope Decisions

## Accepted Scope

## Deferred to TODOS.md
```

**Use this for:** Any review where decisions need to survive beyond the chat.

**Reusable insight:** Strategy decisions should become artifacts, not evaporate into transcript history.

**Sample:**

```markdown
---
status: ACTIVE
skill: plan-ceo-review
created: 2026-05-09
branch: feature/import-diagnostics
mode: HOLD_SCOPE
---

# CEO Plan: Import Diagnostics

## Vision

Users can understand and recover from import failures without contacting support.

## Accepted Scope

- Failure reason summary.
- Link to source rows when available.
- Admin-facing recovery guidance.

## Not in Scope

- Automated data repair.
- Bulk retry orchestration.
```

------

## **24. Spec Review Loop Component**

**Reusable purpose:** Run an adversarial review on the artifact before presenting it.

**Context:** Use this when a generated spec, PRD, architecture doc, or skill instruction file is itself an important deliverable. The loop treats docs like code: write, review, patch, and re-review until the artifact is coherent enough to guide implementation or preserve open concerns explicitly.

**Reusable loop:**

```text
1. Write document.
2. Dispatch independent reviewer.
3. Review on:
   - Completeness
   - Consistency
   - Clarity
   - Scope
   - Feasibility
4. Fix issues.
5. Repeat up to 3 iterations.
6. Persist unresolved concerns if convergence fails.
```

**Use this for:** PRDs, architecture docs, analytics specs, AI-agent instructions, strategy documents.

**Reusable insight:** The skill treats generated docs as code: write, review, patch, re-review.

**Sample:**

```text
Spec review loop:
1. Write `docs/designs/import-diagnostics.md`.
2. Review for contradictions, missing states, and unowned decisions.
3. Patch the spec.
4. Re-review up to 3 iterations.
5. If unresolved concerns remain, add `## Open Questions` with owner and next step.
```

------

## **25. Temporal Interrogation Component**

**Reusable purpose:** Anticipate implementation decisions before they become blockers.

**Context:** Use this in implementation plans where time sequencing exposes hidden dependencies and unresolved choices. By walking through the first hours of work, the skill can identify decisions that must be made before coding, phases that can run in parallel, and risks likely to appear late.

**Reusable frame:**

```text
HOUR 1: Foundations
HOUR 2-3: Core logic
HOUR 4-5: Integration
HOUR 6+: Polish, tests, launch
```

**Extra reusable idea:**

```text
Show both human-time and AI-assisted time.
Example: human 6 hours / CC+gstack 30-60 minutes.
```

**Use this for:** Implementation plans, analytics pipelines, launch checklists.

**Reusable insight:** Implementation speed changes, but decision dependencies do not.

------

# **Review Rubric Components**

These are highly reusable as separate skills or subskills.

**Sample:**

```text
Implementation timeline:
- Hour 1: find import status owner and add failure reason field.
- Hours 2-3: render admin UI states and empty/error copy.
- Hour 4: add regression tests and fixture data.
- Hour 5: browser QA and docs update.

Risky decision before coding: whether failure reasons are stored or derived.
```
