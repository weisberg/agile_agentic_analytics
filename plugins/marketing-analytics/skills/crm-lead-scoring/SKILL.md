---
name: crm-lead-scoring
description: >
  Use when the user mentions lead scoring, predictive scoring, lead qualification,
  MQL, SQL, pipeline analytics, pipeline velocity, win rate, deal velocity, sales
  funnel, opportunity analysis, win/loss analysis, CRM analytics, lead-to-close,
  conversion probability, propensity model, account scoring, or sales attribution.
  Also trigger on 'which leads should sales prioritize' or 'why are we losing deals.'
  If segment enrichment is needed and segments are not defined, suggest running
  audience-segmentation first. Lead quality signals feed into paid-media for
  campaign targeting. Pipeline metrics feed into reporting.
---

# CRM Analytics & Lead Scoring

Predictive lead scoring, pipeline velocity tracking, and win/loss analysis.

| Property       | Value                                                          |
| :------------- | :------------------------------------------------------------- |
| Skill ID       | crm-lead-scoring                                               |
| Priority       | P2 — Supporting (extends core analytics to sales pipeline)     |
| Category       | Sales & Pipeline Analytics                                     |
| Depends On     | data-extraction, audience-segmentation, clv-modeling           |
| Feeds Into     | email-analytics (nurture flows), paid-media (targeting), reporting |

## Objective

Build and maintain predictive lead scoring models that combine firmographic,
demographic, and behavioral signals to predict conversion likelihood. Track
pipeline velocity metrics, perform win/loss analysis, and identify pipeline
bottlenecks. Support integration with Salesforce, HubSpot, and custom CRM
systems.

## Process Steps

1. **Validate inputs.** Load `crm_leads.csv` and `lead_activities.csv` from
   `workspace/raw/`. Verify required columns: `lead_id`, `source`, `stage`,
   `created_date`, `close_date`, `amount`, `outcome` for leads; `lead_id`,
   `activity_type`, `timestamp` for activities. If `segments.json` is available
   from audience-segmentation, load it for enrichment.

2. **Engineer features.** Run `scripts/lead_scoring_model.py` to build the
   feature matrix from CRM fields, website behavior, email engagement, and
   content consumption signals. Firmographic features include company size,
   industry, and geography. Behavioral features include page views, email opens,
   content downloads, and recency of engagement.

3. **Train scoring models.** Train both logistic regression (interpretable
   baseline) and gradient boosting (accuracy-optimized) models with temporal
   holdout cross-validation. Always train on historical data and validate on
   future data to simulate real-world deployment.

4. **Calibrate scores.** Apply isotonic regression or Platt scaling to ensure
   predicted probabilities match observed conversion rates. Validate calibration
   across decile bins; predicted vs. observed rates must align within 5
   percentage points.

5. **Generate SHAP explanations.** Compute SHAP values for every scored lead to
   explain which features drove the prediction. Document the top predictive
   features and verify against domain expert review.

6. **Compute pipeline velocity.** Run `scripts/pipeline_velocity.py` to
   calculate stage-by-stage conversion rates, average deal cycle time,
   time-in-stage distributions, and pipeline coverage ratio against
   quota/target. Compare metrics period-over-period and identify outliers.

7. **Run win/loss analysis.** Execute `scripts/win_loss_analysis.py` to
   statistically compare won vs. lost deals across all available features.
   Identify the stage at which lost deals diverge from won deals, and compute
   competitive win/loss rates when a competitor is mentioned.

8. **Forecast pipeline.** Produce weighted pipeline projections using
   probability-adjusted revenue. Compare weighted pipeline to quota with gap
   analysis.

9. **Generate outputs.** Write structured results to
   `workspace/analysis/lead_scores.json`, `workspace/analysis/pipeline_metrics.json`,
   and `workspace/analysis/win_loss_factors.json`. Compile the CRM dashboard to
   `workspace/reports/crm_dashboard.html`.

## Key Capabilities

### Predictive Lead Scoring

- Feature engineering from CRM fields, website behavior, email engagement, and
  content consumption signals.
- Model training with logistic regression (interpretable) and gradient boosting
  (accuracy) using temporal holdout cross-validation.
- SHAP-based feature importance for model explainability and score
  interpretation. Every scored lead receives a feature-level explanation.
- Score calibration via isotonic regression or Platt scaling to ensure predicted
  probabilities are reliable and actionable.
- Account-based scoring: aggregate multiple contact signals into a company-level
  propensity score.

Refer to `references/lead_scoring_methodology.md` for feature engineering
patterns, model selection criteria, and calibration techniques.

### Pipeline Analytics

- Stage-by-stage conversion rate tracking with period-over-period comparison.
- Deal velocity analysis: time-in-stage distributions with outlier
  identification and bottleneck detection.
- Pipeline coverage: compare weighted pipeline to quota/target with gap
  analysis and risk flagging.
