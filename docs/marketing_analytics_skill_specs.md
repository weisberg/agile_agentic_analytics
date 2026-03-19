

**Marketing Analytics**

**Skill Package Specifications**

for Claude Code Agent Ecosystem

15 Interconnected Skills • Cross-Industry \+ Financial Services

SKILL.md Convention • Agent-Native Design • Composable Architecture

Version 1.0 • March 19, 2026  
*Prepared for Agile Agentic Analytics*

# **Introduction**

# **Building the definitive marketing analytics skill package for Claude Code**

**A comprehensive, interconnected marketing analytics skill portfolio is both achievable and overdue in the Claude Code ecosystem.** The SKILL.md open standard is mature, cross-platform, and well-documented. Existing community skill collections like `coreyhaines31/marketingskills` and `alirezarezvani/claude-skills` prove the pattern works, but no single package delivers the full breadth of marketing analytics — from attribution modeling through CLV prediction to compliance-aware financial services workflows. The MCP server ecosystem already provides connectors for Google Analytics, Meta Ads, HubSpot, and dozens of other marketing platforms. What's missing is the analytical intelligence layer: skills that transform raw data into actionable marketing insights through composable, cross-referencing workflows.

This report covers the SKILL.md specification, existing repositories and MCP servers, the 15 core marketing analytics domains to build skills for, financial services regulatory requirements, agent framework patterns, and skill interconnection architecture.

---

## **The SKILL.md format is stable, open, and cross-platform**

The Agent Skills Open Standard, published at **agentskills.io/specification** and maintained in the `agentskills/agentskills` GitHub repository under Apache 2.0, defines how skills work across Claude Code and beyond. The format has been adopted by OpenAI Codex, GitHub Copilot, Cursor, VS Code, Amp, and Goose — making a well-built skill package portable across nearly all major AI coding agents. Simon Willison described it as "a deliciously tiny specification."

Each skill lives in a directory containing a required `SKILL.md` file with YAML frontmatter (`name`, `description`, optional `license`, `metadata`, `compatibility`, `context`) and Markdown instructions. Supporting files go in `scripts/` (executable Python/Bash/JS), `references/` (context docs loaded on-demand), and `assets/` (templates, fonts). Anthropic's official guidance at `code.claude.com/docs/en/skills` recommends keeping the SKILL.md body **under 500 lines** and moving detailed content to reference files, since skills load progressively: \~50–100 tokens of metadata at startup, under 5,000 tokens of full instructions on activation, and resources on-demand.

The description field is the primary triggering mechanism — Claude uses it to decide when to load a skill. Anthropic's best practices guide recommends writing "pushy" descriptions that explicitly list trigger phrases. For marketing analytics, this means descriptions like *"Use when the user mentions attribution, ROAS, channel performance, campaign ROI, marketing mix modeling, or media effectiveness"* rather than vague summaries.

Distribution is decentralized through Git-based marketplaces. A `marketplace.json` file catalogs plugins in a repository, and users install via `/plugin marketplace add owner/repo`. The official Anthropic marketplace lives at `anthropics/claude-plugins-official` (55+ plugins). Community registries like **claude-plugins.dev** (51,625+ indexed skills), **claudecodeplugins.io** (1,423 skills), and **buildwithclaude.com** (489+ extensions) provide discovery. Skills can also be distributed via npm (`npx skills add author/repo`) or direct Git URLs.

---

## **Existing skill repositories and MCP servers form a strong foundation**

The ecosystem already contains significant building blocks for a marketing analytics package.

**The most relevant existing repositories** include `anthropics/skills` (97,400+ GitHub stars), which contains 50+ official skills including document processing, data analysis, and a powerful `skill-creator` meta-skill. The community collection `alirezarezvani/claude-skills` (5,200+ stars) offers **192+ skills** across engineering, marketing, product, and compliance — all using zero pip installs. Most directly relevant is `coreyhaines31/marketingskills`, a dedicated marketing skill package with skills for analytics tracking (GA4 setup, conversion tracking, UTM parameters, Tag Manager), CRO, A/B testing, SEO auditing, email sequences, and ad creative. It installs via `npx skills add coreyhaines31/marketingskills`. The `ComposioHQ/awesome-claude-skills` list includes pre-built skills for **Google Analytics Automation**, **Mixpanel Automation**, **PostHog Automation**, and **Segment Automation**. The largest community marketplace, `jeremylongshore/claude-code-plugins-plus-skills`, catalogs **340 plugins and 1,367 skills** with its own package manager (CCPI).

**MCP servers provide the data connectivity layer.** Google released an official Google Analytics MCP server at `googleanalytics/google-analytics-mcp` (July 2025\) with tools for account summaries, property details, report execution, and real-time reporting. The `brijr/meta-ads-mcp` server exposes **25 tools** for Meta advertising — impressions, clicks, ROAS, CTR, creative management, and audience operations. A multi-platform Marketing Automation MCP server (`Mohit4022-cloud/Marketing-Automation-MCP-Server`) handles Google Ads, Facebook Ads, and Google Analytics with AI-powered budget optimization and predictive ROI modeling. Additional MCP servers exist for Mixpanel, PostHog, Segment, Mailgun, Google Search Console, and HubSpot. For data warehousing and dashboards, servers exist for PostgreSQL, Snowflake, ClickHouse, Metabase (128+ tools), Apache Superset, Power BI, and Redash. The curated list at `TensorBlock/awesome-mcp-servers` maintains a dedicated marketing/sales/CRM section.

The gap in the ecosystem is clear: **connectivity exists but analytical intelligence does not.** MCP servers extract data; what's needed are skills that perform sophisticated analysis — attribution modeling, statistical experimentation, predictive CLV, compliance checking — and chain these analyses into cohesive workflows.

---

## **The 15 skills every marketing analytics package needs**

Based on comprehensive research of marketing analytics automation practices through 2026, the following skills should form the core portfolio, ordered by strategic value and operational frequency.

**1\. Marketing mix modeling and attribution.** This is the highest-value skill. The landscape has converged on three open-source Bayesian MMM frameworks: Meta's Robyn (R-based, Nevergrad optimization), Google's Meridian (Python/PyMC, geo-level, YouTube reach/frequency integration), and **PyMC-Marketing** (Python, most popular by PyPI downloads, used by HelloFresh and Bolt). A skill should automate the full pipeline: data extraction from ad platforms, adstock/saturation curve fitting, posterior predictive checks, and budget optimization across channels. It should support calibration with incrementality test results and produce scenario-planning outputs ("what if we shift 20% of display budget to search?"). Cross-connections: consumes paid media spend data, feeds dashboard/reporting skill.

**2\. A/B testing and experimentation.** Foundation for all optimization. The skill should handle power analysis, minimum detectable effect calculation, and duration estimation for experiment design. For analysis, it needs frequentist hypothesis testing, Bayesian posterior computation, **CUPED variance reduction** (which reduces variance 30–40% using pre-experiment covariates), and sequential testing with valid any-time p-values. Open-source references include GrowthBook (Bayesian \+ frequentist \+ sequential), PostHog (Bayesian), and the statistical engines behind Statsig and Eppo. The skill should detect Sample Ratio Mismatch and apply multiple comparison corrections (Benjamini-Hochberg). Cross-connections: calibrates MMM models, designs email experiments, validates CRO hypotheses.

**3\. Paid media analytics.** Highest operational frequency. The skill aggregates performance data across Google Ads API (v22+), Meta Marketing API (v18–19+), LinkedIn Ads, TikTok Ads, and DV360 into unified reporting. Key automations: cross-platform ROAS/CPA comparison, anomaly detection (sudden spend spikes, CTR drops), creative fatigue detection, budget pacing monitoring, search term analysis with negative keyword recommendations, and UTM validation. The Meta API alone supports **70+ performance metrics** and can launch \~494K ads/month programmatically. Cross-connections: feeds MMM, consumes attribution outputs for optimization.

**4\. Dashboard and reporting automation.** The integration layer for everything else. This skill generates executive summaries, interactive HTML dashboards, and scheduled reports by pulling outputs from all other skills. It should produce visualizations using plotly/D3.js, support natural language insight generation, and detect cross-channel anomalies. Reference patterns: the Anthropic `xlsx` skill for data processing, Stormy AI's approach for deterministic metric calculation, and Metabase/Superset MCP servers for persistent dashboards. Cross-connections: consumes outputs from every other skill.

**5\. Customer lifetime value modeling.** The skill should implement probabilistic CLV models — **BG/NBD for purchase frequency** and **Gamma-Gamma for monetary value** — using the Python `lifetimes` library or PyMC-Marketing's Bayesian variants. It should automate RFM summary generation from transaction data, produce customer-level CLV predictions with confidence intervals, calculate CLV:CAC ratios, and flag at-risk high-value customers. Cross-connections: drives segmentation, informs paid media acquisition targets, shapes email lifecycle strategy.

**6\. Customer segmentation and cohort analysis.** Automated RFM calculation, K-Means/DBSCAN behavioral clustering with silhouette score optimization, and cohort retention curve generation. The skill should assign interpretable segment labels (Champions, Loyal, At-Risk, Hibernating, Lost) and track segment migration over time. Cross-connections: CLV provides value dimension, email marketing targets segments, paid media builds lookalike audiences from segments.

**7\. Funnel analysis and conversion optimization.** Multi-step funnel tracking with statistical significance testing on drop-off rates, cohort-based funnel comparison, and automated bottleneck identification. Should integrate with GA4 funnel exploration, Mixpanel/Amplitude flow analysis, and session recording tools. Revenue impact estimation per funnel improvement enables prioritization. Cross-connections: feeds A/B testing with CRO hypotheses, consumes web analytics behavioral data.

**8\. Email marketing analytics.** Deliverability monitoring (bounce rates, blocklist checks, SPF/DKIM/DMARC compliance), engagement analysis (click rates over open rates post-iOS 15), lifecycle flow optimization, and send-time optimization. Key platforms: Braze (7.2B+ MAUs), SendGrid (100B+ emails/month), Iterable, Klaviyo. Cross-connections: uses segmentation for targeting, A/B testing for experimentation, CLV for lifecycle stage.

**9\. Web analytics and behavioral analysis.** GA4 API data extraction, user behavior pattern detection, automated anomaly detection on traffic and conversion metrics, and predictive audience creation. Should also support Amplitude and Mixpanel event-based analysis. GA4's predictive audiences (purchase probability, churn probability) are increasingly important. Cross-connections: foundational data layer for funnel analysis, SEO, and paid media landing pages.

**10\. SEO and content analytics.** Google Search Console API integration, keyword ranking tracking, content performance analysis, technical SEO auditing, and competitive gap analysis. The emerging **AI Search Optimization (GEO)** dimension — tracking visibility in AI Overviews, ChatGPT citations, and Perplexity answers — is critical for 2026\. Key APIs: Search Console (free), Semrush (26.2B keyword database), Ahrefs (35T+ link index), DataForSEO (broadest coverage). Cross-connections: organic/paid keyword overlap with paid media, content strategy with competitive intelligence.

**11\. CRM analytics and lead scoring.** Predictive lead scoring model training (logistic regression, gradient boosting), real-time score updates from behavioral signals, pipeline velocity tracking, and win/loss analysis. Integrates with Salesforce Einstein, HubSpot Breeze AI, or custom scikit-learn models. Cross-connections: consumes segmentation, feeds email nurture flows, informs paid media targeting.

**12\. Social media analytics.** Cross-platform performance aggregation (Meta Graph API, LinkedIn, TikTok, YouTube Data API, X/Twitter), sentiment analysis on mentions, content performance prediction, and competitive benchmarking. Cross-connections: share-of-voice feeds competitive intelligence, engagement data feeds attribution models.

**13\. Competitive intelligence.** Competitor keyword tracking, traffic estimation (SimilarWeb), ad creative monitoring (SpyFu, Pathmatics), share-of-voice calculation, and pricing intelligence. Cross-connections: competitor activity serves as a control variable in MMM, keyword competition informs SEO strategy.

**14\. Survey and voice-of-customer analytics.** NPS/CSAT/CES tracking and trend analysis, LLM-powered open-text categorization and theme extraction, sentiment scoring at scale, and cross-correlation of satisfaction metrics with behavioral data. Cross-connections: enriches segmentation with satisfaction dimension, informs content strategy.

**15\. Compliance-aware content review (financial services).** This is the specialized skill for regulated industries. It checks marketing content against SEC Marketing Rule 206(4)-1, FINRA Rule 2210, and FCA requirements. Automates disclosure insertion (past performance disclaimers, fee disclosures, risk warnings), flags cherry-picked performance data, validates gross/net performance equal prominence, and maintains archival records per SEC Rule 17a-4. Reference tools: Red Marker (6x faster than manual reviews), Luthor AI (50+ jurisdictions), Saifr by FIS (real-time compliance suggestions). Cross-connections: gates all content-generating skills in financial services contexts.

---

## **Financial services marketing demands a compliance-first architecture**

Financial services marketing analytics differs from consumer marketing in three fundamental ways: **regulatory compliance is non-negotiable**, sales cycles span 12–36 months, and a single high-net-worth client can represent millions in AUM.

The SEC Marketing Rule (206(4)-1), fully enforceable since November 2022, permits testimonials and endorsements for the first time but requires prominent disclosures about compensation, conflicts, and qualifications. Hypothetical performance requires policies ensuring relevance to the intended audience. **70% of RIA compliance officers** have detected marketing compliance issues requiring attention, and FINRA reviewed **63,000+ communications filings in 2023** alone. In the UK, the FCA intervened in **19,766 promotions in 2024** — a 97.5% increase from the prior year. Every marketing communication must be archived in WORM format for 6+ years under SEC Rule 17a-4.

For investor acquisition campaigns, the skill package needs AUM-centric metrics (not just lead counts), multi-layer attribution across advisor/consultant/institutional channels, and segment-specific funnels for retail, HNW, institutional, and RIA audiences. Account opening funnels in banking see **up to 67–70% abandonment rates** (BAI research), making conversion optimization critical. Email experimentation requires all variants to be pre-approved through compliance workflows, with every test preserving required disclaimers, risk disclosures, and regulatory statements.

Specialized platforms serve this market: ProFundCom (digital marketing analytics for asset managers), Seismic (fund report orchestration), FMG Suite (FINRA-reviewed content libraries), and Salesforce Financial Services Cloud ($225/user/month). Compliance technology is its own category: Smarsh (6,500+ financial firms, 2025 Gartner Magic Quadrant Leader), Global Relay (20,000 customers, 45+ data types), and RegEd for insurance/securities compliance.

