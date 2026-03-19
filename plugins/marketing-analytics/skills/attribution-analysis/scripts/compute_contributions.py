"""Channel-level contribution decomposition from a fitted MMM.

This script decomposes the total observed outcome into contributions from each
media channel, the baseline (intercept), control variables, and noise. It produces
posterior distributions of contributions with credible intervals.

Usage:
    python compute_contributions.py
    python compute_contributions.py --credible-interval 0.90
    python compute_contributions.py --output workspace/analysis/mmm_channel_contributions.json

Input files:
    workspace/models/mmm_fitted.nc — Fitted MMM model with posterior trace

Output files:
    workspace/analysis/mmm_channel_contributions.json — Channel contributions with CIs
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Optional

import arviz as az
import numpy as np
import pandas as pd
from pymc_marketing.mmm import MMM

logger = logging.getLogger(__name__)

WORKSPACE_DIR = Path("workspace")
MODELS_DIR = WORKSPACE_DIR / "models"
ANALYSIS_DIR = WORKSPACE_DIR / "analysis"


def load_fitted_model(models_dir: Path) -> MMM:
    """Load a previously fitted MMM from disk.

    Args:
        models_dir: Path to the models directory containing mmm_fitted.nc.

    Returns:
        Fitted MMM instance with posterior trace loaded.

    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    # TODO: Load model via MMM.load()
    # TODO: Verify the model has a fit_result attribute
    raise NotImplementedError("Model loading not yet implemented")


def compute_channel_contributions(
    mmm: MMM,
    credible_interval: float = 0.90,
) -> dict[str, dict[str, Any]]:
    """Compute posterior channel contributions with credible intervals.

    Uses PyMC-Marketing's built-in contribution decomposition to separate
    the outcome into components attributable to each media channel.

    Args:
        mmm: Fitted MMM instance.
        credible_interval: Width of the credible interval (e.g., 0.90 for 90% CI).

    Returns:
        Dictionary mapping channel names to:
        {
            "mean_contribution": float,
            "median_contribution": float,
            "ci_lower": float,
            "ci_upper": float,
            "share_of_total_mean": float,
            "time_series": {
                "dates": list[str],
                "mean": list[float],
                "ci_lower": list[float],
                "ci_upper": list[float],
            }
        }
    """
    # TODO: Call mmm.compute_channel_contribution_original_scale()
    # TODO: Compute mean, median, and CI across posterior samples
    # TODO: Compute share of total for each channel
    # TODO: Extract time series of contributions per channel
    raise NotImplementedError("Channel contribution computation not yet implemented")


def compute_baseline_contribution(
    mmm: MMM,
    credible_interval: float = 0.90,
) -> dict[str, Any]:
    """Compute the baseline (intercept + controls) contribution.

    The baseline represents the outcome that would occur with zero media spend,
    driven by seasonality, trend, and other non-media factors.

    Args:
        mmm: Fitted MMM instance.
        credible_interval: Width of the credible interval.

    Returns:
        Dictionary with:
        {
            "mean_contribution": float,
            "ci_lower": float,
            "ci_upper": float,
            "share_of_total_mean": float,
            "components": {
                "intercept": float,
                "seasonality": float,
                "trend": float,
                "other_controls": float,
            }
        }
    """
    # TODO: Extract intercept and control contributions from the posterior
    # TODO: Separate into intercept, seasonality, trend, and other controls
    # TODO: Compute credible intervals
    raise NotImplementedError("Baseline contribution computation not yet implemented")


