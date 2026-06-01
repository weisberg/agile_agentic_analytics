# Agile Agentic Analytics - Plugins & Skills

* Plugin: A/B Testing
* Plugin: Campaign Measurement
  * Campaign Planning
  * Campaign Objectives
  * Cross-Sell Analysis
  * Up-Sell Analysis
  * Holdout Analysis
* Plugin: Product Manager
  * Planning
  * Prioritizing
* Plugin: Marketing Analytics
* Plugin: Plugin Manager
  * Manage Plugins
  * Plugin Health
  * Plugin Quality Gate
  * Plugin Release
  * Plugin Work Checkpoint
  * Plugin Devex Review
  * Skill Improve
  * SkillOpt Training Run
  * SkillOpt Rollout Evidence
  * SkillOpt Reflection Edits
  * SkillOpt Validation Gate
  * SkillOpt Slow Meta Update
  * SkillOpt Transfer Release
  * Upstream Skill Harvest
* Plugin: Lead Analyst
  * Analysis Intake
  * Source Inventory
  * Analysis Planning
  * Metric Contract
  * Metric Lineage
  * SQL Review
  * EDA Profile
  * Metric Movement Diagnostic
  * Cohort Analysis
  * Segment Diagnostics
  * Dashboard Spec
  * Dashboard Audit
  * Forecast Scenario
  * Data Quality Audit
  * Analysis Brief
  * Analysis Review
  * Executive Readout
  * Decision Log
  * Metric Steward Agent
  * Data Quality Auditor Agent
  * Lead Analyst Agent
  * Analysis Planner Agent
  * Insight Editor Agent
* Plugin: Knowledge Base
  * Core Operations
  * Retrieval And Graph
  * Ingestion
  * Knowledge Work
  * Publishing And Automation
  * KB Agents



## Plugin: A/B Testing

## Plugin: Campaign Measurement





## Plugin: Product Manager

### PRD Writer

### PRD to Plan



## Plugin: Marketing Analytics

### Shared

* **Definitions**
  * Marketing Taxonomy
* **Schemas**
  * Data Contracts
* **Utils**
  * `common_transforms.py`

### Skills

#### Skill: **Attribution Analysis**

> Use when the user mentions attribution, ROAS optimization, channel contribution, marketing mix model, MMM, media mix, budget allocation, budget optimization, incrementality, adstock, saturation curves, diminishing returns, channel effectiveness, media effectiveness, cross-channel attribution, multi-touch attribution, MTA, Shapley value attribution, or marketing ROI measurement. Also trigger when user asks 'which channel is driving results' or 'where should we spend more.' If campaign spend data is not yet extracted, suggest running data-extraction first. Results feed into reporting and paid-media skills.

##### References

* Incrementality calibration
* MMM Methodology
* PyMC Marketing API

#### Skill: Audience Segmentation

> Use when the user mentions segmentation, customer segments, cohort analysis, RFM analysis, behavioral clustering, K-Means, DBSCAN, customer personas, segment profiles, retention curves, cohort retention, segment migration, customer tiers, high-value customers, at-risk segment, churn cohort, acquisition cohort, engagement tiers, or audience definition. Also trigger on 'group our customers' or 'which customers should we target.' If CLV scores are available from clv-modeling, they enrich segment profiles. Segments feed into experimentation (stratification), email-analytics (targeting), paid-media (lookalike audiences), and reporting skills.

#### Skill: CLV Modeling

#### Competitive Intel

#### Compliance Review

#### CRM Lead Scoring

#### Email Analytics

#### Experimentation

> Use when the user mentions A/B test, experiment, hypothesis test, statistical significance, p-value, confidence interval, CUPED, variance reduction, power analysis, sample size calculation, minimum detectable effect, MDE, sequential test, early stopping, Bayesian AB test, multi-armed bandit, experiment design, split test, holdout test, control group, treatment effect, incrementality test, causal inference, or uplift modeling. Also trigger on 'did this change work' or 'how long should we run this test.' If segment-level analysis is needed and segments are not defined, suggest running audience-segmentation first.

##### Reference

* Bayesian A/B
* CUPED Methodology
* Experiment Design
* Sequential Testing

