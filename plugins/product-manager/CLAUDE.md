# Product Manager Plugin — Skill Index

Skills for product management workflows: discovery, prioritization, roadmapping, and turning requirements into executable agentic plans.

## Skills

- **prd-writer** (`name: prd-author`) — Produces Product Requirements Documents, specs, product briefs, one-pagers, and PR/FAQs. Triggers: write a PRD, draft a spec, product doc, one-pager, PR/FAQ, feature brief, critique/level up a PRD. Does not trigger on engineering design docs, RFCs, or ADRs.
- **prd-to-plan** (`name: prd-to-agent-plan`) — Converts a PRD/spec into a structured `PLAN.md` for agentic execution: phases, tasks, dependencies, validation gates, sub-agent assignments, context bundles. Triggers: turn this PRD into a plan, agentic plan, execution plan, task graph, decompose this spec, scrum-master plan.

## Typical Flow

```
idea/brief --[prd-writer]--> PRD.md --[prd-to-plan]--> PLAN.md --> agentic execution
```
