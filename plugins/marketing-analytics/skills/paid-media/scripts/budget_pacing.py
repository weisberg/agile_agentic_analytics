"""Budget pacing calculation for paid media campaigns.

Tracks daily spend against monthly budget plans and projects month-end variance
using exponential smoothing. Generates pacing alerts when projected spend
deviates from plan beyond configurable thresholds.

Per development guidelines, exponential smoothing is used instead of simple
linear extrapolation to handle intra-month spend acceleration patterns. All
monetary calculations use Python's Decimal type.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_SMOOTHING_ALPHA: float = 0.3
DEFAULT_WARNING_THRESHOLD: float = 0.10  # 10% variance
DEFAULT_CRITICAL_THRESHOLD: float = 0.20  # 20% variance


@dataclass
class PacingResult:
    """Budget pacing result for a single campaign."""

    campaign_id: str
    platform: str
    budget_plan: Decimal
    spend_to_date: Decimal
    days_elapsed: int
    days_remaining: int
    projected_spend: Decimal
    variance_pct: Decimal
    alert_level: str  # "none", "warning", "critical"
    daily_target_remaining: Optional[Decimal]


# ---------------------------------------------------------------------------
# Exponential smoothing
# ---------------------------------------------------------------------------


def exponential_smoothing(
    daily_spend: list[Decimal],
    alpha: float = DEFAULT_SMOOTHING_ALPHA,
) -> Decimal:
    """Compute the exponentially smoothed daily spend rate.

    Applies simple exponential smoothing (SES) to a sequence of daily spend
    values and returns the smoothed estimate for the next day.

    Parameters
    ----------
    daily_spend:
        Chronologically ordered list of daily spend values (Decimal).
    alpha:
        Smoothing factor between 0 and 1. Higher values give more weight
        to recent observations.

    Returns
    -------
    Decimal
        Smoothed daily spend rate estimate.

    Raises
    ------
    ValueError
        If *daily_spend* is empty or *alpha* is not in (0, 1].
    """
    # TODO: iterate daily_spend applying SES: s_t = alpha * x_t + (1 - alpha) * s_{t-1}
    raise NotImplementedError


def apply_dow_seasonality(
    smoothed_rate: Decimal,
    days_remaining_by_dow: dict[int, int],
    dow_factors: dict[int, Decimal],
) -> Decimal:
    """Adjust the smoothed daily rate for day-of-week spending patterns.

    Instead of projecting a flat daily rate, scales each remaining day by
    its historical day-of-week factor.

    Parameters
    ----------
    smoothed_rate:
        Base smoothed daily spend rate from ``exponential_smoothing``.
    days_remaining_by_dow:
        Count of remaining days in the month by day-of-week index (0=Mon).
    dow_factors:
        Historical spend factor per day-of-week (1.0 = average day).

    Returns
    -------
    Decimal
        Projected total spend for the remaining days.
    """
    # TODO: sum smoothed_rate * dow_factor for each remaining day
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Pacing calculation
# ---------------------------------------------------------------------------


def compute_pacing(
    daily_spend: list[Decimal],
    budget_plan: Decimal,
    current_date: date,
    month_start: date,
    month_end: date,
    alpha: float = DEFAULT_SMOOTHING_ALPHA,
    dow_factors: Optional[dict[int, Decimal]] = None,
) -> PacingResult:
    """Compute budget pacing for a single campaign.

    Parameters
    ----------
    daily_spend:
        List of daily spend values from month start through current date.
    budget_plan:
        Monthly budget target (Decimal).
    current_date:
        The current reporting date.
    month_start:
        First day of the budget month.
    month_end:
        Last day of the budget month.
    alpha:
        Exponential smoothing factor.
    dow_factors:
        Optional day-of-week adjustment factors. If ``None``, a flat
        projection is used.

    Returns
    -------
    PacingResult
        Pacing status including projected spend and alert level.
    """
    # TODO: sum spend_to_date, project remaining via exponential smoothing,
    #       compute variance, determine alert level
    raise NotImplementedError


def determine_alert_level(
    variance_pct: Decimal,
    warning_threshold: float = DEFAULT_WARNING_THRESHOLD,
    critical_threshold: float = DEFAULT_CRITICAL_THRESHOLD,
) -> str:
    """Map a variance percentage to an alert level.

    Parameters
    ----------
    variance_pct:
        (projected_spend - budget_plan) / budget_plan as a Decimal.
        Can be positive (overspend) or negative (underspend).
    warning_threshold:
        Absolute variance percentage triggering a warning.
    critical_threshold:
        Absolute variance percentage triggering a critical alert.

    Returns
    -------
    str
        ``"critical"``, ``"warning"``, or ``"none"``.
    """
    # TODO: compare abs(variance_pct) against thresholds
    raise NotImplementedError


def compute_daily_target_remaining(
    budget_plan: Decimal,
    spend_to_date: Decimal,
    days_remaining: int,
) -> Optional[Decimal]:
    """Calculate the required daily spend for remaining days to hit budget.

    Parameters
    ----------
    budget_plan:
        Monthly budget target.
    spend_to_date:
        Actual spend through the current date.
    days_remaining:
        Number of days left in the budget month.

    Returns
    -------
    Optional[Decimal]
        Required daily spend, or ``None`` if no days remain.
    """
    # TODO: (budget_plan - spend_to_date) / days_remaining using Decimal
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Batch pipeline
# ---------------------------------------------------------------------------


def compute_dow_factors(
    historical_spend: pd.DataFrame,
) -> dict[int, Decimal]:
    """Compute day-of-week spend factors from historical data.

    The factor for each DOW is the ratio of that DOW's average daily spend
    to the overall average daily spend.

    Parameters
    ----------
    historical_spend:
        DataFrame with ``date`` and ``spend`` columns covering at least
        4 weeks of history.

    Returns
    -------
    dict[int, Decimal]
        Mapping of DOW index (0=Monday) to spend factor (Decimal).
    """
    # TODO: group by DOW, compute mean, divide by overall mean
    raise NotImplementedError


def run_pacing_report(
    df: pd.DataFrame,
    budget_plans: dict[str, Decimal],
    current_date: date,
    alpha: float = DEFAULT_SMOOTHING_ALPHA,
) -> list[PacingResult]:
    """Run budget pacing analysis for all campaigns in a unified DataFrame.

    Parameters
    ----------
    df:
        Unified media performance DataFrame with ``campaign_id``, ``platform``,
        ``date``, and ``spend`` columns.
    budget_plans:
        Mapping of campaign_id to monthly budget target (Decimal).
    current_date:
        Current reporting date for determining elapsed/remaining days.
    alpha:
        Exponential smoothing factor.

    Returns
    -------
    list[PacingResult]
        Pacing results for all campaigns, sorted by absolute variance
        descending (most off-pace first).
    """
    # TODO: group by campaign, extract daily spend, compute DOW factors,
    #       apply compute_pacing to each, sort by |variance|
    raise NotImplementedError