The practical implication for skill design: **every content-generating or content-analyzing skill must have a compliance mode** that activates when the workspace is tagged as financial services. This mode adds disclosure checking, archival triggers, and pre-approval workflow prompts. The compliance review skill should function as a mandatory gate in any content publication workflow.

---

## **Agent framework patterns converge on description-driven, single-purpose tools**

Analysis of LangChain, CrewAI, AutoGen, Semantic Kernel, and OpenAI's tools reveals convergent design principles that should inform the skill package architecture.

All frameworks define tools through three elements: a **name** (unique identifier), a **description** (semantic metadata enabling LLM selection), and a **typed schema** (JSON Schema, Pydantic, or Zod for input/output validation). LangChain uses the `@tool` decorator or `BaseTool` subclass. CrewAI wraps agents with `role`, `goal`, and `backstory` attributes plus tool lists. Semantic Kernel uses `@kernel_function` decorators with rich description strings. MCP defines tools with `name`, `title`, `description`, and `inputSchema`. The lesson: **invest heavily in descriptions.** The quality of tool descriptions is the single largest determinant of whether an LLM selects the right tool at the right time.

Composability patterns fall into five categories used across frameworks. **Prompt chaining** (sequential execution where output feeds the next input) works for linear workflows like data extraction → transformation → analysis. **Routing** (classify input, direct to specialist) works for triaging marketing questions to the appropriate skill. **Parallelization** (fan-out, aggregate results) works for pulling data from multiple ad platforms simultaneously. **Orchestrator-worker** (central agent delegates to specialists) maps to CrewAI's hierarchical process and AutoGen's group chat. **Evaluator-optimizer** (generate → evaluate → refine) applies to iterative campaign optimization. Anthropic's own "Building Effective Agents" guide recommends starting with the simplest pattern that works and only escalating complexity when needed.

For marketing analytics specifically, CrewAI's role-based architecture maps naturally to marketing team structures: a Market Analyst agent, a Data Analyst agent, and a Strategy Developer agent, each with specialized tools. LangGraph's graph-based workflows support the DAG patterns needed for complex analytics pipelines. The MCP protocol's session-based state management enables passing campaign context (IDs, date ranges, segment definitions) between tool calls without re-extraction.

---

## **Skills should interconnect through shared schemas, filesystem state, and complementary descriptions**

The SKILL.md specification does not include a formal dependency declaration mechanism between skills. Instead, Claude **automatically composes multiple skills** when a task requires it — Anthropic describes this as "one of the most powerful parts of the Skills feature." Effective interconnection relies on three mechanisms.

**Shared data contracts in reference files.** A `shared/schemas/data_contracts.md` file defines the canonical shapes for campaign data, attribution reports, segment definitions, and CLV predictions. Each skill's SKILL.md references this shared schema for both its expected inputs and its outputs. This creates implicit coupling through structure rather than explicit dependency declarations. JSON Schema is the recommended format for these contracts, with semantic constraints (e.g., "conversion\_rate must be between 0 and 1") and versioning rules for backward compatibility.

**Filesystem-based state management.** Skills store intermediate results as files in a workspace directory structure: `workspace/raw/` for extracted data, `workspace/processed/` for normalized data, `workspace/analysis/` for analytical outputs, and `workspace/reports/` for final deliverables. Each skill checks for prerequisite files before executing and writes its outputs to predictable locations. This pattern enables recovery from failures, supports multi-session workflows, and maintains Claude's progressive disclosure architecture — only the data needed for the current skill gets loaded into context.

**Complementary "pushy" descriptions that form an implicit workflow graph.** Each skill's description explicitly names other skills as prerequisites or downstream consumers. For example, the attribution analysis skill's description states: *"Expects normalized campaign data. If not available, suggest running data-extraction first. Results feed into campaign-optimizer and performance-reporter."* Claude then orchestrates the correct sequence automatically. Anthropic recommends adding a master list of all skills to the project's `CLAUDE.md` file to improve discovery, since Claude tends to "under-trigger" skills.

The recommended portfolio organization is a **domain-grouped monorepo** with this structure:

.claude/skills/marketing-analytics/  
├── data-extraction/          \# Platform data collection  
│   ├── SKILL.md  
│   ├── scripts/  
│   └── references/  
├── attribution-analysis/     \# MMM and MTA  
├── experimentation/          \# A/B testing and CUPED  
├── audience-segmentation/    \# RFM and clustering  
├── clv-modeling/             \# Lifetime value prediction  
├── funnel-analysis/          \# Conversion optimization  
├── email-analytics/          \# Deliverability and engagement  
├── paid-media/               \# Cross-platform ad analytics  
├── seo-content/              \# Organic search and content  
├── social-analytics/         \# Social media performance  
├── crm-lead-scoring/         \# Pipeline and scoring  
├── competitive-intel/        \# Market and competitor research  
├── voc-analytics/            \# Survey and sentiment  
├── reporting/                \# Dashboards and summaries  
├── compliance-review/        \# Financial services regulatory  
└── shared/  
    ├── schemas/data\_contracts.md  
    ├── definitions/marketing\_taxonomy.md  
    └── utils/common\_transforms.py

Each skill follows the separation-of-concerns principle from Anthropic's best practices: the SKILL.md contains *process* (ordered steps Claude follows), reference files contain *context* (domain knowledge, schemas, metric definitions), and scripts contain *deterministic computation* (statistical calculations, data transformations). This maps directly to how Stormy AI demonstrated effective marketing analytics skills: "shifting from vibes-based chatting to deterministic code execution for marketing ROI."

---

## **Conclusion: a composable system, not a monolithic tool**

The most important architectural insight is that this skill package should function as a **system of interconnected specialists, not a single omnibus tool.** Each skill handles one analytical domain with depth. Skills communicate through shared data contracts and filesystem state. Claude orchestrates them into multi-step workflows based on complementary descriptions. The compliance review skill acts as a mandatory gate in financial services contexts.

The ecosystem is ready for this. The SKILL.md standard is stable and cross-platform. MCP servers provide connectivity to every major marketing platform. Open-source statistical libraries (PyMC-Marketing, lifetimes, GrowthBook) provide analytical engines. What's missing — and what this package should deliver — is the **orchestration intelligence**: knowing when to run attribution analysis vs. experimentation, how to chain segmentation into CLV prediction into campaign optimization, and when to invoke compliance review before any content touches a regulated audience.

Three design principles should guide development. First, **progressive disclosure everywhere** — metadata loads at startup, full instructions on activation, data on-demand. Second, **deterministic computation for all statistics** — use Python scripts for hypothesis tests, CLV models, and attribution calculations rather than asking the LLM to estimate. Third, **description-driven composition** — invest more time in writing precise, trigger-rich descriptions than in any other aspect of the skill, because the description is what determines whether Claude activates the right skill at the right time.

Notable repositories to reference during development include `anthropics/skills` (official patterns, especially the `xlsx` skill for data processing), `coreyhaines31/marketingskills` (closest existing marketing package), `ComposioHQ/awesome-claude-skills` (analytics platform integrations), and `googleanalytics/google-analytics-mcp` (official GA4 MCP server). The Anthropic cookbooks at `anthropics/claude-cookbooks/blob/main/skills/README.md` provide additional patterns for financial reporting and data analysis. For financial services compliance patterns, Red Marker and Luthor AI demonstrate the automated review approach that the compliance skill should emulate.

# **Executive Summary**

This document contains the development specifications for 15 interconnected Claude Code skills that together form the definitive marketing analytics skill package. Each specification provides the skill’s objective, SKILL.md trigger description, functional scope, key capabilities, input/output data contracts, reference files, scripts, cross-skill integration points, financial services considerations, development guidelines, and acceptance criteria.

The skills are designed as a composable portfolio. They communicate through shared data contracts defined in a common schema file, exchange intermediate results via a structured filesystem workspace, and reference each other through complementary SKILL.md descriptions that enable Claude to automatically orchestrate multi-skill workflows. The compliance-review skill acts as a mandatory gate for all customer-facing content in regulated financial services contexts.

## **Priority Tiers**

| Tier | Skills | Rationale |
| :---- | :---- | :---- |
| P0 | Attribution, Experimentation, Paid Media, Reporting, Compliance (FS) | Foundational — highest strategic value; integration layer; mandatory for FS |
| P1 | CLV, Segmentation, Funnel, Email, Web Analytics, SEO/Content | Strategic/Tactical — direct revenue impact; enables downstream skills |
| P2 | CRM/Lead Scoring, Social, Competitive Intel, VoC Analytics | Supporting — extends core analytics; enriches other skills |

## **Skill Format Options**

Each skill supports two distribution formats:

**Option A: SKILL.md Convention (Recommended)**

The Agent Skills Open Standard format, using a SKILL.md file with YAML frontmatter (name, description, metadata) and Markdown instructions. Supporting files in scripts/, references/, and assets/ directories. Distributed via Git-based plugin marketplaces (anthropics/claude-plugins-official, claude-plugins.dev, or private enterprise registries). Installed via /plugin marketplace add owner/repo or npx skills add. Cross-platform compatible with Claude Code, OpenAI Codex, Cursor, GitHub Copilot, and other SKILL.md-compatible agents.

**Option B: Custom Agent Framework Format**

For teams using custom agent architectures (e.g., the Agile Agentic Analytics framework with named sub-agents like athena-analyst), each skill specification maps to a sub-agent definition with: agent name and role description derived from the skill name and objective; tool list derived from the scripts section; knowledge base derived from reference files; system prompt derived from the SKILL.md body; and inter-agent communication protocols derived from the integration section. The data contracts and filesystem workspace patterns remain identical between formats.

# **Portfolio Architecture**

The 15 skills connect through three mechanisms:

**Shared Data Contracts**

A shared/schemas/data\_contracts.md file defines canonical JSON schemas for campaign data, attribution reports, segment definitions, CLV predictions, experiment results, and compliance review outputs. Every skill references this shared schema for both inputs and outputs, creating implicit structural coupling without explicit dependency declarations.

**Filesystem-Based State Management**

Skills store intermediate results in a structured workspace directory: workspace/raw/ for extracted data, workspace/processed/ for normalized data, workspace/analysis/ for analytical outputs, workspace/reports/ for final deliverables, and workspace/compliance/ for regulatory review artifacts. Each skill checks for prerequisite files before executing and writes outputs to predictable locations.

**Description-Driven Composition**

Each skill’s SKILL.md description explicitly names other skills as prerequisites or downstream consumers. Claude orchestrates the correct execution sequence automatically based on these complementary descriptions. A master skill index in the project’s CLAUDE.md file improves discovery and reduces under-triggering.

## **Workspace Directory Structure**

| Directory | Purpose |
| :---- | :---- |
| workspace/raw/ | Data extracted from source platforms (CSV, JSON) by data-extraction skill |
| workspace/processed/ | Normalized, cleaned data ready for analysis (segments, unified media) |
| workspace/analysis/ | Analytical outputs: model results, scores, anomalies, rankings |
| workspace/reports/ | Final deliverables: HTML dashboards, XLSX exports, PPTX decks, DOCX reports |
| workspace/compliance/ | Compliance review artifacts: review reports, compliant content, archival manifests |
| shared/schemas/ | Data contracts shared across all skills (JSON Schema definitions) |
| shared/definitions/ | Marketing taxonomy, metric glossary, industry benchmark tables |
| shared/utils/ | Common Python utilities used by multiple skills (date handling, formatting) |

# **Individual Skill Specifications**

The following sections provide detailed development specifications for each of the 15 skills in the marketing analytics package. Skills are ordered by priority tier and strategic value.

# **Skill 1: Marketing Mix Modeling & Attribution**

*Bayesian marketing mix modeling, multi-touch attribution, and incrementality measurement*

| Skill ID | attribution-analysis |
| :---- | :---- |
| **Priority** | P0 — Foundational (highest strategic value) |
| **Category** | Measurement & Attribution |
| **Depends On** | data-extraction, paid-media |
| **Feeds Into** | reporting, paid-media (budget optimization), experimentation (calibration) |

## **Objective**

Automate the end-to-end marketing mix modeling pipeline: data ingestion from ad platforms, adstock and saturation curve fitting using Bayesian methods, posterior predictive validation, channel-level contribution decomposition, and budget optimization with scenario planning. Support calibration with incrementality lift test results. Produce executive-ready attribution reports with confidence intervals and actionable budget reallocation recommendations.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions attribution, ROAS optimization, channel contribution, marketing mix model, MMM, media mix, budget allocation, budget optimization, incrementality, adstock, saturation curves, diminishing returns, channel effectiveness, media effectiveness, cross-channel attribution, multi-touch attribution, MTA, Shapley value attribution, or marketing ROI measurement. Also trigger when user asks ‘which channel is driving results’ or ‘where should we spend more.’ If campaign spend data is not yet extracted, suggest running data-extraction first. Results feed into reporting and paid-media skills.*

## **Functional Scope**

* Bayesian MMM using PyMC-Marketing (primary) with Robyn/Meridian as alternatives

* Multi-touch attribution using Shapley values, Markov chains, and data-driven models

* Incrementality lift test design (geo-based, time-based holdouts) and result integration

* Adstock transformation (geometric, Weibull) and Hill saturation curve fitting

* Budget optimization via constrained posterior sampling with scenario planning

* Prior calibration from historical lift tests, industry benchmarks, or expert knowledge

## **Key Capabilities**

**Data Preparation**

* Normalize spend, impressions, and conversion data across platforms into unified weekly/daily grain

* Automatically detect and impute missing data windows with flagged confidence adjustments

* Generate control variables: seasonality (Fourier), holidays, macroeconomic indicators, competitor activity

**Model Fitting**

* Fit Bayesian MMM with MCMC sampling (NUTS) via PyMC-Marketing’s MMM class

* Estimate adstock (carry-over) and saturation (diminishing returns) parameters per channel

* Compute posterior channel contributions with credible intervals

* Run posterior predictive checks and WAIC/LOO model comparison

**Budget Optimization**

* Solve constrained optimization: maximize total conversions/revenue subject to budget constraints

* Generate scenario analyses: ‘what if we shift X% from display to search?’

* Produce marginal ROAS curves showing next-dollar efficiency per channel

