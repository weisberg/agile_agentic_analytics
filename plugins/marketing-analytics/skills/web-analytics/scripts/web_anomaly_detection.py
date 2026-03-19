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
from dataclasses import asdict, dataclass, field
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
    if date_column not in df.columns:
        raise ValueError(f"Date column '{date_column}' not found in DataFrame")
    if metric_column not in df.columns:
        raise ValueError(f"Metric column '{metric_column}' not found in DataFrame")

    # Ensure the metric column is numeric.
    if not pd.api.types.is_numeric_dtype(df[metric_column]):
        raise ValueError(
            f"Metric column '{metric_column}' must be numeric, "
            f"got {df[metric_column].dtype}"
        )

    # Check for all-null metric.
    if df[metric_column].isna().all():
        raise ValueError(f"Metric column '{metric_column}' contains only null values")

    # Parse dates and check history length.
    dates = pd.to_datetime(df[date_column])
    unique_dates = dates.dropna().dt.normalize().unique()
    n_days = len(unique_dates)

    if n_days < min_history_days:
        raise ValueError(
            f"Insufficient history: {n_days} days available, "
            f"{min_history_days} required"
        )

    # Check for large date gaps (more than 3 consecutive missing days).
    sorted_dates = pd.DatetimeIndex(sorted(unique_dates))
    gaps = sorted_dates[1:] - sorted_dates[:-1]
    max_gap = gaps.max() if len(gaps) > 0 else pd.Timedelta(0)
    if max_gap > pd.Timedelta(days=3):
        raise ValueError(
            f"Large date gap detected: {max_gap.days} consecutive days missing"
        )

    return True


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
    from statsmodels.tsa.seasonal import STL

    # Fill any internal missing values via linear interpolation for STL.
    filled = series.copy()
    if filled.isna().any():
        filled = filled.interpolate(method="linear").ffill().bfill()

    stl = STL(filled, period=period, robust=True)
    result = stl.fit()

    return result.trend, result.seasonal, result.resid


