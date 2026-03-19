"""Creative fatigue detection for paid media campaigns.

Analyzes creative-level performance curves to detect fatigue — declining
conversion-weighted CTR over time due to audience overexposure. Fits piecewise
regressions, computes fatigue scores, and recommends rotation timing.

See references/creative_fatigue.md for full methodology documentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MIN_DAYS_FOR_SCORING: int = 7
SMOOTHING_WINDOW: int = 3
FATIGUE_THRESHOLD_ROTATE: int = 60
FATIGUE_THRESHOLD_IMMEDIATE: int = 80
PROJECTION_HORIZON_DAYS: int = 3
PEAK_DECLINE_ALERT_PCT: float = 0.50

PLATFORM_FATIGUE_MULTIPLIERS: dict[str, float] = {
    "google": 1.0,
    "meta": 1.0,
    "linkedin": 0.7,
    "tiktok": 0.7,
    "dv360": 1.0,
}


@dataclass
class FatigueResult:
    """Fatigue analysis result for a single creative."""

    creative_id: str
    platform: str
    campaign_id: str
    ad_group_id: str
    first_impression_date: str
    days_active: int
    peak_cwctr: float
    current_cwctr: float
    fatigue_score: int
    fatigue_label: str
    decay_slope: Optional[float]
    projected_days_to_50pct: Optional[int]
    frequency: Optional[float]
    recommendation: str


# ---------------------------------------------------------------------------
# Metric computation
# ---------------------------------------------------------------------------


def compute_conversion_weighted_ctr(
    df: pd.DataFrame,
    campaign_median_conv_rate: float,
) -> pd.Series:
    """Compute conversion-weighted CTR (cwCTR) for creative time series.

    cwCTR = CTR * (conversion_rate / median_conversion_rate)

    This weights CTR by the creative's relative conversion efficiency,
    preventing top-of-funnel creatives from being incorrectly flagged.

    Parameters
    ----------
    df:
        Creative-level daily DataFrame with ``ctr`` and ``conversion_rate``
        columns.
    campaign_median_conv_rate:
        Median conversion rate across the campaign for the observation window.

    Returns
    -------
    pd.Series
        Conversion-weighted CTR values aligned with the input index.
    """
    # TODO: compute cwCTR = ctr * (conversion_rate / campaign_median_conv_rate)
    raise NotImplementedError


def smooth_series(
    series: pd.Series,
    window: int = SMOOTHING_WINDOW,
) -> pd.Series:
    """Apply centered moving average smoothing to a time series.

    Parameters
    ----------
    series:
        Raw daily metric values.
    window:
        Window size for the centered moving average.

    Returns
    -------
    pd.Series
        Smoothed series with NaN at the edges where the window is incomplete.
    """
    # TODO: apply centered rolling mean with min_periods=1
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Piecewise regression
# ---------------------------------------------------------------------------


def fit_piecewise_regression(
    series: pd.Series,
) -> dict[str, Any]:
    """Fit a two-phase piecewise linear regression (plateau + decay).

    Identifies the breakpoint between the plateau phase (slope ~ 0) and the
    decay phase (negative slope) by minimizing the combined residual sum of
    squares across all candidate breakpoints.

    Parameters
    ----------
    series:
        Smoothed cwCTR time series indexed by integer day number
        (0 = first impression day).

    Returns
    -------
    dict
        Keys:
        - ``breakpoint``: int, day index where decay begins.
        - ``plateau_slope``: float, slope of the plateau phase.
        - ``plateau_intercept``: float, intercept of the plateau phase.
        - ``decay_slope``: float, slope of the decay phase.
        - ``decay_intercept``: float, intercept of the decay phase.
        - ``residual_ss``: float, combined residual sum of squares.
    """
    # TODO: iterate candidate breakpoints, fit OLS on each segment, pick min RSS
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Fatigue scoring
# ---------------------------------------------------------------------------


def compute_fatigue_score(
    peak_cwctr: float,
    current_cwctr: float,
) -> int:
    """Compute fatigue score from 0 (fresh) to 100 (exhausted).

    fatigue_score = clamp(0, 100, 100 * (1 - current_cwctr / peak_cwctr))

    Parameters
    ----------
    peak_cwctr:
        Maximum smoothed cwCTR observed during the plateau phase.
    current_cwctr:
        Most recent smoothed cwCTR value.

    Returns
    -------
    int
        Fatigue score between 0 and 100.
    """
    # TODO: implement clamped fatigue score calculation
    raise NotImplementedError


def fatigue_label(score: int) -> str:
    """Map a fatigue score to a human-readable label.

    Parameters
    ----------
    score:
        Fatigue score between 0 and 100.

    Returns
    -------
    str
        One of ``"Fresh"``, ``"Early wear"``, ``"Moderate"``, ``"Fatigued"``,
        ``"Exhausted"``.
    """
    # TODO: map score ranges to labels per references/creative_fatigue.md
    raise NotImplementedError


def project_days_to_threshold(
    current_cwctr: float,
    peak_cwctr: float,
    decay_slope: float,
    threshold_pct: float = PEAK_DECLINE_ALERT_PCT,
) -> Optional[int]:
    """Project how many days until cwCTR drops below threshold % of peak.

    Parameters
    ----------
    current_cwctr:
        Most recent smoothed cwCTR.
    peak_cwctr:
        Peak cwCTR from the plateau phase.
    decay_slope:
        Daily rate of cwCTR decline (negative value).
    threshold_pct:
        Fraction of peak below which an alert is triggered. Default 0.50.

    Returns
    -------
    Optional[int]
        Estimated days until threshold crossing, or ``None`` if the creative
        is already below threshold or the slope is non-negative (not decaying).
    """
    # TODO: (threshold_pct * peak - current) / decay_slope, rounded up
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Rotation recommendation
# ---------------------------------------------------------------------------


def generate_recommendation(
    fatigue_score: int,
    projected_days: Optional[int],
    frequency: Optional[float],
) -> str:
    """Generate a rotation recommendation string.

    Applies the heuristic rules from references/creative_fatigue.md:
    - score > 80 or projected_days <= 3 -> rotate immediately
    - score > 60 -> queue replacement
    - frequency > 3.0 and score > 40 -> rotate soon
    - otherwise -> continue monitoring

    Parameters
    ----------
    fatigue_score:
        Fatigue score (0-100).
    projected_days:
        Days until 50% of peak threshold, or ``None``.
    frequency:
        Ad frequency (impressions / unique reach), or ``None`` if unavailable.

    Returns
    -------
    str
        Human-readable recommendation.
    """
    # TODO: implement rotation heuristic decision tree
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def analyze_creative(
    creative_df: pd.DataFrame,
    campaign_median_conv_rate: float,
    platform: str,
) -> Optional[FatigueResult]:
    """Run full fatigue analysis for a single creative.

    Parameters
    ----------
    creative_df:
        Daily performance DataFrame for one creative, with columns ``date``,
        ``ctr``, ``conversion_rate``, ``impressions``, and optionally
        ``frequency``. Must be sorted by date.
    campaign_median_conv_rate:
        Median conversion rate for the parent campaign.
    platform:
        Platform identifier for applying platform-specific multipliers.

    Returns
    -------
    Optional[FatigueResult]
        Fatigue analysis result, or ``None`` if the creative has fewer than
        ``MIN_DAYS_FOR_SCORING`` days of data.
    """
    # TODO: compute cwCTR -> smooth -> piecewise regression -> score -> recommend
    raise NotImplementedError


def analyze_all_creatives(
    df: pd.DataFrame,
) -> list[FatigueResult]:
    """Run fatigue analysis across all creatives in a unified dataset.

    Groups by ``(platform, campaign_id, creative_id)`` and applies
    ``analyze_creative`` to each group.

    Parameters
    ----------
    df:
        Creative-level performance DataFrame with columns ``platform``,
        ``campaign_id``, ``creative_id``, ``ad_group_id``, ``date``,
        ``ctr``, ``conversion_rate``, ``impressions``, and optionally
        ``frequency``.

    Returns
    -------
    list[FatigueResult]
        Fatigue results sorted by fatigue score descending (most fatigued first).
    """
    # TODO: group by creative, compute campaign medians, map analyze_creative
    raise NotImplementedError
