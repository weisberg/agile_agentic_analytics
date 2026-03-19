"""
Lead Scoring Model — Feature engineering, model training, SHAP explanation,
and score calibration for predictive lead scoring.

Uses logistic regression (interpretable baseline) and gradient boosting
(accuracy-optimized) with temporal holdout validation. SHAP values provide
per-lead feature explanations. Calibration ensures predicted probabilities
match observed conversion rates.

Dependencies:
    pandas, numpy, scikit-learn, shap

Inputs:
    workspace/raw/crm_leads.csv
    workspace/raw/lead_activities.csv
    workspace/processed/segments.json (optional)

Outputs:
    workspace/analysis/lead_scores.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
from numpy.typing import NDArray


# ---------------------------------------------------------------------------
# Feature Engineering
# ---------------------------------------------------------------------------


def load_crm_leads(filepath: str | Path) -> pd.DataFrame:
    """Load and validate CRM lead/opportunity data.

    Parameters
    ----------
    filepath : str | Path
        Path to ``crm_leads.csv``. Required columns: ``lead_id``, ``source``,
        ``stage``, ``created_date``, ``close_date``, ``amount``, ``outcome``.

    Returns
    -------
    pd.DataFrame
        Validated lead dataframe with parsed date columns.

    Raises
    ------
    ValueError
        If required columns are missing.
    """
    # TODO: load CSV, validate required columns, parse dates
    raise NotImplementedError


def load_lead_activities(filepath: str | Path) -> pd.DataFrame:
    """Load and validate lead activity/behavioral data.

    Parameters
    ----------
    filepath : str | Path
        Path to ``lead_activities.csv``. Required columns: ``lead_id``,
        ``activity_type``, ``timestamp``.

    Returns
    -------
    pd.DataFrame
        Validated activity dataframe with parsed timestamp column.

    Raises
    ------
    ValueError
        If required columns are missing.
    """
    # TODO: load CSV, validate required columns, parse timestamps
    raise NotImplementedError


def load_segments(filepath: str | Path) -> Optional[dict[str, Any]]:
    """Load optional segment enrichment from audience-segmentation.

    Parameters
    ----------
    filepath : str | Path
        Path to ``segments.json``.

    Returns
    -------
    dict or None
        Segment mapping if file exists, otherwise ``None``.
    """
    # TODO: load segments.json if it exists, return None otherwise
    raise NotImplementedError


def engineer_firmographic_features(leads: pd.DataFrame) -> pd.DataFrame:
    """Build firmographic features from CRM lead fields.

    Creates features including:
    - Company size bucket (SMB / Mid-Market / Enterprise)
    - Industry one-hot encoding (top 15 + Other)
    - Log-transformed annual revenue
    - Geographic region encoding

    Parameters
    ----------
    leads : pd.DataFrame
        Raw CRM leads dataframe.

    Returns
    -------
    pd.DataFrame
        Firmographic feature matrix indexed by ``lead_id``.
    """
    # TODO: log-transform company size, one-hot encode industry, map geography
    raise NotImplementedError


def engineer_behavioral_features(
    activities: pd.DataFrame,
    scoring_date: pd.Timestamp,
    windows: list[int] | None = None,
) -> pd.DataFrame:
    """Build behavioral features from lead activity data.

    Creates time-windowed aggregations (7, 30, 90 days) for:
    - Page views, email opens/clicks, content downloads, form submissions
    - Recency of last activity (days since last engagement)
    - Activity velocity (week-over-week change)
    - Channel diversity (distinct activity types)
    - High-intent signal flag (pricing page, demo request, contact-sales form)

    Parameters
    ----------
    activities : pd.DataFrame
        Lead activities dataframe with ``lead_id``, ``activity_type``,
        ``timestamp``.
    scoring_date : pd.Timestamp
        Reference date for computing recency and time windows.
    windows : list[int] or None
        Time windows in days for aggregation. Defaults to ``[7, 30, 90]``.

    Returns
    -------
    pd.DataFrame
        Behavioral feature matrix indexed by ``lead_id``.
    """
    if windows is None:
        windows = [7, 30, 90]
    # TODO: aggregate activities per window, compute recency, velocity, diversity
    raise NotImplementedError


def engineer_derived_features(
    leads: pd.DataFrame,
    behavioral: pd.DataFrame,
    scoring_date: pd.Timestamp,
) -> pd.DataFrame:
    """Build derived features combining lead metadata and behavioral signals.

    Includes:
    - Lead age (days since created_date)
    - Activity intensity (total activities / lead age)
    - Engagement score (weighted sum of behavioral features)

    Parameters
    ----------
    leads : pd.DataFrame
        CRM leads dataframe.
    behavioral : pd.DataFrame
        Behavioral feature matrix.
    scoring_date : pd.Timestamp
        Reference date for age calculation.

    Returns
    -------
    pd.DataFrame
        Derived feature matrix indexed by ``lead_id``.
    """
    # TODO: compute lead age, activity intensity, engagement score
    raise NotImplementedError


def build_feature_matrix(
    leads: pd.DataFrame,
    activities: pd.DataFrame,
    scoring_date: pd.Timestamp,
    segments: Optional[dict[str, Any]] = None,
) -> tuple[pd.DataFrame, pd.Series]:
    """Assemble the complete feature matrix and target variable.

    Combines firmographic, behavioral, and derived features. Optionally
    enriches with segment membership from audience-segmentation.

    Parameters
    ----------
    leads : pd.DataFrame
        CRM leads dataframe.
    activities : pd.DataFrame
        Lead activities dataframe.
    scoring_date : pd.Timestamp
        Reference date for feature engineering.
    segments : dict or None
        Optional segment enrichment data.

    Returns
    -------
    tuple[pd.DataFrame, pd.Series]
        Feature matrix ``X`` and binary target ``y`` (1 = converted, 0 = not).
    """
    # TODO: call sub-functions, merge features, encode target, handle missing
    raise NotImplementedError


# ---------------------------------------------------------------------------
# CRM Field Mapping
# ---------------------------------------------------------------------------


def map_crm_fields(
    df: pd.DataFrame,
    crm_type: str = "salesforce",
    custom_mapping: Optional[dict[str, str]] = None,
) -> pd.DataFrame:
    """Map CRM-specific field names to canonical names.

    Supports Salesforce and HubSpot naming conventions with an optional
    custom mapping override.

    Parameters
    ----------
    df : pd.DataFrame
        Raw CRM dataframe with platform-specific column names.
    crm_type : str
        CRM platform: ``"salesforce"`` or ``"hubspot"``.
    custom_mapping : dict or None
        Optional column name mapping ``{crm_name: canonical_name}``.

    Returns
    -------
    pd.DataFrame
        Dataframe with canonical column names.

    Raises
    ------
    ValueError
        If ``crm_type`` is not supported.
    """
    # TODO: apply Salesforce or HubSpot field mapping, then custom overrides
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Model Training
# ---------------------------------------------------------------------------


def temporal_train_test_split(
    X: pd.DataFrame,
    y: pd.Series,
    test_fraction: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split data by time for temporal holdout validation.

    Sorts by ``created_date`` (must be in X index or columns) and assigns
    the most recent ``test_fraction`` of records to the test set.

    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix.
    y : pd.Series
        Target variable.
    test_fraction : float
        Fraction of data (by date order) to use for validation.

    Returns
    -------
    tuple
        ``(X_train, X_test, y_train, y_test)``
    """
    # TODO: sort by date, split at temporal boundary
    raise NotImplementedError