* Account for saturation: flag channels approaching diminishing returns ceiling

**Reporting**

* Channel contribution waterfall charts with uncertainty bands

* Budget reallocation recommendation tables with expected lift estimates

* Model diagnostics dashboard: trace plots, R-hat, effective sample size, posterior predictive coverage

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/campaign\_spend\_{platform}.csv — Daily/weekly spend by channel from data-extraction skill

* workspace/raw/conversions.csv — Outcome variable (leads, revenue, signups) at matching grain

* workspace/raw/external\_factors.csv — Optional: seasonality indices, competitor spend, macro indicators

* workspace/analysis/incrementality\_results.json — Optional: calibration priors from experimentation skill

**Outputs**

* workspace/analysis/mmm\_channel\_contributions.json — Posterior mean and credible intervals per channel

* workspace/analysis/mmm\_budget\_optimization.json — Optimal allocation under current and scenario budgets

* workspace/analysis/mmm\_diagnostics.json — MCMC convergence metrics, model fit statistics

* workspace/reports/mmm\_executive\_summary.html — Interactive report with charts and recommendations

## **Reference Files**

* references/mmm\_methodology.md — Bayesian MMM theory, adstock/saturation math, prior specification guidance

* references/pymc\_marketing\_api.md — PyMC-Marketing MMM class reference and usage patterns

* references/incrementality\_calibration.md — How to translate lift test results into informative priors

* shared/schemas/data\_contracts.md — Canonical campaign data schema

## **Scripts (Deterministic Computation)**

* scripts/fit\_mmm.py — Core MMM fitting with PyMC-Marketing (MCMC sampling, diagnostics)

* scripts/optimize\_budget.py — Constrained optimization using posterior samples

* scripts/compute\_contributions.py — Decompose fitted model into channel-level contributions

* scripts/validate\_model.py — Posterior predictive checks, WAIC, LOO-CV computation

## **Cross-Skill Integration**

This skill is the strategic hub of the portfolio. It consumes normalized campaign data from data-extraction and spend metrics from paid-media. Its budget optimization outputs directly inform paid-media’s budget pacing. Incrementality test results from the experimentation skill serve as calibration priors, creating a virtuous cycle: experiments validate the model, the model guides budget allocation, and budget changes create new natural experiments. The reporting skill consumes all MMM outputs for executive dashboards. In financial services mode, all reports must pass through compliance-review before distribution.

## **Financial Services Considerations**

* Performance claims derived from MMM must include confidence intervals and methodology disclaimers

* Past performance language must comply with SEC Marketing Rule — invoke compliance-review skill

* Attribution to specific fund products requires net-of-fees adjustment and benchmark comparison

* Models should account for long sales cycles (12–36 months for institutional AUM acquisition)

## **Development Guidelines**

1. Use PyMC-Marketing as the primary framework; include fallback to lightweight Robyn-style ridge regression for teams without MCMC infrastructure

2. All statistical computations must run in deterministic Python scripts, never estimated by the LLM

3. Default to weekly data grain; support daily when sample size exceeds 2 years of history

4. Include prior sensitivity analysis: run with vague vs informative priors and compare posteriors

5. Store all MCMC trace data for reproducibility; use ArviZ for diagnostics and visualization

6. Implement progressive disclosure: metadata loads basic description, full instructions load on activation, MCMC scripts load on-demand

## **Acceptance Criteria**

* Model achieves R-hat \< 1.05 for all parameters with effective sample size \> 400

* Posterior predictive check covers 90%+ of observed data within 90% credible interval

* Budget optimizer produces feasible allocations that sum to the specified total budget

* Scenario analysis correctly propagates uncertainty from posterior to predictions

* Channel contribution decomposition sums to total observed outcome within 2% tolerance

* Full pipeline executes end-to-end from raw data to executive report in a single agent session

# **Skill 2: A/B Testing & Experimentation**

*Statistical experiment design, CUPED variance reduction, sequential testing, and causal analysis*

| Skill ID | experimentation |
| :---- | :---- |
| **Priority** | P0 — Foundational (powers all optimization) |
| **Category** | Experimentation & Causal Inference |
| **Depends On** | data-extraction, audience-segmentation (for stratification) |
| **Feeds Into** | attribution-analysis (calibration priors), funnel-analysis, email-analytics, reporting |

## **Objective**

Provide a complete experimentation toolkit: power analysis and minimum detectable effect calculation for experiment design; frequentist and Bayesian analysis for completed experiments; CUPED variance reduction to accelerate learning; sequential testing with always-valid confidence intervals for early stopping; and automated diagnostics including Sample Ratio Mismatch detection and novelty/primacy effect identification. Produce structured experiment result reports suitable for both technical and executive audiences.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions A/B test, experiment, hypothesis test, statistical significance, p-value, confidence interval, CUPED, variance reduction, power analysis, sample size calculation, minimum detectable effect, MDE, sequential test, early stopping, Bayesian AB test, multi-armed bandit, experiment design, split test, holdout test, control group, treatment effect, incrementality test, causal inference, or uplift modeling. Also trigger on ‘did this change work’ or ‘how long should we run this test.’ If segment-level analysis is needed and segments are not defined, suggest running audience-segmentation first.*

## **Functional Scope**

* Pre-experiment: power analysis, MDE calculator, duration estimator, randomization design

* Frequentist analysis: z-test, t-test, chi-squared, proportion tests with multiple comparison correction

* Bayesian analysis: Beta-Binomial for conversion, Normal-NormalInverseGamma for revenue, posterior probability of being best

* CUPED variance reduction using pre-experiment covariates (30–40% variance reduction typical)

* Sequential testing: mSPRT, always-valid confidence intervals, alpha-spending functions

* Diagnostics: SRM detection, AA test validation, novelty/primacy effect detection, interaction effects

## **Key Capabilities**

**Experiment Design**

* Calculate required sample size given baseline rate, MDE, power (default 80%), and significance level (default 5%)

* Estimate experiment duration based on historical traffic volume and required sample size

* Design stratified randomization schemes for low-traffic segments

* Generate experiment specification documents with hypothesis, metrics, guardrails, and decision criteria

**Statistical Analysis**

* Execute frequentist hypothesis tests with effect sizes, p-values, and confidence intervals

* Compute CUPED-adjusted estimates: regress metric on pre-experiment covariate, analyze residuals

* Run Bayesian analysis: posterior distributions, probability of being best, expected loss

* Apply Benjamini-Hochberg correction for multiple metric testing; flag significant vs exploratory results

**Sequential Monitoring**

* Implement always-valid confidence intervals using mixture sequential probability ratio test

* Support group sequential designs with O’Brien-Fleming or Pocock spending functions

* Generate monitoring dashboards showing cumulative effect estimates with valid stopping boundaries

**Diagnostics & Reporting**

* Detect Sample Ratio Mismatch with chi-squared goodness-of-fit test (flag if p \< 0.001)

* Identify novelty/primacy effects through time-windowed analysis

* Produce structured result reports: effect size, CI, practical significance, recommendation

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/experiment\_data.csv — User-level data with variant assignment, metric values, timestamps

* workspace/raw/pre\_experiment\_covariates.csv — Pre-period metric values for CUPED (optional but recommended)

* workspace/processed/segments.json — Segment definitions from audience-segmentation (optional, for subgroup analysis)

**Outputs**

* workspace/analysis/experiment\_results.json — Structured results: effect sizes, CIs, p-values, Bayesian posteriors

* workspace/analysis/cuped\_adjustment.json — CUPED theta estimates and variance reduction achieved

* workspace/analysis/incrementality\_results.json — Lift estimates consumable by attribution-analysis for MMM calibration

* workspace/reports/experiment\_report.html — Visual report with forest plots, posterior distributions, monitoring charts

## **Reference Files**

* references/experiment\_design.md — Power analysis formulas, MDE tables, duration estimation methodology

* references/cuped\_methodology.md — CUPED math, covariate selection guidance, theta derivation

* references/sequential\_testing.md — mSPRT theory, alpha-spending functions, valid stopping rules

* references/bayesian\_ab.md — Conjugate prior selection, loss function interpretation, decision rules

* shared/schemas/data\_contracts.md — Experiment data schema (variant, user\_id, metric, timestamp)

## **Scripts (Deterministic Computation)**

* scripts/power\_analysis.py — Sample size and MDE calculation for proportions and continuous metrics

* scripts/frequentist\_test.py — z-test, t-test, chi-squared, proportion test with BH correction

* scripts/bayesian\_test.py — Posterior computation, probability of being best, expected loss

* scripts/cuped.py — CUPED covariate regression, theta estimation, adjusted metric computation

* scripts/sequential\_test.py — mSPRT boundaries, always-valid CIs, alpha-spending

* scripts/srm\_check.py — Sample Ratio Mismatch detection with diagnostic breakdown

## **Cross-Skill Integration**

The experimentation skill is the scientific backbone of the portfolio. Its incrementality test results calibrate the attribution-analysis MMM priors. The funnel-analysis skill generates hypotheses that experimentation validates. The email-analytics skill delegates all send-time and subject-line testing to experimentation. CUPED leverages pre-experiment behavioral data from web-analytics. In financial services mode, all experiment variants involving customer-facing content must pass compliance-review before launch.

## **Financial Services Considerations**

* All experiment variants involving investor-facing content must be pre-approved by compliance

* Required regulatory disclosures must appear in all variants — cannot be the variable under test

* Experiment result claims used in marketing materials must include statistical methodology footnotes

* Email experiments must maintain CAN-SPAM and SEC archival requirements across all variants

## **Development Guidelines**

7. All statistical computations must be deterministic Python scripts using scipy.stats and numpy; never let the LLM estimate p-values

8. CUPED implementation must validate that the covariate was measured entirely pre-treatment to avoid post-treatment bias

9. Default to two-sided tests; one-sided only when explicitly justified in the experiment spec

10. Always compute both frequentist and Bayesian results; let the user choose their decision framework

11. Sequential test implementation must guarantee Type I error control at the nominal level

12. Include automated guardrail metric checking: if any guardrail metric degrades beyond threshold, flag the experiment

## **Acceptance Criteria**

* Power analysis produces sample sizes within 5% of analytical formulas for known distributions

* CUPED adjustment produces variance reduction of 20%+ on realistic simulated data with correlated covariates

* Sequential test maintains Type I error rate below nominal alpha (verified via 10,000 simulation runs)

* SRM detection correctly identifies 95%+ of intentionally imbalanced datasets at 0.1% threshold

* Bayesian posterior probabilities match analytical conjugate solutions for Beta-Binomial test cases

* End-to-end pipeline from raw data to experiment report executes in under 60 seconds for 1M-row datasets

# **Skill 3: Paid Media Analytics**

*Cross-platform ad performance aggregation, anomaly detection, and creative optimization*

| Skill ID | paid-media |
| :---- | :---- |
| **Priority** | P0 — Foundational (highest operational frequency) |
| **Category** | Channel Analytics |
| **Depends On** | data-extraction |
| **Feeds Into** | attribution-analysis, reporting, funnel-analysis |

## **Objective**

Unify performance data from Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads, and DV360 into a single normalized reporting layer. Automate cross-platform ROAS/CPA comparison, anomaly detection on spend and performance metrics, creative fatigue identification, budget pacing monitoring, and search term analysis with negative keyword recommendations. Produce daily/weekly performance snapshots and flag accounts requiring immediate attention.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions paid media, ad performance, Google Ads, Meta Ads, Facebook Ads, LinkedIn Ads, TikTok Ads, DV360, SEM, PPC, display advertising, programmatic, ROAS, CPA, CPM, CPC, CTR, ad spend, budget pacing, creative fatigue, ad creative, quality score, search terms, negative keywords, bid strategy, campaign optimization, ad copy analysis, or audience targeting performance. Also trigger on ‘how are our ads performing’ or ‘are we on track with ad spend.’*

## **Functional Scope**

* Cross-platform normalization: unify metrics across Google, Meta, LinkedIn, TikTok, DV360 taxonomies

* Anomaly detection: Z-score and isolation forest methods on spend, CPA, CTR, conversion rate

* Creative fatigue: detect declining CTR/conversion curves per creative, recommend rotation schedule

* Budget pacing: daily spend vs plan tracking with projected month-end variance and alerts

* Search term analysis: identify high-spend low-conversion terms, generate negative keyword lists

* Audience performance: segment ROAS by demographic, interest, placement, device, and time-of-day

## **Key Capabilities**

**Data Normalization**

* Map platform-specific metrics to unified taxonomy: impressions, clicks, spend, conversions, revenue

* Handle attribution window differences (Meta 7-day click vs Google 30-day) with transparent labeling

* Currency normalization for multi-market campaigns

**Performance Analysis**

* Cross-platform efficiency comparison: ROAS, CPA, CPM, CPC benchmarked against targets and history

* Campaign-level performance decomposition: volume × efficiency matrix for prioritization

* Automated insight generation: ‘Search CPA increased 23% WoW driven by broad match expansion in Campaign X’

**Anomaly Detection & Alerting**

* Statistical anomaly detection using rolling Z-scores and seasonal decomposition

* Configurable alert thresholds for spend overrun, CPA spike, CTR drop, conversion rate decline

* Root cause analysis: drill from alert to campaign, ad group, and keyword level

**Creative & Search Intelligence**

* Creative fatigue scoring: declining performance curves with suggested rotation timing

* Search term mining: high-impression low-conversion terms flagged as negative keyword candidates

* Ad copy performance comparison: headline/description element-level analysis

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/campaign\_spend\_{platform}.csv — Platform-specific campaign data from data-extraction

* workspace/raw/search\_terms\_{platform}.csv — Search term reports (Google, Microsoft)

* workspace/raw/creative\_performance\_{platform}.csv — Creative-level metrics

**Outputs**

* workspace/processed/unified\_media\_performance.csv — Normalized cross-platform dataset

* workspace/analysis/media\_anomalies.json — Flagged anomalies with severity, metric, and root cause

* workspace/analysis/creative\_fatigue.json — Creative health scores and rotation recommendations

* workspace/analysis/negative\_keywords.json — Recommended negative keywords with waste estimates

* workspace/reports/media\_performance\_snapshot.html — Cross-platform performance dashboard

## **Reference Files**

* references/platform\_api\_mapping.md — Metric taxonomy mapping across Google, Meta, LinkedIn, TikTok, DV360

* references/anomaly\_detection.md — Z-score, isolation forest, and seasonal decomposition methods

