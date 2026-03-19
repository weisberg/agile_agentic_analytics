---
name: paid-media
description: >
  Use when the user mentions paid media, ad performance, Google Ads, Meta Ads,
  Facebook Ads, LinkedIn Ads, TikTok Ads, DV360, SEM, PPC, display advertising,
  programmatic, ROAS, CPA, CPM, CPC, CTR, ad spend, budget pacing, creative
  fatigue, ad creative, quality score, search terms, negative keywords, bid
  strategy, campaign optimization, ad copy analysis, or audience targeting
  performance. Also trigger on 'how are our ads performing' or 'are we on track
  with ad spend.'
category: Channel Analytics
priority: P0
depends_on:
  - data-extraction
feeds_into:
  - attribution-analysis
  - reporting
  - funnel-analysis
---

# Paid Media Analytics

Cross-platform ad performance aggregation, anomaly detection, and creative optimization.

## Objective

Unify performance data from Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads, and
DV360 into a single normalized reporting layer. Automate cross-platform ROAS/CPA
comparison, anomaly detection on spend and performance metrics, creative fatigue
identification, budget pacing monitoring, and search term analysis with negative
keyword recommendations. Produce daily and weekly performance snapshots and flag
accounts requiring immediate attention.

## Data Normalization

Map platform-specific metrics to a unified taxonomy so that every downstream
consumer operates on a single schema regardless of data origin.

### Unified metric taxonomy

| Unified Metric | Google Ads        | Meta Ads           | LinkedIn Ads       | TikTok Ads        | DV360              |
|----------------|-------------------|--------------------|--------------------|--------------------|---------------------|
| impressions    | Impressions       | impressions        | impressions        | impressions        | impressions         |
| clicks         | Clicks            | clicks             | clicks             | clicks             | clicks              |
| spend          | Cost              | spend              | costInLocalCurrency| spend              | revenue             |
| conversions    | Conversions       | actions (purchase) | externalWebsiteConversions | conversions | totalConversions   |
| revenue        | ConversionValue   | action_values      | conversionValueInLocalCurrency | value  | totalConversionValue|

### Key normalization rules

- Handle attribution window differences with transparent labeling (Meta 7-day
  click vs Google 30-day click).
- Currency normalization for multi-market campaigns — convert all spend and
  revenue to a single reporting currency using daily FX rates.
- Deduplicate conversions where multiple platforms claim credit for the same
  event by flagging overlap windows.
- Use `scripts/normalize_platforms.py` for deterministic transformation.

See `references/platform_api_mapping.md` for the full metric taxonomy.

## Performance Analysis

### Cross-platform efficiency comparison

Compare ROAS, CPA, CPM, and CPC across platforms, benchmarked against:

- Client-defined targets (from workspace config)
- Historical rolling averages (7-day, 28-day)
- Industry benchmarks where available

### Volume vs efficiency matrix

Decompose campaign performance into a 2x2 matrix:

| Quadrant           | Volume | Efficiency | Action                        |
|--------------------|--------|------------|-------------------------------|
| Scale winners      | High   | High       | Increase budget               |
| Efficient niche    | Low    | High       | Test scaling headroom         |
| Expensive scale    | High   | Low        | Optimize or reduce budget     |
| Underperformers    | Low    | Low        | Pause or restructure          |

### Automated insight generation

Generate natural-language insights from metric movements:

> "Search CPA increased 23% WoW driven by broad match expansion in Campaign X."

Always attribute the direction, magnitude, period, and root cause.

## Anomaly Detection

Statistical anomaly detection on spend, CPA, CTR, and conversion rate using
multiple complementary methods.

### Methods

1. **Rolling Z-score** — flag values exceeding a configurable threshold (default
   |z| > 2.5) relative to a 28-day rolling window.
2. **Isolation forest** — unsupervised tree-based method for multivariate
   anomalies that Z-score may miss.
3. **Seasonal decomposition** — STL decomposition to separate trend, seasonal,
   and residual components; flag residuals beyond threshold.

See `references/anomaly_detection.md` for method details and tuning guidance.

### Alert configuration

| Metric          | Default threshold | Severity |
|-----------------|-------------------|----------|
| Daily spend     | > 150% of plan    | Critical |
| CPA             | > 2.0 z-score     | High     |
| CTR             | < -2.0 z-score    | Medium   |
| Conversion rate | < -2.5 z-score    | High     |

### Root cause drill-down

When an anomaly fires, drill from account level down to campaign, ad group, and
keyword level to identify the source. Output must include the specific entity
responsible and the metric delta.

Use `scripts/detect_anomalies.py` for computation.

## Creative Fatigue Detection

Detect declining performance curves per creative and recommend rotation timing.

### Methodology

- Track conversion-weighted CTR (not raw CTR) over the creative's lifetime to
  avoid incorrectly flagging top-of-funnel awareness creatives.
- Fit a piecewise regression to the performance curve: plateau phase followed by
  decay phase.
- Score each creative's fatigue level from 0 (fresh) to 100 (exhausted).
- Recommend rotation when projected performance drops below 50% of peak within
  the next 3 days.

See `references/creative_fatigue.md` for the full detection methodology.

Use `scripts/creative_fatigue.py` for computation.

## Budget Pacing

