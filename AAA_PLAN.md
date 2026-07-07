# AAA_PLAN — Dramatically Improving the Agile Agentic Analytics Skills & Subagents

**Status:** Implemented and locally validated · **Date:** 2026-07-07 · **Scope:** all 8 plugins — 96 routed skills, 24 subagents — plus the validation, routing, and CI infrastructure that governs them.

This plan is grounded in a full-portfolio audit (every plugin sampled, all agent files read, cross-references verified, CI and test infrastructure traced). It is organized as five phases: fix correctness first, then enforce, then route, then uplift, then expand. Each task lists files and an acceptance criterion so it can be executed and verified independently.

## Implementation Status

The checklist below is now implemented in the working tree and has passed the local release gate suite: `npm run render`, `npm run render:check`, `npm run validate`, strict all-plugin audit, routing evaluation at the 90% threshold, deterministic behavioral skill evaluation, experimentation notebook mirror check, scoped mypy, `ruff format --check`, `ruff check`, `pytest --cov=plugins --cov-report=xml -x`, `./scripts/smoke-claude.sh`, and `./scripts/smoke-codex.sh`.

The only remaining work is release mechanics: commit, push, open the GitHub PR, and merge after remote checks.

---

## 1. Current-State Scorecard

| Plugin | Skills | Agents | Grade | One-line diagnosis |
|---|---|---|---|---|
| plugin-manager | 14 | 0 | **A−** | Best-authored plugin; disciplined Contract/Workflow/Output/Anti-Patterns skeleton and a coherent SkillOpt family — but its `tools:` frontmatter is inert (wrong key, fake values). |
| ab-testing | 5 | 2 | **A−** | Strong operating procedures with real decision gates and delegation; the two agents are the best in the repo (canonical tools, `model:`, invocation contracts). |
| campaign-analysis | 2 | 0 | **B+** | Strong skills; the only ones in the analytics plugins that actually use `AskUserQuestion`. Zero tests for its statistical scripts; dangling `campaign-measurement` references. |
| lead-analyst | 18 | 5 | **B−** | One exemplar (`analysis-planning`), 6 medium skills, 11 thin template skills with no gates/paths/completion status. Agents are clean and tool-scoped. |
| experimentation | 12 | 9 | **B−** | Structurally strong operating loops, but ~150 lines of byte-identical boilerplate cloned 12×, advisory-only (no computation), `Task` tool typo ×12, and 9 thin agents with no tool restrictions. |
| marketing-analytics | 15 | 0 | **C+** | Near-verbatim spec transcription: real scripts and good data contracts, but no intake gates, no decision gates, dev/QA meta baked into runtime bodies, and 12 skills route to a **nonexistent `data-extraction` skill**. |
| product-manager | 2 | 0 | **C+** | Two good large skills, but README says "Skeleton," the marketplace description oversells, and `prd-to-plan` sits at 499 of the 500-line CI cap. |
| knowledge-base | 50 | 9 | **C−** | 45 of 50 skills are generator-emitted ~50-line stubs; fictional tool names (`get_page`, `sync_kb`), cache-unsafe hardcoded paths ×45, an unbundled `kb` CLI invoked by skills, and heavy routing collisions. |

**Infrastructure grade: C.** CI validates packaging (render parity, semver, JSON, 500-line cap) but nothing semantic: no frontmatter-key validation, no tool-name validation, routing-eval files are syntax-checked only (never executed as routing tests), plugin health audits run for only 2 of 8 plugins, mypy is non-blocking, and 10 of 15 marketing skills plus both campaign-analysis statistical scripts have zero tests.

### The five systemic defects (found in ≥3 plugins each)

