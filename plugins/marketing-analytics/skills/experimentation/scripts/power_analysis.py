"""Power analysis: sample size and MDE calculation for A/B experiments.

Supports both proportion metrics (conversion rates) and continuous metrics
(revenue, session duration). Uses scipy.stats for all statistical computations.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy import stats


@dataclass
class PowerAnalysisResult:
    """Result container for power analysis calculations.

    Attributes:
        sample_size_per_group: Required observations per experiment group.
        total_sample_size: Total observations across all groups.
        mde_absolute: Minimum detectable effect in absolute metric units.
        mde_relative: Minimum detectable effect as fraction of baseline.
        estimated_duration_days: Estimated experiment duration given traffic.
        power: Statistical power (1 - Type II error rate).
        alpha: Significance level (Type I error rate).
        num_groups: Number of experiment groups (including control).
    """

    sample_size_per_group: int
    total_sample_size: int
    mde_absolute: float
    mde_relative: float
    estimated_duration_days: Optional[int]
    power: float
    alpha: float
    num_groups: int


def calculate_sample_size_proportion(
    baseline_rate: float,
    mde_relative: float,
    alpha: float = 0.05,
    power: float = 0.80,
    num_groups: int = 2,
    two_sided: bool = True,
) -> PowerAnalysisResult:
    """Calculate required sample size for a proportion (conversion rate) test.

    Uses the normal approximation to the binomial for the two-sample
    proportion z-test.

    Args:
        baseline_rate: Control group expected conversion rate (e.g., 0.05 for 5%).
        mde_relative: Minimum detectable effect as a relative change
            (e.g., 0.10 for a 10% relative lift).
        alpha: Significance level. Default 0.05.
        power: Statistical power (1 - beta). Default 0.80.
        num_groups: Number of groups including control. Default 2.
        two_sided: Whether to use a two-sided test. Default True.

    Returns:
        PowerAnalysisResult with computed sample sizes and parameters.

    Raises:
        ValueError: If baseline_rate is not in (0, 1) or mde_relative <= 0.
    """
    # TODO: Validate inputs (baseline_rate in (0,1), mde_relative > 0, etc.)
    # TODO: Compute absolute MDE from baseline_rate and mde_relative
    # TODO: Compute pooled proportion p_bar
    # TODO: Look up Z critical values for alpha and power
    # TODO: Apply the two-sample proportion sample size formula:
    #   n = (Z_{a/2} * sqrt(2*p_bar*(1-p_bar)) + Z_b * sqrt(p_c*(1-p_c) + p_t*(1-p_t)))^2 / delta^2
    # TODO: Return PowerAnalysisResult
    raise NotImplementedError("Sample size calculation for proportions not yet implemented")


def calculate_sample_size_continuous(
    baseline_mean: float,
    baseline_std: float,
    mde_relative: float,
    alpha: float = 0.05,
    power: float = 0.80,
    num_groups: int = 2,
    two_sided: bool = True,
) -> PowerAnalysisResult:
    """Calculate required sample size for a continuous metric test.

    Uses the two-sample t-test formula assuming equal variances.

    Args:
        baseline_mean: Control group expected mean.
        baseline_std: Control group expected standard deviation.
        mde_relative: Minimum detectable effect as a relative change
            (e.g., 0.05 for a 5% relative lift in the mean).
        alpha: Significance level. Default 0.05.
        power: Statistical power (1 - beta). Default 0.80.
        num_groups: Number of groups including control. Default 2.
        two_sided: Whether to use a two-sided test. Default True.

    Returns:
        PowerAnalysisResult with computed sample sizes and parameters.

    Raises:
        ValueError: If baseline_std <= 0 or mde_relative <= 0.
    """
    # TODO: Validate inputs
    # TODO: Compute absolute MDE: delta = baseline_mean * mde_relative
    # TODO: Apply formula: n = (Z_{a/2} + Z_b)^2 * 2 * sigma^2 / delta^2
    # TODO: Return PowerAnalysisResult
    raise NotImplementedError("Sample size calculation for continuous metrics not yet implemented")


def calculate_mde(
    sample_size_per_group: int,
    baseline_rate: Optional[float] = None,
    baseline_mean: Optional[float] = None,
    baseline_std: Optional[float] = None,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sided: bool = True,
) -> float:
    """Calculate the minimum detectable effect for a given sample size.

    Inverts the sample size formula to find the MDE achievable with the
    available sample. Exactly one of (baseline_rate) or (baseline_mean,
    baseline_std) must be provided.

    Args:
        sample_size_per_group: Available observations per group.
        baseline_rate: Baseline conversion rate (for proportion tests).
        baseline_mean: Baseline mean (for continuous metric tests).
        baseline_std: Baseline standard deviation (for continuous metric tests).
        alpha: Significance level. Default 0.05.
        power: Statistical power. Default 0.80.
        two_sided: Whether to use a two-sided test. Default True.

    Returns:
        The minimum detectable effect as a relative change.

    Raises:
        ValueError: If inputs are inconsistent or insufficient.
    """
    # TODO: Determine metric type from provided parameters
    # TODO: Invert the appropriate sample size formula to solve for delta
    # TODO: Convert absolute delta to relative MDE
    raise NotImplementedError("MDE calculation not yet implemented")


def estimate_duration(
    required_sample_size_total: int,
    daily_traffic: int,
    traffic_allocation: float = 1.0,
    min_days: int = 7,
    round_to_weeks: bool = True,
) -> int:
    """Estimate experiment duration in days.

    Args:
        required_sample_size_total: Total sample needed across all groups.
        daily_traffic: Average daily eligible users.
        traffic_allocation: Fraction of traffic allocated to experiment
            (e.g., 0.5 for 50%). Default 1.0.
        min_days: Minimum experiment duration in days. Default 7.
        round_to_weeks: If True, round up to the nearest full week. Default True.

    Returns:
        Estimated duration in days.

    Raises:
        ValueError: If daily_traffic <= 0 or traffic_allocation not in (0, 1].
    """
    # TODO: Validate inputs
    # TODO: Compute raw duration: ceil(required_sample / (daily_traffic * allocation))
    # TODO: Apply minimum duration constraint
    # TODO: Round to full weeks if requested
    raise NotImplementedError("Duration estimation not yet implemented")
