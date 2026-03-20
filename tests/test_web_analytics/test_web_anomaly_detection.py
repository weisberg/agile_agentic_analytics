"""Tests for web-analytics / web_anomaly_detection.py

Covers Z-score anomaly detection on clean and spiked time series data.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Make the scripts directory importable.
_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "marketing-analytics"
    / "skills"
    / "web-analytics"
    / "scripts"
)
sys.path.insert(0, str(_SCRIPTS_DIR))

from web_anomaly_detection import (
    AnomalyConfig,
    compute_z_scores,
    detect_anomalies,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_clean_daily_series(n_days: int = 90, seed: int = 0) -> pd.DataFrame:
    """Generate a clean daily sessions time series with weekly seasonality.

    The series has a gentle upward trend and 7-day seasonality with low noise,
    so no data points should be flagged as anomalous.
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n_days, freq="D")
    trend = np.linspace(1000, 1200, n_days)
    seasonal = 100 * np.sin(2 * np.pi * np.arange(n_days) / 7)
    noise = rng.normal(0, 15, size=n_days)  # very low noise
    sessions = trend + seasonal + noise
    return pd.DataFrame({"date": dates, "sessions": sessions.round(0)})


def _make_spiked_series(
    n_days: int = 90,
    spike_day: int = 60,
    spike_magnitude: float = 5000.0,
    seed: int = 0,
) -> pd.DataFrame:
    """Generate a daily series with one huge spike injected."""
    df = _make_clean_daily_series(n_days=n_days, seed=seed)
    df.loc[spike_day, "sessions"] += spike_magnitude
    return df


# ---------------------------------------------------------------------------
# test_z_score_detection  -- detects injected anomalies
# ---------------------------------------------------------------------------

class TestZScoreDetection:
    """Verify that a large injected spike is detected as anomalous."""

    def test_spike_detected(self):
        """A +5000 spike on day 60 should be flagged."""
        df = _make_spiked_series(n_days=90, spike_day=60, spike_magnitude=5000.0)
        config = AnomalyConfig(
            z_score_threshold=3.0,
            seasonal_period=7,
            min_history_days=56,
        )
        anomalies = detect_anomalies(df, "date", "sessions", config)

        anomaly_dates = {a.anomaly_date for a in anomalies}
        expected_date = df.loc[60, "date"].date()
        assert expected_date in anomaly_dates, (
            f"Spike on {expected_date} was not detected. "
            f"Detected dates: {anomaly_dates}"
        )

    def test_spike_direction_above(self):
        """The injected spike should be flagged as 'above' expected."""
        df = _make_spiked_series(n_days=90, spike_day=60, spike_magnitude=5000.0)
        config = AnomalyConfig(z_score_threshold=3.0, min_history_days=56)
        anomalies = detect_anomalies(df, "date", "sessions", config)

        spike_date = df.loc[60, "date"].date()
        spike_anomalies = [a for a in anomalies if a.anomaly_date == spike_date]
        assert len(spike_anomalies) >= 1
        assert spike_anomalies[0].direction == "above"

    def test_negative_spike_detected(self):
        """A large negative spike should also be flagged."""
        df = _make_clean_daily_series(n_days=90, seed=1)
        df.loc[70, "sessions"] -= 4000.0  # inject a crash
        config = AnomalyConfig(z_score_threshold=3.0, min_history_days=56)
        anomalies = detect_anomalies(df, "date", "sessions", config)

        crash_date = df.loc[70, "date"].date()
        crash_anomalies = [a for a in anomalies if a.anomaly_date == crash_date]
        assert len(crash_anomalies) >= 1
        assert crash_anomalies[0].direction == "below"

    def test_z_score_exceeds_threshold(self):
        """Detected anomalies should all have |z_score| >= threshold."""
        df = _make_spiked_series(n_days=90, spike_day=60, spike_magnitude=5000.0)
        config = AnomalyConfig(z_score_threshold=3.0, min_history_days=56)
        anomalies = detect_anomalies(df, "date", "sessions", config)

        for a in anomalies:
            assert abs(a.z_score) >= 3.0


# ---------------------------------------------------------------------------
# test_no_false_positives_on_clean_data
# ---------------------------------------------------------------------------

class TestNoFalsePositivesOnCleanData:
    """Clean data with low noise should produce no (or very few) alerts."""

    def test_clean_series_no_anomalies(self):
        """A well-behaved series with minimal noise should trigger no alerts."""
        df = _make_clean_daily_series(n_days=90, seed=42)
        config = AnomalyConfig(
            z_score_threshold=3.0,
            seasonal_period=7,
            min_history_days=56,
        )
        anomalies = detect_anomalies(df, "date", "sessions", config)

        # Allow up to 1 spurious alert (statistical noise), but ideally 0
        assert len(anomalies) <= 1, (
            f"Expected 0-1 anomalies on clean data, got {len(anomalies)}"
        )

    def test_higher_threshold_fewer_alerts(self):
        """Raising the z-score threshold should reduce or eliminate alerts."""
        df = _make_spiked_series(n_days=90, spike_day=60, spike_magnitude=800.0)

        config_low = AnomalyConfig(z_score_threshold=2.0, min_history_days=56)
        config_high = AnomalyConfig(z_score_threshold=4.0, min_history_days=56)

        anomalies_low = detect_anomalies(df, "date", "sessions", config_low)
        anomalies_high = detect_anomalies(df, "date", "sessions", config_high)

        assert len(anomalies_high) <= len(anomalies_low)


# ---------------------------------------------------------------------------
# compute_z_scores unit tests
# ---------------------------------------------------------------------------

class TestComputeZScores:
    """Unit tests for the z-score computation helper."""

    def test_constant_series(self):
        """A constant series should produce all-zero z-scores."""
        residuals = pd.Series([5.0] * 50)
        z = compute_z_scores(residuals)
        assert (z == 0.0).all()

    def test_known_outlier(self):
        """An obvious outlier should have a high z-score."""
        residuals = pd.Series([0.0] * 49 + [100.0])
        z = compute_z_scores(residuals)
        assert abs(z.iloc[-1]) > 3.0

    def test_symmetric_distribution(self):
        """Z-scores of symmetric residuals should have near-zero median."""
        rng = np.random.default_rng(99)
        residuals = pd.Series(rng.normal(0, 1, size=1000))
        z = compute_z_scores(residuals)
        assert abs(z.median()) < 0.5