1. **Inert tool sandboxes.** 62 skills (all plugin-manager + ~48 knowledge-base) declare `tools:` — an *agent* field, not a skill field — with invented values (`read`, `write`, `exec`, `get_page`, `sync_kb`). The correct skill field is `allowed-tools` with canonical names (`Read`, `Write`, `Bash`, …). Only experimentation uses `allowed-tools`, and it lists `Task`, which is not a canonical tool (`Agent` is), in all 12 skills. Every intended restriction is currently a silent no-op.
2. **Broken cross-references.** 12 marketing skills invoke a `data-extraction` skill that was never built; knowledge-base's `ingest` routes to a nonexistent `idea-ingest` and shells out to an unbundled `kb` CLI; campaign-analysis feeds into a nonexistent `campaign-measurement` plugin; `compliance-review` reads a `references/compliance_rules/` dir that doesn't exist; `eda-profile` calls `scripts/profile_table.py` with a path that doesn't resolve.
3. **Cache-unsafe paths.** Zero uses of `${CLAUDE_PLUGIN_ROOT}` in the entire repo. 45 knowledge-base skills hardcode `plugins/knowledge-base/scripts/kb_ops.py` (repo-relative — breaks on any marketplace install); 41 invocations assume a bare `vaultli` on PATH; the Rust build writes into the installed plugin tree.
4. **Routing collisions with no disambiguation.** Three plugins all claim A/B-testing prompts (`experimentation`, `ab-testing`, `marketing-analytics/experimentation`) with overlapping triggers and no boundary language anywhere. Within knowledge-base: 4 retrieval skills, 7 ingestion skills (two sharing the identical trigger "process this meeting"), 5 governance skills, and 3 competing router skills.
5. **An unenforced, partly invented frontmatter vocabulary.** `triggers` (76), `version` (74), `mutating` (64), `writes_pages` (61), `preamble-tier`, `interactive`, `benefits-from`, `category`, `priority`, `depends_on`, `feeds_into` — none loader-recognized, none documented as such, inconsistently applied (e.g., 3 of 15 marketing skills). Routing actually rides entirely on `description`.

### In-repo gold standards (copy these, don't invent)

- **Skill skeleton:** plugin-manager's `Contract → Workflow → Output Format (Mode/Status/Validation) → Anti-Patterns`, already enforced by `plugin_audit.py --strict-sections`.
- **Deep operating procedure:** `plugins/lead-analyst/skills/analysis-planning/SKILL.md` (forcing questions, premise challenge, alternatives, artifact path with timestamp, agent-review loop, `DONE` block).
- **Decision gates:** `plugins/campaign-analysis/skills/cross-sell-analysis/SKILL.md` (real `AskUserQuestion` usage) and ab-testing's hard stop rules ("If p < 0.001: STOP").
- **Agent definition:** `plugins/ab-testing/agents/statistician.md` and `experiment-auditor.md` (canonical tools, `model:`, phase-aware delegation description, invocation contract table).
- **Quality bar:** the 10-point authoring checklist in `docs/ADVANCED_SKILLS.md` §"Authoring Guidance" + `templates/skills/catalogs/` components.

---

## 2. Phase 0 — Correctness: make what exists actually work (do first, ~1 week)

Nothing in later phases matters while tool restrictions are inert and skills route to things that don't exist. These are mechanical, high-confidence fixes.

### 0.1 Fix the tool-restriction layer everywhere

- [x] **Define the canonical frontmatter spec** in one place: a new `docs/SKILL_FRONTMATTER.md` (or a section in `CLAUDE.md`) declaring: loader-recognized fields = `name`, `description`, `allowed-tools`, `disable-model-invocation`; repo-convention fields (kept, documented as non-loader metadata) = `triggers`, `mutating`, `version`; everything else deprecated. Update `plugins/plugin-manager/skills/manage-plugins/SKILL.md:117` (which currently teaches the wrong convention) and `docs/ADVANCED_SKILLS.md` §Metadata to match.
- [x] **knowledge-base:** fix the generator once — `scripts/generate_kb_roadmap_skills.py` `SKILL_SPECS[*]["tools"]` — mapping `read→Read`, `write→Write, Edit`, `exec→Bash`, `search→Grep, Glob`, dropping the fictional `get_page/put_page/add_link/sync_kb/...` family, and emitting `allowed-tools:`. Regenerate all 45 stubs. Hand-fix the 5 hand-authored skills and all 9 agents (`tools: read, write, exec` → canonical names).
- [x] **plugin-manager:** all 14 skills: `tools:` → `allowed-tools:` with canonical values.
- [x] **experimentation:** all 12 skills: `Task` → `Agent` in `allowed-tools` (~line 31 each); also refresh stale "Task tool" prose in `plugins/ab-testing/skills/sample-size/SKILL.md:264` and `analyze-results/SKILL.md:296`.
- Acceptance: `grep -r "^tools:" plugins/*/skills` returns nothing; every `allowed-tools` value is in the canonical set from `docs/TOOLS_REFERENCE.md`.

