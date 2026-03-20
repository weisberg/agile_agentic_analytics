---
name: clv-modeling
description: >
  Use when the user mentions CLV, LTV, customer lifetime value, customer value prediction,
  lifetime revenue, CLV:CAC ratio, BG/NBD, Gamma-Gamma, RFM summary, purchase frequency
  prediction, monetary value prediction, churn probability, customer retention modeling,
  expected transactions, customer-level forecasting, or high-value customer identification.
  Also trigger on 'which customers are most valuable' or 'predict future customer revenue.'
  If transaction data is not yet extracted, suggest running data-extraction first.
  CLV predictions enrich audience-segmentation with a value dimension and feed into
  paid-media (acquisition targets), email-analytics (lifecycle), and reporting skills.
---

Implement probabilistic customer lifetime value modeling using BG/NBD for purchase frequency
prediction and Gamma-Gamma for monetary value estimation. Produce customer-level CLV
predictions with confidence intervals, CLV:CAC ratio calculations, cohort-level CLV curves,
and at-risk high-value customer alerts. Support both contractual (subscription) and
non-contractual (transactional) business models.

Parse `$ARGUMENTS` for any inline parameters, file paths, or configuration overrides.

## Objective

Build a complete CLV modeling pipeline that:
- Generates RFM summaries from raw transaction data
- Fits BG/NBD and Gamma-Gamma models for non-contractual settings
- Fits Beta-Geometric models for contractual/subscription settings
- Produces customer-level CLV predictions with confidence intervals
- Calculates CLV:CAC ratios when acquisition cost data is available
- Identifies at-risk high-value customers for retention targeting
- Supports Bayesian extensions via PyMC-Marketing for full posterior distributions

## Step 1: RFM Summary Generation

Generate Recency-Frequency-Monetary-Tenure summaries from transaction-level data.

### Data Requirements
- Input: `workspace/raw/transactions.csv` with columns `customer_id`, `date`, `amount`
- Parse dates robustly (ISO 8601, US, European formats)
- Set the observation period end date (default: max transaction date)

### Processing Rules
- **Frequency**: count of repeat purchases (excludes first purchase)
- **Recency**: time between first purchase and last purchase (in chosen time unit)
- **T (Tenure)**: time between first purchase and observation period end
- **Monetary Value**: mean transaction value of repeat purchases only
- One-time purchasers: frequency=0, recency=0, monetary=NaN (excluded from Gamma-Gamma)

### Data Quality Checks
- Flag duplicate transactions (same customer, date, amount)
- Flag negative amounts and zero-value transactions
- Flag impossible dates (future dates, dates before business inception)
- Report summary statistics: customer count, date range, transaction volume

Run `scripts/rfm_summary.py` to produce the RFM summary DataFrame.

## Step 2: BG/NBD Model Fitting

Fit the BG/NBD (Beta-Geometric/Negative Binomial Distribution) model to predict future
purchase frequency and probability of being alive.

### Maximum Likelihood Estimation
- Use the `lifetimes` library `BetaGeoFitter` for MLE fitting
- Input: RFM summary (frequency, recency, T columns)
- Penalizer coefficient: start with 0.0, increase if convergence issues arise
- Validate convergence: check that log-likelihood is finite and parameters are positive

### Key Outputs
- Model parameters: r, alpha, a, b
- Per-customer expected transactions for horizon period
- Per-customer probability-alive score
- Frequency/recency matrix heatmap for model diagnostics

### Gamma-Gamma Model
- Fit only on customers with frequency > 0 (repeat purchasers)
- Validate independence assumption: correlation between frequency and monetary < 0.3
- If correlation exceeds threshold, warn and document potential bias
- Output: expected average monetary value per transaction per customer

### Combined CLV Calculation

```
CLV = E[transactions] * E[monetary_value] * margin * discount_factor
```

- `margin`: configurable, default 1.0 (gross margin multiplier)
- `discount_rate`: configurable, default to WACC or 0.10 annual rate
- `horizon`: configurable, default 12 months

Run `scripts/fit_bgnbd.py` to fit models and generate parameters.

## Step 3: Bayesian Extensions

When richer uncertainty quantification is needed, use PyMC-Marketing for Bayesian CLV.

### PyMC-Marketing BG/NBD
- Use `pymc_marketing.clv.BetaGeoModel` for full posterior estimation
- Configure sampler: 1000 tune, 1000 draw, 4 chains minimum
- Check convergence: R-hat < 1.01, ESS > 400 for all parameters
- Extract posterior predictive distributions for per-customer CLV

### PyMC-Marketing Gamma-Gamma
- Use `pymc_marketing.clv.GammaGammaModel` for monetary value posteriors
- Same convergence diagnostics as BG/NBD

### Posterior CLV Distributions
- Combine BG/NBD and Gamma-Gamma posteriors for full CLV uncertainty
- Report median CLV with 80% and 95% credible intervals per customer
- Compare interval widths to bootstrapped MLE estimates

### When to Use Bayesian vs. MLE
- MLE: fast exploration, large datasets (>100K customers), initial modeling
- Bayesian: final production models, small datasets, when confidence intervals matter,
  regulatory or stakeholder presentations requiring uncertainty quantification

## Step 4: Contractual CLV (Subscription Models)

For subscription-based businesses, use the Beta-Geometric/Beta-Binomial model.

### Input
- `workspace/raw/subscriptions.csv` with columns: `customer_id`, `start_date`,
  `end_date` (null if still active), `plan_value`
- Convert to survival data: number of renewal periods, whether churned

### Beta-Geometric Model
- Model churn probability per renewal period with Beta-distributed heterogeneity
- Estimate expected remaining lifetime per customer
- CLV = expected_remaining_periods * period_revenue * discount_factor

