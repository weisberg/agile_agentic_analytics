# Agile Agentic Analytics — Skill Index

## Repository Layout

Tracked top-level paths in this repository (run `git ls-files | awk -F/ '{print $1}' | sort -u` to verify):

| Path | Contents |
|------|----------|
| `CLAUDE.md` | This operating index. |
| `AGENTS.md` | Agent-facing pointer to this index. |
| `README.md` | Public-facing repo overview. |
| `LICENSE` | Repo license. |
| `PLUGINS_AND_SKILLS.md` | Catalog of plugins and their skills. |
| `PLUGIN_ARCHITECTURE.md` | Architectural notes for plugin design across the repo. |
| `PLUGIN_SKILLS.md` | Long-form notes on skill behavior per plugin. |
| `pyproject.toml`, `pytest.ini`, `requirements.txt`, `requirements-dev.txt` | Python project and test configuration. |
| `.claude-plugin/` | Repo-level marketplace manifest (`marketplace.json`). |
| `.github/` | GitHub workflows and repo metadata. |
| `docs/` | Authoritative reference docs (see Documentation Map below). |
| `docs/CREATE_PLUGINS.md`, `docs/PLUGINS_REFERENCE.md`, `docs/CREATE_CUSTOM_SUBAGENTS.md`, `docs/HOOKS_REFERENCE.md`, `docs/TOOLS_REFERENCE.md`, `docs/ADVANCED_SKILLS.md`, `docs/marketing_analytics_skill_specs.md` | Plugin, agent, hook, tool, and marketing-analytics reference material. |
| `templates/skills/` | Reusable skill component pattern library. |
| `templates/skills/catalogs/01-core-runtime.md` … `12-safety-utility-setup.md` | Type-based component catalogs (12 files, components 1-101). |
| `plugins/` | Distributable plugins. One subdirectory per plugin. |
| `plugins/ab-testing/` | A/B testing plugin (`agents/`, `skills/{analyze-results, design-experiment, experiment-report, review-experiment, sample-size}`). |
| `plugins/experimentation/` | Experimentation plugin (`agents/`, `references/`, `skills/{advanced-experiment-analysis, compliance-trust-review, early-signal-monitoring, email-incrementality, executive-evidence-brief, experiment-decision-review, experiment-operating-model, measurement-integration, null-results-knowledge-base, personalization-governance, power-duration-planning, safe-experiment-design}`). |
| `plugins/marketing-analytics/` | Marketing analytics portfolio (`shared/{definitions, schemas, utils}`, `skills/{attribution-analysis, audience-segmentation, clv-modeling, competitive-intel, compliance-review, crm-lead-scoring, email-analytics, experimentation, funnel-analysis, paid-media, reporting, seo-content, social-analytics, voc-analytics, web-analytics}`). |
| `plugins/product-manager/` | Product management plugin (`agents/`, `commands/`, `skills/{prd-to-plan, prd-writer}`). |
| `plugins/campaign-analysis/` | Campaign analysis plugin (`skills/{up-sell-analysis, cross-sell-analysis}`). |
| `knowledge/experimentation/` | Knowledge base material for the experimentation plugin. |
| `examples/` | Worked example workflows (`clv_segmentation_workflow.md`, `funnel_optimization.md`, `quick_start.md`, `generate_sample_data.py`, `data/`). |
| `tests/` | Pytest suite (`conftest.py`, `fixtures/`, and per-skill test packages: `test_audience_segmentation`, `test_email_analytics`, `test_funnel_analysis`, `test_integration`, `test_voc_analytics`, `test_web_analytics`). |

Note: `.claude/` (local Claude settings) and `plugins/campaign-measurement/` exist locally but are not tracked in git. Top-level `agents/`, `bin/`, `hooks/`, `scripts/`, `skills/` are also untracked — git does not preserve empty directories, so these only appear once they contain files.

## Documentation Map

This repository includes official Anthropic Claude Code documentation, a marketing analytics product specification, and advanced skill-design notes in `docs/`. Treat these files as source material when creating, changing, validating, or extending plugins and skills. The notes below summarize what each document is for and when to consult it.