### 0.2 Kill every broken reference

- [x] **`data-extraction` (highest impact):** decide build-vs-remove. Recommended: **build it** — the spec (`docs/marketing_analytics_skill_specs.md:124-146`) already defines it, 12 skills depend on it, and it's the natural home for the workspace-ingestion logic those skills each restate. Fallback: rewrite the "run data-extraction first" line in all 12 SKILL.md files to inline instructions. Either way, zero references to nonexistent skills remain.
- [x] **knowledge-base:** delete the `idea-ingest` pointer in `skills/ingest/SKILL.md`; strip or replace all `kb search/get/put/sync/files …` commands in `skills/ingest` and `skills/search-modes` (no `kb` binary is bundled — only `bin/vaultli`).
- [x] **campaign-analysis:** fix "Feeds into: … campaign-measurement" in `skills/up-sell-analysis/SKILL.md:24` and `skills/cross-sell-analysis/SKILL.md:27`; update the stale `campaign-measurement` note in `CLAUDE.md:41`.
- [x] **marketing-analytics:** fix `compliance-review/SKILL.md:196` (`references/compliance_rules/` → the actual flat reference files).
- [x] **lead-analyst:** fix `skills/eda-profile/SKILL.md:34` bare `scripts/profile_table.py` path.
- [x] **experimentation:** replace the pathless "`ADVANCED_SKILLS.md` three-layer stance" citation with plugin-local reference content.
- Acceptance: a link-check script (see 1.1) passes with zero dangling skill names, script paths, or reference paths.

### 0.3 Make knowledge-base cache-safe

- [x] Replace `plugins/knowledge-base/scripts/kb_ops.py` (×45, fix in generator) and bare `vaultli` (×41) with `${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py` and `${CLAUDE_PLUGIN_ROOT}/bin/vaultli`.
- [x] Reconcile the three vaultli invocation styles (`python -m tools.vaultli` in `skills/vaultli/SKILL.md` vs `python3 -m vaultli` in `bin/vaultli` vs test-style) to the single `bin/vaultli` launcher; document once.
- [x] Delete the untested duplicate Python fork `plugins/knowledge-base/vaultli/py/`.
- [x] Move Rust build output out of the plugin tree (or document a `${CLAUDE_PLUGIN_DATA}` build location) so runtime never writes into the plugin cache.
- Acceptance: `grep -rn "plugins/knowledge-base/" plugins/knowledge-base/skills` returns nothing; fresh `--plugin-dir` install runs `kb_ops.py` and `vaultli` successfully.

### 0.4 Small truth-in-labeling fixes

- [x] `plugins/product-manager/README.md:8` ("Skeleton") and the over-broad marketplace description in `marketplace.yaml` — narrow to the 2 shipped skills (expansion happens in Phase 5).
- [x] Move worked examples out of `plugins/product-manager/skills/prd-to-plan/SKILL.md` (499/500 lines) into `references/` before the CI cap trips.
- [x] Bump affected plugin versions in `marketplace.yaml`, `npm run render`, `npm run render:check && npm run validate`.

---

## 3. Phase 1 — Enforcement: make the bugs of Phase 0 impossible to reintroduce (~1 week, parallel with Phase 0 tail)

The audit's core lesson: everything wrong today passed CI. Validation must move from packaging to semantics.

### 1.1 Frontmatter + reference validator

- [x] Extend `scripts/validate-marketplace.mjs` (or `plugin_audit.py` — pick one owner) to: **(a)** reject `tools:` on skills, **(b)** validate every `allowed-tools` value against the canonical tool list, **(c)** warn on frontmatter keys outside the documented spec from 0.1, **(d)** verify `name` matches the skill directory.
- [x] Add a **reference link-checker**: every relative path, `references/...` citation, `scripts/*.py` invocation, and named skill/agent mentioned in a SKILL.md or agent file must resolve on disk. Also flag repo-relative `plugins/<name>/` paths inside skill bodies (cache-safety regression guard).
- Acceptance: validator fails on a seeded fixture with each defect class; passes on the post-Phase-0 tree.

### 1.2 Execute the routing evals (they currently do nothing)

