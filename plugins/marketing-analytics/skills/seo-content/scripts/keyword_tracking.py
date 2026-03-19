#!/usr/bin/env python3
"""Keyword position tracking, mover detection, and trend analysis.

Analyzes Google Search Console data to identify keyword ranking changes,
classify movers (improvements, declines, new, lost), and compute trend
metrics using 7-day rolling averages to smooth daily fluctuations.

Usage:
    python keyword_tracking.py \
        --input workspace/raw/search_console.csv \
        --output workspace/analysis/keyword_performance.json

Inputs:
    - workspace/raw/search_console.csv (query, page, clicks, impressions,
      ctr, position, date)

Outputs:
    - workspace/analysis/keyword_performance.json with ranking trends,
      movers, new/lost rankings
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class KeywordMover:
    """Represents a keyword with a significant position change."""

    query: str
    page: str
    previous_position: float
    current_position: float
    position_change: float
    direction: Literal["improved", "declined", "new", "lost"]
    previous_clicks: float
    current_clicks: float
    previous_impressions: float
    current_impressions: float


@dataclass
class KeywordTrend:
    """Rolling trend data for a single keyword."""

    query: str
    page: str
    dates: list[str] = field(default_factory=list)
    positions: list[float] = field(default_factory=list)
    clicks: list[float] = field(default_factory=list)
    impressions: list[float] = field(default_factory=list)
    rolling_avg_position: list[float] = field(default_factory=list)
    trend_direction: Literal["improving", "stable", "declining"] = "stable"
    trend_slope: float = 0.0


def load_search_console_data(input_path: str | Path) -> pd.DataFrame:
    """Load and validate Search Console CSV data.

    Args:
        input_path: Path to the search_console.csv file.

    Returns:
        A DataFrame with validated columns and parsed date types.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If required columns are missing.
    """
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(path)

    required_columns = {"query", "page", "clicks", "impressions", "ctr", "position", "date"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    logger.info(
        "Loaded %d rows from %s (date range: %s to %s)",
        len(df),
        input_path,
        df["date"].min().date(),
        df["date"].max().date(),
    )
    return df


def compute_rolling_averages(
    df: pd.DataFrame,
    window_days: int = 7,
    metrics: list[str] | None = None,
) -> pd.DataFrame:
    """Compute rolling averages for keyword metrics.

    Uses a 7-day rolling window (configurable) to smooth daily
    fluctuations in position, clicks, and impressions per keyword-page
    pair.

    Args:
        df: Search Console DataFrame with date, query, page, and metric
            columns.
        window_days: Rolling window size in days (default 7).
        metrics: Metric columns to smooth. Defaults to
            ["position", "clicks", "impressions"].

    Returns:
        DataFrame with additional rolling average columns named
        "{metric}_rolling_{window_days}d".
    """
    if metrics is None:
        metrics = ["position", "clicks", "impressions"]

    df = df.sort_values(["query", "page", "date"]).copy()

    for metric in metrics:
        col_name = f"{metric}_rolling_{window_days}d"
        df[col_name] = (
            df.groupby(["query", "page"])[metric]
            .transform(lambda s: s.rolling(window=window_days, min_periods=1).mean())
        )

    logger.info(
        "Computed %d-day rolling averages for metrics: %s",
        window_days,
        metrics,
    )
    return df


def detect_position_changes(
    df: pd.DataFrame,
    current_period_days: int = 7,
    comparison_period_days: int = 7,
    threshold: float = 5.0,
) -> list[KeywordMover]:
    """Detect keywords with significant position changes.

    Compares the average position in the current period to the comparison
    period. Keywords with position change greater than the threshold are
    classified as movers.

    Args:
        df: Search Console DataFrame with rolling averages applied.
        current_period_days: Number of recent days for the current period.
        comparison_period_days: Number of days for the prior comparison
            period (immediately preceding the current period).
        threshold: Minimum absolute position change to qualify as a mover
            (default 5.0 positions).

    Returns:
        A list of KeywordMover objects sorted by absolute position change
        descending.
    """
    max_date = df["date"].max()
    current_start = max_date - pd.Timedelta(days=current_period_days - 1)
    comparison_end = current_start - pd.Timedelta(days=1)
    comparison_start = comparison_end - pd.Timedelta(days=comparison_period_days - 1)

    current_df = df[df["date"] >= current_start]
    comparison_df = df[(df["date"] >= comparison_start) & (df["date"] <= comparison_end)]

    current_agg = (
        current_df.groupby(["query", "page"])
        .agg(
            current_position=("position", "mean"),
            current_clicks=("clicks", "sum"),
            current_impressions=("impressions", "sum"),
        )
        .reset_index()
    )

    comparison_agg = (
        comparison_df.groupby(["query", "page"])
        .agg(
            previous_position=("position", "mean"),
            previous_clicks=("clicks", "sum"),
            previous_impressions=("impressions", "sum"),
        )
        .reset_index()
    )

    merged = current_agg.merge(comparison_agg, on=["query", "page"], how="inner")
    merged["position_change"] = merged["previous_position"] - merged["current_position"]

    # Filter by threshold
    significant = merged[merged["position_change"].abs() >= threshold]

    movers: list[KeywordMover] = []
    for _, row in significant.iterrows():
        direction: Literal["improved", "declined"] = (
            "improved" if row["position_change"] > 0 else "declined"
        )
        movers.append(
            KeywordMover(
                query=row["query"],
                page=row["page"],
                previous_position=round(float(row["previous_position"]), 2),
                current_position=round(float(row["current_position"]), 2),
                position_change=round(float(row["position_change"]), 2),
                direction=direction,
                previous_clicks=float(row["previous_clicks"]),
                current_clicks=float(row["current_clicks"]),
                previous_impressions=float(row["previous_impressions"]),
                current_impressions=float(row["current_impressions"]),
            )
        )

    movers.sort(key=lambda m: abs(m.position_change), reverse=True)
    logger.info("Detected %d keyword movers (threshold=%.1f)", len(movers), threshold)
    return movers


def identify_new_keywords(
    df: pd.DataFrame,
    current_period_days: int = 7,
    lookback_days: int = 30,
) -> list[KeywordMover]:
    """Identify keywords that appeared in search results for the first time.

    A keyword is "new" if it has impressions in the current period but
    zero impressions in the lookback period.

    Args:
        df: Search Console DataFrame.
        current_period_days: Number of recent days to check for presence.
        lookback_days: Number of prior days to check for absence.

    Returns:
        A list of KeywordMover objects with direction="new".
    """
    max_date = df["date"].max()
    current_start = max_date - pd.Timedelta(days=current_period_days - 1)
    lookback_end = current_start - pd.Timedelta(days=1)
    lookback_start = lookback_end - pd.Timedelta(days=lookback_days - 1)

    current_df = df[df["date"] >= current_start]
    lookback_df = df[(df["date"] >= lookback_start) & (df["date"] <= lookback_end)]

    current_keys = set(
        current_df.groupby(["query", "page"]).groups.keys()
    )
    lookback_keys = set(
        lookback_df.groupby(["query", "page"]).groups.keys()
    ) if len(lookback_df) > 0 else set()

    new_keys = current_keys - lookback_keys

    new_keywords: list[KeywordMover] = []
    for query, page in new_keys:
        subset = current_df[(current_df["query"] == query) & (current_df["page"] == page)]
        new_keywords.append(
            KeywordMover(
                query=query,
                page=page,
                previous_position=0.0,
                current_position=round(float(subset["position"].mean()), 2),
                position_change=0.0,
                direction="new",
                previous_clicks=0.0,
                current_clicks=float(subset["clicks"].sum()),
                previous_impressions=0.0,
                current_impressions=float(subset["impressions"].sum()),
            )
        )

    new_keywords.sort(key=lambda m: m.current_impressions, reverse=True)
    logger.info("Identified %d new keywords", len(new_keywords))
    return new_keywords


def identify_lost_keywords(
    df: pd.DataFrame,
    current_period_days: int = 7,
    lookback_days: int = 30,
) -> list[KeywordMover]:
    """Identify keywords that dropped out of search results.

    A keyword is "lost" if it had impressions in the lookback period but
    zero impressions in the current period.

    Args:
        df: Search Console DataFrame.
        current_period_days: Number of recent days to check for absence.
        lookback_days: Number of prior days to check for prior presence.

    Returns:
        A list of KeywordMover objects with direction="lost".
    """
    max_date = df["date"].max()
    current_start = max_date - pd.Timedelta(days=current_period_days - 1)
    lookback_end = current_start - pd.Timedelta(days=1)
    lookback_start = lookback_end - pd.Timedelta(days=lookback_days - 1)

    current_df = df[df["date"] >= current_start]
    lookback_df = df[(df["date"] >= lookback_start) & (df["date"] <= lookback_end)]

    current_keys = set(
        current_df.groupby(["query", "page"]).groups.keys()
    ) if len(current_df) > 0 else set()
    lookback_keys = set(
        lookback_df.groupby(["query", "page"]).groups.keys()
    ) if len(lookback_df) > 0 else set()

    lost_keys = lookback_keys - current_keys

    lost_keywords: list[KeywordMover] = []
    for query, page in lost_keys:
        subset = lookback_df[
            (lookback_df["query"] == query) & (lookback_df["page"] == page)
        ]
        lost_keywords.append(
            KeywordMover(
                query=query,
                page=page,
                previous_position=round(float(subset["position"].mean()), 2),
                current_position=0.0,
                position_change=0.0,
                direction="lost",
                previous_clicks=float(subset["clicks"].sum()),
                current_clicks=0.0,
                previous_impressions=float(subset["impressions"].sum()),
                current_impressions=0.0,
            )
        )

    lost_keywords.sort(key=lambda m: m.previous_impressions, reverse=True)
    logger.info("Identified %d lost keywords", len(lost_keywords))
    return lost_keywords


def compute_keyword_trends(
    df: pd.DataFrame,
    min_impressions: int = 100,
    window_days: int = 7,
) -> list[KeywordTrend]:
    """Compute trend data for each keyword over the full date range.

    Fits a linear regression on the rolling average position over time
    to determine trend direction and slope. Only includes keywords with
    sufficient impression volume.

    Args:
        df: Search Console DataFrame with rolling averages.
        min_impressions: Minimum total impressions to include a keyword
            in trend analysis.
        window_days: Rolling window used for smoothed position values.

    Returns:
        A list of KeywordTrend objects with slope and direction
        classification (improving if slope < -0.5, declining if > 0.5,
        stable otherwise).
    """
    rolling_col = f"position_rolling_{window_days}d"
    if rolling_col not in df.columns:
        df = compute_rolling_averages(df, window_days=window_days, metrics=["position"])

    # Filter by minimum impressions
    kw_impressions = df.groupby(["query", "page"])["impressions"].sum()
    eligible = kw_impressions[kw_impressions >= min_impressions].index

    trends: list[KeywordTrend] = []
    for query, page in eligible:
        subset = df[(df["query"] == query) & (df["page"] == page)].sort_values("date")
        if len(subset) < 2:
            continue

        dates = subset["date"].dt.strftime("%Y-%m-%d").tolist()
        positions = subset["position"].tolist()
        clicks = subset["clicks"].tolist()
        impressions = subset["impressions"].tolist()
        rolling_positions = subset[rolling_col].tolist()

        # Fit linear regression: position vs. ordinal day index
        x = np.arange(len(subset), dtype=float)
        y = np.array(rolling_positions, dtype=float)
        valid_mask = ~np.isnan(y)
        if valid_mask.sum() < 2:
            continue

        x_valid = x[valid_mask]
        y_valid = y[valid_mask]
        coeffs = np.polyfit(x_valid, y_valid, 1)
        slope = float(coeffs[0])

        # Classify trend: lower position = better ranking, so negative slope = improving
        if slope < -0.5:
            direction: Literal["improving", "stable", "declining"] = "improving"
        elif slope > 0.5:
            direction = "declining"
        else:
            direction = "stable"

        trends.append(
            KeywordTrend(
                query=query,
                page=page,
                dates=dates,
                positions=[round(p, 2) for p in positions],
                clicks=[round(c, 2) for c in clicks],
                impressions=[round(i, 2) for i in impressions],
                rolling_avg_position=[round(r, 2) if not np.isnan(r) else None for r in rolling_positions],
                trend_direction=direction,
                trend_slope=round(slope, 4),
            )
        )

    logger.info(
        "Computed trends for %d keywords (min_impressions=%d)",
        len(trends),
        min_impressions,
    )
    return trends


def identify_organic_paid_overlap(
    df: pd.DataFrame,
    paid_keywords_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Find keywords where the site ranks organically and also runs paid ads.

    Cross-references organic keyword data with a paid keyword list to
    identify cost-saving opportunities.

    Args:
        df: Search Console DataFrame with organic keyword data.
        paid_keywords_path: Path to a CSV of paid keywords (must have a
            "keyword" column). If None, returns an empty list.

    Returns:
        A list of dicts with query, organic_position, organic_clicks,
        and estimated_savings_opportunity flag.
    """
    if paid_keywords_path is None:
        return []

    paid_path = Path(paid_keywords_path)
    if not paid_path.exists():
        logger.warning("Paid keywords file not found: %s", paid_keywords_path)
        return []

    paid_df = pd.read_csv(paid_path)
    if "keyword" not in paid_df.columns:
        logger.warning("Paid keywords CSV missing 'keyword' column")
        return []

    paid_keywords = set(paid_df["keyword"].str.lower().str.strip())

    # Aggregate organic data per query
    organic_agg = (
        df.groupby("query")
        .agg(
            organic_position=("position", "mean"),
            organic_clicks=("clicks", "sum"),
            organic_impressions=("impressions", "sum"),
        )
        .reset_index()
    )

    organic_agg["query_lower"] = organic_agg["query"].str.lower().str.strip()
    overlap = organic_agg[organic_agg["query_lower"].isin(paid_keywords)]

    results: list[dict[str, Any]] = []
    for _, row in overlap.iterrows():
        # Flag keywords ranking in top 3 organically as savings opportunities
        savings_opportunity = row["organic_position"] <= 3.0
        results.append({
            "query": row["query"],
            "organic_position": round(float(row["organic_position"]), 2),
            "organic_clicks": float(row["organic_clicks"]),
            "organic_impressions": float(row["organic_impressions"]),
            "estimated_savings_opportunity": savings_opportunity,
        })

    results.sort(key=lambda r: r["organic_clicks"], reverse=True)
    logger.info("Found %d organic/paid keyword overlaps", len(results))
    return results