def validate_decomposition(
    channel_contributions: dict[str, dict[str, Any]],
    baseline_contribution: dict[str, Any],
    observed_total: float,
    tolerance: float = 0.02,
) -> dict[str, Any]:
    """Validate that contributions sum to the observed total within tolerance.

    This is a critical sanity check: the decomposition should be exhaustive,
    meaning all components sum to the observed outcome.

    Args:
        channel_contributions: Per-channel contribution results.
        baseline_contribution: Baseline contribution results.
        observed_total: Total observed outcome to compare against.
        tolerance: Maximum acceptable relative difference (default 2%).

    Returns:
        Dictionary with:
        {
            "total_contributions": float,
            "observed_total": float,
            "relative_difference": float,
            "within_tolerance": bool,
        }
    """
    # TODO: Sum all channel mean contributions + baseline mean contribution
    # TODO: Compare to observed total
    # TODO: Compute relative difference
    # TODO: Return validation result
    raise NotImplementedError("Decomposition validation not yet implemented")


def compute_contribution_summary(
    channel_contributions: dict[str, dict[str, Any]],
    baseline_contribution: dict[str, Any],
) -> pd.DataFrame:
    """Create a summary table of all contributions.

    Produces a DataFrame suitable for waterfall chart generation, with
    rows for each channel, the baseline, and the total.

    Args:
        channel_contributions: Per-channel contribution results.
        baseline_contribution: Baseline contribution results.

    Returns:
        DataFrame with columns: component, contribution_mean, ci_lower,
        ci_upper, share_pct, cumulative.
    """
    # TODO: Combine channel and baseline contributions
    # TODO: Sort by contribution size (descending)
    # TODO: Add total row
    # TODO: Compute cumulative sums for waterfall chart
    raise NotImplementedError("Summary table creation not yet implemented")


def compute_roi_by_channel(
    channel_contributions: dict[str, dict[str, Any]],
    channel_spend: dict[str, float],
    credible_interval: float = 0.90,
) -> dict[str, dict[str, float]]:
    """Compute ROI (return on investment) for each channel.

    ROI = (contribution - spend) / spend, expressed as a percentage.
    Also computes ROAS = contribution / spend.

    Args:
        channel_contributions: Per-channel contribution results (in revenue units).
        channel_spend: Total spend per channel during the model period.
        credible_interval: Width of the credible interval.

    Returns:
        Dictionary mapping channel names to:
        {
            "total_spend": float,
            "roas_mean": float,
            "roas_ci_lower": float,
            "roas_ci_upper": float,
            "roi_pct_mean": float,
            "roi_pct_ci_lower": float,
            "roi_pct_ci_upper": float,
        }
    """
    # TODO: Divide contribution by spend for each channel
    # TODO: Propagate uncertainty from contribution CIs
    # TODO: Compute ROI percentage
    raise NotImplementedError("ROI computation not yet implemented")


def save_contributions(
    channel_contributions: dict[str, dict[str, Any]],
    baseline_contribution: dict[str, Any],
    validation: dict[str, Any],
    roi_by_channel: dict[str, dict[str, float]],
    analysis_dir: Path,
) -> None:
    """Save contribution decomposition results to JSON.

    Args:
        channel_contributions: Per-channel contribution results.
        baseline_contribution: Baseline contribution results.
        validation: Decomposition validation results.
        roi_by_channel: Per-channel ROI/ROAS metrics.
        analysis_dir: Path to the analysis output directory.
    """
    # TODO: Combine all results into output dictionary
    # TODO: Add metadata (timestamp, model version, credible interval width)
    # TODO: Write to mmm_channel_contributions.json
    raise NotImplementedError("Contribution saving not yet implemented")


def main() -> None:
    """Main entry point for contribution decomposition."""
    parser = argparse.ArgumentParser(description="Compute MMM channel contributions")
    parser.add_argument("--credible-interval", type=float, default=0.90, help="Credible interval width (default 0.90)")
    parser.add_argument("--output", type=str, default=None, help="Output file path (default: workspace/analysis/mmm_channel_contributions.json)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # TODO: Implement the main contribution decomposition pipeline
    # 1. Load fitted model
    # 2. Compute channel contributions
    # 3. Compute baseline contribution
    # 4. Validate decomposition sums to observed total
    # 5. Compute ROI/ROAS by channel
    # 6. Save results
    raise NotImplementedError("Main contribution pipeline not yet implemented")


if __name__ == "__main__":
    main()
