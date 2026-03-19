"""
Customer-Level CLV Prediction with Configurable Horizon.

Generates per-customer CLV predictions, probability-alive scores,
CLV:CAC ratios, at-risk identification, and CLV-based segmentation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Optional

import pandas as pd


def predict_expected_transactions(
    rfm: pd.DataFrame,
    bgnbd_model: Any,
    horizon_months: int = 12,
    time_unit: str = "D",
) -> pd.DataFrame:
    """Predict expected future transactions per customer.

    Parameters
    ----------
    rfm : pd.DataFrame
        RFM summary with customer_id, frequency, recency, T.
    bgnbd_model : Any
        Fitted BG/NBD model (lifetimes BetaGeoFitter or PyMC-Marketing BetaGeoModel).
    horizon_months : int
        Prediction horizon in months. Common values: 6, 12, 24.
    time_unit : str
        Time unit of the RFM data (``"D"`` for days, ``"W"`` for weeks).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: ``customer_id``, ``expected_transactions``,
        ``expected_transactions_ci_lower``, ``expected_transactions_ci_upper``.
    """
    # TODO: convert horizon to time units, call model prediction, compute CIs
    raise NotImplementedError


def predict_probability_alive(
    rfm: pd.DataFrame,
    bgnbd_model: Any,
) -> pd.DataFrame:
    """Compute probability-alive scores for all customers.

    Parameters
    ----------
    rfm : pd.DataFrame
        RFM summary with customer_id, frequency, recency, T.
    bgnbd_model : Any
        Fitted BG/NBD model.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: ``customer_id``, ``prob_alive``,
        ``prob_alive_ci_lower``, ``prob_alive_ci_upper``.
    """
    # TODO: call model's probability alive method, add confidence intervals
    raise NotImplementedError


def predict_monetary_value(
    rfm: pd.DataFrame,
    gamma_gamma_model: Any,
) -> pd.DataFrame:
    """Predict expected average monetary value per transaction per customer.

    Parameters
    ----------
    rfm : pd.DataFrame
        RFM summary with customer_id, frequency, monetary_value.
        Customers with frequency == 0 receive NaN predictions.
    gamma_gamma_model : Any
        Fitted Gamma-Gamma model (lifetimes or PyMC-Marketing).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: ``customer_id``, ``expected_monetary_value``.
    """
    # TODO: call model prediction, handle one-time purchasers
    raise NotImplementedError


def compute_clv(
    expected_transactions: pd.DataFrame,
    expected_monetary: pd.DataFrame,
    prob_alive: pd.DataFrame,
    horizon_months: int = 12,
    discount_rate: float = 0.10,
    margin: float = 1.0,
) -> pd.DataFrame:
    """Compute customer-level CLV from component predictions.

    Formula: CLV = E[transactions] * E[monetary_value] * margin * discount_factor

    Parameters
    ----------
    expected_transactions : pd.DataFrame
        Per-customer expected transactions from ``predict_expected_transactions``.
    expected_monetary : pd.DataFrame
        Per-customer expected monetary value from ``predict_monetary_value``.
    prob_alive : pd.DataFrame
        Per-customer probability-alive from ``predict_probability_alive``.
    horizon_months : int
        Prediction horizon used for the discount factor calculation.
    discount_rate : float
        Annual discount rate (e.g., 0.10 for 10%). Defaults to WACC-like rate.
    margin : float
        Gross margin multiplier applied to revenue (e.g., 0.3 for 30% margin).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: ``customer_id``, ``predicted_clv``,
        ``clv_ci_lower``, ``clv_ci_upper``, ``prob_alive``,
        ``expected_transactions``, ``expected_monetary_value``,
        ``horizon_months``, ``discount_rate``, ``margin``.
    """
    # TODO: merge component predictions, compute CLV with discount factor
    raise NotImplementedError


def compute_clv_cac_ratio(
    clv_predictions: pd.DataFrame,
    acquisition_costs_path: Optional[str | Path] = None,
) -> pd.DataFrame:
    """Calculate CLV:CAC ratios when acquisition cost data is available.

    Parameters
    ----------
    clv_predictions : pd.DataFrame
        Customer-level CLV predictions with ``customer_id`` and ``predicted_clv``.
    acquisition_costs_path : str, Path, or None
        Path to ``acquisition_costs.json`` from the paid-media skill.
        Expected format: list of {customer_id, cac} or {segment, cac}.
        If None or file missing, ratio columns are filled with NaN and
        a warning flag is set.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with added columns: ``cac``, ``clv_cac_ratio``,
        ``cac_data_available`` (bool).
    """
    # TODO: load CAC data if available, merge, compute ratio, flag missing
    raise NotImplementedError


def identify_at_risk_customers(
    clv_predictions: pd.DataFrame,
    clv_percentile_threshold: float = 0.90,
    prob_alive_threshold: float = 0.50,
) -> pd.DataFrame:
    """Identify high-value customers at risk of churning.

    Criteria:
    - High-value: predicted CLV in the top percentile (default: top 10%)
    - At-risk: probability-alive below threshold (default: 50%)

    Parameters
    ----------
    clv_predictions : pd.DataFrame
        Customer-level predictions with ``predicted_clv`` and ``prob_alive``.
    clv_percentile_threshold : float
        Percentile cutoff for high-value classification (0.90 = top 10%).
    prob_alive_threshold : float
        Probability-alive below which a customer is considered at-risk.

    Returns
    -------
    pd.DataFrame
        Subset of at-risk high-value customers with columns:
        ``customer_id``, ``predicted_clv``, ``prob_alive``,
        ``expected_transactions``, ``days_since_last_purchase``,
        ``risk_priority`` (ranked by CLV descending).
    """
    # TODO: filter by CLV percentile and prob_alive, rank by priority
    raise NotImplementedError


def assign_clv_segments(
    clv_predictions: pd.DataFrame,
    tiers: Optional[dict[str, float]] = None,
) -> pd.DataFrame:
    """Assign customers to CLV-based value tiers.

    Parameters
    ----------
    clv_predictions : pd.DataFrame
        Customer-level predictions with ``predicted_clv``.
    tiers : dict or None
        Mapping of tier name to percentile threshold. Defaults to:
        ``{"Platinum": 0.90, "Gold": 0.75, "Silver": 0.50, "Bronze": 0.0}``.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with added ``clv_segment`` column.
    """
    # TODO: compute percentile ranks, assign tier labels
    raise NotImplementedError


def save_predictions(
    clv_predictions: pd.DataFrame,
    at_risk: pd.DataFrame,
    segments: pd.DataFrame,
    output_dir: str | Path = "workspace/analysis",
) -> dict[str, Path]:
    """Save all prediction outputs to JSON files.

    Saves:
    - ``clv_predictions.json`` -- full customer-level predictions
    - ``at_risk_customers.json`` -- high-value at-risk subset
    - ``clv_segments.json`` -- CLV tier assignments

    Parameters
    ----------
    clv_predictions : pd.DataFrame
        Full prediction DataFrame.
    at_risk : pd.DataFrame
        At-risk customer DataFrame.
    segments : pd.DataFrame
        Segment assignment DataFrame.
    output_dir : str or Path
        Output directory.

    Returns
    -------
    dict[str, Path]
        Mapping of output name to saved file path.
    """
    # TODO: ensure directory, write JSON files with orient="records"
    raise NotImplementedError


def run_prediction_pipeline(
    rfm_path: str | Path,
    bgnbd_model_path: str | Path,
    gamma_gamma_model_path: str | Path,
    horizon_months: int = 12,
    discount_rate: float = 0.10,
    margin: float = 1.0,
    acquisition_costs_path: Optional[str | Path] = None,
    output_dir: str | Path = "workspace/analysis",
) -> dict[str, pd.DataFrame]:
    """Run the full CLV prediction pipeline.

    Parameters
    ----------
    rfm_path : str or Path
        Path to RFM summary CSV.
    bgnbd_model_path : str or Path
        Path to serialized BG/NBD model.
    gamma_gamma_model_path : str or Path
        Path to serialized Gamma-Gamma model.
    horizon_months : int
        Prediction horizon in months.
    discount_rate : float
        Annual discount rate.
    margin : float
        Gross margin multiplier.
    acquisition_costs_path : str, Path, or None
        Path to acquisition cost data.
    output_dir : str or Path
        Directory for output files.

    Returns
    -------
    dict
        Keys: ``"predictions"``, ``"at_risk"``, ``"segments"``.
        Values: corresponding DataFrames.
    """
    # TODO: load data and models, call prediction functions, save outputs
    raise NotImplementedError


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate customer-level CLV predictions")
    parser.add_argument("--rfm", required=True, help="Path to RFM summary CSV")
    parser.add_argument("--bgnbd-model", required=True, help="Path to fitted BG/NBD model")
    parser.add_argument("--gg-model", required=True, help="Path to fitted Gamma-Gamma model")
    parser.add_argument("--horizon", type=int, default=12, help="Horizon in months")
    parser.add_argument("--discount-rate", type=float, default=0.10)
    parser.add_argument("--margin", type=float, default=1.0)
    parser.add_argument("--cac-data", default=None, help="Path to acquisition costs JSON")
    parser.add_argument("--output-dir", default="workspace/analysis")
    args = parser.parse_args()

    results = run_prediction_pipeline(
        rfm_path=args.rfm,
        bgnbd_model_path=args.bgnbd_model,
        gamma_gamma_model_path=args.gg_model,
        horizon_months=args.horizon,
        discount_rate=args.discount_rate,
        margin=args.margin,
        acquisition_costs_path=args.cac_data,
        output_dir=args.output_dir,
    )
    for name, df in results.items():
        print(f"{name}: {len(df)} rows")
