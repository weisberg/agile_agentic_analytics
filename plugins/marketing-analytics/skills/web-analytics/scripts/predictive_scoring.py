"""Logistic regression propensity scoring for conversion and churn.

Builds logistic regression models to score users by their propensity to
convert (for unconverted visitors) and propensity to churn (for returning
visitors showing declining engagement). Uses temporal holdout validation
to avoid data leakage.

Dependencies:
    - pandas
    - numpy
    - scikit-learn
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd


@dataclass
class ScoringConfig:
    """Configuration for predictive audience scoring.

    Attributes:
        model_type: Type of propensity model to build.
        features: List of feature column names to use in the model.
        target_column: Name of the binary target column.
        holdout_date: Date that splits training (before) and validation
            (on or after). Ensures temporal separation to prevent leakage.
        regularization_strength: Inverse regularization strength (C) for
            logistic regression. Default 1.0.
        min_auc_threshold: Minimum AUC-ROC on the holdout set for the
            model to be considered valid. Default 0.70.
        class_weight: How to handle class imbalance. Default "balanced".
        score_threshold: Probability threshold for high-propensity
            classification. Default 0.5.
    """

    model_type: Literal["conversion", "churn"] = "conversion"
    features: list[str] = field(default_factory=lambda: [
        "session_count",
        "avg_pages_per_session",
        "avg_session_duration",
        "days_since_first_visit",
        "days_since_last_visit",
        "content_affinity_score",
        "top_channel",
        "device_category",
    ])
    target_column: str = "converted"
    holdout_date: date | None = None
    regularization_strength: float = 1.0
    min_auc_threshold: float = 0.70
    class_weight: str = "balanced"
    score_threshold: float = 0.5


@dataclass
class ScoringResult:
    """Results from a propensity scoring model.

    Attributes:
        model_type: "conversion" or "churn".
        auc_roc: AUC-ROC on the temporal holdout set.
        auc_pr: AUC of the Precision-Recall curve on holdout.
        coefficients: Dict mapping feature names to their logistic
            regression coefficients.
        intercept: Model intercept.
        holdout_size: Number of samples in the holdout set.
        training_size: Number of samples in the training set.
        positive_rate_train: Fraction of positive labels in training.
        positive_rate_holdout: Fraction of positive labels in holdout.
        is_valid: True if AUC-ROC meets the minimum threshold.
        scores: DataFrame with user_id and propensity_score columns.
    """

    model_type: str
    auc_roc: float
    auc_pr: float
    coefficients: dict[str, float]
    intercept: float
    holdout_size: int
    training_size: int
    positive_rate_train: float
    positive_rate_holdout: float
    is_valid: bool
    scores: pd.DataFrame = field(default_factory=pd.DataFrame)


def prepare_features(
    df: pd.DataFrame,
    features: list[str],
    target_column: str,
) -> tuple[pd.DataFrame, pd.Series]:
    """Prepare feature matrix and target vector for modeling.

    Handles categorical encoding (one-hot for low-cardinality categoricals),
    missing value imputation (median for numeric, mode for categorical),
    and feature scaling (standardization).

    Args:
        df: Raw user-level DataFrame.
        features: List of feature column names.
        target_column: Name of the binary target column.

    Returns:
        Tuple of (X, y) where X is the processed feature DataFrame and
        y is the binary target Series.

    Raises:
        ValueError: If required columns are missing or target is not binary.
    """
    # TODO: Validate columns exist, encode categoricals, impute missing,
    # standardize numeric features, return X and y.
    raise NotImplementedError("prepare_features not yet implemented")


def temporal_train_test_split(
    df: pd.DataFrame,
    date_column: str,
    holdout_date: date,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data into training and holdout sets based on date.

    All records before holdout_date go to training; records on or after
    go to holdout. This prevents temporal data leakage.

    Args:
        df: Full DataFrame with a date column.
        date_column: Name of the date column used for splitting.
        holdout_date: Cutoff date (exclusive for training, inclusive for
            holdout).

    Returns:
        Tuple of (train_df, holdout_df).

    Raises:
        ValueError: If either split is empty.
    """
    # TODO: Filter by date, validate non-empty splits, return.
    raise NotImplementedError("temporal_train_test_split not yet implemented")