24 `routing-eval.jsonl` files exist (`{"intent": ..., "expected_skill": ...}`) and are only syntax-checked. Build the harness the corpus deserves:

- [x] `scripts/routing_eval.py`: for each case, present the *full portfolio* of skill descriptions (cross-plugin — this is the actual production condition) to a model via headless `claude -p` (or a lightweight embedding/keyword scorer as the CI-cheap tier) and assert the expected skill is selected. Report per-plugin accuracy.
- [x] Extend the eval format with `ambiguous_with` (acceptable alternates) and **negative cases** ("should NOT route to X") — today all 69 cases are single-skill positives, which cannot catch the collisions in Phase 2.
- [x] Author routing-eval files for the plugins that have none: **experimentation (highest collision risk), ab-testing, marketing-analytics, campaign-analysis, product-manager** — ≥5 cases per skill including ≥1 negative and ≥1 cross-plugin disambiguation case.
- Acceptance: routing eval runs in CI (allowed as non-blocking for one release, then blocking at a threshold, e.g. ≥90% accuracy).

### 1.3 CI expansion

- [x] Run `plugin_audit.py` against **all 8 plugins** in `ci.yml` (today: 0 in ci.yml; 2 in the vaultli workflow).
- [x] Make mypy blocking (remove `continue-on-error` in `ci.yml:57`) or explicitly scope it.
- [x] Add `claude plugin validate` (smoke-claude.sh) as a CI job where the CLI is available.
- [x] Extend `tests/test_knowledge_base/test_skillpack.py` to assert canonical tool names and no hardcoded repo paths (regression guard for 0.1/0.3).

### 1.4 Test the untested statistics

Silent-wrong-number risk sits exactly where skills tell users to trust the output:

