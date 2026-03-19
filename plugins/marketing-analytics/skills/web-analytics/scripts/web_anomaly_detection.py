"""Seasonal decomposition and Z-score anomaly detection on web metrics.

Applies STL (Seasonal and Trend decomposition using Loess) to daily web
traffic and conversion time series, then flags residuals that exceed a
configurable Z-score threshold. Supports root cause decomposition by
breaking anomalies down across source, device, geography, and page
dimensions.

Dependencies:
    - pandas
    - numpy
    - statsmodels (for STL decomposition)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class AnomalyConfig:
    """Configuration for web anomaly detection.

    Attributes:
        z_score_threshold: Number of standard deviations beyond which a
            residual is flagged as anomalous. Default 3.0.
        seasonal_period: Period length in days for STL decomposition.
            Default 7 (weekly seasonality).
        min_history_days: Minimum number of days of history required for
            stable seasonal baselines. Default 56 (8 weeks).
        suppression_dates: Set of dates to suppress (holidays, launches).
        decomposition_dimensions: Dimensions to break down when explaining
            an anomaly (e.g., ["source", "device", "country", "page"]).
    """

    z_score_threshold: float = 3.0
    seasonal_period: int = 7
    min_history_days: int = 56
    suppression_dates: set[date] = field(default_factory=set)
    decomposition_dimensions: list[str] = field(
        default_factory=lambda: ["source", "device", "country", "page"]
    )


@dataclass
class Anomaly:
    """A detected anomaly in a web metric time series.

    Attributes:
        metric_name: Name of the metric (e.g., "sessions", "conversion_rate").
        anomaly_date: Date the anomaly was detected.
        observed_value: Actual observed value on the anomaly date.
        expected_value: Expected value based on trend + seasonal components.
        z_score: Z-score of the residual.
        direction: "above" or "below" expected.
        root_causes: Dict mapping dimension names to their contribution
            breakdown (list of dicts with "value" and "contribution" keys).
    """

    metric_name: str
    anomaly_date: date
    observed_value: float
    expected_value: float
    z_score: float
    direction: str
    root_causes: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


def validate_time_series(
    df: pd.DataFrame,
    date_column: str,
    metric_column: str,
    min_history_days: int,
) -> bool:
    """Validate that the time series has sufficient history for decomposition.

    Args:
        df: DataFrame containing the time series data.
        date_column: Name of the date column.
        metric_column: Name of the metric column to validate.
        min_history_days: Minimum required days of data.

    Returns:
        True if the time series is valid for analysis.

    Raises:
        ValueError: If the time series has insufficient history, missing
            dates, or non-numeric metric values.
    """
    # TODO: Check that df has at least min_history_days rows, no large
    # date gaps, and that metric_column is numeric and non-null.
    raise NotImplementedError("validate_time_series not yet implemented")


def run_stl_decomposition(
    series: pd.Series,
    period: int,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Apply STL decomposition to a time series.

    Uses statsmodels STL with robust fitting to handle outliers during
    decomposition.

    Args:
        series: Daily metric values indexed by date.
        period: Seasonal period in days (typically 7).

    Returns:
        Tuple of (trend, seasonal, residual) Series.
    """
    # TODO: Use statsmodels.tsa.seasonal.STL with robust=True.
    # Return the three decomposition components.
    raise NotImplementedError("run_stl_decomposition not yet implemented")


def compute_z_scores(residuals: pd.Series) -> pd.Series:
    """Compute Z-scores for residual values.

    Uses robust statistics (median and MAD) rather than mean and std to
    reduce sensitivity to outliers in the baseline.

    Args:
        residuals: Residual component from STL decomposition.

    Returns:
        Series of Z-scores aligned with the input index.
    """
    # TODO: Compute median and MAD of residuals, then Z = (r - median) / MAD.
    # Handle MAD = 0 edge case.
    raise NotImplementedError("compute_z_scores not yet implemented")


def detect_anomalies(
    df: pd.DataFrame,
    date_column: str,
    metric_column: str,
    config: AnomalyConfig,
) -> list[Anomaly]:
    """Detect anomalies in a single metric time series.

    Applies STL decomposition, computes Z-scores on residuals, and flags
    dates where the absolute Z-score exceeds the configured threshold.
    Suppresses dates in the suppression calendar.

    Args:
        df: DataFrame containing the time series.
        date_column: Name of the date column.
        metric_column: Name of the metric column to analyze.
        config: Anomaly detection configuration.

    Returns:
        List of Anomaly objects for flagged dates, sorted by absolute
        Z-score descending.
    """
    # TODO: Validate time series, run STL decomposition, compute Z-scores,
    # filter by threshold, exclude suppression dates, build Anomaly objects.
    raise NotImplementedError("detect_anomalies not yet implemented")


def decompose_root_causes(
    df: pd.DataFrame,
    anomaly_date: date,
    metric_column: str,
    dimensions: list[str],
) -> dict[str, list[dict[str, Any]]]:
    """Break down an anomaly into dimensional contributions.

    For each dimension, computes the contribution of each dimension value
    to the overall anomaly by comparing observed vs. expected at the
    dimension-value level.

    Args:
        df: Full-granularity DataFrame with dimension columns.
        anomaly_date: The date of the anomaly.
        metric_column: The metric exhibiting the anomaly.
        dimensions: List of dimension column names to decompose across.

    Returns:
        Dict mapping dimension name to a list of dicts, each with:
        - "value": the dimension value (e.g., "google", "mobile")
        - "contribution": signed contribution to the anomaly
        - "pct_contribution": percentage of total anomaly explained
    """
    # TODO: For each dimension, group by dimension value, compute
    # observed - expected for the anomaly date, rank by contribution.
    raise NotImplementedError("decompose_root_causes not yet implemented")


def run_anomaly_detection(
    input_path: Path,
    output_path: Path,
    metrics: list[str],
    config: AnomalyConfig | None = None,
) -> list[Anomaly]:
    """Run full anomaly detection pipeline and write results.

    Args:
        input_path: Path to the web metrics CSV/JSON file.
        output_path: Path to write the anomalies JSON output.
        metrics: List of metric column names to analyze.
        config: Optional anomaly detection config (uses defaults if None).

    Returns:
        Flat list of all detected Anomaly objects across all metrics.
    """
    # TODO: Load data, iterate over metrics, detect anomalies, decompose
    # root causes, serialize to JSON, write to output_path.
    raise NotImplementedError("run_anomaly_detection not yet implemented")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Web metric anomaly detection")
    parser.add_argument("--input", default="workspace/processed/web_metrics.csv")
    parser.add_argument("--output", default="workspace/analysis/web_anomalies.json")
    parser.add_argument("--metrics", nargs="+", default=["sessions", "conversions", "conversion_rate"])
    parser.add_argument("--z-threshold", type=float, default=3.0)
    parser.add_argument("--min-history", type=int, default=56)

    args = parser.parse_args()

    anomaly_config = AnomalyConfig(
        z_score_threshold=args.z_threshold,
        min_history_days=args.min_history,
    )

    anomalies = run_anomaly_detection(
        input_path=Path(args.input),
        output_path=Path(args.output),
        metrics=args.metrics,
        config=anomaly_config,
    )
    print(f"Detected {len(anomalies)} anomalies")