def generate_keyword_report(
    movers: list[KeywordMover],
    new_keywords: list[KeywordMover],
    lost_keywords: list[KeywordMover],
    trends: list[KeywordTrend],
    overlap: list[dict[str, Any]],
    output_path: str | Path = "workspace/analysis/keyword_performance.json",
) -> dict[str, Any]:
    """Compile keyword tracking results into a structured JSON report.

    Args:
        movers: Keywords with significant position changes.
        new_keywords: Newly discovered keywords.
        lost_keywords: Keywords that dropped from results.
        trends: Trend data for tracked keywords.
        overlap: Organic/paid keyword overlap data.
        output_path: Destination file path for the JSON report.

    Returns:
        A summary dict with counts for each category and the output path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Classify movers
    improved = [m for m in movers if m.direction == "improved"]
    declined = [m for m in movers if m.direction == "declined"]

    # Classify trends
    improving_trends = [t for t in trends if t.trend_direction == "improving"]
    declining_trends = [t for t in trends if t.trend_direction == "declining"]
    stable_trends = [t for t in trends if t.trend_direction == "stable"]

    report = {
        "metadata": {
            "analysis_date": date.today().isoformat(),
            "total_keywords_tracked": len(trends),
        },
        "movers": {
            "improved": [asdict(m) for m in improved],
            "declined": [asdict(m) for m in declined],
        },
        "new_keywords": [asdict(m) for m in new_keywords],
        "lost_keywords": [asdict(m) for m in lost_keywords],
        "trends": {
            "improving": [asdict(t) for t in improving_trends],
            "declining": [asdict(t) for t in declining_trends],
            "stable_count": len(stable_trends),
        },
        "organic_paid_overlap": overlap,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    summary = {
        "movers_improved": len(improved),
        "movers_declined": len(declined),
        "new_keywords": len(new_keywords),
        "lost_keywords": len(lost_keywords),
        "trends_improving": len(improving_trends),
        "trends_declining": len(declining_trends),
        "trends_stable": len(stable_trends),
        "organic_paid_overlaps": len(overlap),
        "output_path": str(output_path),
    }

    logger.info("Keyword report written to %s", output_path)
    return summary


def run_keyword_tracking(
    input_path: str = "workspace/raw/search_console.csv",
    output_path: str = "workspace/analysis/keyword_performance.json",
    paid_keywords_path: str | None = None,
    position_change_threshold: float = 5.0,
    rolling_window_days: int = 7,
    min_impressions: int = 100,
) -> dict[str, Any]:
    """End-to-end keyword tracking pipeline.

    Orchestrates data loading, rolling average computation, mover
    detection, new/lost keyword identification, trend analysis, and
    report generation.

    Args:
        input_path: Path to the Search Console CSV.
        output_path: Destination for the keyword performance JSON.
        paid_keywords_path: Optional path to paid keyword CSV.
        position_change_threshold: Minimum position change for movers.
        rolling_window_days: Rolling average window size.
        min_impressions: Minimum impressions for trend analysis.

    Returns:
        A summary dict with counts and output file path.
    """
    # 1. Load data
    df = load_search_console_data(input_path)

    # 2. Compute rolling averages
    df = compute_rolling_averages(df, window_days=rolling_window_days)

    # 3. Detect position changes
    movers = detect_position_changes(
        df, threshold=position_change_threshold
    )

    # 4. Identify new and lost keywords
    new_keywords = identify_new_keywords(df)
    lost_keywords = identify_lost_keywords(df)

    # 5. Compute trends
    trends = compute_keyword_trends(
        df, min_impressions=min_impressions, window_days=rolling_window_days
    )

    # 6. Organic/paid overlap
    overlap = identify_organic_paid_overlap(df, paid_keywords_path)

    # 7. Generate report
    summary = generate_keyword_report(
        movers=movers,
        new_keywords=new_keywords,
        lost_keywords=lost_keywords,
        trends=trends,
        overlap=overlap,
        output_path=output_path,
    )

    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Keyword position tracking and trend analysis"
    )
    parser.add_argument("--input", default="workspace/raw/search_console.csv")
    parser.add_argument("--output", default="workspace/analysis/keyword_performance.json")
    parser.add_argument("--paid-keywords", default=None, help="Path to paid keyword CSV")
    parser.add_argument("--threshold", type=float, default=5.0, help="Position change threshold")
    parser.add_argument("--window", type=int, default=7, help="Rolling window days")

    args = parser.parse_args()

    result = run_keyword_tracking(
        input_path=args.input,
        output_path=args.output,
        paid_keywords_path=args.paid_keywords,
        position_change_threshold=args.threshold,
        rolling_window_days=args.window,
    )
    print(json.dumps(result, indent=2))
