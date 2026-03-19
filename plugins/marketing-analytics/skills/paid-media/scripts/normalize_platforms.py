"""Platform data normalization for paid media analytics.

Maps platform-specific campaign data exports (Google Ads, Meta Ads, LinkedIn Ads,
TikTok Ads, DV360) into a unified media performance schema. Handles metric name
mapping, attribution window labeling, currency conversion, and derived metric
computation.

All monetary calculations use Python's Decimal type to avoid floating-point
rounding errors.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Platform configuration
# ---------------------------------------------------------------------------

PLATFORM_METRIC_MAP: dict[str, dict[str, str]] = {
    "google": {
        "Impressions": "impressions",
        "Clicks": "clicks",
        "Cost": "spend",
        "Conversions": "conversions",
        "ConversionValue": "revenue",
    },
    "meta": {
        "impressions": "impressions",
        "outbound_clicks": "clicks",
        "spend": "spend",
        "actions_purchase": "conversions",
        "action_values_purchase": "revenue",
    },
    "linkedin": {
        "impressions": "impressions",
        "clicks": "clicks",
        "costInLocalCurrency": "spend",
        "externalWebsiteConversions": "conversions",
        "conversionValueInLocalCurrency": "revenue",
    },
    "tiktok": {
        "impressions": "impressions",
        "clicks": "clicks",
        "spend": "spend",
        "conversions": "conversions",
        "value": "revenue",
    },
    "dv360": {
        "impressions": "impressions",
        "clicks": "clicks",
        "revenue": "spend",
        "totalConversions": "conversions",
        "totalConversionValue": "revenue",
    },
}

ATTRIBUTION_WINDOWS: dict[str, str] = {
    "google": "30-day click",
    "meta": "7-day click, 1-day view",
    "linkedin": "30-day click",
    "tiktok": "7-day click",
    "dv360": "floodlight",
}

SUPPORTED_PLATFORMS: list[str] = list(PLATFORM_METRIC_MAP.keys())


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def load_platform_data(
    file_path: str | Path,
    platform: str,
) -> pd.DataFrame:
    """Load a platform-specific campaign CSV and return a raw DataFrame.

    Parameters
    ----------
    file_path:
        Path to the platform CSV export
        (e.g., ``workspace/raw/campaign_spend_google.csv``).
    platform:
        One of ``google``, ``meta``, ``linkedin``, ``tiktok``, ``dv360``.

    Returns
    -------
    pd.DataFrame
        Raw data as read from the CSV. No transformations applied.

    Raises
    ------
    ValueError
        If *platform* is not in ``SUPPORTED_PLATFORMS``.
    FileNotFoundError
        If *file_path* does not exist.
    """
    # TODO: implement CSV loading with platform-specific parsing rules
    raise NotImplementedError


def rename_columns(
    df: pd.DataFrame,
    platform: str,
) -> pd.DataFrame:
    """Rename platform-specific columns to the unified metric taxonomy.

    Parameters
    ----------
    df:
        Raw platform DataFrame with original column names.
    platform:
        Platform identifier used to look up the mapping in
        ``PLATFORM_METRIC_MAP``.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns renamed to the unified schema.
    """
    # TODO: apply PLATFORM_METRIC_MAP renaming, handle missing columns gracefully
    raise NotImplementedError


def convert_google_micros(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Convert Google Ads micro-unit columns to standard currency decimals.

    Google Ads reports cost in micros (1,000,000 micros = 1 currency unit).
    This function divides specified columns by 1e6 using ``Decimal`` arithmetic.

    Parameters
    ----------
    df:
        DataFrame containing Google Ads data with micro-unit columns.
    columns:
        Column names to convert. Defaults to ``["spend"]``.

    Returns
    -------
    pd.DataFrame
        DataFrame with converted columns.
    """
    # TODO: divide specified columns by Decimal("1000000")
    raise NotImplementedError


def normalize_currency(
    df: pd.DataFrame,
    source_currency: str,
    target_currency: str = "USD",
    fx_rates: Optional[dict[str, Decimal]] = None,
) -> pd.DataFrame:
    """Convert monetary columns from source currency to target currency.

    Parameters
    ----------
    df:
        DataFrame with ``spend`` and ``revenue`` columns in *source_currency*.
    source_currency:
        ISO 4217 code of the source currency (e.g., ``"EUR"``).
    target_currency:
        ISO 4217 code of the target currency. Defaults to ``"USD"``.
    fx_rates:
        Mapping of date strings (``YYYY-MM-DD``) to exchange rates. If
        ``None``, defaults to a rate of ``Decimal("1")`` (no conversion).

    Returns
    -------
    pd.DataFrame
        DataFrame with ``spend`` and ``revenue`` converted to *target_currency*.
    """
    # TODO: apply daily FX rates to spend and revenue columns using Decimal
    raise NotImplementedError


def add_attribution_label(
    df: pd.DataFrame,
    platform: str,
) -> pd.DataFrame:
    """Add an ``attribution_window`` column describing the platform's default window.

    Parameters
    ----------
    df:
        Normalized DataFrame.
    platform:
        Platform identifier for looking up ``ATTRIBUTION_WINDOWS``.

    Returns
    -------
    pd.DataFrame
        DataFrame with an ``attribution_window`` string column added.
    """
    # TODO: add column from ATTRIBUTION_WINDOWS lookup
    raise NotImplementedError


def compute_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute CPC, CTR, CPA, and ROAS from base metrics.

    Uses ``Decimal`` division. Returns ``None`` for any derived metric where
    the denominator is zero.

    Parameters
    ----------
    df:
        DataFrame with ``spend``, ``clicks``, ``impressions``, ``conversions``,
        and ``revenue`` columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with ``cpc``, ``ctr``, ``cpa``, and ``roas`` columns added.
    """
    # TODO: safe Decimal division with zero-denominator handling
    raise NotImplementedError


def normalize_platform(
    file_path: str | Path,
    platform: str,
    target_currency: str = "USD",
    fx_rates: Optional[dict[str, Decimal]] = None,
) -> pd.DataFrame:
    """End-to-end normalization pipeline for a single platform.

    Orchestrates loading, column renaming, currency conversion, attribution
    labeling, and derived metric computation.

    Parameters
    ----------
    file_path:
        Path to the raw platform CSV.
    platform:
        Platform identifier.
    target_currency:
        Reporting currency. Defaults to ``"USD"``.
    fx_rates:
        Optional daily FX rates for currency conversion.

    Returns
    -------
    pd.DataFrame
        Fully normalized DataFrame conforming to the unified media schema.
    """
    # TODO: chain load -> rename -> currency -> attribution -> derived
    raise NotImplementedError


def unify_all_platforms(
    raw_dir: str | Path,
    target_currency: str = "USD",
    fx_rates: Optional[dict[str, Decimal]] = None,
) -> pd.DataFrame:
    """Normalize and concatenate data from all available platforms.

    Scans *raw_dir* for files matching ``campaign_spend_{platform}.csv``,
    normalizes each, and concatenates into a single DataFrame sorted by
    ``(date, platform, campaign_id)``.

    Parameters
    ----------
    raw_dir:
        Directory containing raw platform CSVs.
    target_currency:
        Reporting currency for all monetary values.
    fx_rates:
        Optional daily FX rates.

    Returns
    -------
    pd.DataFrame
        Unified cross-platform DataFrame.
    """
    # TODO: discover platform files, normalize each, concatenate, sort
    raise NotImplementedError
