#!/usr/bin/env python3
"""Content performance analysis: topic clustering, decay detection, and
underperformer identification.

Maps content pages to topic clusters and measures cluster-level organic
performance. Detects content decay (pages with declining traffic over
configurable thresholds) and identifies underperformers with high
impressions but low CTR.

Usage:
    python content_analysis.py \
        --gsc-input workspace/raw/search_console.csv \
        --inventory workspace/raw/content_inventory.csv \
        --output workspace/analysis/content_performance.json

Inputs:
    - workspace/raw/search_console.csv (query, page, clicks, impressions,
      ctr, position, date)
    - workspace/raw/content_inventory.csv (url, title, category,
      publish_date)
    - workspace/processed/web_metrics.json (optional, from web-analytics)

Outputs:
    - workspace/analysis/content_performance.json with page-level and
      cluster-level metrics, decay flags, and underperformer flags
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
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class TopicCluster:
    """A group of related content pages forming a topic cluster."""

    cluster_name: str
    pillar_url: str | None
    page_urls: list[str] = field(default_factory=list)
    total_clicks: float = 0.0
    total_impressions: float = 0.0
    avg_position: float = 0.0
    avg_ctr: float = 0.0
    page_count: int = 0


@dataclass
class ContentDecayAlert:
    """A page flagged for significant traffic decline."""

    url: str
    title: str
    category: str
    peak_clicks_period: str
    current_clicks_period: str
    peak_clicks: float
    current_clicks: float
    decline_pct: float
    trend_p_value: float
    publish_date: str | None


@dataclass
class ContentUnderperformer:
    """A page with high impressions but low CTR, suggesting optimization
    potential in title or meta description."""

    url: str
    title: str
    impressions: float
    clicks: float
    ctr: float
    avg_position: float
    expected_ctr: float
    ctr_gap: float


def load_content_inventory(
    inventory_path: str | Path,
) -> pd.DataFrame:
    """Load and validate the content inventory CSV.

    Args:
        inventory_path: Path to content_inventory.csv.

    Returns:
        DataFrame with columns: url, title, category, publish_date.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If required columns are missing.
    """
    path = Path(inventory_path)
    if not path.exists():
        raise FileNotFoundError(f"Content inventory not found: {inventory_path}")

    df = pd.read_csv(path)

    required_columns = {"url", "title", "category", "publish_date"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["publish_date"] = pd.to_datetime(df["publish_date"], errors="coerce")
    logger.info("Loaded content inventory with %d pages", len(df))
    return df


def load_web_metrics(
    metrics_path: str | Path,
) -> dict[str, Any] | None:
    """Load web metrics JSON from the web-analytics skill (optional).

    Args:
        metrics_path: Path to web_metrics.json.

    Returns:
        Parsed JSON dict, or None if the file does not exist.
    """
    path = Path(metrics_path)
    if not path.exists():
        logger.info("Web metrics file not found at %s, skipping", metrics_path)
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info("Loaded web metrics from %s", metrics_path)
    return data


def map_to_topic_clusters(
    gsc_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    cluster_column: str = "category",
) -> list[TopicCluster]:
    """Map content pages to topic clusters and aggregate performance.

    Groups pages by the specified cluster column (default: category) from
    the content inventory and computes cluster-level metrics.

    Args:
        gsc_df: Search Console DataFrame aggregated to page level.
        inventory_df: Content inventory DataFrame with URL and category.
        cluster_column: Column in inventory_df to use for clustering.

    Returns:
        A list of TopicCluster objects with aggregated metrics.
    """
    # Aggregate GSC data to page level
    page_agg = (
        gsc_df.groupby("page")
        .agg(
            total_clicks=("clicks", "sum"),
            total_impressions=("impressions", "sum"),
            avg_position=("position", "mean"),
            avg_ctr=("ctr", "mean"),
        )
        .reset_index()
    )

    # Join with inventory on URL
    merged = page_agg.merge(
        inventory_df[["url", cluster_column]],
        left_on="page",
        right_on="url",
        how="inner",
    )

    clusters: list[TopicCluster] = []
    for cluster_name, group in merged.groupby(cluster_column):
        # Identify pillar page as the one with highest clicks
        pillar_idx = group["total_clicks"].idxmax()
        pillar_url = group.loc[pillar_idx, "page"]

        clusters.append(
            TopicCluster(
                cluster_name=str(cluster_name),
                pillar_url=pillar_url,
                page_urls=group["page"].tolist(),
                total_clicks=float(group["total_clicks"].sum()),
                total_impressions=float(group["total_impressions"].sum()),
                avg_position=round(float(group["avg_position"].mean()), 2),
                avg_ctr=round(float(group["avg_ctr"].mean()), 4),
                page_count=len(group),
            )
        )

    clusters.sort(key=lambda c: c.total_clicks, reverse=True)
    logger.info("Mapped pages to %d topic clusters", len(clusters))
    return clusters


def _mann_kendall_test(data: np.ndarray) -> tuple[float, float]:
    """Run a simplified Mann-Kendall trend test.

    Args:
        data: 1-D array of observations ordered in time.

    Returns:
        (tau, p_value) where tau is the Kendall tau statistic and
        p_value is the two-sided significance level.
    """
    n = len(data)
    if n < 3:
        return 0.0, 1.0

    # Use scipy's kendalltau with an ordinal time index
    x = np.arange(n, dtype=float)
    tau, p_value = stats.kendalltau(x, data)
    return float(tau), float(p_value)


def detect_content_decay(
    gsc_df: pd.DataFrame,
    inventory_df: pd.DataFrame | None = None,
    decline_threshold_pct: float = 20.0,
    lookback_days: int = 90,
    min_peak_clicks: float = 50.0,
) -> list[ContentDecayAlert]:
    """Detect pages with statistically significant traffic decline.

    Compares recent traffic to peak traffic within the lookback period.
    Uses a Mann-Kendall trend test to distinguish real decline from
    random noise.

    Args:
        gsc_df: Search Console DataFrame with date, page, and clicks.
        inventory_df: Optional content inventory for metadata enrichment.
        decline_threshold_pct: Minimum percentage decline to flag
            (default 20%).
        lookback_days: Number of days to analyze for trend (default 90).
        min_peak_clicks: Minimum peak-period clicks for a page to be
            eligible for decay detection (filters low-traffic pages).

    Returns:
        A list of ContentDecayAlert objects for flagged pages, sorted
        by decline percentage descending.
    """
    max_date = gsc_df["date"].max()
    lookback_start = max_date - pd.Timedelta(days=lookback_days)
    recent_df = gsc_df[gsc_df["date"] >= lookback_start].copy()

    # Aggregate clicks by page and week
    recent_df["week"] = recent_df["date"].dt.to_period("W")
    weekly = (
        recent_df.groupby(["page", "week"])
        .agg(weekly_clicks=("clicks", "sum"))
        .reset_index()
    )

    # Sort weeks for each page
    weekly["week_start"] = weekly["week"].apply(lambda w: w.start_time)
    weekly = weekly.sort_values(["page", "week_start"])

    # Build inventory lookup
    inv_lookup: dict[str, dict[str, Any]] = {}
    if inventory_df is not None:
        for _, row in inventory_df.iterrows():
            inv_lookup[row["url"]] = {
                "title": str(row.get("title", "")),
                "category": str(row.get("category", "")),
                "publish_date": (
                    row["publish_date"].strftime("%Y-%m-%d")
                    if pd.notna(row.get("publish_date"))
                    else None
                ),
            }

    alerts: list[ContentDecayAlert] = []

    for page, group in weekly.groupby("page"):
        if len(group) < 3:
            continue

        clicks_series = group["weekly_clicks"].values
        weeks = group["week_start"].values

        # Identify peak and current periods
        # Peak: best rolling 2-week window; Current: last 2 weeks
        if len(clicks_series) < 2:
            continue

        # Find peak 2-week period
        best_sum = 0.0
        best_idx = 0
        for i in range(len(clicks_series) - 1):
            window_sum = clicks_series[i] + clicks_series[i + 1]
            if window_sum > best_sum:
                best_sum = window_sum
                best_idx = i

        peak_clicks = float(best_sum)
        if peak_clicks < min_peak_clicks:
            continue

        # Current: last 2 weeks
        current_clicks = float(clicks_series[-2] + clicks_series[-1]) if len(clicks_series) >= 2 else float(clicks_series[-1])

        if peak_clicks == 0:
            continue

        decline_pct = ((peak_clicks - current_clicks) / peak_clicks) * 100.0

        if decline_pct < decline_threshold_pct:
            continue

        # Mann-Kendall trend test on weekly clicks
        tau, p_value = _mann_kendall_test(clicks_series)

        # Only flag if the trend is statistically significant (p < 0.05)
        # and tau is negative (declining)
        if p_value >= 0.05 or tau >= 0:
            continue

        # Format period labels
        peak_period = str(pd.Timestamp(weeks[best_idx]).date())
        current_period = str(pd.Timestamp(weeks[-2]).date()) if len(weeks) >= 2 else str(pd.Timestamp(weeks[-1]).date())

        meta = inv_lookup.get(str(page), {})
        alerts.append(
            ContentDecayAlert(
                url=str(page),
                title=meta.get("title", ""),
                category=meta.get("category", ""),
                peak_clicks_period=peak_period,
                current_clicks_period=current_period,
                peak_clicks=round(peak_clicks, 1),
                current_clicks=round(current_clicks, 1),
                decline_pct=round(decline_pct, 1),
                trend_p_value=round(p_value, 6),
                publish_date=meta.get("publish_date"),
            )
        )

    alerts.sort(key=lambda a: a.decline_pct, reverse=True)
    logger.info("Detected %d pages with content decay", len(alerts))
    return alerts


def identify_underperformers(
    gsc_df: pd.DataFrame,
    inventory_df: pd.DataFrame | None = None,
    min_impressions: float = 1000.0,
    ctr_gap_threshold: float = 0.02,
) -> list[ContentUnderperformer]:
    """Identify pages with high impressions but below-expected CTR.

    Computes expected CTR based on average position using a position-CTR
    curve, then flags pages where actual CTR falls significantly below
    expected CTR.

    Args:
        gsc_df: Search Console DataFrame with page-level metrics.
        inventory_df: Optional content inventory for metadata enrichment.
        min_impressions: Minimum impressions for a page to be evaluated
            (default 1000).
        ctr_gap_threshold: Minimum CTR gap (expected - actual) to flag
            a page (default 0.02, i.e., 2 percentage points).

    Returns:
        A list of ContentUnderperformer objects sorted by CTR gap
        descending.
    """
    # Aggregate to page level
    page_agg = (
        gsc_df.groupby("page")
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            avg_position=("position", "mean"),
        )
        .reset_index()
    )
    page_agg["ctr"] = page_agg["clicks"] / page_agg["impressions"].replace(0, np.nan)

    # Filter by minimum impressions
    eligible = page_agg[page_agg["impressions"] >= min_impressions].copy()

    if eligible.empty:
        return []

    # Build position-CTR curve from the overall dataset
    # Bucket positions into integer ranges and compute average CTR per bucket
    eligible["position_bucket"] = eligible["avg_position"].round(0).clip(1, 100).astype(int)

    position_ctr_curve = (
        eligible.groupby("position_bucket")["ctr"]
        .mean()
        .to_dict()
    )

    # Fallback CTR curve based on industry benchmarks for positions not in data
    default_ctr_curve = {
        1: 0.30, 2: 0.15, 3: 0.10, 4: 0.07, 5: 0.05,
        6: 0.04, 7: 0.03, 8: 0.025, 9: 0.02, 10: 0.015,
    }

    def get_expected_ctr(position: float) -> float:
        bucket = max(1, min(100, round(position)))
        if bucket in position_ctr_curve:
            return position_ctr_curve[bucket]
        if bucket in default_ctr_curve:
            return default_ctr_curve[bucket]
        # For positions > 10, decay proportionally
        return max(0.005, 0.015 * (10.0 / bucket))

    # Build inventory lookup
    inv_lookup: dict[str, str] = {}
    if inventory_df is not None:
        inv_lookup = dict(zip(inventory_df["url"], inventory_df["title"]))

    underperformers: list[ContentUnderperformer] = []
    for _, row in eligible.iterrows():
        expected = get_expected_ctr(row["avg_position"])
        actual = float(row["ctr"]) if pd.notna(row["ctr"]) else 0.0
        gap = expected - actual

        if gap >= ctr_gap_threshold:
            underperformers.append(
                ContentUnderperformer(
                    url=str(row["page"]),
                    title=inv_lookup.get(str(row["page"]), ""),
                    impressions=float(row["impressions"]),
                    clicks=float(row["clicks"]),
                    ctr=round(actual, 4),
                    avg_position=round(float(row["avg_position"]), 2),
                    expected_ctr=round(expected, 4),
                    ctr_gap=round(gap, 4),
                )
            )

    underperformers.sort(key=lambda u: u.ctr_gap, reverse=True)
    logger.info("Identified %d underperforming pages", len(underperformers))
    return underperformers


def score_content_freshness(
    inventory_df: pd.DataFrame,
    gsc_df: pd.DataFrame,
    stale_threshold_days: int = 180,
) -> pd.DataFrame:
    """Score content freshness and recommend update priorities.

    Combines content age (days since publish or last update) with
    current traffic to prioritize which pages would benefit most from
    a content refresh.

    Args:
        inventory_df: Content inventory with publish_date column.
        gsc_df: Search Console data for traffic context.
        stale_threshold_days: Days after which content is considered
            potentially stale (default 180).

    Returns:
        DataFrame with columns: url, title, days_since_publish,
        current_monthly_clicks, freshness_score, update_priority.
    """
    today = pd.Timestamp.now().normalize()

    # Compute days since publish
    inv = inventory_df.copy()
    inv["days_since_publish"] = (today - inv["publish_date"]).dt.days
    inv["days_since_publish"] = inv["days_since_publish"].fillna(0).astype(int)

    # Get recent 30-day traffic per page
    max_date = gsc_df["date"].max()
    recent_start = max_date - pd.Timedelta(days=30)
    recent_traffic = (
        gsc_df[gsc_df["date"] >= recent_start]
        .groupby("page")
        .agg(current_monthly_clicks=("clicks", "sum"))
        .reset_index()
    )

    result = inv.merge(
        recent_traffic,
        left_on="url",
        right_on="page",
        how="left",
    )
    result["current_monthly_clicks"] = result["current_monthly_clicks"].fillna(0)

    # Freshness score: 0 (fresh) to 1 (stale)
    # Normalized age with a sigmoid-like ramp around the stale threshold
    result["freshness_score"] = result["days_since_publish"].apply(
        lambda d: min(1.0, max(0.0, (d - stale_threshold_days / 2) / stale_threshold_days))
    )

    # Update priority: combine freshness score with traffic importance
    # High traffic + stale = highest priority
    max_clicks = result["current_monthly_clicks"].max()
    if max_clicks > 0:
        traffic_norm = result["current_monthly_clicks"] / max_clicks
    else:
        traffic_norm = 0.0

    result["update_priority_score"] = (
        result["freshness_score"] * 0.5 + traffic_norm * 0.5
    )

    # Assign priority labels
    def priority_label(score: float) -> str:
        if score >= 0.7:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"

    result["update_priority"] = result["update_priority_score"].apply(priority_label)

    output_cols = [
        "url", "title", "days_since_publish",
        "current_monthly_clicks", "freshness_score", "update_priority",
    ]
    # Keep only columns that exist
    output_cols = [c for c in output_cols if c in result.columns]

    result = result[output_cols].sort_values("freshness_score", ascending=False)
    logger.info("Scored freshness for %d pages", len(result))
    return result.reset_index(drop=True)


def generate_content_report(
    clusters: list[TopicCluster],
    decay_alerts: list[ContentDecayAlert],
    underperformers: list[ContentUnderperformer],
    freshness_df: pd.DataFrame | None = None,
    output_path: str | Path = "workspace/analysis/content_performance.json",
) -> dict[str, Any]:
    """Compile content analysis results into a structured JSON report.

    Args:
        clusters: Topic cluster performance data.
        decay_alerts: Pages flagged for traffic decay.
        underperformers: Pages with CTR optimization potential.
        freshness_df: Optional freshness scoring data.
        output_path: Destination file path for the JSON report.

    Returns:
        A summary dict with counts and the output path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "metadata": {
            "analysis_date": date.today().isoformat(),
        },
        "topic_clusters": [asdict(c) for c in clusters],
        "content_decay_alerts": [asdict(a) for a in decay_alerts],
        "underperformers": [asdict(u) for u in underperformers],
    }

    if freshness_df is not None and not freshness_df.empty:
        report["freshness_scores"] = freshness_df.to_dict(orient="records")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    summary = {
        "topic_clusters": len(clusters),
        "decay_alerts": len(decay_alerts),
        "underperformers": len(underperformers),
        "freshness_scored_pages": len(freshness_df) if freshness_df is not None else 0,
        "output_path": str(output_path),
    }

    logger.info("Content report written to %s", output_path)
    return summary


