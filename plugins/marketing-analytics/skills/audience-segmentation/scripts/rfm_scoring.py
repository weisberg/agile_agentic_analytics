"""RFM Scoring Module

Computes Recency, Frequency, and Monetary metrics from transaction data,
assigns quintile-based scores, maps composite scores to named customer
segments, and persists results.

Usage:
    from scripts.rfm_scoring import compute_rfm, assign_quintiles, label_segments

Dependencies:
    pandas, numpy
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default configuration
# ---------------------------------------------------------------------------

DEFAULT_ANALYSIS_WINDOW_DAYS: int = 365
DEFAULT_QUINTILE_BINS: int = 5
DEFAULT_RFM_WEIGHTS: dict[str, float] = {
    "recency": 0.4,
    "frequency": 0.3,
    "monetary": 0.3,
}

SEGMENT_RULES: list[dict[str, Any]] = [
    {"name": "Champions", "R": (4, 5), "F": (4, 5), "M": (4, 5)},
    {"name": "Loyal Customers", "R": (3, 5), "F": (4, 5), "M": (3, 5)},
    {"name": "Potential Loyalists", "R": (4, 5), "F": (1, 3), "M": (1, 3)},
    {"name": "New Customers", "R": (5, 5), "F": (1, 1), "M": (1, 3)},
    {"name": "Promising", "R": (3, 4), "F": (1, 2), "M": (1, 2)},
    {"name": "Needs Attention", "R": (3, 3), "F": (3, 3), "M": (3, 3)},
    {"name": "At-Risk", "R": (1, 2), "F": (4, 5), "M": (4, 5)},
    {"name": "About to Sleep", "R": (1, 3), "F": (1, 2), "M": (1, 2)},
    {"name": "Hibernating", "R": (1, 2), "F": (1, 3), "M": (1, 3)},
    {"name": "Lost", "R": (1, 1), "F": (1, 1), "M": (1, 2)},
]


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def load_transactions(
    filepath: str | Path,
    date_column: str = "date",
    customer_id_column: str = "customer_id",
    amount_column: str = "amount",
) -> pd.DataFrame:
    """Load and validate transaction data from a CSV file.

    Parameters
    ----------
    filepath : str or Path
        Path to the transactions CSV file.
    date_column : str
        Name of the date column in the CSV.
    customer_id_column : str
        Name of the customer identifier column.
    amount_column : str
        Name of the transaction amount column.

    Returns
    -------
    pd.DataFrame
        Validated transaction DataFrame with parsed dates.

    Raises
    ------
    FileNotFoundError
        If the transactions file does not exist.
    ValueError
        If required columns are missing.
    """
    # TODO: Implement file loading, column validation, date parsing
    raise NotImplementedError("load_transactions not yet implemented")


def compute_rfm(
    transactions: pd.DataFrame,
    analysis_date: Optional[datetime] = None,
    customer_id_column: str = "customer_id",
    date_column: str = "date",
    amount_column: str = "amount",
    window_days: int = DEFAULT_ANALYSIS_WINDOW_DAYS,
) -> pd.DataFrame:
    """Compute raw RFM metrics for each customer.

    Parameters
    ----------
    transactions : pd.DataFrame
        Transaction data with at least customer_id, date, and amount columns.
    analysis_date : datetime, optional
        Reference date for recency calculation. Defaults to today.
    customer_id_column : str
        Name of the customer identifier column.
    date_column : str
        Name of the date column.
    amount_column : str
        Name of the transaction amount column.
    window_days : int
        Number of days of history to include.

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by customer_id with columns:
        - recency (int): days since last transaction
        - frequency (int): number of transactions
        - monetary (float): total spend
    """
    # TODO: Filter to analysis window, group by customer, compute R/F/M
    raise NotImplementedError("compute_rfm not yet implemented")


def assign_quintiles(
    rfm_df: pd.DataFrame,
    n_bins: int = DEFAULT_QUINTILE_BINS,
) -> pd.DataFrame:
    """Assign quintile scores (1-5) for each RFM dimension.

    Recency is inverted so that lower values (more recent) get higher scores.
    Falls back to rank-based assignment if quantile boundaries are non-unique.

    Parameters
    ----------
    rfm_df : pd.DataFrame
        DataFrame with raw recency, frequency, monetary columns.
    n_bins : int
        Number of quantile bins (default 5 for quintiles).

    Returns
    -------
    pd.DataFrame
        Original DataFrame with additional columns:
        - r_score (int): Recency quintile score 1-5
        - f_score (int): Frequency quintile score 1-5
        - m_score (int): Monetary quintile score 1-5
        - rfm_composite (str): Concatenated score string, e.g., "543"
        - rfm_weighted (float): Weighted composite score
    """
    # TODO: Apply pd.qcut with fallback to pd.cut, invert recency, compute composites
    raise NotImplementedError("assign_quintiles not yet implemented")


def label_segments(
    rfm_scored: pd.DataFrame,
    rules: Optional[list[dict[str, Any]]] = None,
) -> pd.DataFrame:
    """Map RFM quintile scores to named business segments.

    Applies rules in priority order (first match wins).

    Parameters
    ----------
    rfm_scored : pd.DataFrame
        DataFrame with r_score, f_score, m_score columns.
    rules : list of dict, optional
        Segment mapping rules. Each dict has keys: name, R (min, max),
        F (min, max), M (min, max). Defaults to SEGMENT_RULES.

    Returns
    -------
    pd.DataFrame
        Original DataFrame with an additional 'segment' column.

    Raises
    ------
    ValueError
        If any customer is not assigned to a segment (rules are not exhaustive).
    """
    # TODO: Iterate rules, apply range checks, assign segment names
    raise NotImplementedError("label_segments not yet implemented")


def save_rfm_boundaries(
    rfm_df: pd.DataFrame,
    analysis_date: datetime,
    output_path: str | Path,
) -> None:
    """Persist quintile boundary values for auditability.

    Parameters
    ----------
    rfm_df : pd.DataFrame
        DataFrame with raw recency, frequency, monetary values.
    analysis_date : datetime
        The reference date used for this scoring run.
    output_path : str or Path
        Path to write the boundaries JSON file.
    """
    # TODO: Compute quantile boundaries, write to JSON
    raise NotImplementedError("save_rfm_boundaries not yet implemented")


def run_rfm_pipeline(
    transactions_path: str | Path,
    output_dir: str | Path,
    analysis_date: Optional[datetime] = None,
    window_days: int = DEFAULT_ANALYSIS_WINDOW_DAYS,
    n_bins: int = DEFAULT_QUINTILE_BINS,
) -> pd.DataFrame:
    """Execute the full RFM scoring pipeline end-to-end.

    Steps:
    1. Load transactions
    2. Compute raw RFM metrics
    3. Assign quintile scores
    4. Label named segments
    5. Save boundaries and segment assignments

    Parameters
    ----------
    transactions_path : str or Path
        Path to the transactions CSV file.
    output_dir : str or Path
        Directory to write output files.
    analysis_date : datetime, optional
        Reference date for recency. Defaults to today.
    window_days : int
        Number of days of history to include.
    n_bins : int
        Number of quantile bins.

    Returns
    -------
    pd.DataFrame
        Complete RFM-scored DataFrame with segment labels.
    """
    # TODO: Orchestrate the full pipeline
    raise NotImplementedError("run_rfm_pipeline not yet implemented")