| Document | Use It For | Key Sections |
|----------|------------|--------------|
| `docs/CREATE_PLUGINS.md` | Practical plugin creation workflow. Use this before creating a new plugin, converting standalone `.claude/` config into a plugin, or testing local plugin changes. | Plugin vs standalone config; quickstart; plugin structure overview; adding skills, LSP, monitors, and settings; local testing with `--plugin-dir`; migration from `.claude/`. |
| `docs/PLUGINS_REFERENCE.md` | Deep technical plugin reference. Use this when editing manifests, component paths, plugin-provided agents/hooks/MCP/LSP/monitors, user config, cache-sensitive file access, install scopes, CLI behavior, debugging, or versioning. | Component reference; manifest schema; path behavior rules; `userConfig`; `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`; plugin cache and path traversal limits; CLI commands; validation/debugging; version management. |
| `docs/CREATE_CUSTOM_SUBAGENTS.md` | Subagent design and operation. Use this when adding or changing plugin agents in `plugins/<plugin>/agents/`, deciding whether an agent should be project/user/plugin-scoped, restricting tools, choosing models, or designing automatic delegation behavior. | Built-in agents; `/agents` workflow; scopes and precedence; frontmatter fields; tool restrictions; hooks for subagents; foreground/background execution; context management; example reviewer/debugger/data-scientist agents. |
| `docs/HOOKS_REFERENCE.md` | Hook lifecycle and schema reference. Use this before adding plugin hooks, skill/agent hooks, or project hooks, and whenever a hook needs to block, approve, transform, notify, run async work, call MCP tools, or use prompt/agent-based evaluation. | Lifecycle; hook locations; matcher patterns; handler fields; stdin JSON input; exit-code and JSON output; all event schemas; prompt hooks; agent hooks; async hooks; security best practices; debugging hooks. |
| `docs/TOOLS_REFERENCE.md` | Claude Code tool names and behavior. Use this when writing tool allow/deny rules, subagent `tools` or `disallowedTools`, hook matchers, permission settings, or tool-aware skill instructions. | Tool name table; permission requirements; Bash cwd/env behavior; LSP behavior; Monitor tool; PowerShell behavior; checking available tools. |
| `docs/marketing_analytics_skill_specs.md` | Product and implementation specification for the marketing analytics portfolio. Use this when adding, revising, or validating marketing analytics skills, scripts, references, schemas, financial-services behavior, or cross-skill workflows. | SKILL.md format guidance; 15-skill portfolio; priority tiers; portfolio architecture; workspace directory structure; per-skill objectives, trigger descriptions, functional scope, data contracts, scripts, cross-skill integration, financial-services considerations, development guidelines, acceptance criteria; appendices for data contracts and interconnection matrix. |
| `docs/ADVANCED_SKILLS.md` | Advanced design-pattern reference distilled from the gstack `SKILL.md` corpus. Use this when a skill needs more than basic instructions: routing, evidence gates, AskUserQuestion decisions, review chaining, browser QA, design review, release workflows, memory, safety hooks, or distinctive voice/style. | Core thesis; metadata conventions; generated preamble patterns; AskUserQuestion pattern; voice and prose style; completeness principle; evidence-first workflows; planning/design/browser/review/release/memory/safety patterns; skill-by-skill advanced feature map; authoring checklist. |
| `docs/THINKING_IN_BETS.md` | Canonical decision-quality framework for regulated marketing and experimentation. Use whenever a skill designs, runs, reads out, or governs an experiment or campaign that influences customers in a high-trust environment. Defines the pre-registration schema, the readout schema (results + decision_quality + resulting_check + next_bet), and the (good/bad outcome × good/bad process) 2×2 that keeps "lucky wins" from being treated as license to ship. Referenced by experimentation, ab-testing, campaign-analysis, and marketing-analytics skills. | Core thesis ("good decisions ≠ good outcomes"); the seven principles with operational behavior (embrace uncertainty, avoid resulting, truth-seeking, pre-register, accountability, pre-mortem + backcasting, long-term learning); pre-registration template; readout template; 2×2; when the framework is non-optional. |
| `templates/skills/COMPONENTS.md` | Index for reusable gstack-style skill and plugin workflow components. Use this before creating or refactoring a skill so the workflow has explicit routing, decision gates, evidence, outputs, safety, and persistence. | Directory structure; 12 type-based catalogs; component ranges 1-101; quick lookup by skill type; links to catalog files under `templates/skills/catalogs/`. |
| `templates/skills/COMPONENT_SAMPLES.md` | Index for concrete snippets that implement the reusable components. Use this after choosing component types from `COMPONENTS.md` to find inline samples for frontmatter, decision briefs, review tables, evidence manifests, browser flows, release gates, and safety prompts. | Sample catalog index; links to catalog files; each numbered component section embeds its own `Sample`; copy/adapt workflow. |

### Documentation Usage Rules

