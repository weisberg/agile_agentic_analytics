"""Revenue impact projection per funnel stage improvement.

This module estimates the revenue gain from improving conversion rates at each
funnel stage. It uses historical revenue-per-converter data and conservative
projection methodology (50th percentile of improvement range).

Typical usage:
    from funnel_stats import FunnelStats, BottleneckScore
    impacts = estimate_revenue_impact(funnel_stats, bottlenecks, revenue_data)
    save_revenue_impact(impacts, "workspace/analysis/revenue_impact.json")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class ImprovementScenario:
    """Projected revenue impact for a specific improvement at one stage.

    Attributes:
        improvement_ppts: The assumed conversion rate improvement in percentage
            points (e.g., 1.0 means +1pp).
        additional_converters: Estimated additional users who would convert.
        additional_revenue: Estimated additional revenue in currency units.
        additional_revenue_pct: Additional revenue as a percentage of current
            total funnel revenue.
    """

    improvement_ppts: float
    additional_converters: int
    additional_revenue: float
    additional_revenue_pct: float


@dataclass
class StageRevenueImpact:
    """Revenue impact analysis for a single funnel stage.

    Attributes:
        stage_index: Zero-based index of this stage.
        stage_name: Human-readable stage name.
        current_conversion_rate: Current conversion rate at this stage.
        current_volume: Number of users entering this stage.
        revenue_per_converter: Historical average (or median) revenue per user
            who completes the entire funnel from this stage onward.
        scenarios: List of improvement scenarios (e.g., +1pp, +5pp, +10pp).
        bottleneck_rank: Rank from bottleneck scoring (None if not ranked).
    """

    stage_index: int
    stage_name: str
    current_conversion_rate: float
    current_volume: int
    revenue_per_converter: float
    scenarios: list[ImprovementScenario]
    bottleneck_rank: Optional[int] = None


@dataclass
class RevenueImpactReport:
    """Complete revenue impact analysis across all funnel stages.

    Attributes:
        funnel_name: Name of the analyzed funnel.
        total_current_revenue: Total revenue from current funnel converters.
        currency: Currency code (e.g., "USD").
        stages: Per-stage revenue impact analyses.
        analysis_period: Description of the time period analyzed.
        methodology_note: Explanation of the estimation approach.
    """

    funnel_name: str
    total_current_revenue: float
    currency: str
    stages: list[StageRevenueImpact]
    analysis_period: str
    methodology_note: str = (
        "Revenue projections use the 50th percentile (median) of historical "
        "revenue-per-converter and assume linear impact of conversion rate "
        "improvement. Actual results may vary based on user mix and "
        "seasonality. These are conservative estimates."
    )


def load_revenue_data(
    filepath: str | Path,
    user_id_column: str = "user_id",
    revenue_column: str = "revenue",
    timestamp_column: str = "timestamp",
) -> pd.DataFrame:
    """Load revenue-per-converter data from CSV.

    Reads the revenue data file and validates required columns. Each row
    represents a revenue event (e.g., purchase) tied to a user.

    Args:
        filepath: Path to the revenue CSV file.
        user_id_column: Name of the user identifier column.
        revenue_column: Name of the revenue amount column.
        timestamp_column: Name of the timestamp column.

    Returns:
        A DataFrame with validated revenue data.

    Raises:
        FileNotFoundError: If the revenue file does not exist.
        ValueError: If required columns are missing or revenue contains
            non-numeric values.
    """
    # TODO: Implement revenue data loading and validation
    raise NotImplementedError("load_revenue_data not yet implemented")


def compute_revenue_per_converter(
    revenue_data: pd.DataFrame,
    funnel_result: "FunnelResult",
    user_id_column: str = "user_id",
    revenue_column: str = "revenue",
    use_median: bool = True,
) -> float:
    """Compute revenue per user who completed the funnel.

    Matches revenue data to funnel completers and calculates the central
    tendency of revenue per converter. Uses median by default for robustness
    to outliers.

    Args:
        revenue_data: DataFrame with user-level revenue data.
        funnel_result: The FunnelResult identifying which users completed.
        user_id_column: Name of the user identifier column.
        revenue_column: Name of the revenue amount column.
        use_median: If True, use median (50th percentile). If False, use mean.
            Default True for conservative estimation.

    Returns:
        Revenue per converter (median or mean).

    Raises:
        ValueError: If no funnel completers have matching revenue data.
    """
    # TODO: Implement:
    #   1. Get user IDs who completed funnel
    #   2. Join with revenue data
    #   3. Compute median or mean revenue
    raise NotImplementedError("compute_revenue_per_converter not yet implemented")


def compute_stage_revenue_per_converter(
    revenue_data: pd.DataFrame,
    funnel_result: "FunnelResult",
    stage_index: int,
    user_id_column: str = "user_id",
    revenue_column: str = "revenue",
    use_median: bool = True,
) -> float:
    """Compute revenue per user who converted at a specific stage and beyond.

    For stages closer to the end of the funnel, the revenue per additional
    converter may differ from the overall funnel average. This function
    computes stage-specific revenue estimates.

    Args:
        revenue_data: DataFrame with user-level revenue data.
        funnel_result: The FunnelResult with per-user stage assignments.
        stage_index: The stage to compute revenue for.
        user_id_column: Name of the user identifier column.
        revenue_column: Name of the revenue amount column.
        use_median: If True, use median. If False, use mean.

    Returns:
        Revenue per converter from this stage onward.
    """
    # TODO: Implement stage-specific revenue per converter
    raise NotImplementedError(
        "compute_stage_revenue_per_converter not yet implemented"
    )


def project_improvement_scenario(
    current_volume: int,
    current_conversion_rate: float,
    improvement_ppts: float,
    revenue_per_converter: float,
    total_current_revenue: float,
    downstream_conversion_rate: float = 1.0,
) -> ImprovementScenario:
    """Project revenue impact for a given conversion rate improvement.

    Calculates the additional converters and revenue from improving the
    conversion rate at a specific stage by a given number of percentage points.

    The downstream_conversion_rate accounts for the fact that not all users
    who pass this stage will ultimately convert (purchase). It represents the
    probability of reaching final conversion from this stage onward.

    Args:
        current_volume: Number of users entering the stage.
        current_conversion_rate: Current conversion rate at this stage (0 to 1).
        improvement_ppts: Percentage point improvement (e.g., 5.0 for +5pp).
        revenue_per_converter: Revenue per final converter.
        total_current_revenue: Total current funnel revenue for percentage calc.
        downstream_conversion_rate: Probability of reaching final conversion
            from the improved stage onward (default 1.0, i.e., assume all
            additional passers convert).

    Returns:
        An ImprovementScenario with projected additional converters and revenue.
    """
    # TODO: Implement:
    #   new_rate = min(1.0, current_conversion_rate + improvement_ppts / 100)
    #   additional_passers = current_volume * (new_rate - current_conversion_rate)
    #   additional_converters = additional_passers * downstream_conversion_rate
    #   additional_revenue = additional_converters * revenue_per_converter
    #   additional_revenue_pct = additional_revenue / total_current_revenue * 100
    raise NotImplementedError(
        "project_improvement_scenario not yet implemented"
    )


def estimate_revenue_impact(
    funnel_stats: "FunnelStats",
    bottlenecks: list["BottleneckScore"],
    revenue_data: pd.DataFrame,
    funnel_result: "FunnelResult",
    improvement_scenarios_ppts: list[float] | None = None,
    currency: str = "USD",
    analysis_period: str = "Last 30 days",
    user_id_column: str = "user_id",
    revenue_column: str = "revenue",
) -> RevenueImpactReport:
    """Estimate revenue impact of improving conversion at each funnel stage.

    For each stage, projects the revenue gain from 1, 5, and 10 percentage-
    point improvements (or custom scenarios). Uses conservative (median)
    revenue-per-converter estimates.

    Args:
        funnel_stats: Statistical summary of the funnel from funnel_stats.py.
        bottlenecks: Ranked bottleneck list from funnel_stats.py.
        revenue_data: DataFrame with user-level revenue data.
        funnel_result: The FunnelResult with per-user funnel assignments.
        improvement_scenarios_ppts: List of improvement scenarios in percentage
            points. Default [1.0, 5.0, 10.0].
        currency: Currency code for revenue figures (default "USD").
        analysis_period: Human-readable description of the analysis period.
        user_id_column: Name of the user identifier column.
        revenue_column: Name of the revenue amount column.

    Returns:
        A RevenueImpactReport with per-stage impact projections.
    """
    # TODO: Implement:
    #   1. Compute total current revenue from funnel completers
    #   2. For each stage, compute revenue_per_converter
    #   3. For each stage x scenario, call project_improvement_scenario
    #   4. Attach bottleneck rank to each stage
    #   5. Assemble RevenueImpactReport
    raise NotImplementedError("estimate_revenue_impact not yet implemented")


def save_revenue_impact(
    report: RevenueImpactReport,
    filepath: str | Path,
) -> None:
    """Save revenue impact report to a JSON file.

    Serializes the RevenueImpactReport into the output contract format.

    Args:
        report: The revenue impact report to save.
        filepath: Output path for the JSON file.
    """
    # TODO: Implement JSON serialization of RevenueImpactReport
    raise NotImplementedError("save_revenue_impact not yet implemented")


if __name__ == "__main__":
    import sys

    funnel_results_path = (
        sys.argv[1] if len(sys.argv) > 1
        else "workspace/analysis/funnel_results.json"
    )
    bottleneck_path = (
        sys.argv[2] if len(sys.argv) > 2
        else "workspace/analysis/bottleneck_ranking.json"
    )
    revenue_data_path = (
        sys.argv[3] if len(sys.argv) > 3
        else "workspace/raw/revenue.csv"
    )
    output_path = (
        sys.argv[4] if len(sys.argv) > 4
        else "workspace/analysis/revenue_impact.json"
    )

    # TODO: Load inputs, compute revenue impact, save results
    print("revenue_impact.py: Load funnel + revenue data, project impact per stage")
    raise NotImplementedError("CLI entrypoint not yet implemented")