### Contractual vs. Non-Contractual Selection
- If subscription data is available, default to contractual model
- If only transaction data, default to BG/NBD non-contractual model
- User can override with explicit model selection

## Step 5: Prediction and Scoring

Generate customer-level predictions and actionable segments.

### CLV Predictions
- Produce predictions for configurable horizons: 6, 12, 24 months
- Include point estimate and confidence interval (bootstrapped or posterior)
- Attach prediction metadata: model type, fit date, horizon, parameters

### CLV:CAC Ratio
- Load acquisition costs from `workspace/analysis/acquisition_costs.json` if available
- Calculate per-customer or per-segment CLV:CAC ratio
- Flag customers/segments where ratio < 1.0 (unprofitable)
- If acquisition cost data is missing, flag transparently and skip ratio

### At-Risk High-Value Customers
- Define high-value: top 10% by predicted CLV
- Define at-risk: probability-alive dropped below 50% in the last quarter
- Cross these dimensions to identify the priority retention targets
- Output list with customer_id, predicted_clv, probability_alive, days_since_last_purchase

### CLV-Based Segmentation
- Tier customers by CLV percentile: Platinum (top 10%), Gold (top 25%),
  Silver (top 50%), Bronze (bottom 50%)
- Output segment assignments for use by audience-segmentation skill

Run `scripts/predict_clv.py` to generate predictions and segments.
Run `scripts/validate_clv.py` to assess holdout accuracy.

## Step 6: Model Validation

Validate model quality with temporal holdout methodology.

### Holdout Design
- Split data temporally: calibration period (first N months) and holdout (next M months)
- Fit model on calibration data only
- Predict transactions and monetary value for the holdout period
- Compare predictions to actual holdout observations

### Metrics
- **MAE**: mean absolute error on predicted vs. actual transactions
- **RMSE**: root mean squared error on predicted vs. actual transactions
- **Calibration ratio**: predicted / actual total transactions (target: 0.9-1.1)
- Acceptance: holdout MAE within 20% of calibration period error

### Diagnostic Plots
- Predicted vs. actual frequency scatter plot
- Tracking plot: cumulative predicted vs. actual transactions over time
- Probability-alive calibration: binned predicted vs. observed repurchase rates

## Input / Output Data Contracts

### Inputs
| File | Description | Required |
|------|-------------|----------|
| `workspace/raw/transactions.csv` | Transaction-level data: customer_id, date, amount | Yes |
| `workspace/raw/subscriptions.csv` | Subscription start/end dates for contractual models | Optional |
| `workspace/analysis/acquisition_costs.json` | Per-customer or per-segment CAC from paid-media | Optional |

### Outputs
| File | Description |
|------|-------------|
| `workspace/analysis/clv_predictions.json` | Customer-level CLV with confidence intervals |
| `workspace/analysis/clv_segments.json` | CLV-based customer tiers (Platinum/Gold/Silver/Bronze) |
| `workspace/analysis/at_risk_customers.json` | High-value customers with declining engagement |
| `workspace/reports/clv_analysis.html` | CLV distributions, cohort curves, model diagnostics |

## Cross-Skill Integration

### Audience Segmentation
- Export `clv_segments.json` for value-weighted segment definitions
- CLV tier becomes an enrichment dimension in audience profiles

### Paid Media
- CLV:CAC ratios inform acquisition bid targets by segment
- High-CLV segments justify higher CPAs; low-CLV segments cap bids

### Email Analytics
- Probability-alive scores trigger re-engagement campaigns for at-risk customers
- CLV tiers determine email personalization and offer levels

### Attribution Analysis
- CLV serves as a long-term outcome variable for channel effectiveness assessment
- Attribute CLV (not just conversions) back to marketing touchpoints

### Reporting
- CLV trends, segment distributions, and at-risk alerts appear in executive dashboards

## Financial Services Considerations

- **Multi-product relationships**: aggregate CLV across checking, savings, investment,
  and lending products per household
- **AUM-based CLV**: use fee schedules (basis points on AUM) as the monetary component
  rather than transaction frequency
- **Advisor-intermediated sales**: compute relationship-level CLV aggregated across
  accounts managed by the same advisor, not individual account CLV
- **Regulatory compliance**: CLV predictions used in marketing targeting must comply with
  fair lending and equal opportunity regulations; document model inputs to ensure no
  prohibited factors drive targeting decisions

## Development Guidelines

1. Use the `lifetimes` library for MLE-based models; `PyMC-Marketing` for Bayesian posteriors
2. Always validate with a temporal holdout: fit on first N months, predict next M months,
   compare to actuals
3. Gamma-Gamma model requires frequency > 0; clearly document exclusion of one-time purchasers
4. Discount rate should default to WACC or cost of capital; make it a configurable parameter
5. CLV confidence intervals must be computed, not just point estimates -- use bootstrapping
   or posterior sampling
6. For financial services, implement AUM-weighted CLV variant alongside transaction-based CLV
7. Target pipeline execution: under 90 seconds for 500K customers (MLE path)
8. Bayesian CLV posteriors should produce narrower intervals than bootstrapped MLE on
   identical data

## Acceptance Criteria

- BG/NBD holdout period prediction MAE within 20% of calibration period error
- CLV:CAC calculation correctly handles missing acquisition cost data with transparent flagging
- At-risk identification flags customers with probability-alive < 50% in the last quarter
- Full pipeline from transaction data to CLV predictions executes in under 90 seconds
  for 500K customers
- Bayesian CLV posteriors produce narrower intervals than bootstrapped MLE on identical data
