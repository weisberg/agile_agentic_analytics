"""
Holdout Period Prediction Accuracy Assessment for CLV Models.

Implements temporal holdout validation: fit models on a calibration period,
predict into the holdout period, and compare to actual observations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Optional

import pandas as pd


def temporal_split(
    transactions: pd.DataFrame,
    calibration_end: str,
    holdout_end: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split transaction data into calibration and holdout periods.

    Parameters
    ----------
    transactions : pd.DataFrame
        Full transaction data with ``customer_id``, ``date``, ``amount``.
    calibration_end : str
        ISO date string for the end of the calibration period.
        Transactions on or before this date go to calibration.
    holdout_end : str or None
        ISO date string for the end of the holdout period.
        If None, all transactions after calibration_end are included.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        (calibration_transactions, holdout_transactions)
    """
    # TODO: parse dates, split, validate both sets are non-empty
    raise NotImplementedError


def compute_holdout_actuals(
    holdout_transactions: pd.DataFrame,
    calibration_customers: pd.DataFrame,
) -> pd.DataFrame:
    """Compute actual transaction counts and monetary values in the holdout period.

    Parameters
    ----------
    holdout_transactions : pd.DataFrame
        Transactions occurring in the holdout period.
    calibration_customers : pd.DataFrame
        RFM summary from the calibration period (defines the customer universe).

    Returns
    -------
    pd.DataFrame
        Per-customer holdout actuals with columns: ``customer_id``,
        ``actual_transactions``, ``actual_monetary_value``.
        Customers with no holdout transactions get 0.
    """
    # TODO: count holdout transactions per customer, fill zeros for inactive
    raise NotImplementedError


def evaluate_transaction_predictions(
    predictions: pd.DataFrame,
    actuals: pd.DataFrame,
    prediction_col: str = "expected_transactions",
    actual_col: str = "actual_transactions",
) -> dict[str, float]:
    """Evaluate predicted vs. actual transaction counts.

    Parameters
    ----------
    predictions : pd.DataFrame
        Predicted transactions with ``customer_id`` and ``prediction_col``.
    actuals : pd.DataFrame
        Actual holdout transactions with ``customer_id`` and ``actual_col``.
    prediction_col : str
        Column name for predicted values.
    actual_col : str
        Column name for actual values.

    Returns
    -------
    dict
        Metrics:
        - ``mae`` (float): mean absolute error
        - ``rmse`` (float): root mean squared error
        - ``calibration_ratio`` (float): sum(predicted) / sum(actual)
        - ``correlation`` (float): Pearson correlation between predicted and actual
        - ``n_customers`` (int): number of customers evaluated
    """
    # TODO: merge on customer_id, compute MAE, RMSE, calibration ratio
    raise NotImplementedError


def evaluate_probability_alive(
    prob_alive: pd.DataFrame,
    holdout_transactions: pd.DataFrame,
    n_bins: int = 10,
) -> pd.DataFrame:
    """Assess calibration of probability-alive predictions.

    Bins customers by predicted probability-alive and compares to the
    observed fraction who made at least one purchase in the holdout period.

    Parameters
    ----------
    prob_alive : pd.DataFrame
        Predictions with ``customer_id`` and ``prob_alive``.
    holdout_transactions : pd.DataFrame
        Holdout period transactions.
    n_bins : int
        Number of bins for calibration assessment.

    Returns
    -------
    pd.DataFrame
        Calibration table with columns: ``bin_midpoint``, ``predicted_alive_rate``,
        ``observed_repurchase_rate``, ``n_customers``.
    """
    # TODO: bin by prob_alive, compute observed repurchase rate per bin
    raise NotImplementedError