def train_logistic_regression(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    regularization: str = "elasticnet",
    class_weight: str = "balanced",
) -> Any:
    """Train a logistic regression model (interpretable baseline).

    Parameters
    ----------
    X_train : pd.DataFrame
        Training feature matrix.
    y_train : pd.Series
        Training target.
    regularization : str
        Regularization type: ``"l1"``, ``"l2"``, or ``"elasticnet"``.
    class_weight : str
        Class weighting strategy. Use ``"balanced"`` for low conversion rates.

    Returns
    -------
    sklearn.linear_model.LogisticRegression
        Fitted logistic regression model.
    """
    # TODO: fit LogisticRegression with specified regularization and class_weight
    raise NotImplementedError


def train_gradient_boosting(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 300,
    max_depth: int = 5,
    learning_rate: float = 0.05,
    subsample: float = 0.8,
) -> Any:
    """Train a gradient boosting model (accuracy-optimized).

    Uses cross-validated hyperparameter selection with early stopping on
    validation loss.

    Parameters
    ----------
    X_train : pd.DataFrame
        Training feature matrix.
    y_train : pd.Series
        Training target.
    n_estimators : int
        Maximum number of boosting rounds.
    max_depth : int
        Maximum tree depth.
    learning_rate : float
        Shrinkage rate.
    subsample : float
        Row subsampling fraction.

    Returns
    -------
    sklearn.ensemble.GradientBoostingClassifier
        Fitted gradient boosting model.
    """
    # TODO: fit GradientBoostingClassifier with early stopping
    raise NotImplementedError