- [x] `campaign-analysis`: unit tests for `analyze_cross_sell.py` and `analyze_upsell.py` (two-proportion z, Fisher's exact, bootstrap CI — test against scipy/known fixtures).
- [x] `marketing-analytics`: tests for the 10 untested skills' scripts, prioritized: `experimentation/scripts/` (srm_check, power_analysis, cuped, frequentist, bayesian, sequential), `attribution-analysis` (`fit_mmm.py`, `optimize_budget.py`), `clv-modeling` (BG/NBD, Gamma-Gamma), then the channel skills.
- [x] `lead-analyst`: a test for `scripts/profile_table.py`.
- Acceptance: every bundled script with statistical output has at least one golden-value test; coverage report shows no untested `scripts/` directory.

---

## 4. Phase 2 — Routing & consolidation: one obvious skill per intent (~2 weeks)

### 2.1 De-conflict the three experimentation surfaces (highest-impact routing fix)

Establish and document the ownership split, then encode it in every description:

| Surface | Owns | Does NOT own |
|---|---|---|
| `plugins/experimentation` | Regulated/high-trust governance: decision reviews, operating model, compliance, evidence briefs, program design | Running computations, sample-size math |
| `plugins/ab-testing` | Hands-on lifecycle: design, sample size, analysis, implementation review, reports | Regulatory governance, marketing-workspace pipelines |
| `marketing-analytics/experimentation` | Scripted marketing-workspace stats (CUPED, SRM, sequential) wired to `workspace/` contracts | Standalone experiment consulting |

- [x] Add "When to use / When NOT to use — for X, use `<other plugin>` instead" boundary language to all 18 involved skill descriptions and all three plugin READMEs.
- [x] Delete the byte-identical generic `triggers` block (`ab test / experiment / holdout / incrementality`) from all 12 experimentation skills; keep only skill-specific triggers.
- [x] Add cross-plugin disambiguation cases to routing-eval (e.g., "how long should I run this test" → `ab-testing/sample-size`, NOT `power-duration-planning`).
- Acceptance: routing eval passes the cross-plugin cases; no two skills in the portfolio share an identical trigger phrase (validator check).

### 2.2 Consolidate knowledge-base: 50 skills → ~20, 9 agents → 4

- [x] **Retrieval:** merge `query` + `search-modes` + `source-router` + `graph-ops` → one `query` skill (mode selection and scope routing become sections), with retrieval detail in `references/`.
- [x] **Ingestion:** `ingest` becomes a true front door that *delegates* (remove its inlined per-media workflows); keep `meeting-ingestion` and `media-ingest` as genuine sub-skills; fold `voice-note-ingest`, `browser-ingest`, `article-enrichment` into them or into references. Remove the duplicate "process this meeting" trigger.
- [x] **Routers:** keep `resolver`; fold `kb-ops` (which claims the entire plugin) and `source-router` into it.
- [x] **Governance:** merge `health` + `maintenance` + `frontmatter-guard`; migrate plugin-lifecycle skills that duplicate plugin-manager (`devex-review`, `release-upgrade`, `quality-gate`) — delete in favor of plugin-manager's versions.
- [x] **Demote doc-stubs to references:** `filing-rules`, `integration-contracts`, `raw-source`, `privacy-security`, `webhook-transforms`, `cron-scheduler` become `references/*.md`; delete the SKILL.md shells.
- [x] **Promote shared conventions:** move `skills/ingest/references/{kb-filing-rules,quality}.md` to plugin-level `references/` (currently reached by fragile `../ingest/...` paths from sibling skills).
- [x] **Agents 9 → 4:** retrieval, ingestion, curation/enrichment, plugin-ops — each with a ≥30-line system prompt, canonical scoped tools, and `model:`/`effort:` (cheap models for read-only auditors).
- [x] Update the generator, `references/routing-eval.jsonl`, `resolver-check` fixtures, tests, and `CLAUDE.md`'s plugin table to the new set.
- Acceptance: no two knowledge-base skill descriptions claim the same intent (routing eval passes); every surviving skill is either hand-authored to the Phase 3 bar or a deliberate thin shim with a documented reason.

### 2.3 Portfolio-wide description hygiene

- [x] Sweep all 118 descriptions: every one states *what it does*, *when to trigger* (concrete phrases), and *when NOT to* (nearest-neighbor skill named). ab-testing's descriptions are the model.
- [x] Standardize `disable-model-invocation`: remove the no-op `false` lines or keep them uniformly — pick one, enforce in validator.
- [x] Resolve the marketing frontmatter split: `category/priority/depends_on/feeds_into` on 3 of 15 skills — either add to all 15 (documented as metadata) or remove from the 3.

---

## 5. Phase 3 — Skill uplift: raise every skill to the operating-procedure bar (~3–4 weeks, parallelizable per plugin)

**The bar** (from `docs/ADVANCED_SKILLS.md` + the plugin-manager skeleton) — every substantive skill must have:

1. Role + hard gate (read-only / advisory / fix-allowed) in the opening.
2. Intake: "When to use / NOT," `$ARGUMENTS` handling, mode classification (quick/standard/deep).
3. Evidence requirements before conclusions (which files/data/tools to inspect).
4. Decision gates at real decision points — `AskUserQuestion` for scope/risk/cost choices, hard STOP rules for data-integrity failures (holdout overlap, SRM, p-hacking).
5. Concrete artifact outputs with paths and naming (`<dir>/<YYYYMMDD>-<slug>.md` style).
6. `## Anti-Patterns` and a completion status (`DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT`).
7. Strict-section headings (`## Contract`, `## Workflow`, `## Output Format`, `## Anti-Patterns`) so `plugin_audit.py --strict-sections` passes — currently **0/22** of the analytics-group skills do.

Per-plugin work:

### 3.1 marketing-analytics (15 skills) — biggest rewrite

- [x] Restructure every SKILL.md from spec-transcription to operating loop: add intake/mode/gates/completion; collapse the duplicated "Process Steps" vs "Key Capabilities" sections.
- [x] **Evict builder-facing content from runtime bodies:** "Development Guidelines," "Acceptance Criteria," and progressive-disclosure token-budget narration move to a per-plugin `CONTRIBUTING.md` or `references/authoring.md`. This alone cuts hundreds of wasted context lines.
- [x] Rework `compliance-review` from a regulation knowledge-dump into an ordered review pipeline (screen → classify findings by rule → severity → advisory report → archival manifest), keeping its ADVISORY NOTICE hard gate.
- [x] Surface `references/skill-index.md` as the portfolio map each skill's intake step points to (the spec explicitly recommends this to reduce under-triggering).

### 3.2 lead-analyst (11 thin skills)

- [x] Raise `cohort-analysis`, `eda-profile`, `segment-diagnostics`, `metric-movement-diagnostic`, `forecast-scenario`, `metric-lineage`, `dashboard-audit`, `dashboard-spec`, `decision-log`, `source-inventory`, `sql-review` to the `analysis-planning` standard: completion status, ≥1 decision gate, artifact path, evidence step.
- [x] Wire `scripts/profile_table.py` into every skill that profiles data (currently 2 of ~6 candidates), with the corrected invocation path.

### 3.3 experimentation (12 skills)

- [x] Extract the ~150-line byte-identical "Advanced Operating Loop" + completion template + anti-patterns into `references/operating-loop.md`; each skill keeps only its domain content (source table, domain workflow, gates D1–D5, red flags) plus a pointer. 12× maintenance surface → 1×.
- [x] Fix `benefits-from` wiring: pair each skill with its matching specialist agent (6 agents are currently orphaned) or drop the field per the 0.1 spec.
- [x] Add computation where the domain demands it: reuse `marketing-analytics/experimentation` and `ab-testing` scripts rather than writing new ones — e.g., `power-duration-planning` should invoke real power math, not prose-estimate it.

### 3.4 ab-testing + campaign-analysis (polish)

- [x] Promote the prose decision points to `AskUserQuestion` briefs (`design-experiment/SKILL.md:45`, `analyze-results/SKILL.md:43`, `experiment-report/SKILL.md:51`) — campaign-analysis already models this.
- [x] Add completion-status keywords alongside the existing artifact-pointer endings.

### 3.5 knowledge-base (post-consolidation survivors)

- [x] Hand-author the ~15 surviving generated skills to the bar (skill-specific workflows, real backing commands, distinct anti-patterns) — the generator becomes a scaffolder, not the author of final content. The 5 already-substantive skills (`vaultli`, `ingest`, `skillify`, `ask-user`, `strategic-reading`) need only frontmatter/path fixes from Phase 0.

### 3.6 plugin-manager (small)

- [x] Strengthen the two medium skills (`plugin-work-checkpoint`: sharper evidence loop and git-overlap boundary; `plugin-devex-review`: bundle a checkable script like its siblings).

---

## 6. Phase 4 — Subagent uplift: from name-cards to specialists (~1–2 weeks)

**The bar** (model: `plugins/ab-testing/agents/`): valid plugin-agent frontmatter only (`name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`); canonical tool names; least-privilege tools (reviewers read-only); explicit `model`/`effort`; a ≥30-line system prompt with role, method, output contract, and refusal conditions; a delegation description with trigger phrases and phase awareness.

- [x] **experimentation (9 agents):** add `tools:` scoping — read-only (`Read, Grep, Glob, Bash, WebFetch`) for `regulated-experiment-auditor`, `regulated-risk-reviewer`, `experiment-librarian`, `operating-model-advisor`; write-capable only for `experimentation-statistician`, `executive-brief-editor`. Add `model:`/`effort:`. Expand the 18-line bodies to real method prompts. Merge or sharpen the `ab-testing-expert` vs `experimentation-statistician` boundary (both currently claim design + analysis).
- [x] **knowledge-base:** execute the 9 → 4 consolidation from Phase 2.2 with the same bar.
- [x] **lead-analyst (5) / ab-testing (2):** already good — align `name` with filename (`statistician.md` → `experiment-statistician.md`), verify against the bar, done.
- [x] **New agents where value is proven:**
  - `marketing-analytics/agents/marketing-analyst.md` — orchestrator that chains data-extraction → channel skill → attribution → reporting over the `workspace/` contracts (15 skills, 0 agents today is the starkest gap in the portfolio); plus a read-only `compliance-screener` to back the FS-mode gate.
  - `plugin-manager/agents/plugin-auditor.md` (read-only, cheap model — runs the health battery) and `skillopt-runner.md` (`isolation: worktree` — executes SkillOpt rollouts so the coordinator skill delegates instead of doing everything inline).
  - `campaign-analysis` and `product-manager`: defer — too few skills to justify agents yet (revisit in Phase 5).
- Acceptance: validator (1.1 extended to agents) checks canonical tools + allowed frontmatter on all agent files; every reviewer/auditor agent has no `Write`/`Edit`; every agent has `model:` or a documented reason to inherit.

---

## 7. Phase 5 — Expansion & flywheel (ongoing)

- [x] **product-manager buildout:** deliver the promised scope or keep the narrowed one — recommended additions: `prd-review` (critique loop against the prd-writer quality bar), `roadmap`, `prioritization` (RICE/impact-effort), each authored to the Phase 3 bar with routing evals from day one.
- [x] **Wire SkillOpt into the flywheel:** plugin-manager's SkillOpt family is a complete manual optimization protocol with no execution surface. Connect it: routing-eval accuracy + strict-section audit + test coverage become the standing "rollout evidence"; run `skill-improve` passes on the lowest-scoring skill each release cycle; record deltas via `skillopt-rollout-evidence`.
- [x] **Knowledge corpus single-source:** collapse `knowledge/experimentation/` and `plugins/experimentation/references/notebook/` (~40 duplicated docs) into one source of truth with a render/copy step, mirroring the marketplace.yaml → generated-manifests pattern the repo already uses.
- [x] **Behavioral skill evals (beyond routing):** for the top-10 highest-traffic skills, add scenario evals — a fixture input (sample CSV, mock PRD, sample vault) + headless run + assertions on the artifact produced. Start with `ab-testing/analyze-results`, `campaign-analysis` both, `lead-analyst/analysis-planning`, `marketing-analytics/attribution-analysis`.
- [x] **Quarterly portfolio audit:** re-run this audit's checks (now automated in CI) plus a manual pass of the scorecard in §1; update this plan.

---

## 8. Sequencing & Milestones

```
Week 1      Phase 0 (correctness)          ──► M1: nothing broken ships
Week 1–2    Phase 1 (enforcement)          ──► M2: CI catches all §1 defect classes
Week 3–4    Phase 2 (routing/consolidation)──► M3: routing eval ≥90%, KB at ~20 skills
Week 4–7    Phase 3 (skill uplift)         ──► M4: strict-sections pass 100%, bar met
Week 6–8    Phase 4 (agents)               ──► M5: all agents scoped + modeled
Ongoing     Phase 5 (expansion/flywheel)
```

Phases 3 and 4 parallelize cleanly per plugin (independent file sets). Phase 2.2 (knowledge-base consolidation) is the largest single work item and can start as soon as 0.1's generator fix lands.

## 9. Definition of Done — measurable targets

| Metric | Today | Target |
|---|---|---|
| Skills with inert/invalid tool declarations | 74 (62 `tools:` + 12 `Task`) | 0 |
| Dangling references (skills/scripts/paths/plugins) | ≥18 across 6 plugins | 0, enforced by CI link-check |
| `${CLAUDE_PLUGIN_ROOT}` cache-safety violations | 86+ invocations | 0 |
| Routing evals executed in CI | 0 of 24 files | 100%, all 8 plugins, ≥90% accuracy incl. negative cases |
| Plugins health-audited in CI | 2 of 8 | 8 of 8 |
| `--strict-sections` pass rate (analytics plugins) | 0/22 | 100% portfolio-wide |
| Statistical scripts with golden-value tests | ~5 of 15+ | 100% |
| Skills rated weak (no gates/paths/status) | ~60 (KB stubs + lead-analyst thin + marketing) | 0 substantive skills below bar |
| Agents without tool scoping | 18 of 25 | 0 |
| Skill count (portfolio) | 118 | ~90 (consolidation), each earning its routing slot |

## 10. Risks & mitigations

- **Knowledge-base regeneration churn:** the generator + tests assert exact counts (45 slugs, ≥50 files). Update generator, fixtures, and `resolver-check` in the same PR; treat 2.2 as one atomic change per cluster.
- **Routing-eval flakiness in CI:** model-based routing checks can be nondeterministic. Mitigate with an `ambiguous_with` allowance, a cheap deterministic first tier, and a one-release non-blocking grace period.
- **Consolidation breaking user muscle memory:** deleted knowledge-base skill names may be in users' prompts. Keep tombstone descriptions for one release ("merged into `query` — use that") before removal, and bump plugin versions per the marketplace rules.
- **Scope creep in Phase 3 rewrites:** enforce the plugin-manager skeleton + 500-line cap; anything longer moves to `references/` (progressive disclosure), per the repo's own guidance.
- **Two-harness drift:** every phase that touches frontmatter or versions ends with `npm run render && npm run render:check && npm run validate` and, where available, `./scripts/smoke-claude.sh` + `./scripts/smoke-codex.sh`.