def fit_propensity_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    regularization_strength: float = 1.0,
    class_weight: str = "balanced",
) -> Any:
    """Fit a logistic regression propensity model.

    Uses scikit-learn LogisticRegression with L2 penalty and the specified
    regularization strength and class weight handling.

    Args:
        X_train: Training feature matrix.
        y_train: Training binary target.
        regularization_strength: Inverse regularization strength (C).
        class_weight: "balanced" to handle imbalance, or "none".

    Returns:
        Fitted sklearn LogisticRegression model.
    """
    # TODO: Initialize LogisticRegression with specified params, fit on
    # training data, return fitted model.
    raise NotImplementedError("fit_propensity_model not yet implemented")


def evaluate_model(
    model: Any,
    X_holdout: pd.DataFrame,
    y_holdout: pd.Series,
) -> tuple[float, float]:
    """Evaluate the propensity model on the temporal holdout set.

    Args:
        model: Fitted logistic regression model.
        X_holdout: Holdout feature matrix.
        y_holdout: Holdout binary target.

    Returns:
        Tuple of (auc_roc, auc_pr).
    """
    # TODO: Predict probabilities on holdout, compute AUC-ROC and AUC-PR
    # using sklearn.metrics.
    raise NotImplementedError("evaluate_model not yet implemented")


def score_users(
    model: Any,
    X: pd.DataFrame,
    user_ids: pd.Series,
    score_threshold: float = 0.5,
) -> pd.DataFrame:
    """Score all users with the fitted propensity model.

    Args:
        model: Fitted logistic regression model.
        X: Feature matrix for all users to score.
        user_ids: Series of user identifiers aligned with X.
        score_threshold: Probability threshold for high-propensity label.

    Returns:
        DataFrame with columns: user_id, propensity_score,
        high_propensity (bool).
    """
    # TODO: Predict probabilities, create DataFrame with user_id,
    # propensity_score, and high_propensity flag.
    raise NotImplementedError("score_users not yet implemented")


def extract_coefficients(
    model: Any,
    feature_names: list[str],
) -> tuple[dict[str, float], float]:
    """Extract logistic regression coefficients for interpretability.

    Args:
        model: Fitted logistic regression model.
        feature_names: List of feature names matching the model's input.

    Returns:
        Tuple of (coefficients_dict, intercept).
    """
    # TODO: Extract coef_ and intercept_ from the model, zip with
    # feature names, return sorted by absolute value.
    raise NotImplementedError("extract_coefficients not yet implemented")


def run_predictive_scoring(
    input_path: Path,
    output_path: Path,
    config: ScoringConfig | None = None,
) -> ScoringResult:
    """Run the full predictive scoring pipeline.

    Loads user-level data, prepares features, splits by temporal holdout,
    fits a logistic regression model, evaluates on holdout, scores all
    users, and writes results.

    Args:
        input_path: Path to the user-level behavioral data CSV/JSON.
        output_path: Path to write the predictive_audiences.json output.
        config: Optional scoring config (uses defaults if None).

    Returns:
        ScoringResult with model metrics and user scores.

    Raises:
        ValueError: If the model fails to meet the minimum AUC threshold.
    """
    # TODO: Load data, prepare features, split, fit, evaluate, score,
    # serialize results to JSON.
    raise NotImplementedError("run_predictive_scoring not yet implemented")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Predictive audience scoring")
    parser.add_argument("--input", default="workspace/processed/web_metrics.csv")
    parser.add_argument("--output", default="workspace/analysis/predictive_audiences.json")
    parser.add_argument("--model-type", choices=["conversion", "churn"], default="conversion")
    parser.add_argument("--holdout-date", help="Temporal holdout date (YYYY-MM-DD)")
    parser.add_argument("--min-auc", type=float, default=0.70)

    args = parser.parse_args()

    scoring_config = ScoringConfig(
        model_type=args.model_type,
        holdout_date=date.fromisoformat(args.holdout_date) if args.holdout_date else None,
        min_auc_threshold=args.min_auc,
    )

    result = run_predictive_scoring(
        input_path=Path(args.input),
        output_path=Path(args.output),
        config=scoring_config,
    )
    print(f"Model type: {result.model_type}")
    print(f"AUC-ROC: {result.auc_roc:.4f}")
    print(f"AUC-PR: {result.auc_pr:.4f}")
    print(f"Valid: {result.is_valid}")
    print(f"Scored {len(result.scores)} users")
