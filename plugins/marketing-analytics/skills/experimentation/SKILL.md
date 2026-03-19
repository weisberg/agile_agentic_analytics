---
name: experimentation
description: >
  Use when the user mentions A/B test, experiment, hypothesis test, statistical
  significance, p-value, confidence interval, CUPED, variance reduction, power
  analysis, sample size calculation, minimum detectable effect, MDE, sequential
  test, early stopping, Bayesian AB test, multi-armed bandit, experiment design,
  split test, holdout test, control group, treatment effect, incrementality test,
  causal inference, or uplift modeling. Also trigger on 'did this change work' or
  'how long should we run this test.' If segment-level analysis is needed and
  segments are not defined, suggest running audience-segmentation first.
---

# A/B Testing & Experimentation

Statistical experiment design, CUPED variance reduction, sequential testing,
and causal analysis.

| Property       | Value                                                          |
| :------------- | :------------------------------------------------------------- |
| Skill ID       | experimentation                                                |
| Priority       | P0 — Foundational (powers all optimization)                    |
| Category       | Experimentation & Causal Inference                             |
| Depends On     | data-extraction, audience-segmentation (for stratification)    |
| Feeds Into     | attribution-analysis, funnel-analysis, email-analytics, reporting |

## Objective

Provide a complete experimentation toolkit: power analysis and minimum
detectable effect calculation for experiment design; frequentist and Bayesian
analysis for completed experiments; CUPED variance reduction to accelerate
learning; sequential testing with always-valid confidence intervals for early
stopping; and automated diagnostics including Sample Ratio Mismatch detection
and novelty/primacy effect identification. Produce structured experiment result
reports suitable for both technical and executive audiences.

## Process Steps

1. **Validate inputs.** Load `experiment_data.csv` and verify required columns
   (`user_id`, `variant`, `metric`, `timestamp`). If pre-experiment covariates
   are provided, confirm that covariate measurement window ends before treatment
   assignment.

2. **Run diagnostics.** Execute SRM check via `scripts/srm_check.py`. If the
   chi-squared goodness-of-fit test yields p < 0.001, halt analysis and report
   the mismatch with a diagnostic breakdown by platform, date, and segment.

3. **Design or analyze.**
   - *Pre-experiment path:* Run `scripts/power_analysis.py` to compute required
     sample size, MDE, and estimated duration given historical traffic.
   - *Post-experiment path:* Proceed to step 4.

4. **Apply CUPED (when covariates available).** Run `scripts/cuped.py` to
   regress each metric on its pre-experiment covariate, compute theta, and
   produce adjusted metric values. Log variance reduction achieved.

5. **Run frequentist analysis.** Execute `scripts/frequentist_test.py` on raw
   and CUPED-adjusted metrics. Apply Benjamini-Hochberg correction across all
   metrics. Classify results as significant vs. exploratory.

6. **Run Bayesian analysis.** Execute `scripts/bayesian_test.py` to compute
   posterior distributions, probability of being best, and expected loss for
   each variant.

7. **Run sequential monitoring (if experiment is ongoing).** Execute
   `scripts/sequential_test.py` to compute always-valid confidence intervals
   and check stopping boundaries.

8. **Check guardrail metrics.** For each guardrail metric, verify that no
   variant degrades beyond the pre-defined threshold. Flag violations.

9. **Detect novelty/primacy effects.** Segment results by time window and test
   for trend in effect size over time.

10. **Generate report.** Compile all results into
    `workspace/reports/experiment_report.html` with forest plots, posterior
    distributions, monitoring charts, and a plain-language recommendation.

## Key Capabilities

### Experiment Design

- Calculate required sample size given baseline rate, MDE, power (default 80%),
  and significance level (default 5%).
- Estimate experiment duration based on historical traffic volume and required
  sample size.
- Design stratified randomization schemes for low-traffic segments.
- Generate experiment specification documents with hypothesis, metrics,
  guardrails, and decision criteria.

Refer to `references/experiment_design.md` for power analysis formulas, MDE
lookup tables, and duration estimation methodology.

### Statistical Analysis

- Execute frequentist hypothesis tests with effect sizes, p-values, and
  confidence intervals (z-test, t-test, chi-squared, proportion tests).
- Compute CUPED-adjusted estimates: regress metric on pre-experiment covariate,
  analyze residuals. See `references/cuped_methodology.md`.
- Run Bayesian analysis: posterior distributions, probability of being best,
  expected loss. See `references/bayesian_ab.md`.
- Apply Benjamini-Hochberg correction for multiple metric testing; flag
  significant vs. exploratory results.

### Sequential Monitoring

- Implement always-valid confidence intervals using mixture sequential
  probability ratio test (mSPRT).
- Support group sequential designs with O'Brien-Fleming or Pocock spending
  functions.
- Generate monitoring dashboards showing cumulative effect estimates with valid
  stopping boundaries.

Refer to `references/sequential_testing.md` for theory and implementation
guidance.