def compare_mle_vs_bayesian(
    mle_predictions: pd.DataFrame,
    bayesian_predictions: pd.DataFrame,
    actuals: pd.DataFrame,
) -> dict[str, Any]:
    """Compare MLE and Bayesian model predictions on holdout data.

    Parameters
    ----------
    mle_predictions : pd.DataFrame
        MLE-based predictions with confidence intervals.
    bayesian_predictions : pd.DataFrame
        Bayesian predictions with credible intervals.
    actuals : pd.DataFrame
        Holdout period actuals.

    Returns
    -------
    dict
        Comparison metrics:
        - ``mle_mae`` (float): MAE of MLE predictions
        - ``bayesian_mae`` (float): MAE of Bayesian predictions
        - ``mle_mean_interval_width`` (float): average CI width for MLE
        - ``bayesian_mean_interval_width`` (float): average CI width for Bayesian
        - ``bayesian_narrower`` (bool): True if Bayesian intervals are tighter
        - ``mle_coverage`` (float): fraction of actuals within MLE CIs
        - ``bayesian_coverage`` (float): fraction of actuals within Bayesian CIs
    """
    # TODO: compute MAE for both, interval widths, coverage rates
    raise NotImplementedError


def generate_diagnostic_plots(
    predictions: pd.DataFrame,
    actuals: pd.DataFrame,
    prob_alive_calibration: pd.DataFrame,
    output_path: str | Path = "workspace/reports/clv_validation.html",
) -> Path:
    """Generate validation diagnostic plots as an HTML report.

    Includes:
    - Predicted vs. actual transaction scatter plot
    - Cumulative tracking plot (predicted vs. actual over time)
    - Probability-alive calibration chart
    - Residual distribution histogram

    Parameters
    ----------
    predictions : pd.DataFrame
        Customer-level predictions.
    actuals : pd.DataFrame
        Holdout actuals.
    prob_alive_calibration : pd.DataFrame
        Calibration table from ``evaluate_probability_alive``.
    output_path : str or Path
        Path for the HTML report file.

    Returns
    -------
    Path
        Path to the generated HTML report.
    """
    # TODO: create plots with matplotlib/plotly, render to HTML
    raise NotImplementedError


def run_validation_pipeline(
    transactions_path: str | Path,
    calibration_end: str,
    holdout_end: Optional[str] = None,
    method: Literal["mle", "bayesian", "both"] = "mle",
    horizon_months: Optional[int] = None,
    output_dir: str | Path = "workspace/reports",
) -> dict[str, Any]:
    """Run the full holdout validation pipeline.

    Steps:
    1. Split transactions into calibration and holdout periods
    2. Build RFM summary on calibration data
    3. Fit BG/NBD and Gamma-Gamma models on calibration data
    4. Predict transactions and monetary value for the holdout period
    5. Compare predictions to holdout actuals
    6. Generate diagnostic plots and metrics

    Parameters
    ----------
    transactions_path : str or Path
        Path to the full transaction data CSV.
    calibration_end : str
        ISO date for end of calibration period.
    holdout_end : str or None
        ISO date for end of holdout period. None uses all remaining data.
    method : {"mle", "bayesian", "both"}
        Which fitting method(s) to validate.
    horizon_months : int or None
        If None, inferred from calibration_end to holdout_end duration.
    output_dir : str or Path
        Directory for validation outputs.

    Returns
    -------
    dict
        Validation results:
        - ``metrics`` (dict): MAE, RMSE, calibration_ratio per method
        - ``prob_alive_calibration`` (pd.DataFrame): calibration table
        - ``comparison`` (dict or None): MLE vs. Bayesian comparison if both
        - ``report_path`` (Path): path to HTML diagnostic report
        - ``pass`` (bool): True if MAE within acceptance threshold
    """
    # TODO: orchestrate full validation pipeline
    raise NotImplementedError


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate CLV model with holdout period")
    parser.add_argument("--transactions", required=True, help="Path to transactions CSV")
    parser.add_argument("--calibration-end", required=True, help="ISO date for calibration end")
    parser.add_argument("--holdout-end", default=None, help="ISO date for holdout end")
    parser.add_argument("--method", default="mle", choices=["mle", "bayesian", "both"])
    parser.add_argument("--output-dir", default="workspace/reports")
    args = parser.parse_args()

    results = run_validation_pipeline(
        transactions_path=args.transactions,
        calibration_end=args.calibration_end,
        holdout_end=args.holdout_end,
        method=args.method,
        output_dir=args.output_dir,
    )
    print(f"Validation pass: {results.get('pass', 'N/A')}")
    for method_name, metrics in results.get("metrics", {}).items():
        print(f"  {method_name}: MAE={metrics.get('mae', 'N/A'):.4f}, "
              f"RMSE={metrics.get('rmse', 'N/A'):.4f}")