def compute_z_scores(residuals: pd.Series) -> pd.Series:
    """Compute Z-scores for residual values.

    Uses robust statistics (median and MAD) rather than mean and std to
    reduce sensitivity to outliers in the baseline.

    Args:
        residuals: Residual component from STL decomposition.

    Returns:
        Series of Z-scores aligned with the input index.
    """
    median = residuals.median()
    mad = np.median(np.abs(residuals - median))

    # Scale MAD to be consistent with standard deviation for normal data.
    # MAD * 1.4826 ≈ std for a normal distribution.
    scaled_mad = mad * 1.4826

    if scaled_mad == 0:
        # If MAD is zero (constant residuals), fall back to mean/std.
        std = residuals.std()
        if std == 0:
            return pd.Series(0.0, index=residuals.index)
        return (residuals - residuals.mean()) / std

    return (residuals - median) / scaled_mad


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
    validate_time_series(df, date_column, metric_column, config.min_history_days)

    # Build daily aggregated series.
    ts_df = df[[date_column, metric_column]].copy()
    ts_df[date_column] = pd.to_datetime(ts_df[date_column])
    daily = (
        ts_df.groupby(date_column)[metric_column]
        .sum()
        .sort_index()
    )
    daily.index = pd.DatetimeIndex(daily.index)

    # Fill any missing dates in the range with zero to get a continuous series.
    full_range = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    daily = daily.reindex(full_range, fill_value=0)

    trend, seasonal, residual = run_stl_decomposition(daily, config.seasonal_period)
    z_scores = compute_z_scores(residual)

    expected = trend + seasonal

    anomalies: list[Anomaly] = []
    for dt, z in z_scores.items():
        if abs(z) < config.z_score_threshold:
            continue

        anomaly_dt = dt.date() if hasattr(dt, "date") else dt

        # Suppress known events.
        if anomaly_dt in config.suppression_dates:
            continue

        observed = float(daily.loc[dt])
        exp_val = float(expected.loc[dt])
        direction = "above" if z > 0 else "below"

        anomalies.append(
            Anomaly(
                metric_name=metric_column,
                anomaly_date=anomaly_dt,
                observed_value=observed,
                expected_value=exp_val,
                z_score=float(z),
                direction=direction,
            )
        )

    # Sort by absolute Z-score descending.
    anomalies.sort(key=lambda a: abs(a.z_score), reverse=True)
    return anomalies


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
    result: dict[str, list[dict[str, Any]]] = {}

    # Identify the date column (first column that parses as dates).
    date_col: str | None = None
    for col in df.columns:
        if col.lower() in ("date", "event_date", "report_date"):
            date_col = col
            break
    if date_col is None:
        # Fallback: try to find a datetime-ish column.
        for col in df.columns:
            try:
                pd.to_datetime(df[col].head(5))
                date_col = col
                break
            except Exception:
                continue
    if date_col is None:
        return result

    df_copy = df.copy()
    df_copy["_parsed_date"] = pd.to_datetime(df_copy[date_col]).dt.date

    # Data on the anomaly date.
    anomaly_data = df_copy[df_copy["_parsed_date"] == anomaly_date]

    # Baseline: data from 4 comparable day-of-week periods prior.
    anomaly_weekday = anomaly_date.weekday()
    baseline_mask = (
        (df_copy["_parsed_date"] < anomaly_date)
        & (df_copy["_parsed_date"].apply(lambda d: d.weekday()) == anomaly_weekday)
    )
    baseline_data = df_copy[baseline_mask]

    # Count how many baseline days we have.
    baseline_dates = baseline_data["_parsed_date"].unique()
    n_baseline_days = len(baseline_dates)
    if n_baseline_days == 0:
        return result

    for dim in dimensions:
        if dim not in df.columns:
            continue

        # Observed values on anomaly date, grouped by dimension value.
        observed = anomaly_data.groupby(dim)[metric_column].sum()

        # Expected values: average across baseline same-weekday dates.
        baseline_grouped = baseline_data.groupby(dim)[metric_column].sum()
        expected = baseline_grouped / n_baseline_days

        # Align on the union of dimension values.
        all_values = set(observed.index) | set(expected.index)
        contributions: list[dict[str, Any]] = []
        total_deviation = 0.0

        for val in all_values:
            obs = float(observed.get(val, 0.0))
            exp = float(expected.get(val, 0.0))
            contrib = obs - exp
            total_deviation += contrib
            contributions.append(
                {"value": str(val), "contribution": contrib, "pct_contribution": 0.0}
            )

        # Compute percentage contributions.
        abs_total = abs(total_deviation) if total_deviation != 0 else 1.0
        for entry in contributions:
            entry["pct_contribution"] = round(
                (entry["contribution"] / abs_total) * 100.0
                if abs_total != 0
                else 0.0,
                2,
            )

        # Sort by absolute contribution descending.
        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        result[dim] = contributions

    return result


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
    if config is None:
        config = AnomalyConfig()

    # Load data.
    suffix = input_path.suffix.lower()
    if suffix == ".json":
        df = pd.read_json(input_path)
    else:
        df = pd.read_csv(input_path)

    # Detect the date column.
    date_column = "date"
    for candidate in ("date", "event_date", "report_date"):
        if candidate in df.columns:
            date_column = candidate
            break

    all_anomalies: list[Anomaly] = []

    for metric in metrics:
        if metric not in df.columns:
            continue

        try:
            anomalies = detect_anomalies(df, date_column, metric, config)
        except ValueError:
            # Insufficient data or validation failure for this metric — skip.
            continue

        # Decompose root causes for each anomaly.
        available_dims = [
            d for d in config.decomposition_dimensions if d in df.columns
        ]
        for anomaly in anomalies:
            if available_dims:
                anomaly.root_causes = decompose_root_causes(
                    df, anomaly.anomaly_date, metric, available_dims
                )

        all_anomalies.extend(anomalies)

    # Serialize to JSON.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = []
    for a in all_anomalies:
        d = asdict(a)
        d["anomaly_date"] = a.anomaly_date.isoformat()
        serializable.append(d)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, default=str)

    return all_anomalies


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