* references/creative\_fatigue.md — Fatigue detection methodology and rotation heuristics

* shared/schemas/data\_contracts.md — Unified media schema (campaign\_id, platform, date, metric, value)

## **Scripts (Deterministic Computation)**

* scripts/normalize\_platforms.py — Map platform-specific data to unified schema

* scripts/detect\_anomalies.py — Rolling Z-score and isolation forest anomaly detection

* scripts/creative\_fatigue.py — Time-series regression on creative performance curves

* scripts/search\_term\_analysis.py — Waste identification and negative keyword extraction

* scripts/budget\_pacing.py — Daily pacing calculation with month-end projection

## **Cross-Skill Integration**

Paid media is the primary data producer for attribution-analysis, feeding normalized spend data for MMM channel decomposition. Budget optimization outputs from attribution-analysis directly inform this skill’s pacing targets. Creative performance feeds into the reporting skill for executive dashboards. Funnel-analysis consumes landing page conversion rates from paid media click-throughs. The data-extraction skill handles raw API calls; paid-media operates on the extracted data.

## **Financial Services Considerations**

* Financial product advertising must comply with SEC/FINRA truth-in-advertising rules

* Ad creative for investment products must include required risk disclosures — flag ads missing disclaimers

* Audience targeting for financial products must avoid prohibited discriminatory practices (ECOA, fair lending)

* All ad copy and landing pages must be archived per SEC Rule 17a-4 — trigger compliance-review for new creatives

## **Development Guidelines**

13. Use MCP servers (google-analytics-mcp, meta-ads-mcp) for live data where available; fall back to CSV upload

14. Anomaly detection must account for day-of-week seasonality and known events (Black Friday, quarter-end) to avoid false positives

15. Creative fatigue algorithm must use conversion-weighted CTR, not raw CTR, to avoid flagging top-of-funnel creatives incorrectly

16. Budget pacing projection must use exponential smoothing, not simple linear extrapolation, to handle intra-month spend patterns

17. All monetary calculations must use decimal arithmetic (Python Decimal) to avoid floating-point rounding errors

18. Support incremental data updates (append new dates) rather than requiring full history reload each time

## **Acceptance Criteria**

* Platform normalization correctly maps 95%+ of standard metrics across Google, Meta, LinkedIn, TikTok

* Anomaly detection achieves precision \> 80% and recall \> 70% on labeled test dataset of historical spend anomalies

* Budget pacing projection achieves mean absolute percentage error \< 8% on month-end spend prediction (measured at day 15\)

* Creative fatigue detection flags fatiguing creatives at least 3 days before CTR drops below 50% of peak

* Search term negative keyword recommendations capture 90%+ of identified wasted spend

# **Skill 4: Dashboard & Reporting Automation**

*Automated executive dashboards, cross-skill synthesis, and natural language insight generation*

| Skill ID | reporting |
| :---- | :---- |
| **Priority** | P0 — Foundational (integration layer for all skills) |
| **Category** | Reporting & Visualization |
| **Depends On** | All other skills (consumes their outputs) |
| **Feeds Into** | compliance-review (in FS mode), stakeholder distribution |

## **Objective**

Serve as the universal reporting layer for the entire skill portfolio. Aggregate outputs from every analytical skill into cohesive executive dashboards, weekly performance summaries, and ad-hoc analysis reports. Generate natural language insights that translate statistical results into business-language recommendations. Support HTML interactive dashboards, XLSX data exports, PPTX presentation decks, and DOCX narrative reports. Automate recurring report generation with configurable schedules and distribution lists.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions dashboard, report, executive summary, performance summary, weekly report, monthly report, data visualization, chart, graph, KPI dashboard, marketing scorecard, insight generation, report automation, stakeholder update, board deck, or performance review. Also trigger on ‘summarize our marketing performance’ or ‘create a deck for leadership.’ This skill consumes outputs from all other skills in the portfolio.*

## **Functional Scope**

* Cross-skill output aggregation and synthesis into unified narratives

* Interactive HTML dashboards with plotly/D3.js visualizations

* Natural language insight generation: translate stats into business recommendations

* Multi-format output: HTML, XLSX (via xlsx skill), PPTX (via pptx skill), DOCX (via docx skill)

* Anomaly-driven reporting: auto-highlight metrics that deviate from targets or historical trends

* Configurable report templates: weekly snapshot, monthly deep-dive, quarterly business review, ad-hoc analysis

## **Key Capabilities**

**Data Aggregation**

* Discover and load all workspace/analysis/\*.json files from completed skill runs

* Merge metrics across skills into unified KPI framework with consistent date alignment

* Compute derived metrics: blended ROAS, portfolio-level conversion rate, weighted CLV

**Visualization**

* Generate interactive plotly charts: time series, waterfall, funnel, scatter, heatmap

* Automated chart selection based on metric type: trends for time series, bars for comparisons, funnels for conversion

* Responsive HTML layout with drill-down capability and tooltip interactivity

**Insight Generation**

* Statistical summarization: identify top movers, trend reversals, and anomalies across all metrics

* Natural language interpretation: translate effect sizes and p-values into plain-English recommendations

* Priority-ranked insight list: order findings by business impact magnitude

**Distribution**

* Generate self-contained HTML files that work offline (all assets inlined)

* Export data tables to XLSX for stakeholder manipulation

* Produce PPTX presentation-ready slides from key insights and charts

## **Input / Output Data Contracts**

**Inputs**

* workspace/analysis/\*.json — All analytical outputs from other skills

* workspace/reports/\*.html — Existing skill-level reports to aggregate

* references/report\_templates/ — Configurable templates for different report types

**Outputs**

* workspace/reports/executive\_dashboard.html — Interactive cross-skill dashboard

* workspace/reports/weekly\_summary.html — Weekly performance snapshot with insights

* workspace/reports/data\_export.xlsx — Underlying data tables for all metrics

* workspace/reports/leadership\_deck.pptx — Presentation-ready slide deck

## **Reference Files**

* references/report\_templates.md — Template configurations for weekly/monthly/quarterly reports

* references/visualization\_guide.md — Chart type selection rules, color palettes, accessibility standards

* references/insight\_patterns.md — Pattern library for translating statistical results to business language

* shared/schemas/data\_contracts.md — Unified metric schema consumed from all skills

## **Scripts (Deterministic Computation)**

* scripts/aggregate\_outputs.py — Discover and merge workspace/analysis files into unified dataset

* scripts/generate\_charts.py — Plotly chart generation with automated type selection

* scripts/generate\_insights.py — Statistical pattern detection and natural language templating

* scripts/build\_dashboard.py — Assemble HTML dashboard from charts, tables, and insight narratives

## **Cross-Skill Integration**

The reporting skill is the terminal node in most workflow chains. It consumes MMM contribution decompositions from attribution-analysis, experiment results from experimentation, media performance from paid-media, segment profiles from audience-segmentation, CLV distributions from clv-modeling, funnel conversion rates from funnel-analysis, and compliance flags from compliance-review. Its ability to synthesize across skills is its core value proposition. It also delegates to the docx, pptx, and xlsx skills for document formatting when producing Word, PowerPoint, or Excel outputs.

## **Financial Services Considerations**

* All reports containing performance claims must pass through compliance-review before distribution

* Investment performance reporting must follow GIPS standards where applicable

* Disclaimers and disclosures must appear on every page/slide containing return or performance data

* Reports distributed to external audiences must be archived per SEC Rule 17a-4

## **Development Guidelines**

19. Generate self-contained HTML with inlined CSS/JS and base64-encoded images for offline viewing

20. All charts must be accessible: include alt text, use colorblind-safe palettes, support screen readers

21. Natural language insights must cite the specific metric, magnitude, and time period — never vague claims

22. Template system must be extensible: users should be able to add new report types without modifying core scripts

23. Implement progressive report generation: produce a summary within 30 seconds, enrich with deep analysis over next 2 minutes

24. Use the docx, pptx, and xlsx skills via their existing SKILL.md conventions when generating those file types

## **Acceptance Criteria**

* Dashboard aggregates outputs from at least 5 different skill analysis files into a unified view

* Interactive HTML dashboard loads in under 3 seconds in a modern browser with 50+ charts

* Natural language insights correctly identify the top 3 movers by magnitude across all metrics

* PPTX output produces presentation-ready slides that render correctly in PowerPoint and Google Slides

* Report generation completes within 120 seconds for a full portfolio of skill outputs

# **Skill 5: Customer Lifetime Value Modeling**

*Probabilistic CLV prediction using BG/NBD and Gamma-Gamma models with Bayesian extensions*

| Skill ID | clv-modeling |
| :---- | :---- |
| **Priority** | P1 — Strategic (drives acquisition and retention decisions) |
| **Category** | Customer Analytics |
| **Depends On** | data-extraction, audience-segmentation (enrichment) |
| **Feeds Into** | audience-segmentation (value dimension), paid-media (acquisition targets), email-analytics (lifecycle), reporting |

## **Objective**

Implement probabilistic customer lifetime value modeling using BG/NBD for purchase frequency prediction and Gamma-Gamma for monetary value estimation. Produce customer-level CLV predictions with confidence intervals, CLV:CAC ratio calculations, cohort-level CLV curves, and at-risk high-value customer alerts. Support both contractual (subscription) and non-contractual (transactional) business models.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions CLV, LTV, customer lifetime value, customer value prediction, lifetime revenue, CLV:CAC ratio, BG/NBD, Gamma-Gamma, RFM summary, purchase frequency prediction, monetary value prediction, churn probability, customer retention modeling, expected transactions, customer-level forecasting, or high-value customer identification. Also trigger on ‘which customers are most valuable’ or ‘predict future customer revenue.’*

## **Functional Scope**

* RFM summary generation from raw transaction data (recency, frequency, monetary, tenure)

* BG/NBD model for expected future purchases and probability-alive estimation

* Gamma-Gamma model for expected average monetary value per transaction

* Combined CLV \= E\[transactions\] × E\[monetary value\] × margin with discount rate

* Bayesian extensions via PyMC-Marketing for full posterior CLV distributions

* Contractual CLV: Beta-Geometric/Beta-Binomial for subscription churn modeling

## **Key Capabilities**

**Data Preparation**

* Generate RFM summaries from transaction-level data: recency, frequency, T (tenure), monetary value

* Handle repeat vs first purchase separation for Gamma-Gamma monetary value estimation

* Detect and flag data quality issues: duplicate transactions, negative amounts, impossible dates

**Model Fitting**

* Fit BG/NBD model via maximum likelihood (lifetimes library) or MCMC (PyMC-Marketing)

* Fit Gamma-Gamma model conditional on BG/NBD frequency estimates

* Fit Beta-Geometric model for contractual/subscription customer bases

* Validate models with holdout period prediction accuracy (MAE, RMSE on future transactions)

**Prediction & Scoring**

* Generate customer-level CLV predictions for configurable time horizons (6, 12, 24 months)

* Compute probability-alive scores for all customers with confidence intervals

* Calculate CLV:CAC ratios when acquisition cost data is available from paid-media skill

* Identify at-risk high-value customers: high CLV but declining probability-alive

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/transactions.csv — Transaction-level data (customer\_id, date, amount)

* workspace/raw/subscriptions.csv — Optional: subscription start/end dates for contractual models

* workspace/analysis/acquisition\_costs.json — Optional: per-customer or per-segment CAC from paid-media

**Outputs**

* workspace/analysis/clv\_predictions.json — Customer-level CLV predictions with confidence intervals

* workspace/analysis/clv\_segments.json — CLV-based customer tiers (top 10%, top 25%, etc.)

* workspace/analysis/at\_risk\_customers.json — High-value customers with declining engagement signals

* workspace/reports/clv\_analysis.html — CLV distribution charts, cohort curves, model diagnostics

## **Reference Files**

* references/clv\_methodology.md — BG/NBD, Gamma-Gamma, and Beta-Geometric model theory and formulas

* references/pymc\_marketing\_clv.md — PyMC-Marketing CLV class reference and Bayesian extension patterns

* shared/schemas/data\_contracts.md — Transaction and customer schema definitions

## **Scripts (Deterministic Computation)**

* scripts/rfm\_summary.py — Generate RFM summaries from raw transaction data

* scripts/fit\_bgnbd.py — BG/NBD and Gamma-Gamma model fitting with lifetimes/PyMC-Marketing

* scripts/predict\_clv.py — Customer-level CLV prediction with configurable horizon and discount rate

* scripts/validate\_clv.py — Holdout period prediction accuracy assessment

## **Cross-Skill Integration**

CLV predictions add a value dimension to audience-segmentation, enabling value-weighted segment definitions. Paid-media uses CLV:CAC ratios to set acquisition bid targets by segment. Email-analytics uses probability-alive scores to trigger re-engagement campaigns for at-risk customers. Attribution-analysis uses CLV as an outcome variable for long-term channel effectiveness assessment. The reporting skill includes CLV trends in executive dashboards.

## **Financial Services Considerations**

* CLV models for financial services must account for multi-product relationships (checking \+ savings \+ investment)

* AUM-based CLV must use fee schedules rather than transaction frequency as the monetary component

* Advisor-intermediated sales require relationship-level CLV aggregation, not individual account CLV

* CLV predictions used in marketing targeting must comply with fair lending and equal opportunity regulations

## **Development Guidelines**

25. Use the lifetimes library for MLE-based models; PyMC-Marketing for Bayesian posteriors

26. Always validate with a temporal holdout: fit on first N months, predict next M months, compare to actuals

27. Gamma-Gamma model requires frequency \> 0; clearly document exclusion of one-time purchasers

28. Discount rate should default to WACC or cost of capital; make it a configurable parameter

29. CLV confidence intervals must be computed, not just point estimates — use bootstrapping or posterior sampling

30. For financial services, implement AUM-weighted CLV variant alongside transaction-based CLV

## **Acceptance Criteria**

* BG/NBD holdout period prediction MAE is within 20% of the calibration period error

* CLV:CAC calculation correctly handles missing acquisition cost data with transparent flagging

* At-risk identification flags customers whose probability-alive dropped below 50% within the last quarter

* Full pipeline from transaction data to CLV predictions executes in under 90 seconds for 500K customers

* Bayesian CLV posteriors produce narrower intervals than bootstrapped MLE estimates on identical data

# **Skill 6: Customer Segmentation & Cohort Analysis**

*Automated RFM scoring, behavioral clustering, and cohort retention analysis*

