"""Sample Ratio Mismatch (SRM) detection for A/B experiments.

Detects imbalances in variant assignment that indicate data quality issues
such as bot contamination, lossy logging, or flawed randomization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import stats


@dataclass
class SRMResult:
    """Result of a Sample Ratio Mismatch check.

    Attributes:
        observed_counts: Dict mapping variant name to observed user count.
        expected_ratios: Dict mapping variant name to expected traffic fraction.
        expected_counts: Dict mapping variant name to expected user count.
        chi_squared_statistic: Chi-squared goodness-of-fit test statistic.
        p_value: P-value from the chi-squared test.
        has_mismatch: True if p_value < threshold (indicates SRM).
        threshold: P-value threshold used for detection (default 0.001).
        diagnostic_breakdowns: Optional per-dimension breakdowns.
    """

    observed_counts: Dict[str, int]
    expected_ratios: Dict[str, float]
    expected_counts: Dict[str, float]
    chi_squared_statistic: float
    p_value: float
    has_mismatch: bool
    threshold: float
    diagnostic_breakdowns: Optional[Dict[str, "SRMResult"]]


def run_srm_check(
    observed_counts: Dict[str, int],
    expected_ratios: Optional[Dict[str, float]] = None,
    threshold: float = 0.001,
) -> SRMResult:
    """Run a chi-squared goodness-of-fit test for Sample Ratio Mismatch.

    Tests whether the observed variant assignment counts match the expected
    traffic allocation ratios.

    Args:
        observed_counts: Dict mapping variant name to observed count.
            Example: {"control": 10050, "treatment": 9800}.
        expected_ratios: Dict mapping variant name to expected fraction.
            Example: {"control": 0.5, "treatment": 0.5}.
            If None, assumes equal allocation across all variants.
        threshold: P-value threshold below which to flag SRM. Default 0.001.

    Returns:
        SRMResult with test statistics and mismatch determination.

    Raises:
        ValueError: If observed_counts is empty or ratios don't sum to ~1.0.
    """
    # TODO: Validate inputs
    # TODO: Default to equal ratios if not provided
    # TODO: Compute total N and expected counts per variant
    # TODO: Run chi-squared goodness-of-fit: scipy.stats.chisquare(observed, expected)
    # TODO: Determine has_mismatch = (p_value < threshold)
    # TODO: Return SRMResult
    raise NotImplementedError("SRM check not yet implemented")


def run_srm_diagnostic_breakdown(
    user_data: Dict[str, np.ndarray],
    variant_assignments: np.ndarray,
    variant_names: List[str],
    breakdown_dimensions: List[str],
    expected_ratios: Optional[Dict[str, float]] = None,
    threshold: float = 0.001,
) -> Dict[str, Dict[str, SRMResult]]:
    """Run SRM checks broken down by diagnostic dimensions.

    When SRM is detected, this function identifies which sub-populations
    are responsible by running per-segment SRM checks.

    Args:
        user_data: Dict mapping dimension name to array of dimension values
            (e.g., {"platform": ["ios", "android", ...], "date": [...]}).
        variant_assignments: Array of variant assignment labels per user.
        variant_names: List of variant names in the experiment.
        breakdown_dimensions: Dimensions to slice by (e.g., ["platform", "date"]).
        expected_ratios: Expected traffic allocation. Default equal split.
        threshold: SRM detection threshold. Default 0.001.

    Returns:
        Nested dict mapping dimension_name -> dimension_value -> SRMResult.
        For example: {"platform": {"ios": SRMResult(...), "android": SRMResult(...)}}
    """
    # TODO: Iterate over each breakdown dimension
    # TODO: For each unique value in the dimension, filter users
    # TODO: Count variants in the filtered subset
    # TODO: Run run_srm_check on the subset counts
    # TODO: Collect results keyed by dimension and value
    # TODO: Return nested dict of SRMResult
    raise NotImplementedError("SRM diagnostic breakdown not yet implemented")


def detect_temporal_srm(
    timestamps: np.ndarray,
    variant_assignments: np.ndarray,
    variant_names: List[str],
    expected_ratios: Optional[Dict[str, float]] = None,
    time_granularity: str = "day",
    threshold: float = 0.001,
) -> List[Tuple[str, SRMResult]]:
    """Detect SRM patterns over time to identify when imbalance began.

    Useful for diagnosing whether SRM was present from the start (suggesting
    a randomization bug) or appeared mid-experiment (suggesting a logging
    or filtering issue).

    Args:
        timestamps: Array of timestamps (one per user).
        variant_assignments: Array of variant labels (one per user).
        variant_names: List of variant names.
        expected_ratios: Expected traffic allocation. Default equal split.
        time_granularity: Time bucket granularity ("day" or "hour"). Default "day".
        threshold: SRM detection threshold. Default 0.001.

    Returns:
        List of (time_bucket_label, SRMResult) tuples in chronological order.
    """
    # TODO: Bucket timestamps by granularity (day or hour)
    # TODO: For each time bucket, count variant assignments
    # TODO: Run run_srm_check for each bucket
    # TODO: Return list of (label, SRMResult) tuples
    raise NotImplementedError("Temporal SRM detection not yet implemented")


def generate_srm_report(
    srm_result: SRMResult,
    diagnostic_breakdowns: Optional[Dict[str, Dict[str, SRMResult]]] = None,
    temporal_results: Optional[List[Tuple[str, SRMResult]]] = None,
) -> Dict[str, object]:
    """Generate a structured SRM diagnostic report.

    Args:
        srm_result: Overall SRM check result.
        diagnostic_breakdowns: Per-dimension breakdown results. Default None.
        temporal_results: Per-time-bucket results. Default None.

    Returns:
        Dict with keys: summary, overall_result, breakdowns, temporal_pattern,
        recommendations. Suitable for serialization to JSON.
    """
    # TODO: Build summary string with observed vs expected counts
    # TODO: If SRM detected, include severity assessment
    # TODO: Include per-dimension breakdowns highlighting mismatched segments
    # TODO: Include temporal pattern showing when mismatch started
    # TODO: Generate recommendations (e.g., "investigate iOS logging pipeline")
    # TODO: Return structured report dict
    raise NotImplementedError("SRM report generation not yet implemented")