- Start with `docs/CREATE_PLUGINS.md` for workflow, then confirm exact schema/path/version behavior in `docs/PLUGINS_REFERENCE.md`.
- Use `docs/CREATE_CUSTOM_SUBAGENTS.md` before changing anything in `agents/`, especially plugin-shipped agents because they support fewer frontmatter fields than project/user agents.
- Use `docs/HOOKS_REFERENCE.md` before adding hooks or changing hook matchers. Hook event names and matcher semantics are case-sensitive and event-specific.
- Use `docs/TOOLS_REFERENCE.md` whenever a config references tool names. Tool names in permissions, subagent frontmatter, and hook matchers must match Claude Code's canonical tool names.
- Use `docs/marketing_analytics_skill_specs.md` as the product requirements document for the `marketing-analytics` plugin. It defines what each skill should do, what files it should read/write, and how skills compose.
- Use `docs/ADVANCED_SKILLS.md` for advanced skill behavior and style choices before inventing new workflow machinery. It is the narrative companion to the reusable component catalogs in `templates/skills/`.
- Use `docs/THINKING_IN_BETS.md` whenever a skill designs, runs, reads out, or governs an experiment or campaign in a regulated, high-trust workspace. It owns the pre-registration and readout schemas and the "avoid resulting" discipline; experimentation, ab-testing, campaign-analysis, and marketing-analytics skills reference it rather than duplicating the framework.
- Use `templates/skills/COMPONENTS.md` and `templates/skills/COMPONENT_SAMPLES.md` when authoring skill behavior. The docs in `docs/` define Claude Code packaging and schema rules; the templates define reusable skill workflow patterns.
- Keep `CLAUDE.md` as the compact operating index. Do not paste entire docs into it; link the relevant doc and summarize the current repo convention.

## Docs Directory Guide

Use the Markdown files in `docs/` as the authoritative reference set for plugin packaging, Claude Code behavior, and the marketing analytics skill portfolio.

### Read Order By Task

| Task | Read First | Then Read | Why |
|------|------------|-----------|-----|
| Create a new plugin | `docs/CREATE_PLUGINS.md` | `docs/PLUGINS_REFERENCE.md`, then `templates/skills/COMPONENTS.md` | Start with workflow, confirm manifest/path rules, then choose reusable skill behavior patterns. |
| Convert standalone `.claude/` config into a plugin | `docs/CREATE_PLUGINS.md` | `docs/PLUGINS_REFERENCE.md` | The create guide covers migration shape; the reference covers cache, path, manifest, and versioning details. |
| Add or revise a skill | `docs/marketing_analytics_skill_specs.md` for marketing skills, otherwise `docs/ADVANCED_SKILLS.md` | `templates/skills/COMPONENTS.md` and `templates/skills/COMPONENT_SAMPLES.md` | Product specs define scope; advanced docs and templates define workflow quality. |
| Add a plugin subagent | `docs/CREATE_CUSTOM_SUBAGENTS.md` | `docs/TOOLS_REFERENCE.md`, `docs/PLUGINS_REFERENCE.md` | Subagent docs define frontmatter and delegation behavior; tools and plugin docs define allowed tool names and plugin packaging limits. |
| Add hooks | `docs/HOOKS_REFERENCE.md` | `docs/TOOLS_REFERENCE.md`, `docs/PLUGINS_REFERENCE.md` | Hook docs define event schemas and decisions; tools and plugin docs prevent bad matcher/action names and path mistakes. |
| Add MCP, LSP, monitors, settings, or `bin/` helpers | `docs/PLUGINS_REFERENCE.md` | `docs/TOOLS_REFERENCE.md` when tool names or permissions are involved | Plugin reference owns component schemas and path behavior. |
| Validate allowed tools or permissions | `docs/TOOLS_REFERENCE.md` | `docs/CREATE_CUSTOM_SUBAGENTS.md` for agents, `docs/HOOKS_REFERENCE.md` for hooks | Tool names must be canonical in skills, agents, hooks, and permissions. |
| Build the marketing analytics plugin portfolio | `docs/marketing_analytics_skill_specs.md` | `docs/ADVANCED_SKILLS.md`, `templates/skills/COMPONENTS.md` | The product spec defines the 15-skill system; the advanced skill docs define execution quality and reusable workflow machinery. |

### File Roles

