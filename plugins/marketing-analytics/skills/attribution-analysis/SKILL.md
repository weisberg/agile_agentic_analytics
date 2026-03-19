---
name: Marketing Mix Modeling & Attribution
description: >
  Use when the user mentions attribution, ROAS optimization, channel contribution,
  marketing mix model, MMM, media mix, budget allocation, budget optimization,
  incrementality, adstock, saturation curves, diminishing returns, channel effectiveness,
  media effectiveness, cross-channel attribution, multi-touch attribution, MTA,
  Shapley value attribution, or marketing ROI measurement. Also trigger when user asks
  'which channel is driving results' or 'where should we spend more.' If campaign spend
  data is not yet extracted, suggest running data-extraction first. Results feed into
  reporting and paid-media skills.
---

# Marketing Mix Modeling & Attribution

**Skill ID:** attribution-analysis
**Priority:** P0 — Foundational (highest strategic value)
**Category:** Measurement & Attribution
**Depends On:** data-extraction, paid-media
**Feeds Into:** reporting, paid-media (budget optimization), experimentation (calibration)

---

## Objective

You will automate the end-to-end marketing mix modeling pipeline: data ingestion from
ad platforms, adstock and saturation curve fitting using Bayesian methods, posterior
predictive validation, channel-level contribution decomposition, and budget optimization
with scenario planning. Support calibration with incrementality lift test results.
Produce executive-ready attribution reports with confidence intervals and actionable
budget reallocation recommendations.

---

## Process Steps

Follow these steps in order. Each step must complete successfully before proceeding
to the next. If a step fails, diagnose the issue and retry before moving on.

### Step 1: Data Validation and Preparation

1. Check that required input files exist in `workspace/raw/`:
   - `campaign_spend_{platform}.csv` — Daily or weekly spend by channel
   - `conversions.csv` — Outcome variable (leads, revenue, signups) at matching grain
   - `external_factors.csv` — Optional: seasonality indices, competitor spend, macro indicators
2. If spend data is missing, instruct the user to run the **data-extraction** skill first.
3. Run `scripts/fit_mmm.py --validate` to check data quality:
   - Verify date alignment across all input files
   - Detect and impute missing data windows (flag confidence adjustments)
   - Normalize spend, impressions, and conversion data into a unified grain
4. Default to **weekly** data grain. Only use daily grain when the dataset spans 2+ years.
5. Generate control variables automatically:
   - Seasonality via Fourier terms (yearly and quarterly harmonics)
   - Holiday indicators for the relevant market
   - Macroeconomic indicators if provided in external_factors.csv

### Step 2: Prior Specification

1. Check for `workspace/analysis/incrementality_results.json` from the experimentation skill.
2. If lift test results exist, use `scripts/fit_mmm.py --calibrate` to translate them
   into informative priors. See `references/incrementality_calibration.md`.
3. If no lift test data exists, use weakly informative priors based on:
   - Industry benchmarks for the client's vertical
   - Expert knowledge provided by the user
   - Default half-normal or log-normal priors per `references/mmm_methodology.md`
4. Always run a **prior sensitivity analysis**: fit with both vague and informative priors,
   then compare posteriors to assess prior influence.

### Step 3: Model Fitting

1. Execute `scripts/fit_mmm.py` to fit the Bayesian MMM:
   - Use PyMC-Marketing's `MMM` class as the primary framework
   - Sample with NUTS (No-U-Turn Sampler) via MCMC
   - Estimate adstock (carry-over) parameters per channel: geometric or Weibull decay
   - Estimate saturation (diminishing returns) parameters per channel: Hill function
2. Store all MCMC trace data for reproducibility using ArviZ InferenceData format.
3. If MCMC fails or is impractical, fall back to lightweight ridge regression
   (Robyn-style) and document the methodological tradeoff.

### Step 4: Model Validation

1. Execute `scripts/validate_model.py` to assess model quality:
   - Posterior predictive checks: 90%+ of observed data within 90% credible interval
   - R-hat < 1.05 for all parameters
   - Effective sample size > 400 for all parameters
   - WAIC and LOO-CV for model comparison if multiple specifications are tested
2. If diagnostics fail, adjust the model (reparameterize, increase samples, tighten priors)
   and refit. Do not proceed with a poorly converged model.

### Step 5: Contribution Decomposition

