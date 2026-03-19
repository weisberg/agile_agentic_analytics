"""
RFM Summary Generation from Raw Transaction Data.

Converts transaction-level data (customer_id, date, amount) into
Recency-Frequency-Monetary-Tenure summaries suitable for BG/NBD
and Gamma-Gamma model fitting.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


def load_transactions(
    filepath: str | Path,
    customer_col: str = "customer_id",
    date_col: str = "date",
    amount_col: str = "amount",
    date_format: Optional[str] = None,
) -> pd.DataFrame:
    """Load and parse raw transaction data from CSV.

    Parameters
    ----------
    filepath : str or Path
        Path to the transaction CSV file.
    customer_col : str
        Column name for customer identifier.
    date_col : str
        Column name for transaction date.
    amount_col : str
        Column name for transaction amount.
    date_format : str or None
        Explicit date format string. If None, pandas will infer the format.

    Returns
    -------
    pd.DataFrame
        Cleaned transaction DataFrame with standardized column names:
        ``customer_id``, ``date``, ``amount``.

    Raises
    ------
    FileNotFoundError
        If the transaction file does not exist.
    ValueError
        If required columns are missing from the file.
    """
    # TODO: load CSV, rename columns, parse dates, sort by date
    raise NotImplementedError


def validate_transactions(transactions: pd.DataFrame) -> dict[str, any]:
    """Run data quality checks on transaction data.

    Checks performed:
    - Duplicate transactions (same customer, date, amount)
    - Negative or zero amounts
    - Future dates beyond the observation period
    - Missing values in key columns

    Parameters
    ----------
    transactions : pd.DataFrame
        Transaction DataFrame with columns ``customer_id``, ``date``, ``amount``.

    Returns
    -------
    dict
        Data quality report with keys:
        - ``duplicate_count`` (int): number of exact duplicate rows
        - ``negative_amount_count`` (int): rows with amount <= 0
        - ``future_date_count`` (int): rows with dates in the future
        - ``missing_value_counts`` (dict[str, int]): missing values per column
        - ``total_transactions`` (int): total row count
        - ``unique_customers`` (int): distinct customer count
        - ``date_range`` (tuple[str, str]): earliest and latest dates
        - ``is_clean`` (bool): True if no issues found
    """
    # TODO: implement all quality checks and return summary dict
    raise NotImplementedError


def build_rfm_summary(
    transactions: pd.DataFrame,
    observation_end: Optional[str] = None,
    time_unit: str = "D",
    monetary_repeat_only: bool = True,
) -> pd.DataFrame:
    """Generate RFM summary from transaction-level data.

    Computes per-customer:
    - **frequency**: count of repeat purchases (excludes first)
    - **recency**: time from first purchase to last purchase
    - **T**: time from first purchase to observation end
    - **monetary_value**: mean transaction value (repeat purchases only by default)

    Parameters
    ----------
    transactions : pd.DataFrame
        Cleaned transaction data with ``customer_id``, ``date``, ``amount``.
    observation_end : str or None
        End of the observation period as an ISO date string.
        Defaults to the maximum transaction date in the data.
    time_unit : str
        Pandas time unit for recency and T calculation.
        ``"D"`` for days (default), ``"W"`` for weeks.
    monetary_repeat_only : bool
        If True (default), compute monetary value from repeat purchases only,
        as required by the Gamma-Gamma model.

    Returns
    -------
    pd.DataFrame
        RFM summary with columns: ``customer_id``, ``frequency``, ``recency``,
        ``T``, ``monetary_value``. One row per customer. Customers with
        frequency == 0 have monetary_value = NaN.
    """
    # TODO: group by customer, compute frequency/recency/T/monetary
    raise NotImplementedError


def save_rfm_summary(
    rfm: pd.DataFrame,
    output_path: str | Path = "workspace/analysis/rfm_summary.csv",
) -> Path:
    """Save RFM summary to CSV.

    Parameters
    ----------
    rfm : pd.DataFrame
        RFM summary DataFrame.
    output_path : str or Path
        Destination file path.

    Returns
    -------
    Path
        Resolved path to the saved file.
    """
    # TODO: ensure output directory exists, write CSV
    raise NotImplementedError


def print_rfm_diagnostics(rfm: pd.DataFrame) -> None:
    """Print summary statistics of the RFM table for diagnostic purposes.

    Reports:
    - Total customers and repeat-purchaser count
    - Frequency distribution (mean, median, max)
    - Recency distribution
    - Monetary value distribution (repeat purchasers only)
    - Correlation between frequency and monetary value (Gamma-Gamma check)

    Parameters
    ----------
    rfm : pd.DataFrame
        RFM summary DataFrame.
    """
    # TODO: compute and print diagnostics
    raise NotImplementedError


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate RFM summary from transactions")
    parser.add_argument("--input", required=True, help="Path to transactions CSV")
    parser.add_argument("--output", default="workspace/analysis/rfm_summary.csv")
    parser.add_argument("--observation-end", default=None, help="ISO date for observation end")
    parser.add_argument("--time-unit", default="D", choices=["D", "W"])
    args = parser.parse_args()

    txns = load_transactions(args.input)
    quality = validate_transactions(txns)
    print(f"Data quality report: {quality}")

    rfm = build_rfm_summary(txns, observation_end=args.observation_end, time_unit=args.time_unit)
    print_rfm_diagnostics(rfm)
    save_rfm_summary(rfm, args.output)