| Skill ID | audience-segmentation |
| :---- | :---- |
| **Priority** | P1 — Strategic (used by most downstream skills) |
| **Category** | Customer Analytics |
| **Depends On** | data-extraction, clv-modeling (value enrichment) |
| **Feeds Into** | experimentation (stratification), email-analytics (targeting), paid-media (lookalike), reporting |

## **Objective**

Automate customer segmentation through RFM scoring, behavioral K-Means/DBSCAN clustering with silhouette-based cluster count optimization, and cohort-based retention analysis. Assign interpretable segment labels, track segment migration over time, generate cohort retention curves, and produce segment profiles suitable for targeting in email campaigns and paid media lookalike audiences.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions segmentation, customer segments, cohort analysis, RFM analysis, behavioral clustering, K-Means, DBSCAN, customer personas, segment profiles, retention curves, cohort retention, segment migration, customer tiers, high-value customers, at-risk segment, churn cohort, acquisition cohort, engagement tiers, or audience definition. Also trigger on ‘group our customers’ or ‘which customers should we target.’*

## **Functional Scope**

* RFM scoring: quintile-based recency, frequency, monetary scoring with composite RFM score

* Behavioral clustering: K-Means and DBSCAN with automated feature scaling and cluster count selection

* Cohort retention: acquisition cohort definition, retention curve generation, churn rate calculation

* Segment profiling: demographic, behavioral, and value-based segment descriptions

* Migration tracking: segment transition matrices showing customer movement between segments over time

* Actionable targeting: segment-to-campaign mapping recommendations for email and paid media

## **Key Capabilities**

**RFM Analysis**

* Compute recency (days since last transaction), frequency (transaction count), monetary (total/average spend)

* Assign quintile scores (1–5) per dimension with configurable quantile boundaries

* Map composite RFM scores to named segments: Champions, Loyal, Potential Loyalists, At-Risk, Hibernating, Lost

**Behavioral Clustering**

* Feature engineering from raw behavioral data: session frequency, page depth, content affinity, channel preference

* StandardScaler \+ PCA dimensionality reduction before clustering for stability

* Elbow method \+ silhouette score for optimal cluster count determination (K-Means)

* DBSCAN for irregular-shaped clusters with automated epsilon estimation via k-distance plot

**Cohort Analysis**

* Define cohorts by acquisition month, first-product, or first-channel

* Generate period-over-period retention matrices (monthly, weekly)

* Compute cohort-level metrics: retention rate, revenue per user, LTV trajectory

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/transactions.csv — Transaction data (customer\_id, date, amount, product)

* workspace/raw/behavioral\_events.csv — Optional: web/app events (user\_id, event, timestamp, properties)

* workspace/analysis/clv\_predictions.json — Optional: CLV scores from clv-modeling for value enrichment

**Outputs**

* workspace/processed/segments.json — Customer-level segment assignments with profiles

* workspace/analysis/segment\_profiles.json — Aggregate statistics per segment (size, avg CLV, behavior summary)

* workspace/analysis/cohort\_retention.json — Retention matrices by cohort definition

* workspace/analysis/segment\_migration.json — Transition matrices showing segment movement

* workspace/reports/segmentation\_report.html — Interactive segment explorer with charts

## **Reference Files**

* references/rfm\_methodology.md — RFM scoring rules, segment label mapping, quintile boundary guidance

* references/clustering\_guide.md — K-Means, DBSCAN, silhouette optimization, feature scaling best practices

* shared/schemas/data\_contracts.md — Customer and transaction schema, segment output schema

## **Scripts (Deterministic Computation)**

* scripts/rfm\_scoring.py — RFM computation, quintile assignment, segment labeling

* scripts/behavioral\_clustering.py — Feature engineering, scaling, clustering, silhouette optimization

* scripts/cohort\_retention.py — Cohort definition, retention matrix generation, churn rate calculation

* scripts/segment\_migration.py — Period-over-period segment transition matrix computation

## **Cross-Skill Integration**

Segmentation is a foundational enabler for most downstream skills. The experimentation skill uses segments for stratified randomization and subgroup analysis. Email-analytics targets segments with personalized lifecycle flows. Paid-media builds lookalike audiences from high-value segments. CLV-modeling enriches segments with a value dimension. The reporting skill includes segment trends in executive dashboards. Compliance-review validates that segment-based targeting in financial services avoids prohibited discrimination.

## **Financial Services Considerations**

* Segmentation criteria must not use prohibited characteristics (race, religion, national origin) even indirectly

* Investor accreditation status may be a segmentation dimension but requires special handling under Reg D

* AUM-based tiering must align with firm’s stated service model and fiduciary obligations

* Segment-based marketing targeting must be documented for fair lending examination readiness

## **Development Guidelines**

31. Use scikit-learn for all clustering; provide deterministic random seeds for reproducibility

32. RFM quintile boundaries should be recomputed monthly to account for distribution drift

33. Behavioral clustering features must be normalized (StandardScaler) before distance-based algorithms

34. Always produce both statistical clusters and business-interpretable RFM segments; let the user choose

35. Segment profiles must include size (count and percentage), top behavioral indicators, and average CLV

36. Migration tracking requires consistent segment definitions across periods; document any re-clustering decisions

## **Acceptance Criteria**

* RFM scoring assigns all customers to exactly one of the defined named segments

* K-Means silhouette optimization selects cluster count within the range producing silhouette score \> 0.3

* Cohort retention matrices are mathematically consistent: no cohort exceeds 100% retention

* Segment migration matrix rows sum to 100% (all customers accounted for across periods)

* Segment profiles correctly compute all aggregate statistics verified against manual SQL queries

# **Skill 7: Funnel Analysis & Conversion Optimization**

*Multi-step funnel tracking, bottleneck identification, and revenue impact estimation*

| Skill ID | funnel-analysis |
| :---- | :---- |
| **Priority** | P1 — Tactical (direct conversion impact) |
| **Category** | Conversion Analytics |
| **Depends On** | data-extraction, web-analytics |
| **Feeds Into** | experimentation (CRO hypotheses), reporting, paid-media (landing page optimization) |

## **Objective**

Automate multi-step conversion funnel analysis with statistical significance testing on drop-off rates, cohort-based funnel comparison, and automated bottleneck identification. Estimate revenue impact per funnel improvement to enable prioritization. Support both linear (e.g., landing page → signup → activation) and branching funnels (e.g., multiple entry points converging to purchase).

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions funnel, conversion funnel, drop-off, drop off, conversion rate, conversion optimization, CRO, bottleneck, funnel analysis, checkout flow, signup flow, onboarding funnel, activation funnel, abandonment, cart abandonment, form abandonment, user flow, step completion, or funnel comparison. Also trigger on ‘where are we losing people’ or ‘why is conversion low.’*

## **Functional Scope**

* Multi-step funnel definition from event-level data with configurable step sequences

* Stage-by-stage drop-off calculation with statistical confidence intervals

* Cohort-based funnel comparison: new vs returning, segment A vs B, period-over-period

* Automated bottleneck identification: rank stages by drop-off severity × volume

* Revenue impact estimation: projected revenue gain per percentage point improvement at each stage

* Time-to-convert analysis: median and distribution of time between funnel stages

## **Key Capabilities**

**Funnel Construction**

* Define funnels from event sequences with configurable time windows between steps

* Support both strict (ordered) and relaxed (any order) step sequences

* Handle session-based and user-based funnel aggregation

**Analysis**

* Compute stage-wise conversion rates with Wilson score confidence intervals

* Compare funnel performance across segments, cohorts, or time periods with chi-squared tests

* Rank bottlenecks by composite score: drop-off magnitude × traffic volume × revenue proximity

**Optimization**

* Estimate revenue impact per stage improvement using historical revenue-per-converter

* Generate CRO hypothesis backlog: specific observations about each bottleneck with test suggestions

* Time-to-convert distribution analysis: identify stages where delays correlate with abandonment

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/events.csv — Event-level data (user\_id, event\_name, timestamp, properties)

* workspace/processed/segments.json — Optional: segments from audience-segmentation for comparison

* workspace/raw/revenue.csv — Optional: revenue per converter for impact estimation

**Outputs**

* workspace/analysis/funnel\_results.json — Stage-by-stage conversion rates, drop-offs, CIs

* workspace/analysis/bottleneck\_ranking.json — Priority-ranked bottleneck list with impact estimates

* workspace/analysis/cro\_hypotheses.json — Generated test ideas linked to bottleneck findings

* workspace/reports/funnel\_report.html — Interactive funnel visualization with drill-down

## **Reference Files**

* references/funnel\_methodology.md — Funnel construction rules, confidence interval formulas, bottleneck scoring

* references/cro\_patterns.md — Common CRO patterns and hypothesis templates by funnel stage

* shared/schemas/data\_contracts.md — Event schema, funnel definition schema

## **Scripts (Deterministic Computation)**

* scripts/build\_funnel.py — Funnel construction from event sequences with time window filtering

* scripts/funnel\_stats.py — Conversion rates, CIs, chi-squared comparison, bottleneck scoring

* scripts/revenue\_impact.py — Revenue projection per stage improvement

## **Cross-Skill Integration**

Funnel analysis generates CRO hypotheses that feed directly into the experimentation skill as test candidates. Web-analytics provides the behavioral event stream that funnels are built from. Audience-segmentation enables segment-level funnel comparison. Paid-media landing page performance is a key funnel entry point. The reporting skill includes funnel conversion trends in dashboards.

## **Financial Services Considerations**

* Account opening funnels in financial services see 50–70% abandonment; KYC/AML steps are mandatory and cannot be optimized away

* Funnel optimization must preserve all required regulatory disclosure steps and consent flows

* Investment product purchase funnels must maintain suitability questionnaire integrity

## **Development Guidelines**

37. Use Wilson score intervals for conversion rate CIs (more accurate than normal approximation at low rates)

38. Funnel definitions must be configurable without code changes — store as JSON/YAML step sequences

39. Time-to-convert analysis must handle censored data (users still in funnel at analysis time)

40. Revenue impact should use conservative estimates: 50th percentile of improvement range, not optimistic

41. Support both GA4 event export format and generic event CSV to maximize data source flexibility

42. Bottleneck scoring formula must be documented and adjustable: default to drop-off\_rate × sqrt(volume) × revenue\_proximity

## **Acceptance Criteria**

* Funnel construction correctly handles time-window constraints (users who don’t complete within window are counted as dropped)

* Wilson score CIs are statistically accurate: coverage verified via simulation at 95% nominal level

* Bottleneck ranking agrees with manual expert assessment on 80%+ of top-3 bottleneck identifications

* Revenue impact estimates are within 25% of actual observed revenue change when a bottleneck is subsequently fixed

* Funnel comparison correctly identifies statistically significant differences between segments at p \< 0.05

# **Skill 8: Email Marketing Analytics**

*Deliverability monitoring, engagement analysis, lifecycle flow optimization, and send-time intelligence*

| Skill ID | email-analytics |
| :---- | :---- |
| **Priority** | P1 — Tactical (direct revenue channel in financial services) |
| **Category** | Channel Analytics |
| **Depends On** | data-extraction, audience-segmentation, experimentation |
| **Feeds Into** | reporting, compliance-review (in FS mode) |

## **Objective**

Provide comprehensive email marketing analytics: deliverability health monitoring (bounce rates, blocklist checks, authentication compliance), engagement analysis prioritizing click-based metrics over unreliable open rates, lifecycle flow performance optimization, send-time intelligence, and subject line performance analysis. Delegate all statistical testing of email experiments to the experimentation skill.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions email analytics, email performance, open rate, click rate, deliverability, bounce rate, unsubscribe rate, email engagement, lifecycle email, drip campaign, email automation, send-time optimization, subject line testing, email A/B test, email deliverability, SPF, DKIM, DMARC, email blocklist, inbox placement, email revenue attribution, or email segmentation. Also trigger on ‘how are our emails performing’ or ‘improve email engagement.’*

## **Functional Scope**

* Deliverability monitoring: bounce rate trends, blocklist status, SPF/DKIM/DMARC compliance checking

* Engagement analysis: click rate as primary metric (post-iOS 15), revenue per email, unsubscribe trends

* Lifecycle flow analysis: per-flow conversion rates, time-between-sends optimization, sequence length testing

* Send-time intelligence: historical engagement heatmaps by day-of-week and hour for optimal scheduling

* Subject line analysis: word-level and structure-level performance patterns

* List health: inactive subscriber identification, re-engagement campaign triggers, list hygiene scoring

## **Key Capabilities**

**Deliverability**

* Track hard/soft bounce rates with automated spike detection and root cause suggestions

* Monitor domain reputation indicators and blocklist status

* Validate SPF, DKIM, and DMARC authentication records and flag misconfigurations

**Engagement**

* Calculate click-to-delivered rate (CTDR) as primary engagement metric, de-emphasizing open rates

* Revenue attribution: track downstream conversion and revenue from email click-throughs

* Engagement decay analysis: identify subscribers whose engagement is declining before they churn

**Optimization**

* Generate send-time heatmaps from historical click data by audience segment

* Lifecycle flow throughput analysis: identify flows with highest and lowest conversion efficiency

* Subject line pattern analysis: length, personalization, emoji, urgency words correlated with clicks

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/email\_sends.csv — Send-level data (campaign\_id, send\_time, recipient, delivered, bounced, opened, clicked, converted)

* workspace/processed/segments.json — Segment definitions from audience-segmentation for segment-level analysis

* workspace/raw/email\_flows.csv — Lifecycle flow definitions (flow\_id, step\_number, trigger, delay)

**Outputs**

* workspace/analysis/email\_deliverability.json — Deliverability health scores and issue flags

* workspace/analysis/email\_engagement.json — Campaign and flow-level engagement metrics

* workspace/analysis/send\_time\_heatmap.json — Optimal send-time recommendations by segment

* workspace/analysis/list\_health.json — Inactive subscriber identification and re-engagement targets

* workspace/reports/email\_performance.html — Email analytics dashboard with deliverability, engagement, and flow charts

## **Reference Files**

* references/email\_metrics.md — Metric definitions, post-iOS-15 measurement guidance, industry benchmarks

* references/deliverability\_guide.md — SPF/DKIM/DMARC validation rules, blocklist remediation procedures

* references/lifecycle\_patterns.md — Email lifecycle flow best practices and benchmark conversion rates

