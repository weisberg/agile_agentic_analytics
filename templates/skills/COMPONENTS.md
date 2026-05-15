# Skill Component Catalogs

This directory contains the gstack-style reusable skill component library. The
catalog was split into smaller type-based files so skill authors can open only the
patterns relevant to the skill they are building.

## Directory Structure

```text
templates/skills/
  COMPONENTS.md
  COMPONENT_SAMPLES.md
  catalogs/
    01-core-runtime.md
    02-planning-strategy.md
    03-review-rubrics.md
    04-output-governance.md
    05-orchestration-evidence.md
    06-browser-automation.md
    07-design-systems.md
    08-qa-performance.md
    09-review-fix-security-investigation.md
    10-release-deploy-docs.md
    11-memory-semantic-retro.md
    12-safety-utility-setup.md
```

Each file in `catalogs/` has the same shape:

```text
# <Catalog Type>
Short description
Components: <range>
## **<N>. <Component Name>**
Context paragraph
Reusable component description
Sample snippet
```

## Catalog Index

| Catalog | Components | Contains |
| --- | --- | --- |
| [01-core-runtime.md](catalogs/01-core-runtime.md) | 1-15 | Metadata, preambles, plan-mode safety, AskUserQuestion briefs, first-run prompts, routing, artifact sync, context recovery, voice, completeness, checkpoints, repo ownership, search-before-building, and completion status. |
| [02-planning-strategy.md](catalogs/02-planning-strategy.md) | 16-25 | Base branch detection, pre-review system audits, prerequisite skill offers, review modes, premise challenge, alternatives, expansion control, CEO plan artifacts, spec review loops, and temporal interrogation. |
| [03-review-rubrics.md](catalogs/03-review-rubrics.md) | 26-36 | Architecture, error/rescue maps, security and threat models, data and interaction edges, code quality, tests, performance, observability, deployment, long-term trajectory, and design/UX review rubrics. |
| [04-output-governance.md](catalogs/04-output-governance.md) | 37-46 | Outside voice reviews, cross-model tension handling, required output sections, failure mode registries, TODO proposals, completion summaries, review logs, readiness dashboards, plan-file reports, and review chaining. |
| [05-orchestration-evidence.md](catalogs/05-orchestration-evidence.md) | 47-53 | Specialist role contracts, tool capability budgets, skill orchestration, auto-decision audit trails, question preference tuning, evidence packs, and baseline/trend records. |
| [06-browser-automation.md](catalogs/06-browser-automation.md) | 54-59 | Persistent browser daemons, snapshot refs, untrusted content boundaries, auth handoff, cookie bridges, browser-skill host binding, and prototype-to-permanent skillification. |
| [07-design-systems.md](catalogs/07-design-systems.md) | 60-66 | Live design evidence, taste memory, variant boards, AI-slop detection, UI state matrices, design artifact promotion, and live HTML preview. |
| [08-qa-performance.md](catalogs/08-qa-performance.md) | 67-72 | QA route inference, browser QA fix loops, test bootstrap, weighted health scores, performance budgets, and canary monitoring. |
| [09-review-fix-security-investigation.md](catalogs/09-review-fix-security-investigation.md) | 73-80 | Clean working tree rules, atomic commits, fix-first classification, scope drift audits, specialist review armies, security confidence gates, incident response playbooks, root-cause investigation, and three-strike reassessment. |
| [10-release-deploy-docs.md](catalogs/10-release-deploy-docs.md) | 81-87 | Release pipelines, test failure ownership triage, version queues, changelog voice, deployment discovery, deploy polling, rollback gates, and documentation diff sync. |
| [11-memory-semantic-retro.md](catalogs/11-memory-semantic-retro.md) | 88-92 | Context checkpoints, learning registries, semantic memory trust policies, semantic search guidance, and retrospective analytics. |
| [12-safety-utility-setup.md](catalogs/12-safety-utility-setup.md) | 93-101 | Destructive-command preflights, edit-boundary freeze, guard mode, scoped pair-agent access, cross-model benchmarks, browser-rendered PDFs, inline upgrades, setup wizards, and artifact path taxonomy. |

## How to Use This Directory

1. Open this index when you need to choose the right type-based catalog.
2. Open the matching catalog under `catalogs/`.
3. Read the numbered component section for the context paragraph, reusable pattern, design intent, and sample snippet.
4. Adapt the sample to the target skill's tools, risk level, paths, and user gates.

## Quick Lookup by Skill Type

| Building a skill for... | Start with | Then add |
| --- | --- | --- |
| Any long-running skill | [01-core-runtime.md](catalogs/01-core-runtime.md) | [05-orchestration-evidence.md](catalogs/05-orchestration-evidence.md) |
| Product or implementation planning | [02-planning-strategy.md](catalogs/02-planning-strategy.md) | [03-review-rubrics.md](catalogs/03-review-rubrics.md), [04-output-governance.md](catalogs/04-output-governance.md) |
| Code review or architecture review | [03-review-rubrics.md](catalogs/03-review-rubrics.md) | [09-review-fix-security-investigation.md](catalogs/09-review-fix-security-investigation.md) |
| Browser work or scraping | [06-browser-automation.md](catalogs/06-browser-automation.md) | [05-orchestration-evidence.md](catalogs/05-orchestration-evidence.md) |
| UI, visual design, or HTML preview | [07-design-systems.md](catalogs/07-design-systems.md) | [06-browser-automation.md](catalogs/06-browser-automation.md), [08-qa-performance.md](catalogs/08-qa-performance.md) |
| QA or performance testing | [08-qa-performance.md](catalogs/08-qa-performance.md) | [06-browser-automation.md](catalogs/06-browser-automation.md) |
| Shipping, deploys, or release notes | [10-release-deploy-docs.md](catalogs/10-release-deploy-docs.md) | [04-output-governance.md](catalogs/04-output-governance.md), [09-review-fix-security-investigation.md](catalogs/09-review-fix-security-investigation.md) |
| Persistent memory or retros | [11-memory-semantic-retro.md](catalogs/11-memory-semantic-retro.md) | [01-core-runtime.md](catalogs/01-core-runtime.md) |
| Guardrails, setup, or utility workflows | [12-safety-utility-setup.md](catalogs/12-safety-utility-setup.md) | [01-core-runtime.md](catalogs/01-core-runtime.md) |

## Source Note

These catalogs distill advanced features and style choices from the gstack
`SKILL.md` files. The split is type-based, but the components are intentionally
composable: most real skills should combine the core runtime catalog with one or
two domain catalogs.
