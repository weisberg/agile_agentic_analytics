---
name: web-analytics
description: >
  Use when the user mentions web analytics, GA4, Google Analytics, site traffic,
  page views, sessions, bounce rate, engagement rate, user behavior, session flow,
  site speed, traffic sources, acquisition channels, landing page performance,
  conversion tracking, UTM parameters, event tracking, behavioral analysis,
  Mixpanel, Amplitude, user journey, click path, scroll depth, or heatmap data.
  Also trigger on 'what's happening on our website' or 'where is traffic coming
  from.'
---

# Web Analytics & Behavioral Analysis

GA4 data extraction, behavioral pattern detection, anomaly detection, and
predictive audiences.

| Property       | Value                                                        |
| :------------- | :----------------------------------------------------------- |
| Skill ID       | web-analytics                                                |
| Priority       | P1 — Tactical (foundational data layer)                      |
| Category       | Digital Analytics                                            |
| Depends On     | data-extraction                                              |
| Feeds Into     | funnel-analysis, seo-content, paid-media, audience-segmentation, reporting |

## Objective

Extract and analyze web behavioral data from GA4 (via the official MCP server
or API), Mixpanel, and Amplitude. Automate traffic and conversion anomaly
detection, user behavior pattern identification, session flow analysis, and
predictive audience creation. Serve as the foundational behavioral data layer
that feeds funnel analysis, SEO, paid media landing page optimization, and
segmentation.

## Process Steps

1. **Validate inputs.** Load `ga4_reports.csv` and/or `events.csv` from
   `workspace/raw/`. Verify required columns (date, source, medium, page_path,
   sessions, conversions). Normalize UTM parameters: lowercase source/medium,
   trim whitespace, decode URL-encoded characters.

2. **Extract GA4 data.** If fresh data is needed, use the google-analytics-mcp
   server when available; otherwise run `scripts/extract_ga4.py` against the
   GA4 Data API with the requested dimensions and metrics. Support incremental
   date range appending without full re-extraction.

3. **Compute normalized metrics.** Aggregate raw event data into daily traffic,
   engagement, and conversion metrics. Write results to
   `workspace/processed/web_metrics.json`.

4. **Run anomaly detection.** Execute `scripts/web_anomaly_detection.py` on the
   normalized metrics time series. The script applies STL seasonal
   decomposition (period = 7 days) then flags residuals exceeding the
   configured Z-score threshold. Requires at least 8 weeks of history for
   stable seasonal baselines.

5. **Decompose anomaly root causes.** For each flagged anomaly, break down the
   deviation by source/medium, device category, geography, and landing page to
   identify the largest contributing dimension. Suppress known events
   (holidays, product launches) when a suppression calendar is provided.

6. **Analyze navigation paths.** Run `scripts/path_analysis.py` to build
   second-order (bigram) Markov chain transition matrices from session-level
   page sequences. Identify the top conversion paths, unexpected navigation
   loops, and dead-end pages.

7. **Score content affinity.** For each content category, compute the
   conversion lift ratio: P(convert | visited category) / P(convert). Rank
   categories by affinity score. See `references/behavioral_patterns.md`.

8. **Run exit page analysis.** Rank pages by exit rate weighted by conversion
   proximity (pages closer to the conversion step in the dominant path receive
   higher weight).

9. **Build predictive audiences.** Run `scripts/predictive_scoring.py` to fit
   logistic regression models for propensity-to-convert and
   propensity-to-churn using behavioral features (session count, pages per
   session, content affinity scores, recency). Validate on a temporal holdout
   to avoid data leakage.

10. **Analyze page performance.** Correlate page load time with bounce rate
    across pages. Segment by mobile vs. desktop to surface device-specific
    performance issues.

11. **Write outputs.** Persist all results to the workspace:
    - `workspace/analysis/web_anomalies.json`
    - `workspace/analysis/navigation_paths.json`
    - `workspace/analysis/predictive_audiences.json`

## Key Capabilities

### GA4 Data Extraction

- Connect to GA4 via the official MCP server or Data API for automated report
  retrieval.
- Support Mixpanel and Amplitude event export formats for multi-platform
  analysis.
- Automated UTM parameter validation and source/medium normalization: handle
  case differences, trailing spaces, and URL-encoded characters.
- Incremental data loading: append new date ranges without requiring full
  re-extraction.

Refer to `references/ga4_api.md` for GA4 Data API dimensions, metrics, and
filter syntax.

### Traffic and Conversion Anomaly Detection

- Daily traffic and conversion rate anomaly detection with seasonal adjustment
  using STL decomposition and Z-score thresholds.
- Automated root cause decomposition: break anomaly into source, device,
  geography, and page contributions.
- Configurable alert thresholds with suppression for known events (holidays,
  product launches).

