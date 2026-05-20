---
name: source-router
version: 0.1.0
description: >-
  Route multiple KB source scopes such as personal vaults, team vaults, plugin samples, raw archives, and external connectors.
triggers:
  - "kb source routing"
  - "which kb source"
  - "multi-source kb"
  - "source scopes"
tools:
  - read
  - write
  - vaultli
mutating: true
writes_pages: true
---

# Source Router

## Contract

- Every source has scope, trust level, privacy boundary, and retrieval priority.
- Answers cite which source scope produced each fact.

## Workflow

- Inventory available vaults/connectors and scopes.
- Classify each as personal, team, org, public, sample, or external.
- Apply trust and privacy rules before retrieval or write.
- Use federated search when multiple vaults are relevant.
- Record source-scope decisions in outputs.

## Output Format

- SOURCE ROUTING
- Scopes used, trust, privacy, priority, excluded sources.

## Anti-Patterns

- Mixing personal and team facts without labels.
- Searching every vault when scope is obvious.
