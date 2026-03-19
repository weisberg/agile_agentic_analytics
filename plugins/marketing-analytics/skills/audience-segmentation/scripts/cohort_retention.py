"""Cohort Retention Analysis Module

Defines customer cohorts by acquisition month, first product, or first
channel; generates period-over-period retention matrices; computes retention
rates, churn rates, revenue per user, and LTV trajectories.

Usage:
    from scripts.cohort_retention import (
        assign_cohorts,
        build_retention_matrix,
        compute_churn_rates,
        compute_revenue_per_user,
    )

Dependencies:
    pandas, numpy
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Literal, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

CohortDimension = Literal["acquisition_month", "first_product", "first_channel"]
PeriodGranularity = Literal["month", "week"]


# ---------------------------------------------------------------------------
# Cohort assignment
# ---------------------------------------------------------------------------


def assign_cohorts(
    transactions: pd.DataFrame,
    dimension: CohortDimension = "acquisition_month",
    customer_id_column: str = "customer_id",
    date_column: str = "date",
    product_column: str = "product",
    channel_column: Optional[str] = None,
) -> pd.DataFrame:
    """Assign each customer to a cohort based on their first transaction.

    Parameters
    ----------
    transactions : pd.DataFrame
        Transaction data with at least customer_id, date columns.
    dimension : CohortDimension
        How to define cohorts:
        - 'acquisition_month': calendar month of first transaction
        - 'first_product': product category of first purchase
        - 'first_channel': marketing channel of first conversion
    customer_id_column : str
        Name of the customer identifier column.
    date_column : str
        Name of the date column.
    product_column : str
        Name of the product column (used for 'first_product' dimension).
    channel_column : str, optional
        Name of the channel column (required for 'first_channel' dimension).

    Returns
    -------
    pd.DataFrame
        Customer-level DataFrame with columns:
        - customer_id
        - cohort: The assigned cohort label
        - first_transaction_date: Date of the customer's first transaction

    Raises
    ------
    ValueError
        If dimension is 'first_channel' but channel_column is not provided
        or not present in the data.
    """
    # TODO: Find first transaction per customer, extract cohort dimension
    raise NotImplementedError("assign_cohorts not yet implemented")


# ---------------------------------------------------------------------------
# Retention matrix
# ---------------------------------------------------------------------------


def build_retention_matrix(
    transactions: pd.DataFrame,
    cohort_assignments: pd.DataFrame,
    granularity: PeriodGranularity = "month",
    n_periods: int = 12,
    customer_id_column: str = "customer_id",
    date_column: str = "date",
) -> pd.DataFrame:
    """Generate a cohort retention matrix.

    Rows represent cohorts, columns represent periods since acquisition
    (period 0 = acquisition period). Cell values are the percentage of
    cohort members who were active in that period.

    Parameters
    ----------
    transactions : pd.DataFrame
        Transaction data.
    cohort_assignments : pd.DataFrame
        Output from assign_cohorts with customer_id, cohort, and
        first_transaction_date columns.
    granularity : PeriodGranularity
        Time period granularity: 'month' or 'week'.
    n_periods : int
        Maximum number of periods to track after acquisition.
    customer_id_column : str
        Name of the customer identifier column.
    date_column : str
        Name of the date column.

    Returns
    -------
    pd.DataFrame
        Retention matrix with cohort labels as index and period offsets
        (0 through n_periods) as columns. Values are retention percentages
        in [0, 100].

    Raises
    ------
    ValueError
        If any retention value exceeds 100% (mathematical inconsistency).
    """
    # TODO: Compute period offsets, pivot to retention matrix, validate <= 100%
    raise NotImplementedError("build_retention_matrix not yet implemented")


# ---------------------------------------------------------------------------
# Derived metrics
# ---------------------------------------------------------------------------


def compute_churn_rates(
    retention_matrix: pd.DataFrame,
) -> pd.DataFrame:
    """Compute period-over-period churn rates from a retention matrix.

    Churn rate for period N = 1 - (retention at N / retention at N-1).

    Parameters
    ----------
    retention_matrix : pd.DataFrame
        Cohort retention matrix from build_retention_matrix.

    Returns
    -------
    pd.DataFrame
        Churn rate matrix with the same shape as the retention matrix.
        Period 0 is NaN (no prior period). Values are in [0, 1].
    """
    # TODO: Compute period-over-period churn from retention deltas
    raise NotImplementedError("compute_churn_rates not yet implemented")


def compute_revenue_per_user(
    transactions: pd.DataFrame,
    cohort_assignments: pd.DataFrame,
    granularity: PeriodGranularity = "month",
    n_periods: int = 12,
    customer_id_column: str = "customer_id",
    date_column: str = "date",
    amount_column: str = "amount",
) -> pd.DataFrame:
    """Compute average revenue per user per period for each cohort.

    Parameters
    ----------
    transactions : pd.DataFrame
        Transaction data.
    cohort_assignments : pd.DataFrame
        Output from assign_cohorts.
    granularity : PeriodGranularity
        Time period granularity.
    n_periods : int
        Maximum periods to track.
    customer_id_column : str
        Name of the customer identifier column.
    date_column : str
        Name of the date column.
    amount_column : str
        Name of the transaction amount column.

    Returns
    -------
    pd.DataFrame
        Revenue-per-user matrix with cohort labels as index and period
        offsets as columns.
    """
    # TODO: Sum revenue per cohort per period, divide by cohort size
    raise NotImplementedError("compute_revenue_per_user not yet implemented")


def compute_ltv_trajectory(
    revenue_per_user: pd.DataFrame,
) -> pd.DataFrame:
    """Compute cumulative LTV trajectory from revenue-per-user data.

    Parameters
    ----------
    revenue_per_user : pd.DataFrame
        Revenue-per-user matrix from compute_revenue_per_user.

    Returns
    -------
    pd.DataFrame
        Cumulative revenue-per-user matrix (running sum across columns).
    """
    # TODO: Cumulative sum across period columns
    raise NotImplementedError("compute_ltv_trajectory not yet implemented")


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def save_cohort_results(
    retention_matrix: pd.DataFrame,
    churn_matrix: pd.DataFrame,
    revenue_per_user: pd.DataFrame,
    ltv_trajectory: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """Serialize all cohort analysis results to a JSON file.

    Parameters
    ----------
    retention_matrix : pd.DataFrame
        Cohort retention matrix.
    churn_matrix : pd.DataFrame
        Churn rate matrix.
    revenue_per_user : pd.DataFrame
        Revenue-per-user matrix.
    ltv_trajectory : pd.DataFrame
        Cumulative LTV trajectory matrix.
    output_path : str or Path
        Path to write the output JSON file.
    """
    # TODO: Convert DataFrames to nested dicts, write JSON
    raise NotImplementedError("save_cohort_results not yet implemented")


# ---------------------------------------------------------------------------
# Pipeline orchestration
# ---------------------------------------------------------------------------


def run_cohort_pipeline(
    transactions_path: str | Path,
    output_dir: str | Path,
    dimension: CohortDimension = "acquisition_month",
    granularity: PeriodGranularity = "month",
    n_periods: int = 12,
) -> dict[str, pd.DataFrame]:
    """Execute the full cohort retention analysis pipeline.

    Steps:
    1. Load transactions
    2. Assign cohorts
    3. Build retention matrix
    4. Compute churn rates
    5. Compute revenue per user
    6. Compute LTV trajectory
    7. Save all results

    Parameters
    ----------
    transactions_path : str or Path
        Path to the transactions CSV file.
    output_dir : str or Path
        Directory to write output files.
    dimension : CohortDimension
        Cohort definition dimension.
    granularity : PeriodGranularity
        Time period granularity.
    n_periods : int
        Maximum periods to track.

    Returns
    -------
    dict[str, pd.DataFrame]
        Keys: 'retention', 'churn', 'revenue_per_user', 'ltv_trajectory'.
    """
    # TODO: Orchestrate the full pipeline
    raise NotImplementedError("run_cohort_pipeline not yet implemented")
