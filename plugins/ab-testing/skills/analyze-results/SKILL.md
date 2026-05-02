---
name: analyze-results
description: Analyze A/B test results with proper statistical methods. Accepts data as CSV, summary stats, or a file path. Reports significance, confidence intervals, effect sizes, and flags common issues.
---

Analyze A/B test results provided by the user. Accept data in any reasonable format:
- Pasted CSV/TSV
- Summary table (variant, visitors, conversions)
- File path to read
- Raw numbers stated in prose

Parse `$ARGUMENTS` for any inline data or file paths.

## Defaults

Use these defaults unless the user or experiment plan specifies otherwise:
- Significance level: 0.05
- Test sidedness: two-sided
- Generated code language: Python

## Analysis Pipeline

### Step 1: Parse and Validate Data

- Identify the metric type: proportion (conversion rate), continuous (mean), or ratio
- Identify the variants (control vs. treatment(s))
- Display a summary table of the input data

### Step 2: SRM Check (Sample Ratio Mismatch)

**Always do this first.** Run a chi-squared goodness-of-fit test comparing observed sample sizes to expected allocation (default 50/50 or as stated by user).

- If p < 0.01: **CRITICAL WARNING** — sample ratio mismatch detected. Results may be invalid. Explain common causes (bot filtering, redirect failures, bucketing bugs) and recommend investigating before interpreting results.
- If p >= 0.01: note that SRM check passed.

### Step 3: Statistical Test

Choose the appropriate test based on metric type:

**Proportions (conversion rate):**
- Two-proportion z-test (or chi-squared test for equivalence)
- Report: conversion rates, absolute difference, relative lift, 95% CI, p-value

**Continuous metrics (mean values):**
- Welch's t-test (does not assume equal variance)
- Report: means, difference, relative lift, 95% CI, p-value

**Revenue / skewed metrics:**
- Recommend and generate code for: bootstrap confidence intervals, Mann-Whitney U, or log-transformed t-test
- Explain why standard t-tests may be unreliable

**Multiple variants (>2):**
- Apply correction: Bonferroni, Holm, or Dunnett's test
- Clearly show both uncorrected and corrected p-values

### Step 4: Effect Size

- **Proportions:** Cohen's h
- **Continuous:** Cohen's d
- Interpret: small (<0.2), medium (0.2-0.8), large (>0.8)

### Step 5: Post-hoc Power

If the result is NOT statistically significant:
- Calculate the achieved power given the observed effect size
- If power is low (<0.5), note that the test was underpowered and the null result is inconclusive

### Step 6: Plain-English Interpretation

Provide a clear summary, e.g.:
> "Variant B increased conversion rate by 3.2% (relative), from 12.0% to 12.4%. The 95% confidence interval for the absolute difference is [0.1%, 0.7%]. This result is statistically significant (p = 0.008) with a small effect size (Cohen's h = 0.12)."

### Step 7: Flag Issues

Check for and flag:
- **SRM** (already done in step 2)
- **Novelty/primacy effects** if duration data is available (compare early vs. late results)
- **Simpson's paradox** if segment data is present
- **Multiple testing** if multiple metrics are being analyzed
- **Low sample size** relative to what a power analysis would recommend

### Step 8: Reproducible Code

Generate a complete Python script using `scipy.stats` and/or `statsmodels` that reproduces the full analysis. The code should:
- Be runnable as-is (include imports and data)
- Print all key results
- Include comments explaining each step