### Behavioral Pattern Detection

- Identify high-conversion navigation paths using Markov chain transition
  analysis with second-order (bigram) transitions.
- Exit page analysis: rank pages by exit rate weighted by conversion proximity.
- Content affinity scoring: which content categories correlate with downstream
  conversion.

Refer to `references/behavioral_patterns.md` for Markov chain path analysis
and content affinity scoring methodology.

### Session Flow Analysis

- Build session-level page sequence models from event data.
- Identify common navigation paths, unexpected loops, and dead-end pages.
- Compute path-to-conversion probability for each navigation step.

### Predictive Audience Creation

- Propensity-to-convert scoring via logistic regression on behavioral features.
- Propensity-to-churn scoring for returning visitors showing declining
  engagement.
- Temporal holdout validation to avoid data leakage; target AUC > 0.70.

### Page Performance

- Correlate page load time with bounce rate to quantify speed impact.
- Segment mobile vs. desktop behavioral differences.
- Identify high-traffic pages with disproportionately slow load times.

## Input / Output Data Contracts

### Inputs

| File | Description | Required |
| :--- | :---------- | :------- |
| `workspace/raw/ga4_reports.csv` | GA4 report data from data-extraction or MCP server | Yes |
| `workspace/raw/events.csv` | Event-level data from GA4, Mixpanel, or Amplitude | No (for path analysis) |

### Outputs

| File | Description |
| :--- | :---------- |
| `workspace/processed/web_metrics.json` | Normalized web analytics metrics (traffic, engagement, conversion) |
| `workspace/analysis/web_anomalies.json` | Detected anomalies with root cause decomposition |
| `workspace/analysis/navigation_paths.json` | Common user paths with conversion correlation scores |
| `workspace/analysis/predictive_audiences.json` | Propensity scores for conversion and churn |

## Cross-Skill Integration

Web analytics is the foundational behavioral data source:

- **funnel-analysis:** Builds conversion funnels from web event sequences
  produced by this skill.
- **seo-content:** Uses traffic data from this skill to measure organic search
  performance and content engagement.
- **paid-media:** Analyzes landing page conversion from ad click-throughs using
  web metrics and session data.
- **audience-segmentation:** Incorporates behavioral features (session
  frequency, content affinity scores) into cluster models.
- **reporting:** Anomalies detected here surface in executive dashboards.
  Predictive audience scores feed audience-level reporting.
- **experimentation:** CUPED variance reduction leverages pre-experiment
  behavioral data sourced from this skill's pipelines.

## Financial Services Considerations

When operating in financial services mode:

- Financial services websites must track regulatory disclosure page views for
  compliance verification.
- Investor portal analytics require authenticated user tracking with PII
  handling compliant with privacy regulations (GDPR, CCPA, SEC).
- Cookie consent compliance affects data collection; this skill must flag
  consent rate as a data quality metric and report on consent-rate trends.
- Regulatory page visit completeness should be verified: ensure all required
  disclosures have been rendered before conversion events.

## Development Guidelines

1. Prefer the google-analytics-mcp server for GA4 data when available; fall
   back to the Data API Python client.

2. Anomaly detection must use at least 8 weeks of history for stable seasonal
   baselines.

3. Path analysis Markov chains should use second-order (bigram) transitions for
   more accurate modeling.

4. Predictive audience scoring must validate on a temporal holdout to avoid
   data leakage.

5. Support incremental data loading: append new date ranges without requiring
   full re-extraction.

6. UTM parameter normalization must handle common inconsistencies: case
   differences, trailing spaces, and URL-encoded characters.

7. All statistical and ML computations must be deterministic Python scripts.
   Never let the LLM perform numerical estimation directly.

## Scripts

| Script | Purpose |
| :----- | :------ |
| `scripts/extract_ga4.py` | GA4 report builder with configurable dimensions and metrics |
| `scripts/web_anomaly_detection.py` | Seasonal decomposition and Z-score anomaly detection on web metrics |
| `scripts/path_analysis.py` | Markov chain navigation path analysis and conversion path identification |
| `scripts/predictive_scoring.py` | Logistic regression propensity scoring for conversion and churn |

## Reference Files

| Reference | Content |
| :-------- | :------ |
| `references/ga4_api.md` | GA4 Data API dimensions, metrics, and filter syntax |
| `references/behavioral_patterns.md` | Markov chain path analysis, content affinity scoring methodology |

## Acceptance Criteria

- GA4 data extraction successfully retrieves reports for all standard
  dimensions and metrics.
- Anomaly detection achieves false positive rate < 5% on a 90-day historical
  validation period.
- Navigation path analysis correctly identifies the top 5 conversion paths
  verified against manual GA4 exploration.
- Predictive audience scores achieve AUC > 0.70 on temporal holdout validation
  for conversion propensity.
