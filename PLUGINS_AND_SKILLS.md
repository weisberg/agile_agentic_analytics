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
  * Upstream Skill Harvest
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

### Upstream Skill Harvest

Use for importing, adapting, diffing, and periodically reviewing skills harvested
from GBrain or GStack into marketplace plugins.

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



