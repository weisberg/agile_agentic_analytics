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







