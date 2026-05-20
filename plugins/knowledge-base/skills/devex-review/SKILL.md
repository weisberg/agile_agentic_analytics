---
name: devex-review
version: 0.1.0
description: >-
  Review the knowledge-base plugin onboarding, README flow, local testing path, vaultli help, sample vault, and contributor experience.
triggers:
  - "kb devex review"
  - "review kb onboarding"
  - "fresh clone kb test"
  - "make kb easier"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: true
---

# Devex Review

## Contract

- Review measures fresh-user path and produces concrete doc or issue fixes.
- Missing prerequisites and confusing paths are treated as product bugs.
- The quickstart ends with a visible success signal.

## Workflow

- Use `/plugin-manager:plugin-devex-review` for `knowledge-base`.
- Run or verify `claude --plugin-dir`, `vaultli --help`, plugin health, and sample vault commands.
- Fix README flow and path confusion.
- Create follow-up issues for larger blockers.

## Output Format

- KB DEVEX REVIEW
- Fresh-user path, timing, findings, docs changed, issues filed.

## Anti-Patterns

- Reviewing docs without trying commands.
- Leaving users without a first successful command.
