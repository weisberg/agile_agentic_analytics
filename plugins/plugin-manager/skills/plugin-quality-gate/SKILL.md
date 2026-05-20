---
name: plugin-quality-gate
version: 0.1.0
description: |
  Optional cross-model or second-opinion quality gate for high-impact plugin
  skills before tests and releases cement behavior. Use when reviewing
  strategic, routing, ingestion, release, safety, or skill-generation workflows
  where one model's judgment is not enough. Inspired by GBrain cross-modal
  review and GStack benchmark-models patterns.
triggers:
  - "plugin quality gate"
  - "cross-model review this skill"
  - "benchmark plugin skill"
  - "second opinion on this plugin"
  - "quality gate this skill"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: false
writes_to:
  - .plugin-manager/reviews/
---

# Plugin Quality Gate

## Contract

Use this gate before release for high-impact skills:

- skills that mutate user data, files, git state, or plugin manifests
- skill-generation or skill-harvesting workflows
- release, publish, and upgrade workflows
- routing skills whose mistakes send users down the wrong workflow
- privacy, security, or citation-sensitive workflows

The gate produces a review artifact with:

- task being evaluated
- artifact under review
- model/provider reviewers used, or waiver reason
- score or verdict by dimension
- top requested improvements
- applied fixes or known gaps

## Workflow

1. **Decide whether gate is required**
   - Required for high-impact or release-blocking workflow changes.
   - Optional for docs-only edits.
   - Waive for trivial outputs under 200 tokens or thin wrappers around a
     deterministic command; record the waiver.

2. **Prepare artifact**
   - Usually a `SKILL.md`, release plan, health report, or generated output.
   - Include the task prompt and success criteria.

3. **Run available review**
   - Prefer an existing cross-provider gateway if configured.
   - If no gateway is configured, run a manual second-opinion review and record
     that the automated gate was unavailable.
   - Keep cost bounded: one cycle by default, up to three cycles for major
     releases.

4. **Iterate**
   - Apply concrete improvements.
   - Re-run or re-check when the first verdict found material issues.
   - Do not write tests that lock in behavior until the reviewed behavior is
     good enough.

5. **Store receipt**
   - Save receipts or review notes under `.plugin-manager/reviews/`.
   - Bind the receipt to the reviewed file path and current git SHA.

## Review Dimensions

- Goal fit: does it solve the stated plugin problem?
- Specificity: does it name files, commands, gates, and outputs?
- Safety: does it protect user edits, secrets, and one-way operations?
- Testability: can a future agent verify it?
- Plugin fit: does it belong in this plugin or in a target plugin?

## Output Format

```text
PLUGIN QUALITY GATE
Artifact: <path>
Task: <one-line task>
Gate: passed|failed|waived|inconclusive
Reviewers: <models/providers or manual>
Receipt: .plugin-manager/reviews/<file>.md
Improvements:
- <applied or pending>
Known gaps:
- <gap or none>
```

## Anti-Patterns

- Using only one model's unstructured praise as a gate.
- Running expensive review on trivial edits.
- Ignoring review findings and calling the gate complete.
- Writing tests before the reviewed behavior reaches the quality bar.
- Losing receipts, model names, or waiver rationale.

