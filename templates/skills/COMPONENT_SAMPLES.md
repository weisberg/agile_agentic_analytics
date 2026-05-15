# Skill Component Samples

Samples are no longer kept in one large standalone file. Each type-based catalog
under `catalogs/` now embeds the sample directly inside the matching numbered
component section.

Each component section contains:

- a context paragraph explaining where and how to use it
- reusable guidance and authoring intent
- a `Sample` snippet to copy and adapt

Use this file as the sample index.

## Directory Structure

```text
templates/skills/
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

## Sample Catalog Index

| Catalog | Components | Sample focus |
| --- | --- | --- |
| [01-core-runtime.md](catalogs/01-core-runtime.md) | 1-15 | Frontmatter, preflight shell, plan-mode rules, decision briefs, first-run prompts, routing blocks, artifact sync, context recovery, writing style, completeness, checkpoints, repo mode, search-before-building, and completion status. |
| [02-planning-strategy.md](catalogs/02-planning-strategy.md) | 16-25 | Base detection commands, system audit commands, prerequisite offers, mode prompts, premise checks, implementation alternatives, expansion decisions, CEO plan artifacts, spec review loops, and implementation timelines. |
| [03-review-rubrics.md](catalogs/03-review-rubrics.md) | 26-36 | Architecture diagrams, error tables, threat tables, edge-case lists, code quality checks, test plans, performance checks, observability plans, rollout plans, trajectory checks, and UI state maps. |
| [04-output-governance.md](catalogs/04-output-governance.md) | 37-46 | Outside reviewer prompts, cross-model tension notes, final report sections, failure registries, TODO decision prompts, completion summaries, JSON review logs, dashboards, plan-file reports, and next-review prompts. |
| [05-orchestration-evidence.md](catalogs/05-orchestration-evidence.md) | 47-53 | Role contracts, capability budgets, phase pipelines, auto-decision JSON, question preference checks, evidence manifests, and baseline metric records. |
| [06-browser-automation.md](catalogs/06-browser-automation.md) | 54-59 | Browser session contracts, accessibility snapshot refs, prompt-injection boundaries, auth handoff flow, browser-skill frontmatter, and skillification checklists. |
| [07-design-systems.md](catalogs/07-design-systems.md) | 60-66 | Screenshot evidence records, taste-memory JSON, variant board prompts, AI-slop checks, UI state matrices, design promotion steps, and live preview protocols. |
| [08-qa-performance.md](catalogs/08-qa-performance.md) | 67-72 | Route inference records, QA fix-loop notes, test bootstrap plans, health score YAML, performance budget YAML, and canary monitoring plans. |
| [09-review-fix-security-investigation.md](catalogs/09-review-fix-security-investigation.md) | 73-80 | Clean-tree ownership notes, fix classification examples, scope drift reports, specialist review pass lists, security findings, incident playbooks, root-cause writeups, and reassessment notes. |
| [10-release-deploy-docs.md](catalogs/10-release-deploy-docs.md) | 81-87 | Release sequences, test failure triage, version queue reports, changelog entries, deploy discovery notes, deploy monitor gates, and docs sync reports. |
| [11-memory-semantic-retro.md](catalogs/11-memory-semantic-retro.md) | 88-92 | Checkpoint files, learning records, semantic memory policies, semantic search guidance, and weekly retro summaries. |
| [12-safety-utility-setup.md](catalogs/12-safety-utility-setup.md) | 93-101 | Destructive command prompts, freeze boundary notes, guard mode summaries, pair-agent access JSON, benchmark config, PDF config, upgrade prompts, setup wizard flow, and artifact path examples. |

## How to Copy a Sample

1. Choose the catalog that matches the skill type.
2. Jump to the relevant numbered component.
3. Read the context paragraph and reusable guidance.
4. Copy the `Sample` snippet.
5. Replace example names, paths, URLs, commands, and risk gates while preserving the intended context and behavior.

For the full directory overview and quick lookup by skill type, use
[COMPONENTS.md](COMPONENTS.md).