| File | Role In This Repo |
|------|-------------------|
| `docs/CREATE_PLUGINS.md` | Practical "how do I make a plugin?" guide. Use for first-pass structure, local testing, adding skills/agents/hooks/MCP/LSP/monitors/settings, and standalone-to-plugin migration. |
| `docs/PLUGINS_REFERENCE.md` | Deep schema and runtime reference. Use when exact manifest fields, path rules, cache behavior, install scopes, CLI commands, `userConfig`, `${CLAUDE_PLUGIN_ROOT}`, or `${CLAUDE_PLUGIN_DATA}` matter. |
| `docs/CREATE_CUSTOM_SUBAGENTS.md` | Subagent guide. Use for agent frontmatter, delegation descriptions, scoped tools, model/effort choices, foreground/background behavior, context management, and examples. |
| `docs/HOOKS_REFERENCE.md` | Hook reference. Use for lifecycle events, matcher syntax, command/http/mcp/prompt/agent hooks, stdin JSON, exit codes, async behavior, and blocking/approval decisions. |
| `docs/TOOLS_REFERENCE.md` | Tool and permission reference. Use for canonical tool names, permission requirements, Bash behavior, LSP behavior, Monitor behavior, and tool availability. |
| `docs/marketing_analytics_skill_specs.md` | Product requirements for this repository's marketing analytics plugin family. Use for skill objectives, trigger phrases, data contracts, cross-skill dependencies, output paths, financial-services mode, and acceptance criteria. |
| `docs/ADVANCED_SKILLS.md` | Advanced skill-design reference. Use for gstack-style skill architecture, voice, evidence gates, decision briefs, planning/review/design/browser/QA/release/memory/safety patterns, and authoring checklists. |

### Pairing Rules

- Pair `docs/CREATE_PLUGINS.md` with `docs/PLUGINS_REFERENCE.md` for any plugin work: the first gives the workflow, the second gives the exact rules.
- Pair `docs/CREATE_CUSTOM_SUBAGENTS.md` with `docs/TOOLS_REFERENCE.md` for agent work: subagents are only reliable when tool restrictions use canonical names.
- Pair `docs/HOOKS_REFERENCE.md` with `docs/TOOLS_REFERENCE.md` for hook work: hook matchers and tool names are both strict.
- Pair `docs/marketing_analytics_skill_specs.md` with `templates/skills/catalogs/` when implementing a marketing analytics skill: the spec defines what the skill must do, the catalogs define reusable execution patterns.
- Pair `docs/ADVANCED_SKILLS.md` with `templates/skills/COMPONENTS.md` when designing new skill workflows: `ADVANCED_SKILLS.md` explains the style and philosophy, while the component catalogs provide reusable pieces and samples.

## Skill And Plugin Component Templates

The reusable skill architecture lives under `templates/skills/`. Treat these files as the local pattern library for creating or improving skills inside plugins.

### Directory

| Path | Purpose |
|------|---------|
| `templates/skills/COMPONENTS.md` | Main index for the component catalog. Start here to choose the right type-based catalog. |
| `templates/skills/COMPONENT_SAMPLES.md` | Sample-focused index. Use it when you already know which component type you need and want copy-pasteable snippets. |
| `templates/skills/catalogs/*.md` | The actual type-based catalogs. Each numbered component section contains context, reusable guidance, and an embedded sample. |

### Catalogs

| Catalog | Components | Use It For |
|---------|------------|------------|
| `01-core-runtime.md` | 1-15 | Skill metadata, runtime preambles, plan-mode safety, decision briefs, first-run prompts, routing, artifact sync, context recovery, voice, completeness, checkpoints, repo ownership, search-before-building, and completion status. |
| `02-planning-strategy.md` | 16-25 | Planning workflows, base branch detection, system audits, prerequisite offers, review modes, premise challenge, alternatives, expansion control, strategy artifacts, spec review loops, and implementation timelines. |
| `03-review-rubrics.md` | 26-36 | Architecture, errors, security, data edges, code quality, tests, performance, observability, deployment, long-term trajectory, and UX rubrics. |
| `04-output-governance.md` | 37-46 | Outside voices, cross-model tensions, required outputs, failure registries, TODO proposals, completion summaries, review logs, dashboards, plan-file reports, and review chaining. |
| `05-orchestration-evidence.md` | 47-53 | Specialist role contracts, tool capability budgets, multi-skill orchestration, auto-decision audit trails, question tuning, evidence packs, and baseline/trend records. |
| `06-browser-automation.md` | 54-59 | Browser daemon workflows, snapshot refs, untrusted content boundaries, auth handoff, cookie bridges, browser-skill host binding, and skillification. |
| `07-design-systems.md` | 60-66 | Live design evidence, taste memory, variant boards, AI-slop detection, UI state matrices, design artifact promotion, and live HTML preview. |
| `08-qa-performance.md` | 67-72 | Route inference, browser QA fix loops, test bootstrap, health scoring, performance budgets, and canary monitoring. |
| `09-review-fix-security-investigation.md` | 73-80 | Clean working trees, atomic commits, fix-first classification, scope drift, specialist review, security confidence gates, incident response, root-cause investigation, and three-strike reassessment. |
| `10-release-deploy-docs.md` | 81-87 | Release pipelines, test failure ownership, version queues, changelog voice, deployment discovery, rollback gates, and documentation sync. |
| `11-memory-semantic-retro.md` | 88-92 | Context checkpoints, learning registries, semantic memory trust, semantic search guidance, and retrospective analytics. |
| `12-safety-utility-setup.md` | 93-101 | Destructive-command preflights, edit boundaries, guard mode, scoped pair-agent access, cross-model benchmarks, browser-rendered PDFs, inline upgrades, setup wizards, and artifact path taxonomy. |