- Pipeline forecasting: weighted pipeline with probability-adjusted revenue
  projections.

Refer to `references/pipeline_metrics.md` for velocity definitions and
coverage ratio benchmarks.

### Win/Loss Intelligence

- Statistical comparison of won vs. lost deals across all available features
  using hypothesis tests (t-test for continuous, chi-squared for categorical).
- Temporal divergence analysis: identify at which pipeline stage lost deals
  begin diverging from won deals in behavior or engagement.
- Competitive win/loss: when a competitor is mentioned, quantify the change in
  win rate and deal cycle time.
- Ranked feature importance showing the strongest differentiators between won
  and lost outcomes.

### Lead Source Attribution

- Identify which marketing channels and campaigns produce the highest-quality
  leads (measured by conversion rate and deal value).
- Feed lead quality signals back to paid-media for campaign targeting
  optimization.

## Input / Output Data Contracts

### Inputs

| File | Description | Required |
| :--- | :---------- | :------- |
| `workspace/raw/crm_leads.csv` | Lead/opportunity data: `lead_id`, `source`, `stage`, `created_date`, `close_date`, `amount`, `outcome` | Yes |
| `workspace/raw/lead_activities.csv` | Behavioral activities: `lead_id`, `activity_type`, `timestamp` | Yes |
| `workspace/processed/segments.json` | Segment enrichment from audience-segmentation | No |

### Outputs

| File | Description |
| :--- | :---------- |
| `workspace/analysis/lead_scores.json` | Lead-level propensity scores with SHAP feature explanations |
| `workspace/analysis/pipeline_metrics.json` | Pipeline velocity, conversion rates, coverage ratio |
| `workspace/analysis/win_loss_factors.json` | Win/loss analysis with ranked feature importance |
| `workspace/reports/crm_dashboard.html` | Lead scoring and pipeline analytics dashboard |

## Cross-Skill Integration

Lead scoring models consume behavioral signals from **web-analytics** and
**email-analytics** engagement data. **CLV-modeling** provides expected value
estimates for score-weighted prioritization. **Audience-segmentation** enriches
leads with segment membership, enabling segment-aware scoring and pipeline
analysis. **Paid-media** uses lead quality data to optimize campaign targeting
toward high-converting lead sources. The **reporting** skill includes pipeline
health metrics in executive dashboards.

When segment enrichment is needed and segments are not yet defined, prompt the
user to run audience-segmentation first before proceeding with segment-aware
lead scoring.

## Financial Services Considerations

When operating in financial services mode:

- Lead scoring for financial products must comply with fair lending requirements
  and avoid prohibited characteristics (race, religion, national origin, etc.)
  as scoring features.
- Advisor-mediated channels require relationship-level scoring, not just
  individual lead scoring. Aggregate signals at the household or advisor-book
  level.
- Pipeline analytics must account for regulatory approval stages (compliance
  review, legal sign-off) in cycle time calculations. These stages should be
  tracked separately and not penalize velocity metrics.
- Experiment result claims derived from lead scoring used in marketing materials
  must include statistical methodology footnotes.

## Development Guidelines

1. Use scikit-learn for model training; always include logistic regression as an
   interpretable baseline alongside gradient boosting.

2. SHAP values are required for model explainability; never deploy a scoring
   model without feature importance documentation.

3. Temporal holdout validation is mandatory: train on historical data, validate
   on future data to simulate real-world performance. Never use random splits
   for time-series scoring data.

4. Score calibration must use isotonic regression or Platt scaling to ensure
   predicted probabilities are reliable.

5. Model retraining cadence should be configurable; default to monthly with
   automated drift detection comparing current feature distributions to training
   distributions.

6. Support both Salesforce and HubSpot field naming conventions with a mapping
   layer. CRM-specific field names should be abstracted into canonical names
   before feature engineering.

## Scripts

| Script | Purpose |
| :----- | :------ |
| `scripts/lead_scoring_model.py` | Feature engineering, model training, SHAP explanation, calibration |
| `scripts/pipeline_velocity.py` | Stage conversion rates, deal cycle time distributions, coverage ratio |
| `scripts/win_loss_analysis.py` | Feature comparison between won/lost deals, divergence point identification |

## Reference Files

| Reference | Content |
| :-------- | :------ |
| `references/lead_scoring_methodology.md` | Feature engineering guide, model selection criteria, calibration techniques |
| `references/pipeline_metrics.md` | Pipeline velocity definitions, coverage ratio benchmarks |

## Acceptance Criteria

- Lead scoring model achieves AUC > 0.75 on temporal holdout validation set.
- Calibrated probabilities match observed conversion rates within 5 percentage
  points across decile bins.
- SHAP feature importance correctly identifies the top 5 predictive features
  verified against domain expert review.
- Pipeline velocity calculations match manual CRM report outputs within 2%
  tolerance.
- Win/loss analysis identifies at least 3 statistically significant
  differentiating factors (p < 0.05).