Track daily spend against plan and project month-end variance.

### Pacing calculation

- Use **exponential smoothing** (not simple linear extrapolation) to handle
  intra-month spend acceleration patterns.
- Account for weekday/weekend spend patterns and known events (Black Friday,
  quarter-end).
- Generate alerts when projected month-end spend deviates from plan by more than
  a configurable threshold (default 10%).

### Output

| Field              | Description                                  |
|--------------------|----------------------------------------------|
| campaign_id        | Campaign identifier                          |
| budget_plan        | Monthly budget target                        |
| spend_to_date      | Actual spend through current date             |
| projected_spend    | Exponential-smoothing month-end projection   |
| variance_pct       | (projected - plan) / plan as percentage       |
| alert_level        | None / Warning / Critical                    |

Use `scripts/budget_pacing.py` for computation.

## Search Term Analysis

Mine search term reports to identify waste and generate negative keyword lists.

### Waste identification

Flag search terms meeting any of:

- High impressions, zero conversions, spend above threshold
- CPA exceeding 3x campaign average
- Irrelevant semantic match (brand misspellings, competitor terms if unwanted)

### Negative keyword extraction

- Group flagged terms into thematic clusters.
- Recommend match type (exact, phrase) based on term specificity.
- Estimate monthly waste savings per recommended negative keyword.

Use `scripts/search_term_analysis.py` for computation.

## Input / Output Data Contracts

### Inputs

| File pattern                                  | Description                              |
|-----------------------------------------------|------------------------------------------|
| `workspace/raw/campaign_spend_{platform}.csv` | Platform-specific campaign data from data-extraction |
| `workspace/raw/search_terms_{platform}.csv`   | Search term reports (Google, Microsoft)  |
| `workspace/raw/creative_performance_{platform}.csv` | Creative-level metrics             |

### Outputs

| File                                             | Description                                      |
|--------------------------------------------------|--------------------------------------------------|
| `workspace/processed/unified_media_performance.csv` | Normalized cross-platform dataset              |
| `workspace/analysis/media_anomalies.json`        | Flagged anomalies with severity, metric, root cause |
| `workspace/analysis/creative_fatigue.json`       | Creative health scores and rotation recommendations |
| `workspace/analysis/negative_keywords.json`      | Recommended negative keywords with waste estimates |
| `workspace/reports/media_performance_snapshot.html` | Cross-platform performance dashboard           |

### Unified media schema

The normalized output uses the following schema:

| Column        | Type    | Description                            |
|---------------|---------|----------------------------------------|
| date          | date    | Reporting date (YYYY-MM-DD)            |
| platform      | string  | google / meta / linkedin / tiktok / dv360 |
| campaign_id   | string  | Platform-native campaign identifier    |
| campaign_name | string  | Human-readable campaign name           |
| ad_group_id   | string  | Ad group or ad set identifier          |
| impressions   | integer | Impression count                       |
| clicks        | integer | Click count                            |
| spend         | decimal | Spend in reporting currency            |
| conversions   | decimal | Conversion count                       |
| revenue       | decimal | Revenue in reporting currency          |
| cpc           | decimal | Derived: spend / clicks                |
| ctr           | decimal | Derived: clicks / impressions          |
| cpa           | decimal | Derived: spend / conversions           |
| roas          | decimal | Derived: revenue / spend               |

## Cross-Skill Integration

| Skill                | Relationship                                                  |
|----------------------|---------------------------------------------------------------|
| data-extraction      | Upstream: provides raw platform CSV files consumed by this skill |
| attribution-analysis | Downstream: receives normalized spend data for MMM channel decomposition. Budget optimization outputs from attribution-analysis inform pacing targets. |
| reporting            | Downstream: creative performance and pacing data feed executive dashboards |
| funnel-analysis      | Downstream: consumes landing page conversion rates from paid media click-throughs |

## Financial Services Considerations

When analyzing paid media for financial services clients:

- Financial product advertising must comply with SEC/FINRA truth-in-advertising
  rules.
- Ad creative for investment products must include required risk disclosures.
  Flag ads missing disclaimers.
- Audience targeting for financial products must avoid prohibited discriminatory
  practices (ECOA, fair lending).
- All ad copy and landing pages must be archived per SEC Rule 17a-4. Trigger
  `compliance-review` for new creatives.

## Development Guidelines

1. Use MCP servers (`google-analytics-mcp`, `meta-ads-mcp`) for live data where
   available; fall back to CSV upload.
2. Anomaly detection must account for day-of-week seasonality and known events
   (Black Friday, quarter-end) to avoid false positives.
3. Creative fatigue algorithm must use conversion-weighted CTR, not raw CTR, to
   avoid flagging top-of-funnel creatives incorrectly.
4. Budget pacing projection must use exponential smoothing, not simple linear
   extrapolation, to handle intra-month spend patterns.
5. All monetary calculations must use `decimal.Decimal` (Python) to avoid
   floating-point rounding errors.
6. Support incremental data updates (append new dates) rather than requiring
   full history reload each time.
7. Reference files in `references/` for methodology details; keep SKILL.md
   focused on instructions and contracts.
8. Scripts in `scripts/` handle deterministic computation; the LLM handles
   interpretation, insight generation, and recommendation framing.
