---
name: sample-size
description: Calculate required sample size and experiment duration for an A/B test. Provide baseline rate and minimum detectable effect, or answer interactively.
---

Calculate the required sample size for an A/B test. Parse any parameters from `$ARGUMENTS` (e.g., "baseline 5% mde 10% relative") or collect them interactively.

## Required Inputs

Gather these from the user (use defaults where noted):

| Parameter | Description | Default |
|-----------|-------------|---------|
| Baseline rate | Current conversion rate OR baseline mean + std dev for continuous metrics | _required_ |
| MDE | Minimum detectable effect (absolute or relative) | _required_ |
| Significance level (alpha) | Type I error rate | 0.05 |
| Statistical power (1 - beta) | Probability of detecting a true effect | 0.80 |
| Number of variants | Including control | 2 |
| Sidedness | One-sided or two-sided test | Two-sided |
| Daily traffic | Visitors per day (optional, to estimate duration) | _optional_ |

## Output

### 1. Sample Size Calculation

- Show the formula used:
  - **Proportions:** `n = (Z_alpha + Z_beta)^2 * (p1(1-p1) + p2(1-p2)) / (p2 - p1)^2`
  - **Continuous:** `n = (Z_alpha + Z_beta)^2 * 2 * sigma^2 / delta^2`
- Walk through the calculation step by step
- State the required sample size **per variant**
- State the total sample size across all variants

### 2. Duration Estimate

If daily traffic was provided:
- `Duration = sample_size_per_variant * num_variants / daily_traffic`
- Round up to whole days
- Recommend running for at least 1-2 full weeks to capture day-of-week effects

### 3. Sensitivity Table

Show sample size at multiple MDE levels to help the user choose:

| Relative MDE | Absolute MDE | Sample Size per Variant | Duration (days) |
|-------------|-------------|------------------------|-----------------|
| 1% | ... | ... | ... |
| 2% | ... | ... | ... |
| 5% | ... | ... | ... |
| 10% | ... | ... | ... |
| 20% | ... | ... | ... |

### 4. Warnings

Flag if applicable:
- Very large sample size (>1M per variant) — consider whether the MDE is too small or if the metric is too noisy
- Very short duration (<7 days) — novelty effects and day-of-week bias risk
- Multiple variants — explain the sample size multiplier
- Multiple primary metrics — explain the need for correction and its effect on required sample size
- Low baseline rate — note that proportions tests lose power with extreme baselines

### 5. Reproducible Code

Generate a Python snippet using `statsmodels.stats.power` or manual calculation that reproduces the result:

```python
from statsmodels.stats.power import NormalIndPower, TTestIndPower
# or manual calculation with scipy.stats.norm
```
