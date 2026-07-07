# product-manager

A Claude Code plugin for turning product ideas into requirements and then into
executable, agent-ready plans. It ships two skills that chain end to end.

## Skills

| Skill | What it does | Triggers on |
|-------|--------------|-------------|
| **prd-writer** | Produces Product Requirements Documents, specs, product briefs, one-pagers, and "Working Backwards" PR/FAQs. Also critiques and levels up an existing PRD. | "write a PRD", "draft a spec", "product doc", "one-pager", "PR/FAQ", "feature brief", "critique this PRD". Does *not* trigger for engineering design docs, RFCs, or ADRs. |
| **prd-to-plan** | Converts a PRD or spec into a structured `PLAN.md` for agentic execution: phases, tasks, dependencies, validation gates, sub-agent assignments, and context bundles. | "turn this PRD into a plan", "agentic plan", "execution plan", "task graph", "decompose this spec", "break this down for Claude Code", "scrum-master plan". |

## How they chain

```
idea / brief --[prd-writer]--> PRD.md --[prd-to-plan]--> PLAN.md --> agentic execution
```

`prd-writer` numbers requirements (`R1`, `R2`, …) and surfaces open questions;
`prd-to-plan` consumes those requirement IDs to build a PRD-to-task crosswalk and
turns leftover open questions into Phase 0 discovery tasks. Each skill can also be
used on its own — `prd-writer` for authoring or reviewing a doc, `prd-to-plan`
against any PRD that already exists.

`prd-to-plan` keeps its worked templates (the `PLAN.md` skeleton, task
specification template, risk register, and antipattern catalog) in
`skills/prd-to-plan/references/examples.md`.

## Local testing

```bash
claude --plugin-dir ./plugins/product-manager
```

Reload after edits with `/reload-plugins`. Validate the manifest, skill
frontmatter, and structure with `claude plugin validate`.