def run_content_analysis(
    gsc_input_path: str = "workspace/raw/search_console.csv",
    inventory_path: str = "workspace/raw/content_inventory.csv",
    web_metrics_path: str = "workspace/processed/web_metrics.json",
    output_path: str = "workspace/analysis/content_performance.json",
    decay_threshold_pct: float = 20.0,
    decay_lookback_days: int = 90,
    ctr_gap_threshold: float = 0.02,
    min_impressions: float = 1000.0,
) -> dict[str, Any]:
    """End-to-end content performance analysis pipeline.

    Orchestrates data loading, topic clustering, decay detection,
    underperformer identification, freshness scoring, and report
    generation.

    Args:
        gsc_input_path: Path to Search Console CSV.
        inventory_path: Path to content inventory CSV.
        web_metrics_path: Path to web metrics JSON (optional).
        output_path: Destination for the content performance JSON.
        decay_threshold_pct: Decline percentage threshold for decay.
        decay_lookback_days: Days to look back for decay detection.
        ctr_gap_threshold: CTR gap threshold for underperformers.
        min_impressions: Minimum impressions for underperformer analysis.

    Returns:
        A summary dict with counts and output file path.
    """
    # 1. Load GSC data
    gsc_path = Path(gsc_input_path)
    if not gsc_path.exists():
        raise FileNotFoundError(f"GSC input not found: {gsc_input_path}")

    gsc_df = pd.read_csv(gsc_path)
    required = {"query", "page", "clicks", "impressions", "ctr", "position", "date"}
    missing = required - set(gsc_df.columns)
    if missing:
        raise ValueError(f"GSC data missing columns: {missing}")
    gsc_df["date"] = pd.to_datetime(gsc_df["date"])

    # 2. Load content inventory
    inventory_df: pd.DataFrame | None = None
    try:
        inventory_df = load_content_inventory(inventory_path)
    except FileNotFoundError:
        logger.warning("Content inventory not found, some analyses will be limited")

    # 3. Load web metrics (optional)
    _web_metrics = load_web_metrics(web_metrics_path)

    # 4. Topic clustering
    clusters: list[TopicCluster] = []
    if inventory_df is not None:
        clusters = map_to_topic_clusters(gsc_df, inventory_df)

    # 5. Content decay detection
    decay_alerts = detect_content_decay(
        gsc_df,
        inventory_df=inventory_df,
        decline_threshold_pct=decay_threshold_pct,
        lookback_days=decay_lookback_days,
    )

    # 6. Underperformer identification
    underperformers = identify_underperformers(
        gsc_df,
        inventory_df=inventory_df,
        min_impressions=min_impressions,
        ctr_gap_threshold=ctr_gap_threshold,
    )

    # 7. Freshness scoring
    freshness_df: pd.DataFrame | None = None
    if inventory_df is not None:
        freshness_df = score_content_freshness(inventory_df, gsc_df)

    # 8. Generate report
    summary = generate_content_report(
        clusters=clusters,
        decay_alerts=decay_alerts,
        underperformers=underperformers,
        freshness_df=freshness_df,
        output_path=output_path,
    )

    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Content performance analysis"
    )
    parser.add_argument("--gsc-input", default="workspace/raw/search_console.csv")
    parser.add_argument("--inventory", default="workspace/raw/content_inventory.csv")
    parser.add_argument("--web-metrics", default="workspace/processed/web_metrics.json")
    parser.add_argument("--output", default="workspace/analysis/content_performance.json")
    parser.add_argument("--decay-threshold", type=float, default=20.0)
    parser.add_argument("--decay-lookback", type=int, default=90)
    parser.add_argument("--ctr-gap", type=float, default=0.02)

    args = parser.parse_args()

    result = run_content_analysis(
        gsc_input_path=args.gsc_input,
        inventory_path=args.inventory,
        web_metrics_path=args.web_metrics,
        output_path=args.output,
        decay_threshold_pct=args.decay_threshold,
        decay_lookback_days=args.decay_lookback,
        ctr_gap_threshold=args.ctr_gap,
    )
    print(json.dumps(result, indent=2))