### Authoring Workflow

- For plugin packaging, manifests, component paths, hook schemas, agent frontmatter, and Claude Code behavior, use the official docs in `docs/`.
- For the skill's actual operating behavior, choose reusable components from `templates/skills/catalogs/`.
- Start most skills with `01-core-runtime.md`; then add the domain catalog that matches the skill type.
- Use `05-orchestration-evidence.md` when a plugin skill coordinates multiple phases, delegates to other skills, records decisions, or needs auditable evidence.
- Use `06-browser-automation.md`, `07-design-systems.md`, and `08-qa-performance.md` for skills that inspect rendered pages, run QA, generate previews, or verify visual behavior.
- Use `09-review-fix-security-investigation.md` and `10-release-deploy-docs.md` for review, fix, security, ship, deploy, and documentation workflows.
- Use `11-memory-semantic-retro.md` and `12-safety-utility-setup.md` for persistent memory, retrospectives, setup flows, and safety guardrails.
- Copy samples only as starting points. Preserve or adapt each component's context paragraph so the sample still explains where and how it should be used, then adapt tool names, file paths, artifact paths, decision gates, and allowed actions to the target plugin and skill.
- Do not paste whole catalogs into a skill. Compose the smallest set of components that gives the skill clear routing, evidence, user control, verification, and completion status.

## Plugin Authoring Rules

### Structure

- Each distributable plugin lives under `plugins/<plugin-name>/`.
- Use `.claude-plugin/plugin.json` for the plugin manifest. If a manifest exists, `name` is the only required field, but this repository should include `description`, `version`, `author`, `license`, and useful `keywords`.
- Only `plugin.json` belongs inside `.claude-plugin/`. Put components at the plugin root: `skills/`, `commands/`, `agents/`, `hooks/`, `monitors/`, `bin/`, `.mcp.json`, `.lsp.json`, `settings.json`, `output-styles/`, and `themes/`.
- Prefer `skills/<name>/SKILL.md` for new capabilities. `commands/` is supported for flat Markdown skills, but `skills/` is the recommended layout.
- Skills need YAML frontmatter with a useful `description`, followed by clear Markdown instructions. Supporting `scripts/`, `references/`, and assets may live alongside the skill.

### Manifest And Paths

