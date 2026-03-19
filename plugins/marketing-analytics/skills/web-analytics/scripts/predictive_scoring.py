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
from dataclasses import asdict, dataclass, field
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


# Cardinality threshold for treating a column as categorical.
_MAX_CATEGORICAL_CARDINALITY = 50


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
    # Validate target column.
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in DataFrame")

    y = df[target_column].copy()
    unique_targets = y.dropna().unique()
    if len(unique_targets) > 2:
        raise ValueError(
            f"Target column '{target_column}' must be binary, "
            f"found {len(unique_targets)} unique values: {unique_targets}"
        )
    # Convert to 0/1 if needed.
    y = y.astype(int)

    # Filter features to those actually present.
    available_features = [f for f in features if f in df.columns]
    if not available_features:
        raise ValueError(
            f"None of the specified features found in DataFrame. "
            f"Requested: {features}, Available: {list(df.columns)}"
        )

    X = df[available_features].copy()

    # Identify categorical vs. numeric columns.
    categorical_cols: list[str] = []
    numeric_cols: list[str] = []

    for col in X.columns:
        if X[col].dtype == "object" or X[col].dtype.name == "category":
            categorical_cols.append(col)
        elif pd.api.types.is_bool_dtype(X[col]):
            categorical_cols.append(col)
        elif X[col].nunique() <= _MAX_CATEGORICAL_CARDINALITY and X[col].dtype in (
            np.int64,
            np.int32,
            int,
        ):
            # Low-cardinality integer columns could be categorical IDs,
            # but we treat them as numeric unless they're clearly labels.
            numeric_cols.append(col)
        else:
            numeric_cols.append(col)

    # Impute missing values.
    for col in numeric_cols:
        if X[col].isna().any():
            median_val = X[col].median()
            X[col] = X[col].fillna(median_val)

    for col in categorical_cols:
        if X[col].isna().any():
            mode_val = X[col].mode()
            fill = mode_val.iloc[0] if len(mode_val) > 0 else "unknown"
            X[col] = X[col].fillna(fill)

    # One-hot encode categoricals.
    if categorical_cols:
        X = pd.get_dummies(X, columns=categorical_cols, drop_first=True, dtype=float)

    # Standardize numeric columns.
    for col in numeric_cols:
        std = X[col].std()
        mean = X[col].mean()
        if std > 0:
            X[col] = (X[col] - mean) / std
        else:
            X[col] = 0.0

    # Ensure all columns are float.
    X = X.astype(float)

    return X, y


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
    if date_column not in df.columns:
        raise ValueError(f"Date column '{date_column}' not found in DataFrame")

    dates = pd.to_datetime(df[date_column]).dt.date
    holdout_dt = holdout_date

    train_mask = dates < holdout_dt
    holdout_mask = dates >= holdout_dt

    train_df = df[train_mask].copy()
    holdout_df = df[holdout_mask].copy()

    if len(train_df) == 0:
        raise ValueError(
            f"Training set is empty. All {len(df)} records are on or after "
            f"holdout_date={holdout_date}"
        )
    if len(holdout_df) == 0:
        raise ValueError(
            f"Holdout set is empty. All {len(df)} records are before "
            f"holdout_date={holdout_date}"
        )

    return train_df, holdout_df


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
    from sklearn.linear_model import LogisticRegression

    weight = class_weight if class_weight != "none" else None

    model = LogisticRegression(
        C=regularization_strength,
        class_weight=weight,
        penalty="l2",
        solver="lbfgs",
        max_iter=1000,
        random_state=42,
    )
    model.fit(X_train, y_train)
    return model


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
    from sklearn.metrics import average_precision_score, roc_auc_score

    y_proba = model.predict_proba(X_holdout)[:, 1]

    # Handle edge case where holdout has only one class.
    unique_classes = y_holdout.unique()
    if len(unique_classes) < 2:
        # AUC is undefined with a single class — return 0.5 (random).
        return 0.5, float(y_holdout.mean())

    auc_roc = roc_auc_score(y_holdout, y_proba)
    auc_pr = average_precision_score(y_holdout, y_proba)

    return float(auc_roc), float(auc_pr)


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
    y_proba = model.predict_proba(X)[:, 1]

    scores_df = pd.DataFrame({
        "user_id": user_ids.values,
        "propensity_score": y_proba,
        "high_propensity": y_proba >= score_threshold,
    })

    scores_df = scores_df.sort_values("propensity_score", ascending=False).reset_index(
        drop=True
    )
    return scores_df


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
    coefs = model.coef_[0]
    intercept = float(model.intercept_[0])

    coef_dict = {
        name: float(coef) for name, coef in zip(feature_names, coefs)
    }

    # Sort by absolute value descending.
    coef_dict = dict(
        sorted(coef_dict.items(), key=lambda item: abs(item[1]), reverse=True)
    )

    return coef_dict, intercept


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
    if config is None:
        config = ScoringConfig()

    # Load data.
    suffix = input_path.suffix.lower()
    if suffix == ".json":
        df = pd.read_json(input_path)
    else:
        df = pd.read_csv(input_path)

    # Detect date column for temporal split.
    date_column: str | None = None
    for candidate in ("date", "event_date", "snapshot_date", "report_date", "observation_date"):
        if candidate in df.columns:
            date_column = candidate
            break

    # Determine holdout date if not specified.
    holdout_date = config.holdout_date
    if holdout_date is None and date_column is not None:
        dates = pd.to_datetime(df[date_column]).dt.date
        min_date = dates.min()
        max_date = dates.max()
        # Use 80/20 temporal split.
        range_days = (max_date - min_date).days
        holdout_date = min_date + pd.Timedelta(days=int(range_days * 0.8)).to_pytimedelta()

    # Detect user ID column.
    user_id_column: str | None = None
    for candidate in ("user_id", "customer_id", "client_id", "visitor_id"):
        if candidate in df.columns:
            user_id_column = candidate
            break

    # Temporal split.
    if date_column is not None and holdout_date is not None:
        train_df, holdout_df = temporal_train_test_split(df, date_column, holdout_date)
    else:
        # Fallback: last 20% as holdout (row-order preserving).
        split_idx = int(len(df) * 0.8)
        train_df = df.iloc[:split_idx].copy()
        holdout_df = df.iloc[split_idx:].copy()

    # Prepare features — fit on training, apply same encoding to holdout.
    # We prepare them together to ensure consistent one-hot columns,
    # then split back.
    combined = pd.concat([train_df, holdout_df], ignore_index=True)
    X_all, y_all = prepare_features(combined, config.features, config.target_column)

    n_train = len(train_df)
    X_train = X_all.iloc[:n_train]
    y_train = y_all.iloc[:n_train]
    X_holdout = X_all.iloc[n_train:]
    y_holdout = y_all.iloc[n_train:]

    # Fit model.
    model = fit_propensity_model(
        X_train, y_train, config.regularization_strength, config.class_weight
    )

    # Evaluate on holdout.
    auc_roc, auc_pr = evaluate_model(model, X_holdout, y_holdout)

    # Extract coefficients.
    feature_names = list(X_all.columns)
    coefficients, intercept = extract_coefficients(model, feature_names)

    # Score all users.
    user_ids = (
        combined[user_id_column]
        if user_id_column is not None
        else pd.Series(range(len(combined)), name="user_id")
    )
    scores_df = score_users(model, X_all, user_ids, config.score_threshold)

    # Compute positive rates.
    positive_rate_train = float(y_train.mean())
    positive_rate_holdout = float(y_holdout.mean())

    is_valid = auc_roc >= config.min_auc_threshold

    result = ScoringResult(
        model_type=config.model_type,
        auc_roc=auc_roc,
        auc_pr=auc_pr,
        coefficients=coefficients,
        intercept=intercept,
        holdout_size=len(holdout_df),
        training_size=len(train_df),
        positive_rate_train=positive_rate_train,
        positive_rate_holdout=positive_rate_holdout,
        is_valid=is_valid,
        scores=scores_df,
    )

    # Serialize results to JSON.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_dict: dict[str, Any] = {
        "model_type": result.model_type,
        "auc_roc": result.auc_roc,
        "auc_pr": result.auc_pr,
        "coefficients": result.coefficients,
        "intercept": result.intercept,
        "holdout_size": result.holdout_size,
        "training_size": result.training_size,
        "positive_rate_train": result.positive_rate_train,
        "positive_rate_holdout": result.positive_rate_holdout,
        "is_valid": result.is_valid,
        "scores": scores_df.to_dict(orient="records"),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_dict, f, indent=2, default=str)

    if not is_valid:
        raise ValueError(
            f"Model AUC-ROC ({auc_roc:.4f}) is below the minimum threshold "
            f"({config.min_auc_threshold}). Model may not be reliable."
        )

    return result


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