1. Execute `scripts/compute_contributions.py` to decompose the outcome into channel-level
   contributions:
   - Compute posterior mean and credible intervals per channel
   - Verify contributions sum to total observed outcome within 2% tolerance
   - Identify the base (intercept + controls) vs. media-driven components
2. Write results to `workspace/analysis/mmm_channel_contributions.json`.

### Step 6: Budget Optimization

1. Execute `scripts/optimize_budget.py` to find optimal budget allocation:
   - Maximize total conversions/revenue subject to total budget constraint
   - Respect per-channel minimum and maximum spend constraints if provided
   - Propagate posterior uncertainty into optimization (use posterior samples)
2. Generate scenario analyses as requested by the user:
   - "What if we shift X% from display to search?"
   - "What if total budget increases/decreases by Y%?"
3. Produce marginal ROAS curves showing next-dollar efficiency per channel.
4. Flag channels approaching saturation ceilings.
5. Write results to `workspace/analysis/mmm_budget_optimization.json`.

### Step 7: Reporting

1. Generate `workspace/analysis/mmm_diagnostics.json` with MCMC convergence metrics.
2. Generate `workspace/reports/mmm_executive_summary.html` containing:
   - Channel contribution waterfall chart with uncertainty bands
   - Budget reallocation recommendation table with expected lift estimates
   - Model diagnostics: trace plots, R-hat, effective sample size, posterior predictive coverage
   - Marginal ROAS curves per channel
3. All visualizations must include confidence/credible intervals. Never present point
   estimates without uncertainty.

---

## Key Capabilities

### Data Preparation
- Normalize spend, impressions, and conversion data across platforms into a unified grain
- Automatically detect and impute missing data windows with flagged confidence adjustments
- Generate control variables: seasonality (Fourier), holidays, macroeconomic indicators,
  competitor activity

### Model Fitting
- Fit Bayesian MMM with MCMC sampling (NUTS) via PyMC-Marketing's MMM class
- Estimate adstock (carry-over) and saturation (diminishing returns) parameters per channel
- Compute posterior channel contributions with credible intervals
- Run posterior predictive checks and WAIC/LOO model comparison

### Budget Optimization
- Solve constrained optimization: maximize total conversions/revenue subject to budget constraints
- Generate scenario analyses: "what if we shift X% from display to search?"
- Produce marginal ROAS curves showing next-dollar efficiency per channel
- Account for saturation: flag channels approaching diminishing returns ceiling

### Multi-Touch Attribution (Supplementary)
- Shapley value attribution for fair credit allocation across touchpoints
- Markov chain models for path-based attribution
- Data-driven models when user-level journey data is available

### Reporting
- Channel contribution waterfall charts with uncertainty bands
- Budget reallocation recommendation tables with expected lift estimates
- Model diagnostics dashboard: trace plots, R-hat, ESS, posterior predictive coverage

---

## Input / Output Data Contracts

### Inputs

| File | Description | Required |
|------|-------------|----------|
| `workspace/raw/campaign_spend_{platform}.csv` | Daily/weekly spend by channel from data-extraction skill. Columns: `date`, `channel`, `spend`, `impressions`, `clicks`. | Yes |
| `workspace/raw/conversions.csv` | Outcome variable at matching grain. Columns: `date`, `conversions`, `revenue`. | Yes |
| `workspace/raw/external_factors.csv` | Seasonality indices, competitor spend, macro indicators. Columns: `date`, `factor_name`, `value`. | No |
| `workspace/analysis/incrementality_results.json` | Calibration priors from experimentation skill. Schema: `{"channel": str, "lift": float, "ci_lower": float, "ci_upper": float}`. | No |

### Outputs

| File | Description |
|------|-------------|
| `workspace/analysis/mmm_channel_contributions.json` | Posterior mean and credible intervals per channel |
| `workspace/analysis/mmm_budget_optimization.json` | Optimal allocation under current and scenario budgets |
| `workspace/analysis/mmm_diagnostics.json` | MCMC convergence metrics, model fit statistics |
| `workspace/reports/mmm_executive_summary.html` | Interactive report with charts and recommendations |

---

## Cross-Skill Integration

This skill is the **strategic hub** of the marketing analytics portfolio:

- **data-extraction** (upstream): Provides normalized campaign spend data. If spend files
  are missing, direct the user to run data-extraction first.
- **paid-media** (bidirectional): Consumes spend metrics as input; budget optimization
  outputs directly inform paid-media's budget pacing and bid strategies.