### CUPED Variance Reduction

- Regress post-experiment metric on pre-experiment covariate to compute theta.
- Produce adjusted metric: Y_adj = Y - theta * (X - mean(X)).
- Typical variance reduction of 30-40% when covariates are well-correlated.
- Validate that covariates are strictly pre-treatment to avoid bias.

### Diagnostics and Reporting

- Detect Sample Ratio Mismatch with chi-squared goodness-of-fit test (flag if
  p < 0.001).
- Identify novelty/primacy effects through time-windowed analysis.
- Produce structured result reports: effect size, CI, practical significance,
  recommendation.

## Input / Output Data Contracts

### Inputs

| File | Description | Required |
| :--- | :---------- | :------- |
| `workspace/raw/experiment_data.csv` | User-level data with variant assignment, metric values, timestamps | Yes |
| `workspace/raw/pre_experiment_covariates.csv` | Pre-period metric values for CUPED | No (recommended) |
| `workspace/processed/segments.json` | Segment definitions from audience-segmentation | No (for subgroup analysis) |

### Outputs

| File | Description |
| :--- | :---------- |
| `workspace/analysis/experiment_results.json` | Structured results: effect sizes, CIs, p-values, Bayesian posteriors |
| `workspace/analysis/cuped_adjustment.json` | CUPED theta estimates and variance reduction achieved |
| `workspace/analysis/incrementality_results.json` | Lift estimates consumable by attribution-analysis for MMM calibration |
| `workspace/reports/experiment_report.html` | Visual report with forest plots, posterior distributions, monitoring charts |

## Cross-Skill Integration

The experimentation skill is the scientific backbone of the analytics portfolio:

- **attribution-analysis:** Incrementality test results from this skill
  calibrate the MMM priors used in attribution modeling.
- **funnel-analysis:** Funnel analysis generates hypotheses about conversion
  bottlenecks; experimentation validates those hypotheses with controlled tests.
- **email-analytics:** All send-time optimization and subject-line testing is
  delegated to this skill for proper statistical rigor.
- **web-analytics:** CUPED leverages pre-experiment behavioral data sourced
  from web analytics pipelines.
- **reporting:** Experiment result summaries feed into executive dashboards
  and periodic performance reports.

## Financial Services Considerations

When operating in financial services mode:

- All experiment variants involving investor-facing content must be pre-approved
  by compliance before launch.
- Required regulatory disclosures must appear in all variants and cannot be the
  variable under test.
- Experiment result claims used in marketing materials must include statistical
  methodology footnotes.
- Email experiments must maintain CAN-SPAM and SEC archival requirements across
  all variants.

## Development Guidelines

1. All statistical computations must be deterministic Python scripts using
   `scipy.stats` and `numpy`. Never let the LLM estimate p-values.

2. CUPED implementation must validate that the covariate was measured entirely
   pre-treatment to avoid post-treatment bias.

3. Default to two-sided tests. One-sided tests are permitted only when
   explicitly justified in the experiment specification.

4. Always compute both frequentist and Bayesian results. Let the user choose
   their decision framework.

5. Sequential test implementation must guarantee Type I error control at the
   nominal level.

6. Include automated guardrail metric checking: if any guardrail metric
   degrades beyond threshold, flag the experiment.

## Scripts

| Script | Purpose |
| :----- | :------ |
| `scripts/power_analysis.py` | Sample size and MDE calculation |
| `scripts/frequentist_test.py` | z-test, t-test, chi-squared, proportion test with BH correction |
| `scripts/bayesian_test.py` | Posterior computation, probability of being best, expected loss |
| `scripts/cuped.py` | CUPED covariate regression, theta estimation, adjusted metrics |
| `scripts/sequential_test.py` | mSPRT boundaries, always-valid CIs, alpha-spending |
| `scripts/srm_check.py` | Sample Ratio Mismatch detection with diagnostic breakdown |

## Reference Files

| Reference | Content |
| :-------- | :------ |
| `references/experiment_design.md` | Power analysis formulas, MDE tables, duration estimation |
| `references/cuped_methodology.md` | CUPED math, covariate selection, theta derivation |
| `references/sequential_testing.md` | mSPRT theory, alpha-spending functions, stopping rules |
| `references/bayesian_ab.md` | Conjugate prior selection, loss functions, decision rules |

## Acceptance Criteria

- Power analysis produces sample sizes within 5% of analytical formulas for
  known distributions.
- CUPED adjustment produces variance reduction of 20%+ on realistic simulated
  data with correlated covariates.
- Sequential test maintains Type I error rate below nominal alpha (verified via
  10,000 simulation runs).
- SRM detection correctly identifies 95%+ of intentionally imbalanced datasets
  at 0.1% threshold.
- Bayesian posterior probabilities match analytical conjugate solutions for
  Beta-Binomial test cases.
- End-to-end pipeline from raw data to experiment report executes in under 60
  seconds for 1M-row datasets.
