# Agile Agentic Analytics — Skill Index

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
