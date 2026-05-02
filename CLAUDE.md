# Agile Agentic Analytics — Skill Index

## Documentation Map

This repository includes official Anthropic Claude Code documentation plus a marketing analytics product specification in `docs/`. Treat these files as source material when creating, changing, validating, or extending plugins and skills. The notes below summarize what each document is for and when to consult it.

| Document | Use It For | Key Sections |
|----------|------------|--------------|
| `docs/CREATE_PLUGINS.md` | Practical plugin creation workflow. Use this before creating a new plugin, converting standalone `.claude/` config into a plugin, or testing local plugin changes. | Plugin vs standalone config; quickstart; plugin structure overview; adding skills, LSP, monitors, and settings; local testing with `--plugin-dir`; migration from `.claude/`. |
| `docs/PLUGINS_REFERENCE.md` | Deep technical plugin reference. Use this when editing manifests, component paths, plugin-provided agents/hooks/MCP/LSP/monitors, user config, cache-sensitive file access, install scopes, CLI behavior, debugging, or versioning. | Component reference; manifest schema; path behavior rules; `userConfig`; `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`; plugin cache and path traversal limits; CLI commands; validation/debugging; version management. |
| `docs/CREATE_CUSTOM_SUBAGENTS.md` | Subagent design and operation. Use this when adding or changing plugin agents in `plugins/<plugin>/agents/`, deciding whether an agent should be project/user/plugin-scoped, restricting tools, choosing models, or designing automatic delegation behavior. | Built-in agents; `/agents` workflow; scopes and precedence; frontmatter fields; tool restrictions; hooks for subagents; foreground/background execution; context management; example reviewer/debugger/data-scientist agents. |
| `docs/HOOKS_REFERENCE.md` | Hook lifecycle and schema reference. Use this before adding plugin hooks, skill/agent hooks, or project hooks, and whenever a hook needs to block, approve, transform, notify, run async work, call MCP tools, or use prompt/agent-based evaluation. | Lifecycle; hook locations; matcher patterns; handler fields; stdin JSON input; exit-code and JSON output; all event schemas; prompt hooks; agent hooks; async hooks; security best practices; debugging hooks. |
| `docs/TOOLS_REFERENCE.md` | Claude Code tool names and behavior. Use this when writing tool allow/deny rules, subagent `tools` or `disallowedTools`, hook matchers, permission settings, or tool-aware skill instructions. | Tool name table; permission requirements; Bash cwd/env behavior; LSP behavior; Monitor tool; PowerShell behavior; checking available tools. |
| `docs/marketing_analytics_skill_specs.md` | Product and implementation specification for the marketing analytics portfolio. Use this when adding, revising, or validating marketing analytics skills, scripts, references, schemas, financial-services behavior, or cross-skill workflows. | SKILL.md format guidance; 15-skill portfolio; priority tiers; portfolio architecture; workspace directory structure; per-skill objectives, trigger descriptions, functional scope, data contracts, scripts, cross-skill integration, financial-services considerations, development guidelines, acceptance criteria; appendices for data contracts and interconnection matrix. |

### Documentation Usage Rules

- Start with `docs/CREATE_PLUGINS.md` for workflow, then confirm exact schema/path/version behavior in `docs/PLUGINS_REFERENCE.md`.
- Use `docs/CREATE_CUSTOM_SUBAGENTS.md` before changing anything in `agents/`, especially plugin-shipped agents because they support fewer frontmatter fields than project/user agents.
- Use `docs/HOOKS_REFERENCE.md` before adding hooks or changing hook matchers. Hook event names and matcher semantics are case-sensitive and event-specific.
- Use `docs/TOOLS_REFERENCE.md` whenever a config references tool names. Tool names in permissions, subagent frontmatter, and hook matchers must match Claude Code's canonical tool names.
- Use `docs/marketing_analytics_skill_specs.md` as the product requirements document for the `marketing-analytics` plugin. It defines what each skill should do, what files it should read/write, and how skills compose.
- Keep `CLAUDE.md` as the compact operating index. Do not paste entire docs into it; link the relevant doc and summarize the current repo convention.

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
