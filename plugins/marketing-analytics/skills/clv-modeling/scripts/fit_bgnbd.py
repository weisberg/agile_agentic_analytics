"""
BG/NBD and Gamma-Gamma Model Fitting.

Fits the BG/NBD model for purchase frequency prediction and the
Gamma-Gamma model for monetary value estimation. Supports both
MLE (lifetimes library) and Bayesian (PyMC-Marketing) fitting methods.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Optional

import pandas as pd


def fit_bgnbd_mle(
    rfm: pd.DataFrame,
    penalizer_coef: float = 0.0,
    frequency_col: str = "frequency",
    recency_col: str = "recency",
    T_col: str = "T",
) -> dict[str, Any]:
    """Fit BG/NBD model using maximum likelihood estimation via lifetimes.

    Parameters
    ----------
    rfm : pd.DataFrame
        RFM summary with frequency, recency, and T columns.
    penalizer_coef : float
        L2 regularization penalty. Increase from 0.0 if convergence fails.
    frequency_col : str
        Column name for purchase frequency.
    recency_col : str
        Column name for recency.
    T_col : str
        Column name for customer tenure.

    Returns
    -------
    dict
        Fitted model results with keys:
        - ``model``: fitted ``BetaGeoFitter`` instance
        - ``params`` (dict): {r, alpha, a, b} parameter estimates
        - ``log_likelihood`` (float): maximized log-likelihood
        - ``converged`` (bool): whether optimization converged
    """
    # TODO: instantiate BetaGeoFitter, call .fit(), extract params
    raise NotImplementedError


def fit_bgnbd_bayesian(
    rfm: pd.DataFrame,
    tune: int = 1000,
    draws: int = 1000,
    chains: int = 4,
    target_accept: float = 0.9,
    model_config: Optional[dict] = None,
    random_seed: int = 42,
) -> dict[str, Any]:
    """Fit BG/NBD model using Bayesian MCMC via PyMC-Marketing.

    Parameters
    ----------
    rfm : pd.DataFrame
        RFM summary with customer_id, frequency, recency, T columns.
    tune : int
        Number of MCMC tuning steps.
    draws : int
        Number of posterior draws per chain.
    chains : int
        Number of MCMC chains.
    target_accept : float
        Target acceptance probability for NUTS sampler.
    model_config : dict or None
        Prior distribution overrides. See PyMC-Marketing docs for keys.
    random_seed : int
        Random seed for reproducibility.

    Returns
    -------
    dict
        Fitted model results with keys:
        - ``model``: fitted ``BetaGeoModel`` instance
        - ``idata``: ArviZ InferenceData with posterior samples
        - ``convergence`` (dict): R-hat and ESS diagnostics per parameter
        - ``converged`` (bool): True if all R-hat < 1.01 and ESS > 400
    """
    # TODO: instantiate BetaGeoModel, call .fit(), check convergence
    raise NotImplementedError


def fit_gamma_gamma_mle(
    rfm: pd.DataFrame,
    penalizer_coef: float = 0.0,
    frequency_col: str = "frequency",
    monetary_col: str = "monetary_value",
) -> dict[str, Any]:
    """Fit Gamma-Gamma model for monetary value using MLE via lifetimes.

    Only customers with frequency > 0 are included. Validates the
    independence assumption between frequency and monetary value.

    Parameters
    ----------
    rfm : pd.DataFrame
        RFM summary. Customers with frequency == 0 are automatically excluded.
    penalizer_coef : float
        L2 regularization penalty.
    frequency_col : str
        Column name for purchase frequency.
    monetary_col : str
        Column name for average monetary value.

    Returns
    -------
    dict
        Fitted model results with keys:
        - ``model``: fitted ``GammaGammaFitter`` instance
        - ``params`` (dict): {p, q, v} parameter estimates
        - ``freq_monetary_correlation`` (float): Pearson correlation
        - ``independence_ok`` (bool): True if correlation < 0.3
        - ``customers_excluded`` (int): count of one-time purchasers dropped
    """
    # TODO: filter frequency > 0, check correlation, fit GammaGammaFitter
    raise NotImplementedError


def fit_gamma_gamma_bayesian(
    rfm: pd.DataFrame,
    tune: int = 1000,
    draws: int = 1000,
    chains: int = 4,
    target_accept: float = 0.9,
    model_config: Optional[dict] = None,
    random_seed: int = 42,
) -> dict[str, Any]:
    """Fit Gamma-Gamma model using Bayesian MCMC via PyMC-Marketing.

    Parameters
    ----------
    rfm : pd.DataFrame
        RFM summary with customer_id, frequency, monetary_value columns.
        Customers with frequency == 0 are automatically excluded.
    tune : int
        Number of MCMC tuning steps.
    draws : int
        Number of posterior draws per chain.
    chains : int
        Number of MCMC chains.
    target_accept : float
        Target acceptance probability.
    model_config : dict or None
        Prior distribution overrides.
    random_seed : int
        Random seed for reproducibility.

    Returns
    -------
    dict
        Fitted model results with keys:
        - ``model``: fitted ``GammaGammaModel`` instance
        - ``idata``: ArviZ InferenceData
        - ``convergence`` (dict): R-hat and ESS diagnostics
        - ``converged`` (bool): all diagnostics pass
    """
    # TODO: filter, instantiate GammaGammaModel, fit, check convergence
    raise NotImplementedError


def fit_beta_geometric(
    subscriptions: pd.DataFrame,
    customer_col: str = "customer_id",
    start_col: str = "start_date",
    end_col: str = "end_date",
    period: str = "M",
) -> dict[str, Any]:
    """Fit Beta-Geometric model for contractual/subscription churn.

    Converts subscription data to renewal-period survival format and fits
    a Beta-Geometric model to estimate per-period churn probabilities.

    Parameters
    ----------
    subscriptions : pd.DataFrame
        Subscription data with customer_id, start_date, end_date (null if active).
    customer_col : str
        Column name for customer identifier.
    start_col : str
        Column name for subscription start date.
    end_col : str
        Column name for subscription end date (null/NaT if still active).
    period : str
        Renewal period granularity: ``"M"`` (month), ``"Q"`` (quarter), ``"Y"`` (year).

    Returns
    -------
    dict
        Fitted model results with keys:
        - ``params`` (dict): {alpha, beta} of the Beta distribution on churn
        - ``mean_churn_rate`` (float): alpha / (alpha + beta)
        - ``retention_curve`` (list[float]): survival probabilities by period
        - ``expected_lifetime`` (dict): per-customer expected remaining periods
    """
    # TODO: convert to survival format, fit BG model, compute retention curve
    raise NotImplementedError


def save_model(
    model_result: dict[str, Any],
    output_dir: str | Path = "workspace/models",
    model_name: str = "bgnbd",
) -> Path:
    """Serialize a fitted model to disk.

    Saves the model object (pickle) and inference data (NetCDF) if available.

    Parameters
    ----------
    model_result : dict
        Output from one of the fit functions.
    output_dir : str or Path
        Directory for saved model artifacts.
    model_name : str
        Base name for the saved files.

    Returns
    -------
    Path
        Path to the primary saved model file.
    """
    # TODO: pickle model, save idata as NetCDF if Bayesian
    raise NotImplementedError


def fit_models(
    rfm_path: str | Path,
    method: Literal["mle", "bayesian"] = "mle",
    subscriptions_path: Optional[str | Path] = None,
    output_dir: str | Path = "workspace/models",
) -> dict[str, dict[str, Any]]:
    """Run the full model fitting pipeline.

    Fits BG/NBD and Gamma-Gamma models (and optionally Beta-Geometric)
    using the specified method.

    Parameters
    ----------
    rfm_path : str or Path
        Path to the RFM summary CSV.
    method : {"mle", "bayesian"}
        Fitting method to use.
    subscriptions_path : str or Path or None
        Path to subscription data for contractual CLV. If provided,
        Beta-Geometric model is also fitted.
    output_dir : str or Path
        Directory for saving fitted model artifacts.

    Returns
    -------
    dict
        Keys: ``"bgnbd"``, ``"gamma_gamma"``, and optionally ``"beta_geo"``.
        Values: result dicts from the respective fit functions.
    """
    # TODO: load RFM, call fit functions, save models, return results
    raise NotImplementedError


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fit BG/NBD and Gamma-Gamma CLV models")
    parser.add_argument("--rfm", required=True, help="Path to RFM summary CSV")
    parser.add_argument("--method", default="mle", choices=["mle", "bayesian"])
    parser.add_argument("--subscriptions", default=None, help="Path to subscriptions CSV")
    parser.add_argument("--output-dir", default="workspace/models")
    args = parser.parse_args()

    results = fit_models(
        rfm_path=args.rfm,
        method=args.method,
        subscriptions_path=args.subscriptions,
        output_dir=args.output_dir,
    )
    for model_name, result in results.items():
        print(f"{model_name}: converged={result.get('converged', 'N/A')}")