- Manifest component path fields include `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `monitors`, `outputStyles`, `themes`, `userConfig`, `channels`, and `dependencies`.
- Any path in `plugin.json` must be relative to the plugin root and start with `./`.
- For `skills`, `commands`, `agents`, `outputStyles`, `themes`, and `monitors`, specifying a custom path replaces the default location. To keep the default and add another location, include both in an array, e.g. `"skills": ["./skills/", "./extras/"]`.
- For hooks, MCP servers, and LSP servers, configs may be declared inline in `plugin.json` or loaded from files such as `hooks/hooks.json`, `.mcp.json`, and `.lsp.json`.
- Avoid duplicating runtime component definitions between marketplace entries and `plugin.json`; keep plugin-owned structure in the plugin manifest unless intentionally using documented marketplace override behavior.

### Components

- Agents live in `agents/*.md`. Plugin agents support frontmatter such as `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, and `isolation`. The only valid `isolation` value is `worktree`; plugin-shipped agents do not support `hooks`, `mcpServers`, or `permissionMode`.
- Hooks live in `hooks/hooks.json` or inline in `plugin.json`. Supported hook action types include `command`, `http`, `mcp_tool`, `prompt`, and `agent`. Use correct event casing such as `PostToolUse`.
- MCP servers live in `.mcp.json` or inline under `mcpServers`. Plugin MCP servers start when the plugin is enabled and should use `${CLAUDE_PLUGIN_ROOT}` for bundled files.
- LSP servers live in `.lsp.json` or inline under `lspServers`. LSP plugins configure connection to language servers; users must install the actual language server binary separately.
- Monitors live in `monitors/monitors.json` or inline under `monitors`. Each monitor needs `name`, `command`, and `description`; optional `when` can be `always` or `on-skill-invoke:<skill-name>`.
- `bin/` executables are added to the Bash tool's `PATH` while the plugin is enabled.
- Plugin `settings.json` currently supports only `agent` and `subagentStatusLine`. Do not put arbitrary domain defaults there; put them in skill instructions, references, `userConfig`, or runtime code that explicitly reads them.

### User Config, State, And File Access

- Use `userConfig` in `plugin.json` for values Claude Code should prompt users for when enabling a plugin. Use `sensitive: true` for secrets; sensitive values go to secure storage rather than normal settings.
- `userConfig` values are available as `${user_config.KEY}` in MCP/LSP configs, hooks, and monitors. They are also exported to subprocesses as `CLAUDE_PLUGIN_OPTION_<KEY>`.
- Use `${CLAUDE_PLUGIN_ROOT}` for files bundled with the installed plugin. This path changes when the plugin updates.
- Use `${CLAUDE_PLUGIN_DATA}` for persistent plugin state such as caches, generated files, virtual environments, or installed dependencies.
- Marketplace-installed plugins are copied into Claude Code's plugin cache, not run directly from this repository. Do not rely on `../` paths outside the plugin root; external files will not be copied into the cache. If external access is unavoidable, use symlinks inside the plugin directory and test after install.

### Testing, Debugging, And Versioning

- Test local plugin changes with `claude --plugin-dir ./plugins/<plugin-name>` and reload with `/reload-plugins`.
- Use `claude --debug` to inspect plugin loading, manifest errors, skill/agent/hook registration, and MCP startup.
- Use `claude plugin validate` or `/plugin validate` to check `plugin.json`, skill/agent/command frontmatter, and hook config syntax/schema.
- Useful plugin CLI commands include `claude plugin install`, `uninstall`, `enable`, `disable`, `update`, `list`, `prune`, and `tag`.
- Install scopes are `user`, `project`, `local`, and `managed`. Project scope writes enabled plugins into `.claude/settings.json`; local scope writes to gitignored local settings.
- Version resolution prefers `plugin.json` `version`, then marketplace entry `version`, then git commit SHA. If `version` is set, users only receive updates when it is bumped. Omit explicit versions for fast-moving internal plugins that should update on every commit.

## Plugins

### ab-testing

A focused A/B testing toolkit with five skills for experiment lifecycle management.

| Skill | Description |
|-------|-------------|
| **design-experiment** | Design a rigorous A/B experiment with hypothesis, metrics, guardrails, and a full experiment plan. |
| **sample-size** | Calculate required sample size and experiment duration for an A/B test. |
| **analyze-results** | Analyze A/B test results with proper statistical methods — significance, confidence intervals, effect sizes. |
| **review-experiment** | Review experiment implementation code for common A/B testing pitfalls — assignment bugs, logging gaps, bucketing leaks. |
| **experiment-report** | Generate a structured, stakeholder-ready experiment report from A/B test results. |

### campaign-analysis

Campaign performance analysis toolkit for measurement, diagnostics, optimization, and stakeholder reporting. Targets existing-customer and acquisition campaigns alike.

| Skill | Trigger Phrases | Description |
|-------|----------------|-------------|
| **up-sell-analysis** | up-sell analysis, expansion campaign results, wallet share lift, AUM lift, deposit growth from campaign, existing customer campaign, in-book campaign, did the campaign move balances, treated vs holdout for existing customers | Measure a campaign's impact on existing clients or account owners. Reports reach, CTR, and change in a value metric (sales, balances, AUM). Runs holdout-vs-treated statistical testing (Welch's t + Mann-Whitney + bootstrap 95% CI) when a holdout is available; otherwise reports pre/post descriptive lift and is explicit about the lack of causal attribution. No conversion-rate metric (audience is already a customer). |
| **cross-sell-analysis** | cross-sell analysis, cross-sell campaign, product attach rate, account open rate, new product adoption from campaign, second product campaign, add-a-product campaign, checking-to-savings campaign, credit card cross-sell, did the campaign drive new account opens, attach campaign | Measure a campaign promoting a NEW product to existing customers. Reports reach, CTR, conversion rate (account open rate), funded balance / value per eligible customer; runs two-proportion z + Fisher's exact + bootstrap CI on conversion lift and Welch's t + Mann-Whitney on value per eligible when a holdout is provided. Enforces eligibility (excludes prior holders), pre-commits the attribution window, and surfaces cannibalization risk. |

### marketing-analytics

A comprehensive 15-skill marketing analytics portfolio. Skills are composable and interconnect through shared data contracts and filesystem-based state management.

#### P0 — Foundational

| Skill | Trigger Phrases | Description |
|-------|----------------|-------------|
| **attribution-analysis** | attribution, ROAS optimization, channel contribution, marketing mix model, MMM, media mix, budget allocation, budget optimization, incrementality, adstock, saturation curves, diminishing returns, multi-touch attribution, MTA, Shapley value, marketing ROI | Bayesian marketing mix modeling, multi-touch attribution, and incrementality measurement. Depends on data-extraction and paid-media. Feeds into reporting, paid-media, experimentation. |
| **experimentation** | A/B test, experiment, hypothesis test, statistical significance, p-value, confidence interval, CUPED, variance reduction, power analysis, sample size, MDE, sequential test, early stopping, Bayesian AB test, split test, holdout test, control group, incrementality test, causal inference, uplift modeling | Statistical experiment design, CUPED variance reduction, sequential testing, and causal analysis. Depends on data-extraction, audience-segmentation. Feeds into attribution-analysis, funnel-analysis, email-analytics, reporting. |
| **paid-media** | paid media, ad performance, Google Ads, Meta Ads, Facebook Ads, LinkedIn Ads, TikTok Ads, DV360, SEM, PPC, ROAS, CPA, CPM, CPC, CTR, ad spend, budget pacing, creative fatigue, quality score, search terms, negative keywords, bid strategy, campaign optimization | Cross-platform ad performance aggregation, anomaly detection, and creative optimization. Depends on data-extraction. Feeds into attribution-analysis, reporting, funnel-analysis. |
| **reporting** | dashboard, report, executive summary, performance summary, weekly report, monthly report, data visualization, chart, graph, KPI dashboard, marketing scorecard, insight generation, report automation, stakeholder update, board deck | Automated executive dashboards, cross-skill synthesis, and natural language insight generation. Consumes outputs from all other skills. In FS mode, routes through compliance-review. |
| **compliance-review** | compliance review, regulatory check, SEC compliance, FINRA compliance, FCA compliance, marketing compliance, disclosure check, disclaimer, performance presentation, testimonial compliance, fair and balanced, risk disclosure, GIPS, investment advertisement, regulatory filing, archival | Automated regulatory content screening for SEC, FINRA, and FCA marketing compliance. Mandatory gate for all customer-facing content in financial services workspaces. |

#### P1 — Strategic / Tactical

| Skill | Trigger Phrases | Description |
|-------|----------------|-------------|
| **clv-modeling** | CLV, LTV, customer lifetime value, customer value prediction, lifetime revenue, CLV:CAC ratio, BG/NBD, Gamma-Gamma, RFM summary, purchase frequency prediction, churn probability, customer retention modeling, high-value customer identification | Probabilistic CLV prediction using BG/NBD and Gamma-Gamma models. Depends on data-extraction. Feeds into audience-segmentation, paid-media, email-analytics, reporting. |
| **audience-segmentation** | segmentation, customer segments, cohort analysis, RFM analysis, behavioral clustering, K-Means, DBSCAN, customer personas, segment profiles, retention curves, cohort retention, segment migration, customer tiers, at-risk segment, audience definition | Automated RFM scoring, behavioral clustering, and cohort retention analysis. Depends on data-extraction, clv-modeling. Feeds into experimentation, email-analytics, paid-media, reporting. |
| **funnel-analysis** | funnel, conversion funnel, drop-off, conversion rate, conversion optimization, CRO, bottleneck, checkout flow, signup flow, onboarding funnel, abandonment, cart abandonment, form abandonment, user flow, funnel comparison | Multi-step funnel tracking, bottleneck identification, and revenue impact estimation. Depends on data-extraction, web-analytics. Feeds into experimentation, reporting, paid-media. |
| **email-analytics** | email analytics, email performance, open rate, click rate, deliverability, bounce rate, unsubscribe rate, lifecycle email, drip campaign, email automation, send-time optimization, subject line testing, SPF, DKIM, DMARC, email blocklist, inbox placement | Deliverability monitoring, engagement analysis, lifecycle flow optimization, and send-time intelligence. Depends on data-extraction, audience-segmentation, experimentation. Feeds into reporting, compliance-review. |
| **web-analytics** | web analytics, GA4, Google Analytics, site traffic, page views, sessions, bounce rate, engagement rate, user behavior, session flow, site speed, traffic sources, landing page performance, UTM parameters, Mixpanel, Amplitude, user journey, click path | GA4 data extraction, behavioral pattern detection, anomaly detection, and predictive audiences. Depends on data-extraction. Feeds into funnel-analysis, seo-content, paid-media, audience-segmentation, experimentation, reporting. |
| **seo-content** | SEO, search engine optimization, keyword ranking, search console, organic search, organic traffic, content performance, keyword research, keyword gap, content audit, technical SEO, backlinks, domain authority, AI Overviews, GEO, generative engine optimization, SERP, featured snippets, page speed | Search Console integration, keyword tracking, content performance, and AI search optimization (GEO). Depends on data-extraction, web-analytics. Feeds into competitive-intel, reporting, paid-media. |

#### P2 — Supporting

| Skill | Trigger Phrases | Description |
|-------|----------------|-------------|
| **crm-lead-scoring** | lead scoring, predictive scoring, lead qualification, MQL, SQL, pipeline analytics, pipeline velocity, win rate, deal velocity, sales funnel, opportunity analysis, win/loss analysis, CRM analytics, lead-to-close, propensity model, account scoring | Predictive lead scoring, pipeline velocity tracking, and win/loss analysis. Depends on data-extraction, audience-segmentation, clv-modeling. Feeds into email-analytics, paid-media, reporting. |
| **social-analytics** | social media analytics, social performance, Facebook insights, Instagram analytics, LinkedIn analytics, TikTok analytics, YouTube analytics, X analytics, Twitter analytics, social engagement, social reach, share of voice, social sentiment, brand mentions, social ROI, social listening | Cross-platform social performance, sentiment analysis, and competitive benchmarking. Depends on data-extraction. Feeds into competitive-intel, attribution-analysis, reporting. |
| **competitive-intel** | competitive analysis, competitor research, competitive intelligence, competitor keywords, competitor ads, share of voice, market share, competitive benchmarking, competitor traffic, SWOT, competitor monitoring, ad spy, pricing intelligence, market positioning | Competitor keyword tracking, traffic estimation, ad creative monitoring, and market positioning. Consumes data from seo-content, social-analytics, paid-media. Feeds into attribution-analysis, reporting. |
| **voc-analytics** | NPS, Net Promoter Score, CSAT, customer satisfaction, CES, Customer Effort Score, survey analytics, survey results, customer feedback, open-text analysis, verbatim analysis, voice of customer, VoC, feedback themes, review analysis, satisfaction tracking | NPS/CSAT/CES tracking, open-text theme extraction, and satisfaction-behavior correlation. Depends on data-extraction, audience-segmentation. Feeds into reporting, seo-content, email-analytics. |

### product-manager

Product management toolkit covering requirements authoring and translation into agentic execution plans.

| Skill | Trigger Phrases | Description |
|-------|----------------|-------------|
| **prd-writer** (`prd-author`) | write a PRD, draft a spec, product doc, one-pager, PR/FAQ, feature brief, critique/level up a PRD | Produces Product Requirements Documents, specs, product briefs, one-pagers, and PR/FAQs. Does not handle engineering design docs, RFCs, or ADRs. |
| **prd-to-plan** (`prd-to-agent-plan`) | turn this PRD into a plan, agentic plan, execution plan, task graph, decompose this spec, break this down for Claude Code, scrum-master plan | Converts a PRD/spec into a structured `PLAN.md` for agentic execution: phases, tasks, dependencies, validation gates, sub-agent assignments, context bundles. |

## Workspace Convention

Skills exchange data through a structured workspace directory:

| Directory | Purpose |
|-----------|---------|
| `workspace/raw/` | Data extracted from source platforms (CSV, JSON) |
| `workspace/processed/` | Normalized, cleaned data ready for analysis |
| `workspace/analysis/` | Analytical outputs: model results, scores, anomalies, rankings |
| `workspace/reports/` | Final deliverables: HTML dashboards, XLSX exports, PPTX decks |
| `workspace/compliance/` | Compliance review artifacts: review reports, archival manifests |
| `shared/schemas/` | Data contracts shared across all skills (JSON Schema definitions) |
| `shared/definitions/` | Marketing taxonomy, metric glossary, industry benchmarks |
| `shared/utils/` | Common Python utilities used by multiple skills |

Each skill checks for prerequisite files before executing and writes outputs to predictable locations. Skills communicate through shared data contracts defined in `shared/schemas/data_contracts.md`.

## Financial Services Mode

When a workspace is tagged as financial services, the **compliance-review** skill acts as a mandatory gate for all customer-facing content. Every skill that produces reports, email content, ad copy, or marketing materials must route output through compliance-review before distribution. This skill checks content against SEC Marketing Rule 206(4)-1, FINRA Rule 2210, and FCA financial promotions requirements. It is advisory only and always recommends human compliance officer review.