* shared/schemas/data\_contracts.md — Email event schema (send, deliver, bounce, open, click, convert)

## **Scripts (Deterministic Computation)**

* scripts/deliverability\_check.py — Bounce rate trend analysis, authentication record validation

* scripts/engagement\_analysis.py — CTDR calculation, revenue attribution, engagement decay detection

* scripts/send\_time\_optimizer.py — Historical engagement heatmap generation by segment and day/hour

* scripts/list\_health.py — Inactive subscriber scoring, re-engagement trigger identification

## **Cross-Skill Integration**

Email analytics delegates all A/B testing (subject lines, send times, content variants) to the experimentation skill rather than implementing its own statistical tests. Audience-segmentation provides targeting segments for performance comparison. CLV probability-alive scores trigger re-engagement flows for at-risk high-value customers. The reporting skill includes email trends in cross-channel dashboards. In financial services mode, all email content and experiment variants must pass compliance-review.

## **Financial Services Considerations**

* All email content for investment products must include required regulatory disclosures and disclaimers

* CAN-SPAM compliance is mandatory; additionally SEC archival rules apply to all investor communications

* Email experiment variants must preserve all compliance-required elements across all variants

* Transactional emails (statements, confirmations) have different regulatory requirements than marketing emails

## **Development Guidelines**

43. Prioritize click-to-delivered rate over open rate as the primary engagement metric due to iOS 15 / Mail Privacy Protection unreliability

44. Send-time optimization must account for time zones in multi-region campaigns

45. Deliverability monitoring should support both ESP API integration (Braze, SendGrid, Iterable) and CSV upload

46. Inactive subscriber threshold should be configurable; default to 90 days without click activity

47. Subject line analysis must use statistical tests (chi-squared on click rates), not just observational patterns

48. Revenue attribution must use consistent attribution windows matching the organization’s standard model

## **Acceptance Criteria**

* Deliverability check correctly identifies misconfigured SPF/DKIM/DMARC records against DNS lookup

* Engagement analysis produces CTDR calculations that match ESP-reported metrics within 1% tolerance

* Send-time heatmap correctly identifies the top 3 send-time windows verified against held-out test sends

* Inactive subscriber identification correctly flags 95%+ of subscribers with zero clicks in the configured lookback period

* Email analytics delegates experiment analysis to experimentation skill via proper workspace file handoff

# **Skill 9: Web Analytics & Behavioral Analysis**

*GA4 data extraction, behavioral pattern detection, anomaly detection, and predictive audiences*

| Skill ID | web-analytics |
| :---- | :---- |
| **Priority** | P1 — Tactical (foundational data layer) |
| **Category** | Digital Analytics |
| **Depends On** | data-extraction |
| **Feeds Into** | funnel-analysis, seo-content, paid-media, audience-segmentation, reporting |

## **Objective**

Extract and analyze web behavioral data from GA4 (via the official MCP server or API), Mixpanel, and Amplitude. Automate traffic and conversion anomaly detection, user behavior pattern identification, session flow analysis, and predictive audience creation. Serve as the foundational behavioral data layer that feeds funnel analysis, SEO, paid media landing page optimization, and segmentation.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions web analytics, GA4, Google Analytics, site traffic, page views, sessions, bounce rate, engagement rate, user behavior, session flow, site speed, traffic sources, acquisition channels, landing page performance, conversion tracking, UTM parameters, event tracking, behavioral analysis, Mixpanel, Amplitude, user journey, click path, scroll depth, or heatmap data. Also trigger on ‘what’s happening on our website’ or ‘where is traffic coming from.’*

## **Functional Scope**

* GA4 data extraction via google-analytics-mcp or Data API with automated report building

* Traffic and conversion anomaly detection using seasonal decomposition and Z-scores

* User behavior pattern detection: high-engagement paths, exit page analysis, content affinity

* Session flow analysis: common navigation paths, unexpected loops, dead-end identification

* Predictive audience identification: propensity-to-convert and propensity-to-churn scoring

* Page performance: load time correlation with bounce rate, mobile vs desktop behavioral differences

## **Key Capabilities**

**Data Extraction**

* Connect to GA4 via official MCP server or Data API for automated report retrieval

* Support Mixpanel and Amplitude event export formats for multi-platform analysis

* Automated UTM parameter validation and source/medium normalization

**Behavioral Analysis**

* Identify high-conversion navigation paths using Markov chain transition analysis

* Exit page analysis: rank pages by exit rate weighted by conversion proximity

* Content affinity scoring: which content categories correlate with downstream conversion

**Anomaly Detection**

* Daily traffic and conversion rate anomaly detection with seasonal adjustment

* Automated root cause decomposition: break anomaly into source, device, geography, and page contributions

* Configurable alert thresholds with suppression for known events (holidays, launches)

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/ga4\_reports.csv — GA4 report data from data-extraction or MCP server

* workspace/raw/events.csv — Event-level data from GA4, Mixpanel, or Amplitude

**Outputs**

* workspace/processed/web\_metrics.json — Normalized web analytics metrics (traffic, engagement, conversion)

* workspace/analysis/web\_anomalies.json — Detected anomalies with root cause decomposition

* workspace/analysis/navigation\_paths.json — Common user paths with conversion correlation scores

* workspace/analysis/predictive\_audiences.json — Propensity scores for conversion and churn

## **Reference Files**

* references/ga4\_api.md — GA4 Data API dimensions, metrics, and filter syntax

* references/behavioral\_patterns.md — Markov chain path analysis, content affinity scoring methodology

* shared/schemas/data\_contracts.md — Web event schema, traffic metric schema

## **Scripts (Deterministic Computation)**

* scripts/extract\_ga4.py — GA4 report builder with configurable dimensions and metrics

* scripts/web\_anomaly\_detection.py — Seasonal decomposition and Z-score anomaly detection on web metrics

* scripts/path\_analysis.py — Markov chain navigation path analysis and conversion path identification

* scripts/predictive\_scoring.py — Logistic regression propensity scoring for conversion and churn

## **Cross-Skill Integration**

Web analytics is the foundational behavioral data source. Funnel-analysis builds funnels from web event sequences. SEO-content uses traffic data to measure organic search performance. Paid-media analyzes landing page conversion from ad click-throughs. Audience-segmentation incorporates behavioral features (session frequency, content affinity) into cluster models. Anomalies detected here surface in the reporting skill’s executive dashboards.

## **Financial Services Considerations**

* Financial services websites must track regulatory disclosure page views for compliance verification

* Investor portal analytics require authenticated user tracking with PII handling compliant with privacy regulations

* Cookie consent compliance (GDPR, CCPA) affects data collection; skill must flag consent rate as a data quality metric

## **Development Guidelines**

49. Prefer the google-analytics-mcp server for GA4 data when available; fall back to Data API Python client

50. Anomaly detection must use at least 8 weeks of history for stable seasonal baselines

51. Path analysis Markov chains should use second-order (bigram) transitions for more accurate modeling

52. Predictive audience scoring must validate on a temporal holdout to avoid data leakage

53. Support incremental data loading: append new date ranges without requiring full re-extraction

54. UTM parameter normalization must handle common inconsistencies: case differences, trailing spaces, encoded characters

## **Acceptance Criteria**

* GA4 data extraction successfully retrieves reports for all standard dimensions and metrics

* Anomaly detection achieves false positive rate \< 5% on a 90-day historical validation period

* Navigation path analysis correctly identifies the top 5 conversion paths verified against manual GA4 exploration

* Predictive audience scores achieve AUC \> 0.70 on temporal holdout validation for conversion propensity

# **Skill 10: SEO & Content Analytics**

*Search Console integration, keyword tracking, content performance, and AI search optimization (GEO)*

| Skill ID | seo-content |
| :---- | :---- |
| **Priority** | P1 — Tactical (organic channel growth) |
| **Category** | Channel Analytics |
| **Depends On** | data-extraction, web-analytics |
| **Feeds Into** | competitive-intel, reporting, paid-media (keyword overlap) |

## **Objective**

Automate SEO and content performance analysis: Google Search Console integration for keyword ranking and click-through data, content performance measurement by topic/category, technical SEO auditing, competitive keyword gap analysis, and the emerging AI search optimization (GEO/AIO) dimension. Track visibility across traditional search results and AI-generated answers (Google AI Overviews, ChatGPT, Perplexity).

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions SEO, search engine optimization, keyword ranking, search console, organic search, organic traffic, content performance, keyword research, keyword gap, content audit, technical SEO, backlinks, domain authority, AI Overviews, AI search, GEO, generative engine optimization, AIO, search visibility, SERP, featured snippets, content optimization, or page speed. Also trigger on ‘how is our content performing’ or ‘which keywords should we target.’*

## **Functional Scope**

* Google Search Console data extraction: queries, impressions, clicks, CTR, position by page and date

* Keyword ranking tracking: position changes, SERP feature wins/losses, new keyword discoveries

* Content performance: page-level traffic, engagement, and conversion analysis by content category/topic

* Technical SEO: Core Web Vitals assessment, crawl error identification, structured data validation

* AI Search Optimization (GEO): tracking brand/content visibility in AI Overviews, ChatGPT, Perplexity citations

* Competitive keyword gap: identify high-value keywords where competitors rank but you do not

## **Key Capabilities**

**Search Intelligence**

* Extract Search Console data via API with automated date range management

* Track keyword position changes: improvements, declines, new rankings, lost rankings

* Identify organic/paid keyword overlap: keywords where you rank organically AND run ads (cost savings opportunity)

**Content Performance**

* Map content to topic clusters and measure cluster-level organic performance

* Identify underperforming content: high impressions but low CTR (title/description optimization needed)

* Track content decay: pages with declining traffic over 3+ month trend

**AI Search (GEO)**

* Monitor brand mentions in AI-generated search results (AI Overviews, conversational AI)

* Track citation frequency and accuracy in LLM-powered search engines

* Recommend content structure optimizations for AI extractability (structured data, clear headers, factual authority)

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/search\_console.csv — GSC data (query, page, clicks, impressions, ctr, position, date)

* workspace/raw/content\_inventory.csv — Content pages with metadata (URL, title, category, publish\_date)

* workspace/processed/web\_metrics.json — Traffic and engagement from web-analytics skill

**Outputs**

* workspace/analysis/keyword\_performance.json — Keyword ranking trends, movers, new/lost rankings

* workspace/analysis/content\_performance.json — Page and topic cluster level traffic and conversion metrics

* workspace/analysis/seo\_audit.json — Technical SEO issues, Core Web Vitals, structured data gaps

* workspace/analysis/keyword\_gap.json — Competitive keyword gap analysis with opportunity scores

* workspace/reports/seo\_dashboard.html — Interactive SEO performance dashboard

## **Reference Files**

* references/search\_console\_api.md — GSC API reference, query dimensions, and filter syntax

* references/geo\_methodology.md — AI search optimization strategies, citation tracking approaches

* references/technical\_seo.md — Core Web Vitals thresholds, structured data requirements, crawl optimization

* shared/schemas/data\_contracts.md — Keyword and content performance schema

## **Scripts (Deterministic Computation)**

* scripts/extract\_gsc.py — Search Console data extraction with automated date range handling

* scripts/keyword\_tracking.py — Position change detection, mover identification, trend analysis

* scripts/content\_analysis.py — Topic cluster mapping, content decay detection, underperformer identification

* scripts/seo\_audit.py — Technical SEO checks: CWV, structured data, crawl errors

## **Cross-Skill Integration**