#### Funnel Analysis

> Use when the user mentions funnel, conversion funnel, drop-off, drop off, conversion rate, conversion optimization, CRO, bottleneck, funnel analysis, checkout flow, signup flow, onboarding funnel, activation funnel, abandonment, cart abandonment, form abandonment, user flow, step completion, or funnel comparison. Also trigger on 'where are we losing people' or 'why is conversion low.' If segment-level funnel comparison is needed and segments are not defined, suggest running audience-segmentation first. Behavioral event data typically comes from web-analytics. CRO hypotheses feed into experimentation for A/B testing. Results feed into reporting and paid-media (landing page optimization) skills.

#### Paid Media

#### Reporting

#### SEO Content

#### Social Analytics

#### VOC Analytics

#### Web Analytics

## Plugin: Plugin Manager

Marketplace maintenance workflows for creating, validating, harvesting, syncing,
and publishing Claude Code plugins.

### Manage Plugins

Use for plugin creation, plugin updates, marketplace entries, plugin validation,
skill moves, and release preparation.

### Plugin Health

Use for manifest, marketplace, skill frontmatter, conformance, routing fixture,
generated-artifact, and CI-readiness audits.

### Plugin Quality Gate

Use for cross-model or second-opinion review of high-impact plugin skills before
tests and releases cement behavior.

### Plugin Release

Use for plugin versioning, documentation sync, validation bundles, upgrade notes,
and release approval gates.

### Plugin Work Checkpoint

Use to save or restore resumable context for long plugin maintenance, release,
or harvest work without storing secrets or large raw diffs.

### Plugin Devex Review

Use for fresh-clone onboarding checks, quickstart testing, prerequisite review,
and contributor-experience improvements.

### Skill Improve

Use for one-pass evidence-backed skill improvements without a full SkillOpt
training loop.

### SkillOpt Training Run

Use for orchestrating offline SkillOpt-style optimization loops for plugin
skills.

### SkillOpt Rollout Evidence

Use for capturing scored train, selection, test, or transfer trajectories.

### SkillOpt Reflection Edits

Use for turning rollout failures and successes into bounded structured edits.

### SkillOpt Validation Gate

Use for accepting candidate skill edits only when held-out validation improves.

### SkillOpt Slow Meta Update

Use for epoch-boundary protected guidance and optimizer-side memory.

### SkillOpt Transfer Release

Use for exporting, transfer-checking, documenting, and promoting a best skill.

### Upstream Skill Harvest

Use for importing, adapting, diffing, and periodically reviewing skills harvested
from GBrain or GStack into marketplace plugins.

## Plugin: Lead Analyst

Senior analyst workflows for evidence-backed business, product, marketing, and
operations analysis.

### Analysis Intake

Use when a stakeholder request is vague, political, broad, or under-specified
and needs to become a crisp analytics intake before planning or execution.

### Source Inventory

Use when the analyst needs to map available tables, files, dashboards,
notebooks, reports, APIs, owners, freshness, grain, access, and source-of-truth
status before analysis.

### Analysis Planning

Use when the user wants to plan an analysis before running it, scope analytical
work, design an investigation, write an analysis plan, decide what data or
metrics are needed, or turn a vague metric/business question into an executable
analyst workplan.

### Metric Contract

Use when the user wants to define, document, reconcile, or review a KPI or
metric, including numerator, denominator, grain, population, source of truth,
caveats, and change control.

### Metric Lineage

Use to trace a KPI or metric from dashboard/report back through SQL, dbt models,
semantic layers, events, source tables, transformations, filters, and owners.

### SQL Review

Use to review SQL, dbt models, BI queries, warehouse transformations, or notebook
queries for analytical correctness.

### EDA Profile

Use for exploratory data analysis profiling before deeper analysis: row counts,
date coverage, schema, missingness, duplicates, distributions, outliers,
categorical levels, grain, and first-cut anomalies.

### Metric Movement Diagnostic

Use when a KPI or metric moved and the team needs to understand why.

### Cohort Analysis

Use to design or perform cohort analysis for retention, activation, repeat
behavior, lifecycle progression, revenue, churn, or product usage.

### Segment Diagnostics

