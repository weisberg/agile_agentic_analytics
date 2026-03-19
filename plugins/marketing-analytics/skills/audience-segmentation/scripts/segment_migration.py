"""Segment Migration Tracking Module

Computes period-over-period segment transition matrices showing how
customers move between segments across consecutive analysis periods.
Validates that all customers are accounted for (rows sum to 100%)
and flags notable migrations.

Usage:
    from scripts.segment_migration import (
        build_transition_matrix,
        detect_notable_migrations,
        run_migration_pipeline,
    )

Dependencies:
    pandas, numpy
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default configuration
# ---------------------------------------------------------------------------

# Migrations considered notable for alerting purposes
NOTABLE_MIGRATIONS: list[dict[str, str]] = [
    {"from": "Champions", "to": "At-Risk"},
    {"from": "Champions", "to": "Hibernating"},
    {"from": "Champions", "to": "Lost"},
    {"from": "Loyal Customers", "to": "At-Risk"},
    {"from": "Loyal Customers", "to": "Hibernating"},
    {"from": "Hibernating", "to": "Loyal Customers"},
    {"from": "Hibernating", "to": "Champions"},
    {"from": "At-Risk", "to": "Champions"},
    {"from": "Lost", "to": "Potential Loyalists"},
]

ROW_SUM_TOLERANCE: float = 0.01  # Acceptable deviation from 100%


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def load_segment_assignments(
    filepath: str | Path,
    customer_id_column: str = "customer_id",
    segment_column: str = "segment",
    period_column: str = "period",
) -> pd.DataFrame:
    """Load segment assignment data for multiple periods.

    Parameters
    ----------
    filepath : str or Path
        Path to a CSV or JSON file containing customer segment assignments
        with a period identifier column.
    customer_id_column : str
        Name of the customer identifier column.
    segment_column : str
        Name of the segment label column.
    period_column : str
        Name of the period identifier column (e.g., '2026-01', '2026-02').

    Returns
    -------
    pd.DataFrame
        Segment assignments with customer_id, segment, and period columns.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If required columns are missing or fewer than 2 periods are present.
    """
    # TODO: Load file, validate columns, ensure at least 2 periods
    raise NotImplementedError("load_segment_assignments not yet implemented")


def build_transition_matrix(
    assignments_period_a: pd.DataFrame,
    assignments_period_b: pd.DataFrame,
    customer_id_column: str = "customer_id",
    segment_column: str = "segment",
    normalize: bool = True,
) -> pd.DataFrame:
    """Build a segment transition matrix between two consecutive periods.

    Parameters
    ----------
    assignments_period_a : pd.DataFrame
        Segment assignments for the earlier period. Must contain
        customer_id and segment columns.
    assignments_period_b : pd.DataFrame
        Segment assignments for the later period. Must contain
        customer_id and segment columns.
    customer_id_column : str
        Name of the customer identifier column.
    segment_column : str
        Name of the segment label column.
    normalize : bool
        If True, express values as percentages (rows sum to 100).
        If False, express as raw counts.

    Returns
    -------
    pd.DataFrame
        Transition matrix where rows represent the segment in period A
        and columns represent the segment in period B. If normalized,
        each row sums to approximately 100%.

    Raises
    ------
    ValueError
        If normalized and any row sum deviates from 100% beyond tolerance.
    """
    # TODO: Merge periods on customer_id, crosstab, optionally normalize
    raise NotImplementedError("build_transition_matrix not yet implemented")


def build_multi_period_transitions(
    segment_assignments: pd.DataFrame,
    customer_id_column: str = "customer_id",
    segment_column: str = "segment",
    period_column: str = "period",
    normalize: bool = True,
) -> dict[str, pd.DataFrame]:
    """Build transition matrices for all consecutive period pairs.

    Parameters
    ----------
    segment_assignments : pd.DataFrame
        Segment assignments spanning multiple periods.
    customer_id_column : str
        Name of the customer identifier column.
    segment_column : str
        Name of the segment label column.
    period_column : str
        Name of the period identifier column.
    normalize : bool
        If True, express values as percentages.

    Returns
    -------
    dict[str, pd.DataFrame]
        Mapping from period-pair label (e.g., '2026-01 -> 2026-02') to
        the corresponding transition matrix.
    """
    # TODO: Sort periods, iterate consecutive pairs, build matrices
    raise NotImplementedError("build_multi_period_transitions not yet implemented")


def validate_transition_matrix(
    matrix: pd.DataFrame,
    tolerance: float = ROW_SUM_TOLERANCE,
) -> bool:
    """Validate that a normalized transition matrix rows sum to ~100%.

    Parameters
    ----------
    matrix : pd.DataFrame
        Normalized transition matrix.
    tolerance : float
        Acceptable absolute deviation from 100% per row.

    Returns
    -------
    bool
        True if all rows are within tolerance, False otherwise.

    Raises
    ------
    ValueError
        If any row sum exceeds the tolerance threshold, with details
        about which rows failed.
    """
    # TODO: Check row sums, raise with details on failures
    raise NotImplementedError("validate_transition_matrix not yet implemented")


def detect_notable_migrations(
    matrix: pd.DataFrame,
    notable_pairs: Optional[list[dict[str, str]]] = None,
    threshold_pct: float = 5.0,
) -> list[dict[str, Any]]:
    """Identify significant customer migrations between segments.

    Parameters
    ----------
    matrix : pd.DataFrame
        Normalized transition matrix (percentages).
    notable_pairs : list of dict, optional
        List of from/to segment pairs to monitor. Each dict has keys
        'from' and 'to'. Defaults to NOTABLE_MIGRATIONS.
    threshold_pct : float
        Minimum percentage to flag a migration as significant.

    Returns
    -------
    list of dict
        Each dict contains:
        - 'from_segment' (str): Origin segment
        - 'to_segment' (str): Destination segment
        - 'percentage' (float): Percentage of origin segment that migrated
        - 'severity' (str): 'high' if > 10%, 'medium' if > 5%, 'low' otherwise
    """
    # TODO: Check each notable pair in the matrix, flag those above threshold
    raise NotImplementedError("detect_notable_migrations not yet implemented")


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def save_migration_results(
    transitions: dict[str, pd.DataFrame],
    notable_migrations: dict[str, list[dict[str, Any]]],
    output_path: str | Path,
) -> None:
    """Serialize migration analysis results to JSON.

    Parameters
    ----------
    transitions : dict[str, pd.DataFrame]
        Mapping of period-pair labels to transition matrices.
    notable_migrations : dict[str, list[dict]]
        Mapping of period-pair labels to lists of notable migration events.
    output_path : str or Path
        Path to write the output JSON file.
    """
    # TODO: Convert DataFrames to nested dicts, combine with notable migrations, write
    raise NotImplementedError("save_migration_results not yet implemented")


# ---------------------------------------------------------------------------
# Pipeline orchestration
# ---------------------------------------------------------------------------


def run_migration_pipeline(
    segment_data_path: str | Path,
    output_dir: str | Path,
    normalize: bool = True,
    threshold_pct: float = 5.0,
) -> dict[str, Any]:
    """Execute the full segment migration tracking pipeline.

    Steps:
    1. Load segment assignments for multiple periods
    2. Build transition matrices for all consecutive period pairs
    3. Validate each matrix (rows sum to 100%)
    4. Detect notable migrations
    5. Save results

    Parameters
    ----------
    segment_data_path : str or Path
        Path to the multi-period segment assignments file.
    output_dir : str or Path
        Directory to write output files.
    normalize : bool
        Whether to normalize transition matrices to percentages.
    threshold_pct : float
        Minimum percentage to flag a migration as significant.

    Returns
    -------
    dict[str, Any]
        Pipeline results including transition matrices and notable migrations.
    """
    # TODO: Orchestrate the full pipeline
    raise NotImplementedError("run_migration_pipeline not yet implemented")