def evaluate_model(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict[str, float]:
    """Evaluate a trained model on the temporal holdout set.

    Computes AUC-ROC, precision-recall AUC, log-loss, and Brier score.

    Parameters
    ----------
    model : fitted sklearn estimator
        Trained classification model.
    X_test : pd.DataFrame
        Test feature matrix.
    y_test : pd.Series
        Test target.

    Returns
    -------
    dict[str, float]
        Dictionary with keys ``auc_roc``, ``auc_pr``, ``log_loss``,
        ``brier_score``.
    """
    # TODO: predict_proba, compute metrics
    raise NotImplementedError


def compare_models(
    lr_metrics: dict[str, float],
    gb_metrics: dict[str, float],
    auc_threshold: float = 0.02,
) -> str:
    """Select the preferred model based on performance comparison.

    If gradient boosting AUC exceeds logistic regression by less than
    ``auc_threshold``, prefer logistic regression for interpretability.

    Parameters
    ----------
    lr_metrics : dict
        Logistic regression evaluation metrics.
    gb_metrics : dict
        Gradient boosting evaluation metrics.
    auc_threshold : float
        Minimum AUC improvement to prefer gradient boosting.

    Returns
    -------
    str
        ``"logistic_regression"`` or ``"gradient_boosting"``.
    """
    # TODO: compare AUC values, apply threshold logic
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------


def calibrate_model(
    model: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    method: str = "isotonic",
) -> Any:
    """Calibrate a model's predicted probabilities.

    Applies Platt scaling (sigmoid) or isotonic regression to transform raw
    model scores into reliable probability estimates.

    Parameters
    ----------
    model : fitted sklearn estimator
        Trained classification model.
    X_train : pd.DataFrame
        Training feature matrix (used for calibration fitting).
    y_train : pd.Series
        Training target.
    method : str
        Calibration method: ``"sigmoid"`` (Platt) or ``"isotonic"``.

    Returns
    -------
    sklearn.calibration.CalibratedClassifierCV
        Calibrated model wrapper.
    """
    # TODO: wrap model in CalibratedClassifierCV, fit
    raise NotImplementedError


def validate_calibration(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_bins: int = 10,
) -> dict[str, Any]:
    """Validate model calibration across decile bins.

    Bins predicted probabilities into deciles and compares predicted vs.
    observed conversion rates. Acceptance criterion: agreement within 5
    percentage points per bin.

    Parameters
    ----------
    model : fitted estimator
        Calibrated model.
    X_test : pd.DataFrame
        Test feature matrix.
    y_test : pd.Series
        Test target.
    n_bins : int
        Number of probability bins (default: 10 for deciles).

    Returns
    -------
    dict[str, Any]
        Keys: ``bins`` (list of bin edges), ``predicted_rates`` (list),
        ``observed_rates`` (list), ``max_deviation`` (float),
        ``calibration_passed`` (bool).
    """
    # TODO: bin predictions, compute observed rates, check deviation threshold
    raise NotImplementedError


# ---------------------------------------------------------------------------
# SHAP Explainability
# ---------------------------------------------------------------------------


def compute_shap_values(
    model: Any,
    X: pd.DataFrame,
    max_samples: int = 1000,
) -> NDArray[np.float64]:
    """Compute SHAP values for model predictions.

    Uses TreeExplainer for tree-based models and LinearExplainer for linear
    models. Subsamples the background dataset if needed for performance.

    Parameters
    ----------
    model : fitted sklearn estimator
        Trained model (logistic regression or gradient boosting).
    X : pd.DataFrame
        Feature matrix for which to compute SHAP values.
    max_samples : int
        Maximum background samples for SHAP computation.

    Returns
    -------
    np.ndarray
        SHAP value matrix of shape ``(n_samples, n_features)``.
    """
    # TODO: select appropriate SHAP explainer, compute values
    raise NotImplementedError


def get_top_features(
    shap_values: NDArray[np.float64],
    feature_names: list[str],
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Rank features by mean absolute SHAP value.

    Parameters
    ----------
    shap_values : np.ndarray
        SHAP value matrix of shape ``(n_samples, n_features)``.
    feature_names : list[str]
        Names corresponding to feature columns.
    top_k : int
        Number of top features to return.

    Returns
    -------
    list[dict[str, Any]]
        Ranked list of dicts with keys ``feature``, ``mean_abs_shap``,
        ``direction`` (positive/negative average impact).
    """
    # TODO: compute mean absolute SHAP per feature, sort, return top_k
    raise NotImplementedError


def explain_lead_score(
    lead_id: str,
    shap_values: NDArray[np.float64],
    feature_names: list[str],
    X: pd.DataFrame,
    top_k: int = 5,
) -> dict[str, Any]:
    """Generate a human-readable SHAP explanation for a single lead.

    Parameters
    ----------
    lead_id : str
        Identifier for the lead to explain.
    shap_values : np.ndarray
        SHAP value matrix.
    feature_names : list[str]
        Feature column names.
    X : pd.DataFrame
        Feature matrix (indexed by lead_id).
    top_k : int
        Number of top contributing features to include.

    Returns
    -------
    dict[str, Any]
        Keys: ``lead_id``, ``score``, ``top_factors`` (list of
        ``{feature, value, shap_contribution, direction}``).
    """
    # TODO: extract lead's SHAP values, rank, format explanation
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Drift Detection
# ---------------------------------------------------------------------------


def compute_psi(
    reference: NDArray[np.float64],
    current: NDArray[np.float64],
    n_bins: int = 10,
) -> float:
    """Compute Population Stability Index between two distributions.

    PSI > 0.1 triggers a warning; PSI > 0.2 triggers mandatory retraining.

    Parameters
    ----------
    reference : np.ndarray
        Reference (training) distribution values.
    current : np.ndarray
        Current (scoring) distribution values.
    n_bins : int
        Number of bins for discretization.

    Returns
    -------
    float
        PSI value.
    """
    # TODO: bin both distributions, compute PSI sum
    raise NotImplementedError


def detect_feature_drift(
    X_train: pd.DataFrame,
    X_current: pd.DataFrame,
    psi_warning: float = 0.1,
    psi_critical: float = 0.2,
) -> dict[str, Any]:
    """Check all features for distribution drift using PSI.

    Parameters
    ----------
    X_train : pd.DataFrame
        Training feature matrix.
    X_current : pd.DataFrame
        Current scoring feature matrix.
    psi_warning : float
        PSI threshold for warning.
    psi_critical : float
        PSI threshold for mandatory retraining.

    Returns
    -------
    dict[str, Any]
        Keys: ``feature_psi`` (dict of feature -> PSI), ``warnings`` (list),
        ``critical`` (list), ``retrain_recommended`` (bool).
    """
    # TODO: compute PSI per feature, classify into warning/critical
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Account-Based Scoring
# ---------------------------------------------------------------------------


def aggregate_to_account_scores(
    lead_scores: pd.DataFrame,
    account_field: str = "company_id",
) -> pd.DataFrame:
    """Aggregate contact-level lead scores to account-level propensity.

    Combines multiple contact signals using max, mean, and count aggregations.

    Parameters
    ----------
    lead_scores : pd.DataFrame
        Lead-level scores with ``lead_id``, ``score``, and ``account_field``.
    account_field : str
        Column name for the account/company identifier.

    Returns
    -------
    pd.DataFrame
        Account-level scores with ``account_id``, ``max_score``,
        ``mean_score``, ``contact_count``, ``account_propensity``.
    """
    # TODO: group by account, aggregate scores, compute account propensity
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def generate_lead_scores_output(
    X: pd.DataFrame,
    model: Any,
    shap_values: NDArray[np.float64],
    feature_names: list[str],
    output_path: str | Path,
) -> None:
    """Generate the lead_scores.json output file.

    Produces lead-level propensity scores with per-lead SHAP feature
    explanations and global feature importance rankings.

    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix for scored leads.
    model : fitted estimator
        Calibrated scoring model.
    shap_values : np.ndarray
        SHAP value matrix.
    feature_names : list[str]
        Feature column names.
    output_path : str | Path
        Path to write ``lead_scores.json``.
    """
    # TODO: score all leads, attach explanations, write JSON
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Main Orchestration
# ---------------------------------------------------------------------------


def run_lead_scoring_pipeline(
    leads_path: str | Path,
    activities_path: str | Path,
    output_path: str | Path,
    segments_path: Optional[str | Path] = None,
    scoring_date: Optional[pd.Timestamp] = None,
    crm_type: str = "salesforce",
    calibration_method: str = "isotonic",
) -> dict[str, Any]:
    """Execute the full lead scoring pipeline.

    Steps:
    1. Load and validate input data
    2. Map CRM fields to canonical names
    3. Engineer features (firmographic, behavioral, derived)
    4. Split data temporally
    5. Train logistic regression and gradient boosting models
    6. Evaluate and select preferred model
    7. Calibrate and validate calibration
    8. Compute SHAP explanations
    9. Detect feature drift (if retraining)
    10. Generate output JSON

    Parameters
    ----------
    leads_path : str | Path
        Path to ``crm_leads.csv``.
    activities_path : str | Path
        Path to ``lead_activities.csv``.
    output_path : str | Path
        Path to write ``lead_scores.json``.
    segments_path : str | Path or None
        Optional path to ``segments.json``.
    scoring_date : pd.Timestamp or None
        Reference date for features. Defaults to current date.
    crm_type : str
        CRM platform for field mapping.
    calibration_method : str
        Calibration technique: ``"isotonic"`` or ``"sigmoid"``.

    Returns
    -------
    dict[str, Any]
        Pipeline summary with model metrics, calibration results,
        top features, and drift status.
    """
    # TODO: orchestrate full pipeline
    raise NotImplementedError