SEO-content shares keyword intelligence with paid-media for organic/paid overlap optimization (stop bidding on keywords where you rank \#1 organically). Competitive-intel uses keyword gap data for competitive positioning analysis. Web-analytics provides the traffic and behavioral data that measures content performance. The reporting skill includes organic search trends in cross-channel dashboards.

## **Financial Services Considerations**

* Financial services content must ensure all landing pages maintain required regulatory disclosures even after SEO optimization

* AI search citations of fund performance must be monitored for accuracy and compliance with SEC Marketing Rule

* Content targeting investment-related keywords must comply with advertising regulations before publication

## **Development Guidelines**

55. Search Console API has a 25,000 row limit per request; implement pagination for high-volume sites

56. Keyword position changes should use a 7-day rolling average to smooth daily fluctuations

57. AI search (GEO) tracking is an emerging practice; design the module to be extensible as new monitoring APIs emerge

58. Content decay detection threshold should be configurable; default to 20% traffic decline over 90 days

59. Competitive gap analysis requires third-party API access (Semrush, Ahrefs); handle missing data gracefully

60. Technical SEO checks should use Lighthouse or PageSpeed Insights API for Core Web Vitals

## **Acceptance Criteria**

* Search Console extraction handles pagination and retrieves complete dataset for sites with 50K+ queries

* Keyword mover detection correctly identifies 95%+ of keywords with position change \> 5 positions

* Content decay detection flags pages with statistically significant traffic decline (not just noise) using trend test

* Competitive keyword gap correctly identifies opportunities verified against manual Semrush/Ahrefs audit

# **Skill 11: CRM Analytics & Lead Scoring**

*Predictive lead scoring, pipeline velocity tracking, and win/loss analysis*

| Skill ID | crm-lead-scoring |
| :---- | :---- |
| **Priority** | P2 — Supporting (extends core analytics to sales pipeline) |
| **Category** | Sales & Pipeline Analytics |
| **Depends On** | data-extraction, audience-segmentation, clv-modeling |
| **Feeds Into** | email-analytics (nurture flows), paid-media (targeting), reporting |

## **Objective**

Build and maintain predictive lead scoring models that combine firmographic, demographic, and behavioral signals to predict conversion likelihood. Track pipeline velocity metrics, perform win/loss analysis, and identify pipeline bottlenecks. Support integration with Salesforce, HubSpot, and custom CRM systems.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions lead scoring, predictive scoring, lead qualification, MQL, SQL, pipeline analytics, pipeline velocity, win rate, deal velocity, sales funnel, opportunity analysis, win/loss analysis, CRM analytics, lead-to-close, conversion probability, propensity model, account scoring, or sales attribution. Also trigger on ‘which leads should sales prioritize’ or ‘why are we losing deals.’*

## **Functional Scope**

* Predictive lead scoring using logistic regression and gradient boosting on firmographic \+ behavioral features

* Pipeline velocity metrics: average deal cycle time, stage conversion rates, pipeline coverage ratio

* Win/loss analysis: identify factors correlated with won vs lost deals using feature importance

* Pipeline forecasting: weighted pipeline with probability-adjusted revenue projections

* Lead source attribution: which marketing channels produce the highest-quality leads

* Account-based scoring: company-level propensity combining multiple contact signals

## **Key Capabilities**

**Lead Scoring**

* Feature engineering from CRM fields, website behavior, email engagement, and content consumption

* Model training with logistic regression (interpretable) and gradient boosting (accuracy) with cross-validation

* SHAP-based feature importance for model explainability and score interpretation

* Score calibration: ensure predicted probabilities match observed conversion rates

**Pipeline Analytics**

* Stage-by-stage conversion rate tracking with period-over-period comparison

* Deal velocity analysis: time-in-stage distributions with outlier identification

* Pipeline coverage: compare weighted pipeline to quota/target with gap analysis

**Win/Loss Intelligence**

* Statistical comparison of won vs lost deals across all available features

* Temporal analysis: at which stage do lost deals diverge from won deals

* Competitive win/loss: when competitor is mentioned, how does win rate change

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/crm\_leads.csv — Lead/opportunity data (lead\_id, source, stage, created\_date, close\_date, amount, outcome)

* workspace/raw/lead\_activities.csv — Behavioral activities (lead\_id, activity\_type, timestamp)

* workspace/processed/segments.json — Optional: segment enrichment from audience-segmentation

**Outputs**

* workspace/analysis/lead\_scores.json — Lead-level propensity scores with feature explanations

* workspace/analysis/pipeline\_metrics.json — Pipeline velocity, conversion rates, coverage ratio

* workspace/analysis/win\_loss\_factors.json — Win/loss analysis with ranked feature importance

* workspace/reports/crm\_dashboard.html — Lead scoring and pipeline analytics dashboard

## **Reference Files**

* references/lead\_scoring\_methodology.md — Feature engineering guide, model selection criteria, calibration techniques

* references/pipeline\_metrics.md — Pipeline velocity definitions, coverage ratio benchmarks

* shared/schemas/data\_contracts.md — CRM opportunity and activity schema

## **Scripts (Deterministic Computation)**

* scripts/lead\_scoring\_model.py — Feature engineering, model training, SHAP explanation, calibration

* scripts/pipeline\_velocity.py — Stage conversion rates, deal cycle time distributions, coverage ratio

* scripts/win\_loss\_analysis.py — Feature comparison between won/lost deals, divergence point identification

## **Cross-Skill Integration**

Lead scoring models consume behavioral signals from web-analytics and email-analytics engagement data. CLV-modeling provides expected value estimates for score-weighted prioritization. Audience-segmentation enriches leads with segment membership. Paid-media uses lead quality data to optimize campaign targeting toward high-converting lead sources. The reporting skill includes pipeline health in executive dashboards.

## **Financial Services Considerations**

* Lead scoring for financial products must comply with fair lending requirements and avoid prohibited characteristics

* Advisor-mediated channels require relationship-level scoring, not just individual lead scoring

* Pipeline analytics must account for regulatory approval stages (compliance review, legal sign-off) in cycle time calculations

## **Development Guidelines**

61. Use scikit-learn for model training; always include logistic regression as an interpretable baseline alongside gradient boosting

62. SHAP values are required for model explainability; never deploy a scoring model without feature importance documentation

63. Temporal holdout validation is mandatory: train on historical data, validate on future data to simulate real-world performance

64. Score calibration must use isotonic regression or Platt scaling to ensure predicted probabilities are reliable

65. Model retraining cadence should be configurable; default to monthly with automated drift detection

66. Support both Salesforce and HubSpot field naming conventions with a mapping layer

## **Acceptance Criteria**

* Lead scoring model achieves AUC \> 0.75 on temporal holdout validation set

* Calibrated probabilities match observed conversion rates within 5 percentage points across decile bins

* SHAP feature importance correctly identifies the top 5 predictive features verified against domain expert review

* Pipeline velocity calculations match manual CRM report outputs within 2% tolerance

* Win/loss analysis identifies at least 3 statistically significant differentiating factors (p \< 0.05)

# **Skill 12: Social Media Analytics**

*Cross-platform social performance, sentiment analysis, and competitive benchmarking*

| Skill ID | social-analytics |
| :---- | :---- |
| **Priority** | P2 — Supporting (brand and awareness channel) |
| **Category** | Channel Analytics |
| **Depends On** | data-extraction |
| **Feeds Into** | competitive-intel, attribution-analysis, reporting |

## **Objective**

Aggregate performance data across social platforms (Meta, LinkedIn, TikTok, YouTube, X/Twitter), perform sentiment analysis on brand mentions, analyze content performance patterns, and benchmark against competitors. Support both organic and paid social analytics with clear delineation.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions social media analytics, social performance, Facebook insights, Instagram analytics, LinkedIn analytics, TikTok analytics, YouTube analytics, X analytics, Twitter analytics, social engagement, social reach, share of voice, social sentiment, brand mentions, social content performance, viral content, social ROI, social listening, or social benchmarking. Also trigger on ‘how are we doing on social’ or ‘what’s performing on LinkedIn.’*

## **Functional Scope**

* Cross-platform performance aggregation: impressions, engagement, reach, shares, comments, video views

* Content performance pattern analysis: post type, format, topic, timing, length correlations

* Sentiment analysis on brand mentions using NLP classification (positive, neutral, negative)

* Share of voice calculation: brand mention volume vs competitors across platforms

* Organic vs paid social delineation: separate metrics for earned vs boosted content

* Influencer/creator performance: track content partnerships and earned media value

## **Key Capabilities**

**Performance Aggregation**

* Normalize engagement metrics across platforms to comparable rates (engagement rate \= engagements / reach)

* Content type benchmarking: compare video, carousel, static image, text, story performance

* Platform-specific deep dives: LinkedIn company page analytics, YouTube channel analytics, TikTok creator metrics

**Content Intelligence**

* Topic/theme analysis: classify posts by topic and measure per-topic engagement rates

* Optimal posting cadence: engagement rate by posting frequency analysis

* Best time to post: historical engagement heatmap by platform, day, and hour

**Sentiment & Listening**

* Sentiment classification using transformer-based NLP on mentions, comments, and replies

* Trend detection: identify emerging conversation themes around your brand or category

* Crisis signal detection: sudden spike in negative sentiment with automated alert

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/social\_performance\_{platform}.csv — Platform-specific post performance data

* workspace/raw/social\_mentions.csv — Brand mentions from social listening tools

* workspace/raw/competitor\_social.csv — Competitor social metrics for benchmarking

**Outputs**

* workspace/analysis/social\_performance.json — Cross-platform engagement metrics with content analysis

* workspace/analysis/social\_sentiment.json — Sentiment scores, topic themes, crisis signals

* workspace/analysis/social\_benchmarks.json — Competitive share of voice and benchmarking data

* workspace/reports/social\_dashboard.html — Cross-platform social analytics dashboard

## **Reference Files**

* references/social\_api\_mapping.md — Metric taxonomy across Meta, LinkedIn, TikTok, YouTube, X platforms

* references/sentiment\_methodology.md — NLP sentiment classification approach and model selection

* shared/schemas/data\_contracts.md — Social post and mention schema

## **Scripts (Deterministic Computation)**

* scripts/normalize\_social.py — Cross-platform metric normalization and engagement rate calculation

* scripts/content\_analysis.py — Topic classification, content type benchmarking, timing analysis

* scripts/sentiment\_analysis.py — Sentiment scoring using transformer models on mentions/comments

* scripts/share\_of\_voice.py — Competitive mention volume and sentiment comparison

## **Cross-Skill Integration**

Social analytics feeds share-of-voice data into competitive-intel for comprehensive competitive monitoring. Attribution-analysis can include social engagement as a channel in the marketing mix model. The reporting skill aggregates social metrics alongside other channels in executive dashboards. Content performance patterns inform the seo-content skill’s content strategy recommendations.

## **Financial Services Considerations**

* Social media posts for financial services must comply with FINRA Rule 2210 communications standards

* Testimonials and endorsements on social media must follow SEC Marketing Rule disclosure requirements

* Employee social media posts about fund performance require pre-approval and archival

* Social media crisis detection should include regulatory inquiry and litigation risk signals

## **Development Guidelines**

67. Use platform APIs where available; fall back to CSV export for platforms with restricted API access

68. Sentiment analysis should use a pre-trained transformer model (e.g., cardiffnlp/twitter-roberta-base-sentiment) not simple keyword matching

69. Engagement rate normalization must account for platform-specific reach calculation differences

70. Share of voice calculations must use consistent time windows and query definitions across competitors

71. Support both organic-only and blended (organic \+ paid) views of social performance

72. Crisis detection threshold should be configurable; default to 3x standard deviation in negative sentiment volume

## **Acceptance Criteria**

* Platform normalization correctly maps engagement metrics across at least 4 major platforms

* Sentiment classification achieves F1 score \> 0.75 on a labeled social media test dataset

* Share of voice calculations are consistent when computed from the same data by independent methods

* Content type benchmarking correctly ranks content formats by engagement rate within each platform

# **Skill 13: Competitive Intelligence**

*Competitor keyword tracking, traffic estimation, ad creative monitoring, and market positioning*

| Skill ID | competitive-intel |
| :---- | :---- |
| **Priority** | P2 — Supporting (strategic awareness) |
| **Category** | Market Intelligence |
| **Depends On** | seo-content, social-analytics, paid-media |
| **Feeds Into** | attribution-analysis (control variables), reporting |

## **Objective**

Provide systematic competitive intelligence: competitor keyword ranking overlap, estimated traffic share, ad creative and messaging monitoring, share-of-voice aggregation across channels, and pricing intelligence. Synthesize competitive signals into actionable strategic recommendations.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions competitive analysis, competitor research, competitive intelligence, competitor keywords, competitor ads, share of voice, market share, competitive benchmarking, competitor traffic, competitor strategy, competitive landscape, SWOT, competitor monitoring, ad spy, competitor ad creative, pricing intelligence, or market positioning. Also trigger on ‘what are competitors doing’ or ‘how do we compare to \[competitor\].’*

## **Functional Scope**

* Competitor keyword overlap and gap analysis using SEO tool APIs (Semrush, Ahrefs, DataForSEO)

* Estimated traffic share comparison using SimilarWeb or proxy methods

* Ad creative monitoring: competitor ad copy, offers, and landing page analysis

* Aggregate share of voice: combine organic search, paid search, social, and earned media signals

* Pricing intelligence: competitor offer monitoring and promotional pattern detection

* Strategic synthesis: translate competitive data into strategic recommendations

## **Key Capabilities**

**Keyword Intelligence**

* Identify keywords where competitors rank and you don’t (gap analysis)

* Track competitor keyword position changes and new keyword targeting

* Calculate organic search share of voice based on weighted keyword rankings

**Ad & Creative Monitoring**

* Track competitor ad copy changes, offer rotations, and landing page updates

* Analyze competitor messaging themes: value propositions, CTAs, emotional appeals

* Identify seasonal patterns in competitor advertising intensity

**Market Positioning**

* Aggregate competitive signals across all channels into a unified competitive scorecard

* Trend competitor activity levels: are they accelerating or decelerating marketing investment?

* Generate strategic recommendations based on competitive gaps and opportunities

## **Input / Output Data Contracts**

**Inputs**

* workspace/analysis/keyword\_performance.json — Your keyword data from seo-content skill

* workspace/analysis/social\_benchmarks.json — Social share of voice from social-analytics

* workspace/raw/competitor\_data.csv — Third-party competitive data (Semrush, SimilarWeb, SpyFu exports)

**Outputs**

* workspace/analysis/competitive\_landscape.json — Aggregated competitive intelligence across all channels

* workspace/analysis/keyword\_gap.json — Competitive keyword opportunities with volume and difficulty scores

* workspace/analysis/competitive\_alerts.json — New competitor activities and strategy shifts detected

* workspace/reports/competitive\_briefing.html — Executive competitive intelligence briefing

## **Reference Files**

* references/competitive\_methodology.md — Share of voice calculation, competitive scoring framework

* references/data\_sources.md — Available competitive data sources, APIs, and their coverage/limitations

* shared/schemas/data\_contracts.md — Competitive data schema

## **Scripts (Deterministic Computation)**

* scripts/keyword\_gap.py — Competitor keyword overlap/gap analysis with opportunity scoring

* scripts/share\_of\_voice.py — Multi-channel share of voice aggregation

* scripts/competitive\_alerting.py — Change detection on competitor activity metrics

* scripts/competitive\_synthesis.py — Aggregate all competitive signals into strategic scorecard

## **Cross-Skill Integration**

Competitive intelligence consumes keyword data from seo-content, social benchmarks from social-analytics, and ad performance baselines from paid-media to build a comprehensive competitive picture. Competitor activity levels can serve as control variables in attribution-analysis MMM models (when a competitor increases spend, your conversion rate may change even without changes to your own activity). The reporting skill includes competitive trends in executive dashboards.

## **Financial Services Considerations**

* Competitive intelligence for financial services must avoid using non-public information or proprietary data

* Competitor performance claims (returns, AUM growth) sourced from public filings are fair game; internal estimates are not

* Ad creative monitoring should flag competitors making potentially non-compliant performance claims for internal awareness

## **Development Guidelines**

73. Design for graceful degradation: some data sources require paid subscriptions (Semrush, Ahrefs); skill should function with whatever data is available

74. Competitive keyword gap analysis should score opportunities by: search volume × (1 \- keyword difficulty) × business relevance

75. Share of voice calculations must be clearly documented with methodology notes and data source limitations

76. Change detection for competitive alerting should use percentage change, not absolute, to handle competitors of different sizes

77. Strategic recommendations must be grounded in specific data points, not generic ‘best practices’ advice

78. Support manual competitor list definition; do not auto-discover competitors to avoid scope creep

## **Acceptance Criteria**

* Keyword gap analysis correctly identifies at least 80% of opportunities compared to manual Semrush/Ahrefs audit

* Share of voice aggregation produces internally consistent rankings across channels

* Competitive alerting detects significant strategy shifts (new keyword targeting, ad copy change) within one analysis cycle

* Strategic recommendations are each linked to at least one specific data point from the competitive analysis

# **Skill 14: Survey & Voice-of-Customer Analytics**

*NPS/CSAT/CES tracking, open-text theme extraction, and satisfaction-behavior correlation*

| Skill ID | voc-analytics |
| :---- | :---- |
| **Priority** | P2 — Supporting (qualitative insight layer) |
| **Category** | Customer Experience Analytics |
| **Depends On** | data-extraction, audience-segmentation |
| **Feeds Into** | reporting, seo-content (content strategy), email-analytics (messaging) |

## **Objective**

Automate voice-of-customer analytics: track NPS, CSAT, and CES metrics over time, extract themes from open-text responses using LLM-powered categorization, perform sentiment scoring at scale, and cross-correlate satisfaction metrics with behavioral data. Enable the organization to systematically translate customer feedback into marketing strategy adjustments.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions NPS, Net Promoter Score, CSAT, customer satisfaction, CES, Customer Effort Score, survey analytics, survey results, customer feedback, open-text analysis, verbatim analysis, sentiment analysis on feedback, voice of customer, VoC, customer comments, feedback themes, review analysis, or satisfaction tracking. Also trigger on ‘what are customers saying’ or ‘analyze our survey results.’*

## **Functional Scope**

* NPS/CSAT/CES metric computation, trend tracking, and statistical change detection

* Open-text theme extraction: LLM-based categorization of free-text responses into actionable themes

* Sentiment scoring: positive/neutral/negative classification with intensity scaling

* Cross-tabulation: satisfaction metrics broken down by segment, product, channel, and touchpoint

* Satisfaction-behavior correlation: link survey responses to behavioral outcomes (retention, CLV, NPS referrals)

* Longitudinal tracking: detect statistically significant shifts in satisfaction over time

## **Key Capabilities**

**Metric Tracking**

* Compute NPS (% Promoters \- % Detractors), CSAT (% satisfied), CES (average effort score)

* Confidence intervals on NPS using bootstrap or delta method

* Trend significance testing: is this month’s NPS statistically different from last quarter’s?

**Text Analytics**

* LLM-based theme extraction: categorize open-text responses into predefined \+ emergent themes

* Theme frequency and sentiment tracking over time

* Key driver analysis: which themes most strongly correlate with Promoter vs Detractor scores

**Correlation & Insight**

* Link survey respondents to behavioral data: do Promoters have higher CLV?

* Touchpoint analysis: which interaction points drive highest and lowest satisfaction?

* Actionable insight generation: translate theme \+ sentiment \+ correlation into specific recommendations

## **Input / Output Data Contracts**

**Inputs**

* workspace/raw/survey\_responses.csv — Survey data (respondent\_id, question\_id, response, score, timestamp)

* workspace/processed/segments.json — Segment definitions from audience-segmentation for cross-tabulation

* workspace/analysis/clv\_predictions.json — Optional: CLV for satisfaction-value correlation

**Outputs**

* workspace/analysis/satisfaction\_metrics.json — NPS, CSAT, CES with CIs and trend significance

* workspace/analysis/text\_themes.json — Theme extraction results with frequency and sentiment

* workspace/analysis/satisfaction\_drivers.json — Key driver analysis linking themes to scores

* workspace/reports/voc\_dashboard.html — Voice-of-customer analytics dashboard

## **Reference Files**

* references/survey\_methodology.md — NPS/CSAT/CES formulas, confidence interval methods, significance testing

* references/text\_analytics.md — Theme extraction prompting patterns, sentiment scoring approach

* shared/schemas/data\_contracts.md — Survey response schema, theme taxonomy

## **Scripts (Deterministic Computation)**

* scripts/compute\_metrics.py — NPS, CSAT, CES computation with bootstrap confidence intervals

* scripts/text\_categorization.py — Theme extraction using LLM API calls with structured output

* scripts/key\_driver\_analysis.py — Correlation/regression of themes against satisfaction scores

* scripts/satisfaction\_trends.py — Time series trend analysis with statistical change detection

## **Cross-Skill Integration**

VoC analytics enriches audience-segmentation with a satisfaction dimension, enabling segments like ‘High-value Detractors’ that are critical for retention marketing. Theme extraction insights inform seo-content’s content strategy (what topics resonate with customers). Email-analytics uses satisfaction scores to personalize messaging (Promoter referral asks vs Detractor recovery outreach). The reporting skill includes satisfaction trends in executive dashboards alongside operational metrics.

## **Financial Services Considerations**

* Survey data in financial services may contain PII and is subject to data protection regulations

* NPS or satisfaction data used in marketing claims must comply with SEC Marketing Rule testimonial provisions

* Open-text responses may contain account-specific information requiring redaction before analysis

## **Development Guidelines**

79. Theme extraction should use an LLM (Claude API) with structured output for consistent categorization rather than traditional NLP topic models

80. NPS confidence intervals must use bootstrapping (not normal approximation) because NPS is bounded and non-Gaussian

81. Key driver analysis should use relative importance metrics (e.g., permutation importance from random forest) not simple correlations

82. Support both predefined theme taxonomies and emergent theme discovery; let the LLM suggest new themes beyond the predefined list

83. Text categorization must handle multilingual responses if the organization operates internationally

84. Satisfaction-behavior linking must use appropriate causal reasoning disclaimers (correlation, not causation)

## **Acceptance Criteria**

* NPS computation matches manual calculation within 0.1 point; bootstrap CIs have nominal coverage at 95%

* Theme extraction achieves 85%+ agreement with human-labeled categories on a validation set of 200 responses

* Key driver analysis correctly identifies the top 3 drivers verified against expert knowledge of known service issues

* Trend detection correctly flags NPS shifts \> 5 points as statistically significant with the appropriate test

# **Skill 15: Compliance-Aware Content Review**

*Automated regulatory content screening for SEC, FINRA, and FCA marketing compliance*

| Skill ID | compliance-review |
| :---- | :---- |
| **Priority** | P0 for Financial Services / P3 for general use |
| **Category** | Regulatory Compliance (Financial Services Specialist) |
| **Depends On** | None (terminal gate skill) |
| **Feeds Into** | All content-producing skills (mandatory gate in FS mode) |

## **Objective**

Automate first-pass regulatory compliance review of marketing content for financial services organizations. Check content against SEC Marketing Rule 206(4)-1, FINRA Rule 2210, and FCA financial promotions requirements. Flag potential violations, insert required disclosures, validate performance presentation requirements, and maintain archival records. Function as a mandatory gate that all content-producing skills must pass through before distribution in financial services contexts.

## **SKILL.md Description (Trigger Text)**

*Use when the user mentions compliance review, regulatory check, SEC compliance, FINRA compliance, FCA compliance, marketing compliance, disclosure check, disclaimer, performance presentation, testimonial compliance, endorsement compliance, fair and balanced, risk disclosure, past performance disclaimer, GIPS, investment advertisement, financial promotion, advertising review, regulatory filing, or archival requirements. ALWAYS trigger automatically when any other skill produces customer-facing content in a workspace tagged as financial services. Also trigger on ‘is this compliant’ or ‘check this for regulatory issues.’*

## **Functional Scope**

* SEC Marketing Rule 206(4)-1: seven general prohibitions, performance presentation, testimonial/endorsement requirements

* FINRA Rule 2210: fair and balanced content, risk/benefit balance, institutional vs retail classification

* FCA financial promotions: clear/fair/not misleading standard, target market assessment, risk warnings

* Disclosure automation: insert required disclaimers for performance, fees, risks, and regulatory status

* Performance validation: gross/net prominence, benchmark comparison, time period presentation

* Archival compliance: flag content for SEC Rule 17a-4 WORM archival and FINRA filing requirements

## **Key Capabilities**

**Content Screening**

* Scan marketing text for potential regulatory violations against SEC, FINRA, and FCA rule databases

* Flag cherry-picked performance data: detect selective time period presentation

* Verify gross and net performance receive equal prominence where both are shown

* Detect superlative claims (‘best,’ ‘guaranteed,’ ‘risk-free’) that violate general prohibitions

**Disclosure Management**

* Generate required disclosures based on content type: performance, testimonial, third-party rating, hypothetical

* Validate that all required disclosures are present and prominently placed

* Insert standard disclaimers: past performance, investment risk, fee disclosure, regulatory registration

**Classification & Routing**

* Classify content as institutional vs retail communication (different FINRA requirements)

* Determine if content requires FINRA pre-filing (new member, options, CMOs)

* Tag content for archival with appropriate retention period and category

**Reporting**

* Generate compliance review report: issues found, severity, rule citation, remediation suggestion

* Track compliance review history for audit trail documentation

* Produce compliance scorecard: pass/fail/warning by content piece

## **Input / Output Data Contracts**

**Inputs**

* workspace/reports/\*.html or workspace/reports/\*.docx — Any content produced by other skills for distribution

* workspace/analysis/mmm\_executive\_summary.html — Attribution reports with performance claims

* workspace/analysis/experiment\_results.json — Results being used in marketing claims

* references/compliance\_rules/ — Regulatory rule database (SEC, FINRA, FCA)

**Outputs**

* workspace/compliance/review\_report.json — Issue-by-issue review with severity, rule citation, and remediation

* workspace/compliance/compliant\_content.html — Content with required disclosures inserted

* workspace/compliance/archival\_manifest.json — Content tagged for regulatory archival with retention metadata

* workspace/compliance/review\_log.json — Audit trail of all reviews performed

## **Reference Files**

* references/sec\_marketing\_rule.md — SEC Rule 206(4)-1 requirements, general prohibitions, performance standards

* references/finra\_rule\_2210.md — FINRA communications standards, filing requirements, content classifications

* references/fca\_financial\_promotions.md — FCA clear/fair/not misleading standard, risk warning requirements

* references/disclosure\_templates.md — Standard disclosure language for performance, risk, fees, testimonials

* references/archival\_requirements.md — SEC Rule 17a-4, FINRA retention rules, WORM format requirements

* shared/schemas/data\_contracts.md — Compliance review output schema

## **Scripts (Deterministic Computation)**

* scripts/content\_scanner.py — Rule-based scanning for regulatory violations using keyword and pattern matching

* scripts/performance\_validator.py — Validate performance presentation: gross/net balance, time period completeness, benchmark inclusion

* scripts/disclosure\_inserter.py — Insert required disclosures based on content type classification

* scripts/archival\_tagger.py — Tag content with archival metadata per SEC 17a-4 and FINRA requirements

## **Cross-Skill Integration**

Compliance review is the mandatory terminal gate in financial services workflows. Every skill that produces customer-facing content — reporting, email-analytics, paid-media (ad copy), seo-content, social-analytics — must route through compliance-review before distribution. The skill does not modify content unilaterally; it flags issues and suggests remediation, preserving the human compliance officer’s final authority. Attribution-analysis reports containing performance claims trigger automatic compliance review. The skill maintains an audit-ready review log for regulatory examination readiness.

## **Development Guidelines**

85. Compliance review must function as an advisory tool, not an automated approval system; always recommend human compliance officer final review

86. Rule database must be versioned and updatable without modifying the core skill scripts

87. False positive rate must be below 30% to maintain reviewer trust; prioritize precision over recall for low-severity issues

88. Disclosure templates must support customization per firm — each organization has specific approved language

89. The skill must clearly distinguish between definite violations (superlative claims) and potential issues requiring judgment (tone)

90. Archival tagging must produce metadata compatible with common compliance archival systems (Smarsh, Global Relay)

91. Never claim compliance decisions are authoritative; always label as ‘first-pass review’ requiring human confirmation

## **Acceptance Criteria**

* Content scanner detects 95%+ of SEC general prohibition violations (superlatives, misleading statements) on a test corpus

* Performance validator correctly identifies missing gross/net balance, incomplete time periods, and absent benchmarks

* Disclosure inserter adds the correct disclosure type based on content classification (performance, testimonial, hypothetical)

* False positive rate on the test corpus is below 30% for high-severity findings

* Archival tagger produces compliant metadata validated against SEC 17a-4 format requirements

* Review log maintains a complete, immutable audit trail of all compliance reviews performed

* Skill explicitly states it provides advisory first-pass review, not compliance certification, in all outputs

# **Appendix A: Core Data Contract Schemas**

The following schemas define the canonical data structures shared across skills. All schemas use JSON Schema format with semantic constraints.

## **Campaign Data Schema**

| Field | Type | Required | Description |
| :---- | :---- | :---- | :---- |
| campaign\_id | string | Yes | Unique campaign identifier |
| platform | enum | Yes | google\_ads | meta | linkedin | tiktok | dv360 |
| date | date (ISO 8601\) | Yes | Reporting date |
| spend | decimal | Yes | Daily spend in base currency |
| impressions | integer | Yes | Number of impressions served |
| clicks | integer | Yes | Number of clicks recorded |
| conversions | decimal | Yes | Number of conversions (may be fractional) |
| revenue | decimal | No | Revenue attributed to campaign |

## **Segment Definition Schema**

| Field | Type | Required | Description |
| :---- | :---- | :---- | :---- |
| customer\_id | string | Yes | Unique customer identifier |
| segment\_name | string | Yes | Human-readable segment label |
| segment\_method | enum | Yes | rfm | kmeans | dbscan | manual |
| rfm\_score | string | No | Three-digit RFM score (e.g., ‘555’) |
| cluster\_id | integer | No | Cluster assignment for behavioral clustering |
| probability\_alive | decimal | No | From CLV model (0.0 to 1.0) |
| clv\_estimate | decimal | No | Predicted CLV from clv-modeling skill |
| assigned\_at | datetime | Yes | Timestamp of segment assignment |

## **Experiment Result Schema**

| Field | Type | Required | Description |
| :---- | :---- | :---- | :---- |
| experiment\_id | string | Yes | Unique experiment identifier |
| variant | string | Yes | Variant name (control, treatment\_a, etc.) |
| metric\_name | string | Yes | Name of the measured metric |
| sample\_size | integer | Yes | Number of units in this variant |
| point\_estimate | decimal | Yes | Estimated metric value or treatment effect |
| ci\_lower | decimal | Yes | Lower bound of confidence/credible interval |
| ci\_upper | decimal | Yes | Upper bound of confidence/credible interval |
| p\_value | decimal | No | Frequentist p-value (if applicable) |
| bayesian\_prob\_best | decimal | No | Bayesian probability of being best variant |
| cuped\_adjusted | boolean | Yes | Whether CUPED variance reduction was applied |

# **Appendix B: Skill Interconnection Matrix**

The following table summarizes how each skill connects to others in the portfolio. D \= depends on (consumes output from); F \= feeds into (produces output consumed by).