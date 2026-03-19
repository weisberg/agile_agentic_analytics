"""Frequentist hypothesis tests for A/B experiments.

Provides z-test, t-test, chi-squared, and proportion tests with
Benjamini-Hochberg correction for multiple comparisons.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import stats


class TestType(Enum):
    """Supported frequentist test types."""

    Z_TEST = "z_test"
    T_TEST = "t_test"
    WELCH_T_TEST = "welch_t_test"
    CHI_SQUARED = "chi_squared"
    PROPORTION_Z = "proportion_z"


@dataclass
class FrequentistResult:
    """Result of a single frequentist hypothesis test.

    Attributes:
        test_type: The statistical test used.
        metric_name: Name of the metric tested.
        control_mean: Mean of the control group.
        treatment_mean: Mean of the treatment group.
        effect_size_absolute: Absolute difference (treatment - control).
        effect_size_relative: Relative difference as fraction of control.
        confidence_interval: Tuple of (lower, upper) bounds.
        p_value: Raw (unadjusted) p-value.
        adjusted_p_value: P-value after BH correction (None if not applied).
        test_statistic: Value of the test statistic.
        degrees_of_freedom: Degrees of freedom (None for z-test).
        is_significant: Whether result is significant after correction.
        alpha: Significance level used.
    """

    test_type: TestType
    metric_name: str
    control_mean: float
    treatment_mean: float
    effect_size_absolute: float
    effect_size_relative: float
    confidence_interval: Tuple[float, float]
    p_value: float
    adjusted_p_value: Optional[float]
    test_statistic: float
    degrees_of_freedom: Optional[float]
    is_significant: bool
    alpha: float


def run_proportion_z_test(
    control_successes: int,
    control_total: int,
    treatment_successes: int,
    treatment_total: int,
    alpha: float = 0.05,
    two_sided: bool = True,
    metric_name: str = "conversion_rate",
) -> FrequentistResult:
    """Run a two-sample z-test for proportions.

    Tests whether the treatment conversion rate differs from control.

    Args:
        control_successes: Number of conversions in the control group.
        control_total: Total observations in the control group.
        treatment_successes: Number of conversions in the treatment group.
        treatment_total: Total observations in the treatment group.
        alpha: Significance level. Default 0.05.
        two_sided: Whether to use a two-sided test. Default True.
        metric_name: Name for this metric in results. Default "conversion_rate".

    Returns:
        FrequentistResult with test outcome.

    Raises:
        ValueError: If counts are negative or totals are zero.
    """
    # TODO: Validate inputs (non-negative counts, totals > 0)
    # TODO: Compute proportions p_c and p_t
    # TODO: Compute pooled proportion p_pool
    # TODO: Compute standard error: SE = sqrt(p_pool*(1-p_pool)*(1/n_c + 1/n_t))
    # TODO: Compute z-statistic: z = (p_t - p_c) / SE
    # TODO: Compute p-value from normal distribution
    # TODO: Compute confidence interval for the difference
    # TODO: Return FrequentistResult
    raise NotImplementedError("Proportion z-test not yet implemented")


def run_t_test(
    control_values: np.ndarray,
    treatment_values: np.ndarray,
    alpha: float = 0.05,
    two_sided: bool = True,
    equal_variance: bool = False,
    metric_name: str = "metric",
) -> FrequentistResult:
    """Run a two-sample t-test (or Welch's t-test) on continuous metrics.

    Args:
        control_values: Array of metric values for the control group.
        treatment_values: Array of metric values for the treatment group.
        alpha: Significance level. Default 0.05.
        two_sided: Whether to use a two-sided test. Default True.
        equal_variance: If True, use Student's t-test (pooled variance).
            If False (default), use Welch's t-test.
        metric_name: Name for this metric in results. Default "metric".

    Returns:
        FrequentistResult with test outcome.

    Raises:
        ValueError: If input arrays are empty.
    """
    # TODO: Validate inputs (non-empty arrays)
    # TODO: Compute means and standard deviations
    # TODO: Use scipy.stats.ttest_ind with equal_var parameter
    # TODO: Compute effect size (absolute and relative)
    # TODO: Compute confidence interval for the mean difference
    # TODO: Return FrequentistResult
    raise NotImplementedError("T-test not yet implemented")


def run_chi_squared_test(
    observed_table: np.ndarray,
    alpha: float = 0.05,
    metric_name: str = "categorical_metric",
) -> FrequentistResult:
    """Run a chi-squared test of independence on a contingency table.

    Args:
        observed_table: 2D contingency table of shape (num_variants, num_categories).
            Rows are variants, columns are outcome categories.
        alpha: Significance level. Default 0.05.
        metric_name: Name for this metric in results. Default "categorical_metric".

    Returns:
        FrequentistResult with test outcome.

    Raises:
        ValueError: If table has fewer than 2 rows or 2 columns.
    """
    # TODO: Validate table dimensions
    # TODO: Use scipy.stats.chi2_contingency
    # TODO: Extract chi2 statistic, p-value, degrees of freedom
    # TODO: Compute Cramer's V as effect size
    # TODO: Return FrequentistResult
    raise NotImplementedError("Chi-squared test not yet implemented")


def apply_bh_correction(
    results: List[FrequentistResult],
    alpha: float = 0.05,
) -> List[FrequentistResult]:
    """Apply Benjamini-Hochberg FDR correction to multiple test results.

    Adjusts p-values to control the false discovery rate when testing
    multiple metrics simultaneously.

    Args:
        results: List of FrequentistResult objects from individual tests.
        alpha: Family-wise significance level. Default 0.05.

    Returns:
        Updated list of FrequentistResult objects with adjusted_p_value and
        is_significant fields populated.
    """
    # TODO: Extract raw p-values from results
    # TODO: Sort p-values and compute BH adjusted p-values:
    #   adjusted_p[i] = min(p[i] * m / rank[i], 1.0)
    #   Enforce monotonicity: adjusted_p[i] = min(adjusted_p[i], adjusted_p[i+1])
    # TODO: Update each result with adjusted p-value and significance flag
    raise NotImplementedError("BH correction not yet implemented")


def run_experiment_analysis(
    experiment_data: Dict[str, Dict[str, np.ndarray]],
    metric_types: Dict[str, str],
    alpha: float = 0.05,
    two_sided: bool = True,
    apply_correction: bool = True,
) -> List[FrequentistResult]:
    """Run the full frequentist analysis pipeline on an experiment dataset.

    Automatically selects the appropriate test for each metric type and
    applies BH correction across all metrics.

    Args:
        experiment_data: Nested dict mapping metric_name -> variant_name -> values.
            Example: {"conversion": {"control": array([0,1,...]), "treatment": array([0,1,...])}}
        metric_types: Dict mapping metric_name to type ("proportion" or "continuous").
        alpha: Significance level. Default 0.05.
        two_sided: Whether to use two-sided tests. Default True.
        apply_correction: Whether to apply BH correction. Default True.

    Returns:
        List of FrequentistResult objects, one per metric.
    """
    # TODO: Iterate over metrics
    # TODO: Select test type based on metric_types mapping
    # TODO: For proportion metrics, compute successes and totals from binary arrays
    # TODO: For continuous metrics, run Welch's t-test
    # TODO: Collect all results
    # TODO: Apply BH correction if requested
    # TODO: Return results list
    raise NotImplementedError("Full experiment analysis pipeline not yet implemented")
