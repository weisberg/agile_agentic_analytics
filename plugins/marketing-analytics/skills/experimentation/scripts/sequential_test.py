"""Sequential testing for continuous monitoring of A/B experiments.

Implements mSPRT boundaries, always-valid confidence intervals, and
alpha-spending functions (O'Brien-Fleming, Pocock) for valid early stopping.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import stats


class SpendingFunction(Enum):
    """Supported alpha-spending functions for group sequential designs."""

    OBRIEN_FLEMING = "obrien_fleming"
    POCOCK = "pocock"


@dataclass
class SequentialResult:
    """Result of a sequential test at a single analysis point.

    Attributes:
        metric_name: Name of the metric being monitored.
        current_n: Current sample size per group.
        planned_n: Planned total sample size per group.
        information_fraction: current_n / planned_n.
        effect_estimate: Current estimate of the treatment effect.
        always_valid_ci: Always-valid confidence interval at this point.
        msprt_statistic: Mixture sequential probability ratio test statistic.
        reject_null: Whether the null can be rejected at this look.
        boundary_value: Critical boundary value at this information fraction.
        alpha_spent: Cumulative alpha spent up to this look.
        stop_for_futility: Whether the experiment should stop for futility.
        conditional_power: Estimated power given current trend.
    """

    metric_name: str
    current_n: int
    planned_n: int
    information_fraction: float
    effect_estimate: float
    always_valid_ci: Tuple[float, float]
    msprt_statistic: float
    reject_null: bool
    boundary_value: float
    alpha_spent: float
    stop_for_futility: bool
    conditional_power: float


def compute_msprt_statistic(
    running_mean_diff: float,
    sample_variance: float,
    current_n: int,
    tau_squared: float,
) -> float:
    """Compute the mixture sequential probability ratio test statistic.

    Uses a Gaussian mixing distribution over plausible effect sizes.

    Args:
        running_mean_diff: Current mean difference (treatment - control).
        sample_variance: Estimated variance of individual observations.
        current_n: Current sample size per group.
        tau_squared: Mixing variance parameter controlling test sensitivity.

    Returns:
        The mSPRT likelihood ratio Lambda_n.
    """
    # TODO: Compute Lambda_n using the normal mixture formula:
    #   Lambda = sqrt(sigma^2 / (sigma^2 + n*tau^2)) *
    #            exp(n^2 * mean_diff^2 * tau^2 / (2 * sigma^2 * (sigma^2 + n*tau^2)))
    # TODO: Return Lambda_n
    raise NotImplementedError("mSPRT statistic computation not yet implemented")


def compute_always_valid_ci(
    running_mean_diff: float,
    sample_variance: float,
    current_n: int,
    tau_squared: float,
    alpha: float = 0.05,
) -> Tuple[float, float]:
    """Compute always-valid confidence interval at the current sample size.

    These intervals are valid at every point in time, not just at the
    pre-planned stopping time.

    Args:
        running_mean_diff: Current mean difference (treatment - control).
        sample_variance: Estimated variance of individual observations.
        current_n: Current sample size per group.
        tau_squared: Mixing variance parameter.
        alpha: Significance level. Default 0.05.

    Returns:
        Tuple of (lower_bound, upper_bound) for the always-valid CI.
    """
    # TODO: Compute the always-valid CI half-width using:
    #   half_width = sqrt((sigma^2 + n*tau^2) / (n^2*tau^2) *
    #                     2 * log(1/alpha * sqrt((sigma^2 + n*tau^2) / sigma^2)))
    # TODO: Return (mean_diff - half_width, mean_diff + half_width)
    raise NotImplementedError("Always-valid CI computation not yet implemented")


def obrien_fleming_spending(
    information_fraction: float,
    alpha: float = 0.05,
) -> float:
    """Compute cumulative alpha spent using O'Brien-Fleming spending function.

    Conservative early, spending most alpha near the planned end.

    Args:
        information_fraction: Current fraction of planned information (n/N).
        alpha: Overall significance level. Default 0.05.

    Returns:
        Cumulative alpha spent at this information fraction.
    """
    # TODO: Compute alpha*(t) = 2 * (1 - Phi(Z_{alpha/2} / sqrt(t)))
    # TODO: Handle edge case where information_fraction is near 0
    # TODO: Return cumulative alpha spent
    raise NotImplementedError("O'Brien-Fleming spending not yet implemented")


def pocock_spending(
    information_fraction: float,
    alpha: float = 0.05,
) -> float:
    """Compute cumulative alpha spent using Pocock spending function.

    Spends alpha more evenly across looks compared to O'Brien-Fleming.

    Args:
        information_fraction: Current fraction of planned information (n/N).
        alpha: Overall significance level. Default 0.05.

    Returns:
        Cumulative alpha spent at this information fraction.
    """
    # TODO: Compute alpha*(t) = alpha * ln(1 + (e - 1) * t)
    # TODO: Return cumulative alpha spent
    raise NotImplementedError("Pocock spending not yet implemented")


def compute_boundary(
    information_fraction: float,
    spending_function: SpendingFunction = SpendingFunction.OBRIEN_FLEMING,
    alpha: float = 0.05,
    previous_alpha_spent: float = 0.0,
) -> float:
    """Compute the rejection boundary at a given information fraction.

    Args:
        information_fraction: Current fraction of planned information.
        spending_function: Which spending function to use. Default O'Brien-Fleming.
        alpha: Overall significance level. Default 0.05.
        previous_alpha_spent: Alpha already spent at previous looks. Default 0.0.

    Returns:
        The critical z-value boundary for this look.
    """
    # TODO: Compute alpha to spend at this look:
    #   alpha_this_look = spending(t) - previous_alpha_spent
    # TODO: Convert to z-boundary: Z = Phi^{-1}(1 - alpha_this_look / 2)
    # TODO: Return z-boundary
    raise NotImplementedError("Boundary computation not yet implemented")


def compute_conditional_power(
    current_effect: float,
    current_n: int,
    planned_n: int,
    sample_variance: float,
    alpha: float = 0.05,
) -> float:
    """Estimate conditional power given the current observed trend.

    Used for futility analysis: if conditional power is very low, the
    experiment is unlikely to reach significance.

    Args:
        current_effect: Current estimated effect size.
        current_n: Current sample size per group.
        planned_n: Planned sample size per group.
        sample_variance: Current estimated variance.
        alpha: Significance level. Default 0.05.

    Returns:
        Estimated probability of reaching significance at the planned end.
    """
    # TODO: Project final test statistic assuming current trend continues
    # TODO: Compute probability that projected statistic exceeds critical value
    # TODO: Return conditional power estimate
    raise NotImplementedError("Conditional power not yet implemented")


def run_sequential_analysis(
    control_values: np.ndarray,
    treatment_values: np.ndarray,
    planned_n_per_group: int,
    tau_squared: Optional[float] = None,
    spending_function: SpendingFunction = SpendingFunction.OBRIEN_FLEMING,
    alpha: float = 0.05,
    futility_threshold: float = 0.10,
    metric_name: str = "metric",
) -> SequentialResult:
    """Run sequential analysis at the current data snapshot.

    Computes mSPRT statistic, always-valid CI, spending-function boundary,
    and futility assessment.

    Args:
        control_values: Current array of control group metric values.
        treatment_values: Current array of treatment group metric values.
        planned_n_per_group: Planned total sample size per group.
        tau_squared: Mixing variance for mSPRT. If None, auto-computed from
            planned MDE. Default None.
        spending_function: Alpha-spending function to use. Default O'Brien-Fleming.
        alpha: Overall significance level. Default 0.05.
        futility_threshold: Conditional power threshold below which to flag
            futility. Default 0.10.
        metric_name: Name of the metric. Default "metric".

    Returns:
        SequentialResult with all monitoring statistics.
    """
    # TODO: Compute current sample sizes and information fraction
    # TODO: Compute running mean difference and pooled variance
    # TODO: Auto-compute tau_squared if not provided
    # TODO: Compute mSPRT statistic
    # TODO: Compute always-valid CI
    # TODO: Compute spending-function boundary
    # TODO: Determine if null can be rejected (mSPRT >= 1/alpha or Z > boundary)
    # TODO: Compute conditional power and futility flag
    # TODO: Assemble and return SequentialResult
    raise NotImplementedError("Sequential analysis not yet implemented")
