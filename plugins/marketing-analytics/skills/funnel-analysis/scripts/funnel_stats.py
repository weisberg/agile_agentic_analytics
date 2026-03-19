"""Statistical analysis for funnel conversion data.

This module computes conversion rates with Wilson score confidence intervals,
performs chi-squared tests for cohort comparison, and calculates composite
bottleneck scores for prioritizing optimization efforts.

Typical usage:
    from build_funnel import FunnelResult
    stats = compute_funnel_stats(funnel_result, confidence_level=0.95)
    bottlenecks = rank_bottlenecks(stats)
    save_bottleneck_ranking(bottlenecks, "workspace/analysis/bottleneck_ranking.json")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class WilsonInterval:
    """Wilson score confidence interval for a proportion.

    Attributes:
        point_estimate: The observed proportion (k / n).
        lower: Lower bound of the confidence interval.
        upper: Upper bound of the confidence interval.
        confidence_level: The nominal confidence level (e.g., 0.95).
        n: Total number of trials.
        k: Number of successes.
    """

    point_estimate: float
    lower: float
    upper: float
    confidence_level: float
    n: int
    k: int


@dataclass
class StageStats:
    """Statistical summary for a single funnel stage.

    Attributes:
        stage_index: Zero-based index of this stage.
        stage_name: Human-readable stage name.
        entered: Number of users/sessions entering this stage.
        converted: Number proceeding to the next stage.
        dropped: Number who did not proceed.
        conversion_rate: Wilson interval for the conversion rate.
        drop_off_rate: Wilson interval for the drop-off rate.
        median_time_to_next: Median time in seconds to reach the next stage.
            None for the final stage.
        time_to_next_percentiles: Dict of percentile -> seconds for time to
            next stage (e.g., {25: 120, 50: 300, 75: 900}).
    """

    stage_index: int
    stage_name: str
    entered: int
    converted: int
    dropped: int
    conversion_rate: WilsonInterval
    drop_off_rate: WilsonInterval
    median_time_to_next: Optional[float] = None
    time_to_next_percentiles: dict[int, float] = field(default_factory=dict)


@dataclass
class FunnelStats:
    """Complete statistical summary for a funnel.

    Attributes:
        funnel_name: Name of the analyzed funnel.
        stages: Per-stage statistical summaries.
        overall_conversion: Wilson interval for end-to-end conversion.
        total_entered: Total users/sessions entering stage 0.
        total_completed: Total completing the final stage.
    """

    funnel_name: str
    stages: list[StageStats]
    overall_conversion: WilsonInterval
    total_entered: int
    total_completed: int


@dataclass
class BottleneckScore:
    """Bottleneck ranking entry for a single funnel stage.

    Attributes:
        stage_index: Zero-based index of this stage.
        stage_name: Human-readable stage name.
        drop_off_rate: Observed drop-off rate.
        volume: Number of users entering this stage.
        revenue_proximity: Weight reflecting closeness to final conversion.
        composite_score: The computed bottleneck score:
            drop_off_rate * sqrt(volume) * revenue_proximity.
        rank: Priority rank (1 = highest-priority bottleneck).
    """

    stage_index: int
    stage_name: str
    drop_off_rate: float
    volume: int
    revenue_proximity: float
    composite_score: float
    rank: int


@dataclass
class CohortComparison:
    """Result of comparing funnel performance between two cohorts.

    Attributes:
        stage_index: The funnel stage being compared.
        stage_name: Human-readable stage name.
        cohort_a_name: Name of the first cohort.
        cohort_b_name: Name of the second cohort.
        cohort_a_rate: Conversion rate for cohort A.
        cohort_b_rate: Conversion rate for cohort B.
        chi_squared_statistic: Chi-squared test statistic.
        p_value: P-value from the chi-squared test.
        significant: Whether the difference is statistically significant.
        relative_difference: (rate_b - rate_a) / rate_a as a fraction.
    """

    stage_index: int
    stage_name: str
    cohort_a_name: str
    cohort_b_name: str
    cohort_a_rate: float
    cohort_b_rate: float
    chi_squared_statistic: float
    p_value: float
    significant: bool
    relative_difference: float


def wilson_score_interval(
    k: int,
    n: int,
    confidence_level: float = 0.95,
) -> WilsonInterval:
    """Compute Wilson score confidence interval for a proportion.

    More accurate than the normal (Wald) approximation, especially for
    proportions near 0 or 1. Guaranteed to stay within [0, 1].

    Args:
        k: Number of successes (conversions).
        n: Total number of trials (users entering stage).
        confidence_level: Nominal confidence level (default 0.95).

    Returns:
        A WilsonInterval with point estimate, lower bound, and upper bound.

    Raises:
        ValueError: If k > n or n <= 0 or k < 0.
    """
    # TODO: Implement Wilson score interval formula:
    #   z = norm.ppf(1 - (1 - confidence_level) / 2)
    #   p_hat = k / n
    #   center = (p_hat + z**2 / (2*n)) / (1 + z**2 / n)
    #   margin = z / (1 + z**2 / n) * sqrt(p_hat*(1-p_hat)/n + z**2/(4*n**2))
    #   lower = max(0, center - margin)
    #   upper = min(1, center + margin)
    raise NotImplementedError("wilson_score_interval not yet implemented")


def compute_funnel_stats(
    funnel_result: "FunnelResult",
    confidence_level: float = 0.95,
) -> FunnelStats:
    """Compute statistical summaries for all funnel stages.

    Calculates Wilson score confidence intervals for conversion and drop-off
    rates at each stage, plus the overall end-to-end conversion rate.

    Args:
        funnel_result: A FunnelResult from build_funnel.py containing stage
            counts and per-user results.
        confidence_level: Nominal confidence level for intervals (default 0.95).

    Returns:
        A FunnelStats with per-stage and overall statistical summaries.
    """
    # TODO: Implement:
    #   1. For each stage, compute Wilson CI for conversion and drop-off
    #   2. Compute time-to-next-stage distributions from user_results
    #   3. Compute overall conversion Wilson CI
    raise NotImplementedError("compute_funnel_stats not yet implemented")


def compute_time_to_convert(
    funnel_result: "FunnelResult",
    percentiles: list[int] | None = None,
    handle_censored: bool = True,
) -> list[dict[str, float | None]]:
    """Compute time-to-convert distributions between consecutive stages.

    Analyzes the time elapsed between consecutive funnel steps for each user.
    Handles right-censored data (users still in funnel at analysis time) using
    Kaplan-Meier estimation when enabled.

    Args:
        funnel_result: A FunnelResult with per-user stage timestamps.
        percentiles: List of percentiles to compute (default [25, 50, 75, 90]).
        handle_censored: Whether to apply Kaplan-Meier for censored
            observations (default True).

    Returns:
        A list of dicts, one per stage transition, each containing:
            - "from_stage": stage index
            - "to_stage": next stage index
            - "median_seconds": median time in seconds
            - "percentiles": dict of percentile -> seconds
            - "n_observed": count of users who completed transition
            - "n_censored": count of users censored at this transition
    """
    # TODO: Implement time-to-convert with optional censoring
    raise NotImplementedError("compute_time_to_convert not yet implemented")


def chi_squared_comparison(
    stage_name: str,
    stage_index: int,
    cohort_a_name: str,
    cohort_a_converted: int,
    cohort_a_total: int,
    cohort_b_name: str,
    cohort_b_converted: int,
    cohort_b_total: int,
    alpha: float = 0.05,
) -> CohortComparison:
    """Compare conversion rates between two cohorts using chi-squared test.

    Constructs a 2x2 contingency table and performs a chi-squared test of
    independence. Applies Yates continuity correction when any expected cell
    count is below 5.

    Args:
        stage_name: Human-readable name of the stage being compared.
        stage_index: Zero-based index of the stage.
        cohort_a_name: Label for the first cohort.
        cohort_a_converted: Conversions in cohort A.
        cohort_a_total: Total users in cohort A at this stage.
        cohort_b_name: Label for the second cohort.
        cohort_b_converted: Conversions in cohort B.
        cohort_b_total: Total users in cohort B at this stage.
        alpha: Significance threshold (default 0.05).

    Returns:
        A CohortComparison with test statistic, p-value, and significance flag.

    Raises:
        ValueError: If any count is negative or converted > total.
    """
    # TODO: Implement chi-squared test using scipy.stats.chi2_contingency
    #   with Yates correction for small expected counts
    raise NotImplementedError("chi_squared_comparison not yet implemented")


def compare_cohort_funnels(
    cohort_funnels: dict[str, "FunnelResult"],
    alpha: float = 0.05,
    correction: str = "bonferroni",
) -> list[CohortComparison]:
    """Compare funnel performance across multiple cohorts at each stage.

    Performs pairwise chi-squared comparisons between all cohort pairs at each
    funnel stage. Applies multiple-comparison correction.

    Args:
        cohort_funnels: Mapping of cohort name to FunnelResult.
        alpha: Family-wise significance threshold (default 0.05).
        correction: Multiple comparison correction method. One of
            "bonferroni" or "none" (default "bonferroni").

    Returns:
        A list of CohortComparison results for all pairwise stage comparisons.
    """
    # TODO: Implement pairwise comparison with Bonferroni correction:
    #   adjusted_alpha = alpha / num_comparisons
    raise NotImplementedError("compare_cohort_funnels not yet implemented")


def rank_bottlenecks(
    funnel_stats: FunnelStats,
    total_stages: Optional[int] = None,
    weight_dropoff: float = 1.0,
    weight_volume_exp: float = 0.5,
    weight_proximity: float = 1.0,
) -> list[BottleneckScore]:
    """Rank funnel stages by bottleneck severity.

    Computes a composite bottleneck score for each stage using the formula:
        score = drop_off_rate^weight_dropoff * volume^weight_volume_exp
                * revenue_proximity^weight_proximity

    Default formula: drop_off_rate * sqrt(volume) * revenue_proximity
    where revenue_proximity = 1 / (total_stages - stage_index).

    Args:
        funnel_stats: Statistical summary of the funnel.
        total_stages: Total number of stages. Defaults to len(funnel_stats.stages).
        weight_dropoff: Exponent for drop-off rate (default 1.0).
        weight_volume_exp: Exponent for volume (default 0.5 for sqrt).
        weight_proximity: Exponent for revenue proximity (default 1.0).

    Returns:
        A list of BottleneckScore entries sorted by composite score descending,
        with rank 1 being the highest-priority bottleneck.
    """
    # TODO: Implement bottleneck scoring:
    #   1. Compute revenue_proximity = 1 / (total_stages - stage_index)
    #   2. Compute composite score with configurable exponents
    #   3. Sort descending and assign ranks
    raise NotImplementedError("rank_bottlenecks not yet implemented")


def save_bottleneck_ranking(
    bottlenecks: list[BottleneckScore],
    filepath: str | Path,
) -> None:
    """Save bottleneck ranking to a JSON file.

    Serializes the ranked bottleneck list in the output contract format.

    Args:
        bottlenecks: Ranked list of BottleneckScore entries.
        filepath: Output path for the JSON file.
    """
    # TODO: Implement JSON serialization of bottleneck ranking
    raise NotImplementedError("save_bottleneck_ranking not yet implemented")


def save_funnel_stats(
    funnel_stats: FunnelStats,
    filepath: str | Path,
) -> None:
    """Save funnel statistics to a JSON file.

    Serializes the complete funnel statistical summary in the output contract
    format expected by downstream skills.

    Args:
        funnel_stats: The complete statistical summary.
        filepath: Output path for the JSON file.
    """
    # TODO: Implement JSON serialization of FunnelStats
    raise NotImplementedError("save_funnel_stats not yet implemented")


if __name__ == "__main__":
    import sys

    funnel_results_path = (
        sys.argv[1] if len(sys.argv) > 1
        else "workspace/analysis/funnel_results.json"
    )
    bottleneck_output_path = (
        sys.argv[2] if len(sys.argv) > 2
        else "workspace/analysis/bottleneck_ranking.json"
    )

    # TODO: Load FunnelResult from JSON, compute stats, rank bottlenecks, save
    print("funnel_stats.py: Load funnel results, compute stats, rank bottlenecks")
    raise NotImplementedError("CLI entrypoint not yet implemented")