Use to diagnose which segments explain a metric movement, opportunity, risk, or
performance gap without overclaiming post-hoc slices.

### Dashboard Spec

Use to design a dashboard specification from an operating decision: audience,
cadence, metrics, definitions, source of truth, layout, alerts, drilldowns,
states, and governance.

### Dashboard Audit

Use to review an existing dashboard for decision usefulness, metric definition
quality, freshness, misleading charts, broken filters, stale data, alert
thresholds, and governance.

### Forecast Scenario

Use to design or review forecasts, scenarios, sensitivity analyses, targets,
plans, capacity models, revenue forecasts, demand forecasts, budget scenarios,
or what-if models.

### Data Quality Audit

Use when the user wants to audit whether data, SQL, dashboards, extracts,
notebooks, or metric pipelines are reliable enough for analysis or decision use.

### Analysis Brief

Use when the user asks the lead analyst or senior analyst to analyze data, answer
a business/product/marketing/operations question, diagnose a metric movement,
summarize what the data says, produce an insight brief, or recommend what to do
from evidence.

### Analysis Review

Use when the user wants a senior analyst review of an existing analysis,
dashboard, notebook, SQL query, KPI claim, experiment readout, executive brief,
or report.

### Executive Readout

Use when the user wants to turn analysis into an executive-ready readout,
decision memo, operating-review narrative, stakeholder update, board-ready
summary, or concise recommendation.

### Decision Log

Use to capture, update, or review analytical decisions and follow-through:
recommendation, evidence, confidence, owner decision, action taken, follow-up
date, and outcome.

### Lead Analyst Agent

Use as an independent senior analyst subagent for ambiguous business/data
questions, metric definitions, exploratory analysis, data-quality audits, and
decision-ready insight synthesis.

### Analysis Planner Agent

Use as a planning-focused senior analyst subagent for analysis design, metric
precision, evidence inventory, validity threats, candidate approaches, and plan
review.

### Metric Steward Agent

Use as a metric-definition specialist for KPI contracts and source-of-truth
reconciliation.

### Data Quality Auditor Agent

Use as an evidence-quality specialist for freshness, grain, joins, missingness,
duplicates, definition drift, and decision risk.

### Insight Editor Agent

Use as an executive narrative specialist for sharpening recommendations while
preserving uncertainty and decision-changing caveats.

## Plugin: Knowledge Base

The Knowledge Base plugin provides a 50-skill portfolio for file-based knowledge
vaults, including ingestion, retrieval, graph operations, provenance, privacy,
publishing, automation, release workflows, and bundled `vaultli` maintenance.

### Core Operations

`ask-user`, `kb-ops`, `resolver`, `setup`, `health`, `maintenance`, `dashboard`,
and `vaultli` provide choice gates, routing, first-run setup, operational health,
and local vault CLI access.

### Retrieval And Graph

`query`, `search-modes`, `source-router`, `graph-ops`, `briefing`, and `reports`
answer from the KB first, choose retrieval modes, expand relationships, and
produce cited operational summaries.

### Ingestion

`ingest`, `signal-detector`, `article-enrichment`, `meeting-ingestion`,
`media-ingest`, `voice-note-ingest`, `browser-ingest`, `raw-source`,
`cold-start`, `migrate`, and `archive-crawler` route source material into
cited, back-linked KB pages with raw source preservation.

### Knowledge Work

`enrich`, `citation-fixer`, `frontmatter-guard`, `filing-rules`,
`concept-synthesis`, `book-mirror`, `academic-verify`, `current-research`,
`strategic-reading`, `originals`, and `task-manager` keep pages useful,
fresh, verified, and connected.

### Publishing And Automation

`publish`, `pdf-export`, `webhook-transforms`, `cron-scheduler`,
`background-jobs`, `context-checkpoint`, `privacy-security`, `quality-gate`,
`release-upgrade`, `devex-review`, `integration-contracts`,
`conflict-resolution`, `sample-vault`, and `skillify` cover durable outputs,
scheduled work, safety, validation, and release readiness.

### KB Agents

`kb-curator`, `kb-researcher`, and `kb-ops-auditor` provide specialized
subagent roles for curation, current-source research, and operational audits.
