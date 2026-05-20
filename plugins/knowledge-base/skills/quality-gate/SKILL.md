---
name: quality-gate
version: 0.1.0
description: >-
  Run or record quality gates for high-impact KB skills using cross-model review, receipts, cost guardrails, and waiver notes.
triggers:
  - "kb quality gate"
  - "cross-model kb review"
  - "review this skill"
  - "benchmark kb skill"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: true
---

# Quality Gate

## Contract

- High-impact KB skills get review before tests cement behavior.
- Receipts or waiver rationale are recorded.
- Cost and model/provider choices are explicit.

## Workflow

- Classify whether the change is high-impact.
- Prepare artifact, task, dimensions, and representative input.
- Use `/plugin-manager:plugin-quality-gate` or available cross-provider review.
- Apply improvements and record receipt or waiver.
- Then write or update tests.

## Output Format

- KB QUALITY GATE
- Artifact, reviewers, verdict, receipt, improvements, known gaps.

## Anti-Patterns

- Treating one flattering review as evidence.
- Running expensive gates on trivial edits.
