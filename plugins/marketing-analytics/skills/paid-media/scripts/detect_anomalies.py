"""Anomaly detection for paid media metrics.

Implements rolling Z-score, isolation forest, and seasonal decomposition (STL)
methods for detecting anomalies in spend, CPA, CTR, and conversion rate. Combines
signals from multiple methods into a severity-ranked alert list with root-cause
drill-down.

See references/anomaly_detection.md for full methodology documentation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_ZSCORE_WINDOW: int = 28
DEFAULT_ZSCORE_THRESHOLD: float = 2.5
DEFAULT_MIN_OBSERVATIONS: int = 14

DEFAULT_ISO_N_ESTIMATORS: int = 100
DEFAULT_ISO_CONTAMINATION: float = 0.05
DEFAULT_ISO_MAX_SAMPLES: int = 256

DEFAULT_STL_PERIOD: int = 7
DEFAULT_STL_SEASONAL_WINDOW: int = 13
DEFAULT_STL_TREND_WINDOW: int = 21
DEFAULT_STL_IQR_MULTIPLIER: float = 3.0

METRICS_TO_MONITOR: list[str] = ["spend", "cpa", "ctr", "conversion_rate"]


@dataclass
class AnomalyAlert:
    """Represents a single detected anomaly."""

    date: str
    platform: str
    campaign_id: str
    metric: str
    observed_value: float
    expected_value: float
    z_score: Optional[float] = None
    isolation_score: Optional[float] = None
    stl_residual: Optional[float] = None
    severity: str = "medium"
    root_cause: str = ""


# ---------------------------------------------------------------------------
# Day-of-week adjustment
# ---------------------------------------------------------------------------


def compute_dow_adjustment(
    series: pd.Series,
    dates: pd.Series,
) -> pd.Series:
    """Compute day-of-week adjustment factors for a metric series.

    Calculates the ratio of each day-of-week's historical mean to the overall
    mean, then returns the adjusted series (original / adjustment factor).

    Parameters
    ----------
    series:
        Metric values (e.g., daily spend).
    dates:
        Corresponding date values for determining day-of-week.

    Returns
    -------
    pd.Series
        Seasonally adjusted metric values.
    """
    # TODO: compute DOW means, divide series by per-DOW adjustment factor
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Method 1: Rolling Z-Score
# ---------------------------------------------------------------------------


def rolling_zscore(
    series: pd.Series,
    window: int = DEFAULT_ZSCORE_WINDOW,
    threshold: float = DEFAULT_ZSCORE_THRESHOLD,
    min_observations: int = DEFAULT_MIN_OBSERVATIONS,
) -> pd.DataFrame:
    """Compute rolling Z-scores and flag anomalies.

    Parameters
    ----------
    series:
        Time-ordered metric values (one value per day).
    window:
        Number of trailing days for computing rolling mean and std.
    threshold:
        Absolute Z-score value above which an observation is flagged.
    min_observations:
        Minimum number of prior observations required before computing
        Z-scores. Earlier values receive ``NaN``.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``value``, ``rolling_mean``, ``rolling_std``,
        ``z_score``, and ``is_anomaly`` (bool).
    """
    # TODO: compute rolling mean/std, z-score, boolean flag
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Method 2: Isolation Forest
# ---------------------------------------------------------------------------


def prepare_isolation_features(
    df: pd.DataFrame,
    metrics: list[str] | None = None,
) -> pd.DataFrame:
    """Engineer features for isolation forest from raw metric data.

    Computes day-over-day deltas and 7-day ratio features, then standardizes
    all features to zero mean and unit variance.

    Parameters
    ----------
    df:
        DataFrame with daily metric columns (spend, cpa, ctr, conversion_rate).
    metrics:
        Subset of metrics to use as features. Defaults to
        ``METRICS_TO_MONITOR``.

    Returns
    -------
    pd.DataFrame
        Standardized feature matrix suitable for isolation forest input.
    """
    # TODO: compute deltas, 7-day ratios, standardize
    raise NotImplementedError


def run_isolation_forest(
    features: pd.DataFrame,
    n_estimators: int = DEFAULT_ISO_N_ESTIMATORS,
    contamination: float = DEFAULT_ISO_CONTAMINATION,
    max_samples: int = DEFAULT_ISO_MAX_SAMPLES,
) -> pd.Series:
    """Run isolation forest and return anomaly scores.

    Parameters
    ----------
    features:
        Standardized feature matrix from ``prepare_isolation_features``.
    n_estimators:
        Number of isolation trees in the ensemble.
    contamination:
        Expected proportion of anomalies in the dataset.
    max_samples:
        Number of samples drawn to train each tree.

    Returns
    -------
    pd.Series
        Anomaly scores (negative = more anomalous). Values below -0.3
        are considered anomalies.
    """
    # TODO: fit sklearn IsolationForest, return decision_function scores
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Method 3: Seasonal Decomposition (STL)
# ---------------------------------------------------------------------------


def stl_decompose(
    series: pd.Series,
    period: int = DEFAULT_STL_PERIOD,
    seasonal_window: int = DEFAULT_STL_SEASONAL_WINDOW,
    trend_window: int = DEFAULT_STL_TREND_WINDOW,
    iqr_multiplier: float = DEFAULT_STL_IQR_MULTIPLIER,
) -> pd.DataFrame:
    """Decompose a time series using STL and flag residual anomalies.

    Parameters
    ----------
    series:
        Daily metric values indexed by date.
    period:
        Seasonal period in days (default 7 for weekly).
    seasonal_window:
        Loess window size for the seasonal component.
    trend_window:
        Loess window size for the trend component.
    iqr_multiplier:
        Number of IQRs beyond which a residual is flagged as anomalous.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``trend``, ``seasonal``, ``residual``,
        ``residual_iqr``, and ``is_anomaly`` (bool).
    """
    # TODO: apply statsmodels STL, compute IQR threshold on residuals
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Combined detection pipeline
# ---------------------------------------------------------------------------


def combine_anomaly_signals(
    zscore_flags: pd.Series,
    iso_flags: pd.Series,
    stl_flags: pd.Series,
) -> pd.Series:
    """Determine final severity from the combination of method flags.

    Severity mapping (from references/anomaly_detection.md):
    - All three flagged -> Critical
    - Any two flagged -> High
    - Z-score only -> Medium
    - Isolation or STL only -> Low

    Parameters
    ----------
    zscore_flags:
        Boolean series from rolling Z-score method.
    iso_flags:
        Boolean series from isolation forest method.
    stl_flags:
        Boolean series from STL decomposition method.

    Returns
    -------
    pd.Series
        Severity labels: ``"critical"``, ``"high"``, ``"medium"``, ``"low"``,
        or ``"none"``.
    """
    # TODO: implement severity matrix logic
    raise NotImplementedError


def drill_down_root_cause(
    df: pd.DataFrame,
    anomaly_date: str,
    metric: str,
    platform: str,
) -> str:
    """Drill from account-level anomaly to campaign/ad-group/keyword root cause.

    Parameters
    ----------
    df:
        Full normalized media DataFrame with campaign and ad group detail.
    anomaly_date:
        Date of the anomaly (``YYYY-MM-DD``).
    metric:
        The anomalous metric name.
    platform:
        Platform where the anomaly was detected.

    Returns
    -------
    str
        Human-readable root cause description identifying the entity and
        metric delta responsible for the anomaly.
    """
    # TODO: decompose account-level deviation into campaign/ad-group contributions
    raise NotImplementedError


def detect_anomalies(
    df: pd.DataFrame,
    metrics: list[str] | None = None,
    known_events: list[str] | None = None,
    zscore_threshold: float = DEFAULT_ZSCORE_THRESHOLD,
    iso_contamination: float = DEFAULT_ISO_CONTAMINATION,
    stl_iqr_multiplier: float = DEFAULT_STL_IQR_MULTIPLIER,
) -> list[AnomalyAlert]:
    """Run the full anomaly detection pipeline on a unified media DataFrame.

    Applies all three detection methods per metric, combines signals into
    severity-ranked alerts, performs root-cause drill-down, and suppresses
    alerts for known event dates.

    Parameters
    ----------
    df:
        Unified media performance DataFrame (output of ``normalize_platforms``).
    metrics:
        Metrics to monitor. Defaults to ``METRICS_TO_MONITOR``.
    known_events:
        List of date strings (``YYYY-MM-DD``) for known events where
        anomaly alerts should be suppressed.
    zscore_threshold:
        Z-score threshold for the rolling Z-score method.
    iso_contamination:
        Contamination parameter for isolation forest.
    stl_iqr_multiplier:
        IQR multiplier for STL residual flagging.

    Returns
    -------
    list[AnomalyAlert]
        Anomaly alerts sorted by severity (critical first), then by date.
    """
    # TODO: orchestrate all methods, combine, drill-down, filter known events
    raise NotImplementedError