- **experimentation** (bidirectional): Incrementality test results from experimentation
  serve as calibration priors for the MMM. In return, MMM results identify channels
  where incrementality is uncertain, guiding future experiment design. This creates a
  virtuous cycle: experiments validate the model, the model guides budget allocation,
  and budget changes create new natural experiments.
- **reporting** (downstream): All MMM outputs (contributions, optimization, diagnostics)
  feed into executive dashboards via the reporting skill.
- **compliance-review** (downstream, financial services): In financial services mode,
  all reports must pass through compliance-review before distribution.

When invoking cross-skill workflows:
1. Always check for upstream data availability before starting analysis.
2. Write outputs in the canonical JSON schemas so downstream skills can parse them.
3. Include metadata (timestamp, model version, data range) in all output files.

---

## Financial Services Considerations

When operating in a financial services context, apply these additional requirements:

1. **Confidence intervals required**: All performance claims derived from MMM must include
   credible intervals and methodology disclaimers. Never present bare point estimates.
2. **SEC Marketing Rule compliance**: Past performance language must comply with the SEC
   Marketing Rule. Before distributing any attribution report externally, invoke the
   **compliance-review** skill to validate language and disclosures.
3. **Net-of-fees adjustment**: Attribution to specific fund products requires net-of-fees
   performance calculation and benchmark comparison. Always ask whether results should
   be presented gross or net of fees.
4. **Long sales cycles**: Financial services sales cycles can span 12-36 months
   (especially institutional AUM acquisition). Account for this by:
   - Using longer adstock decay windows
   - Considering lagged conversion models
   - Separating lead-generation attribution from AUM-conversion attribution
5. **Audit trail**: Maintain complete provenance of all model inputs, parameters, and
   outputs for regulatory audit purposes.

---

## Development Guidelines

Follow these guidelines strictly when implementing and running MMM analyses:

1. **PyMC-Marketing first**: Use PyMC-Marketing as the primary framework. Include fallback
   to lightweight Robyn-style ridge regression only when MCMC infrastructure is unavailable
   or the user explicitly requests it.
2. **Deterministic computation**: All statistical computations must run in the Python
   scripts under `scripts/`. Never estimate statistical quantities, posterior distributions,
   p-values, or model parameters within the LLM. The LLM interprets results; scripts
   compute them.
3. **Weekly default grain**: Default to weekly data aggregation. Only use daily grain when
   the dataset contains 2+ years of daily history.
4. **Prior sensitivity**: Always run prior sensitivity analysis. Fit with both vague and
   informative priors, compare posteriors, and report the degree of prior influence.
5. **Reproducibility**: Store all MCMC trace data in ArviZ InferenceData format. Record
   random seeds, sampler settings, and PyMC-Marketing version in diagnostics output.
6. **Progressive disclosure**: This skill loads progressively. Metadata (name, description)
   loads at startup (~100 tokens). Full SKILL.md instructions load on activation (~5,000
   tokens). Reference files and scripts load on-demand during execution.
7. **Uncertainty everywhere**: Never present a result without its uncertainty. Every
   channel contribution, ROAS estimate, and budget recommendation must include credible
   intervals or posterior distributions.

---

## Acceptance Criteria

A completed MMM analysis must satisfy all of the following:

- [ ] R-hat < 1.05 for all estimated parameters
- [ ] Effective sample size > 400 for all estimated parameters
- [ ] Posterior predictive check covers 90%+ of observed data within 90% credible interval
- [ ] Budget optimizer produces feasible allocations that sum to the specified total budget
- [ ] Scenario analysis correctly propagates uncertainty from posterior to predictions
- [ ] Channel contribution decomposition sums to total observed outcome within 2% tolerance
- [ ] Full pipeline executes end-to-end from raw data to executive report in a single session

---

## Reference Files

- `references/mmm_methodology.md` — Bayesian MMM theory, adstock/saturation math, prior guidance
- `references/pymc_marketing_api.md` — PyMC-Marketing MMM class reference and usage patterns
- `references/incrementality_calibration.md` — Translating lift test results into priors

## Scripts

- `scripts/fit_mmm.py` — Core MMM fitting with PyMC-Marketing (MCMC sampling, diagnostics)
- `scripts/optimize_budget.py` — Constrained optimization using posterior samples
- `scripts/compute_contributions.py` — Channel-level contribution decomposition
- `scripts/validate_model.py` — Posterior predictive checks, WAIC, LOO-CV computation
