"""GA4 report builder with configurable dimensions and metrics.

Connects to the Google Analytics 4 Data API to extract report data with
user-specified dimensions, metrics, date ranges, and filters. Supports
incremental loading by appending new date ranges to existing data files.

Dependencies:
    - google-analytics-data (google.analytics.data_v1beta)
    - pandas
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import unquote


@dataclass
class GA4ReportConfig:
    """Configuration for a GA4 Data API report request.

    Attributes:
        property_id: GA4 property ID (e.g., "properties/123456789").
        dimensions: List of GA4 dimension API names (e.g., ["date", "sessionSource"]).
        metrics: List of GA4 metric API names (e.g., ["sessions", "conversions"]).
        start_date: Report start date (inclusive).
        end_date: Report end date (inclusive).
        dimension_filter: Optional nested filter dict matching GA4 API filter syntax.
        metric_filter: Optional nested filter dict for metric-level filtering.
        order_by: Optional list of order-by specifications.
        limit: Maximum rows to return (default 10000).
        offset: Row offset for pagination (default 0).
    """

    property_id: str
    dimensions: list[str]
    metrics: list[str]
    start_date: date
    end_date: date
    dimension_filter: dict[str, Any] | None = None
    metric_filter: dict[str, Any] | None = None
    order_by: list[dict[str, Any]] | None = None
    limit: int = 10_000
    offset: int = 0


@dataclass
class GA4ReportResult:
    """Result container for a GA4 report extraction.

    Attributes:
        rows: List of dicts, each mapping dimension/metric names to values.
        row_count: Total number of rows returned.
        metadata: Additional response metadata (quota usage, etc.).
    """

    rows: list[dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


# Known source aliases for UTM normalization.
_SOURCE_ALIASES: dict[str, str] = {
    "google.com": "google",
    "www.google.com": "google",
    "facebook.com": "facebook",
    "www.facebook.com": "facebook",
    "fb": "facebook",
    "fb.com": "facebook",
    "instagram.com": "instagram",
    "www.instagram.com": "instagram",
    "ig": "instagram",
    "linkedin.com": "linkedin",
    "www.linkedin.com": "linkedin",
    "lnkd.in": "linkedin",
    "twitter.com": "twitter",
    "www.twitter.com": "twitter",
    "t.co": "twitter",
    "x.com": "twitter",
    "bing.com": "bing",
    "www.bing.com": "bing",
    "youtube.com": "youtube",
    "www.youtube.com": "youtube",
    "yt": "youtube",
}

_MEDIUM_ALIASES: dict[str, str] = {
    "referral": "referral",
    "ref": "referral",
    "cost-per-click": "cpc",
    "ppc": "cpc",
    "paid-search": "cpc",
    "paid search": "cpc",
    "email": "email",
    "e-mail": "email",
    "e_mail": "email",
    "social": "social",
    "social-media": "social",
    "organic": "organic",
    "none": "(none)",
    "(not set)": "(none)",
}


def build_report_request(config: GA4ReportConfig) -> dict[str, Any]:
    """Build a GA4 Data API RunReport request body from a config.

    Args:
        config: Report configuration specifying dimensions, metrics, dates,
            and optional filters.

    Returns:
        Dict matching the GA4 Data API RunReport JSON request schema.
    """
    request: dict[str, Any] = {
        "property": config.property_id,
        "dateRanges": [
            {
                "startDate": config.start_date.isoformat(),
                "endDate": config.end_date.isoformat(),
            }
        ],
        "dimensions": [{"name": dim} for dim in config.dimensions],
        "metrics": [{"name": metric} for metric in config.metrics],
        "limit": config.limit,
        "offset": config.offset,
    }

    if config.dimension_filter is not None:
        request["dimensionFilter"] = config.dimension_filter

    if config.metric_filter is not None:
        request["metricFilter"] = config.metric_filter

    if config.order_by is not None:
        request["orderBys"] = config.order_by

    return request


def execute_report(config: GA4ReportConfig) -> GA4ReportResult:
    """Execute a GA4 Data API report request and return parsed results.

    Authenticates using application default credentials or a service account
    key file specified by the GOOGLE_APPLICATION_CREDENTIALS env var.

    Args:
        config: Report configuration.

    Returns:
        GA4ReportResult with parsed rows and metadata.

    Raises:
        RuntimeError: If the API call fails or authentication is missing.
    """
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            FilterExpression,
            Metric,
            RunReportRequest,
        )
    except ImportError as exc:
        raise RuntimeError(
            "google-analytics-data package is required. "
            "Install with: pip install google-analytics-data"
        ) from exc

    try:
        client = BetaAnalyticsDataClient()
    except Exception as exc:
        raise RuntimeError(
            "Failed to initialize GA4 client. Ensure "
            "GOOGLE_APPLICATION_CREDENTIALS is set or application default "
            "credentials are configured."
        ) from exc

    all_rows: list[dict[str, Any]] = []
    current_offset = config.offset
    total_row_count = 0
    metadata: dict[str, Any] = {}

    while True:
        request_kwargs: dict[str, Any] = {
            "property": config.property_id,
            "date_ranges": [
                DateRange(
                    start_date=config.start_date.isoformat(),
                    end_date=config.end_date.isoformat(),
                )
            ],
            "dimensions": [Dimension(name=d) for d in config.dimensions],
            "metrics": [Metric(name=m) for m in config.metrics],
            "limit": config.limit,
            "offset": current_offset,
        }

        try:
            response = client.run_report(RunReportRequest(**request_kwargs))
        except Exception as exc:
            raise RuntimeError(f"GA4 API call failed: {exc}") from exc

        # Parse rows from the response.
        for row in response.rows:
            row_dict: dict[str, Any] = {}
            for i, dim_value in enumerate(row.dimension_values):
                row_dict[config.dimensions[i]] = dim_value.value
            for i, metric_value in enumerate(row.metric_values):
                raw = metric_value.value
                # Attempt numeric conversion.
                try:
                    row_dict[config.metrics[i]] = int(raw)
                except ValueError:
                    try:
                        row_dict[config.metrics[i]] = float(raw)
                    except ValueError:
                        row_dict[config.metrics[i]] = raw
            all_rows.append(row_dict)

        total_row_count = response.row_count

        # Capture quota metadata from the first page.
        if not metadata and hasattr(response, "property_quota") and response.property_quota:
            pq = response.property_quota
            metadata["tokens_per_day_remaining"] = (
                pq.tokens_per_day.remaining if pq.tokens_per_day else None
            )
            metadata["tokens_per_hour_remaining"] = (
                pq.tokens_per_hour.remaining if pq.tokens_per_hour else None
            )

        # Pagination: if we got a full page, there may be more rows.
        if len(response.rows) < config.limit:
            break
        current_offset += config.limit

    metadata["total_api_row_count"] = total_row_count

    return GA4ReportResult(
        rows=all_rows,
        row_count=len(all_rows),
        metadata=metadata,
    )


def normalize_utm_parameters(
    source: str,
    medium: str,
    campaign: str | None = None,
) -> tuple[str, str, str | None]:
    """Normalize UTM parameters for consistent source/medium grouping.

    Handles common inconsistencies: case differences, trailing whitespace,
    and URL-encoded characters.

    Args:
        source: Raw utm_source value.
        medium: Raw utm_medium value.
        campaign: Optional raw utm_campaign value.

    Returns:
        Tuple of (normalized_source, normalized_medium, normalized_campaign).
    """
    # Lowercase, strip whitespace, decode percent-encoded characters.
    norm_source = unquote(source).strip().lower()
    norm_medium = unquote(medium).strip().lower()
    norm_campaign: str | None = None
    if campaign is not None:
        norm_campaign = unquote(campaign).strip().lower()

    # Apply known source aliases.
    norm_source = _SOURCE_ALIASES.get(norm_source, norm_source)

    # Apply known medium aliases.
    norm_medium = _MEDIUM_ALIASES.get(norm_medium, norm_medium)

    # Normalize empty / sentinel values.
    if norm_source in ("", "(not set)", "(none)", "not set", "null"):
        norm_source = "(direct)"
    if norm_medium in ("", "(not set)", "not set", "null"):
        norm_medium = "(none)"
    if norm_campaign is not None and norm_campaign in (
        "",
        "(not set)",
        "not set",
        "null",
        "(none)",
    ):
        norm_campaign = None

    return norm_source, norm_medium, norm_campaign


def load_existing_data(output_path: Path) -> list[dict[str, Any]]:
    """Load previously extracted data for incremental appending.

    Args:
        output_path: Path to the existing CSV or JSON data file.

    Returns:
        List of row dicts from the existing file. Empty list if the file
        does not exist.
    """
    if not output_path.exists():
        return []

    suffix = output_path.suffix.lower()

    if suffix == ".json":
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "rows" in data:
            return data["rows"]
        return []

    if suffix == ".csv":
        rows: list[dict[str, Any]] = []
        with open(output_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Attempt numeric conversion for each value.
                parsed: dict[str, Any] = {}
                for k, v in row.items():
                    if v is None:
                        parsed[k] = v
                        continue
                    try:
                        parsed[k] = int(v)
                    except ValueError:
                        try:
                            parsed[k] = float(v)
                        except ValueError:
                            parsed[k] = v
                rows.append(parsed)
        return rows

    # Unsupported format — return empty.
    return []


def _deduplicate_rows(
    rows: list[dict[str, Any]],
    dimension_keys: list[str],
) -> list[dict[str, Any]]:
    """Remove duplicate rows based on dimension key columns.

    Later rows (i.e., freshly extracted data) take precedence over earlier
    rows when a duplicate key is found.
    """
    seen: dict[tuple[Any, ...], int] = {}
    for idx, row in enumerate(rows):
        key = tuple(row.get(k) for k in dimension_keys)
        seen[key] = idx  # Last occurrence wins.
    deduped_indices = sorted(seen.values())
    return [rows[i] for i in deduped_indices]


def _save_rows(rows: list[dict[str, Any]], output_path: Path) -> None:
    """Write rows to disk in the format indicated by the file extension."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = output_path.suffix.lower()

    if suffix == ".json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, default=str)
    else:
        # Default to CSV.
        if not rows:
            output_path.write_text("")
            return
        fieldnames = list(rows[0].keys())
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def extract_and_save(
    config: GA4ReportConfig,
    output_path: Path,
    incremental: bool = True,
) -> GA4ReportResult:
    """Extract a GA4 report and save results to disk.

    When incremental is True, appends new date range data to the existing
    file rather than overwriting. Deduplicates by date + dimension key.

    Args:
        config: Report configuration.
        output_path: Destination path for the output file.
        incremental: If True, append to existing data; if False, overwrite.

    Returns:
        GA4ReportResult for the newly extracted data.
    """
    result = execute_report(config)

    if incremental:
        existing_rows = load_existing_data(output_path)
        combined = existing_rows + result.rows
        deduped = _deduplicate_rows(combined, config.dimensions)
    else:
        deduped = result.rows

    _save_rows(deduped, output_path)

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract GA4 report data")
    parser.add_argument("--property-id", required=True, help="GA4 property ID")
    parser.add_argument("--dimensions", nargs="+", default=["date", "sessionSource", "sessionMedium"])
    parser.add_argument("--metrics", nargs="+", default=["sessions", "totalUsers", "conversions"])
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", default="workspace/raw/ga4_reports.csv")
    parser.add_argument("--no-incremental", action="store_true")

    args = parser.parse_args()

    report_config = GA4ReportConfig(
        property_id=args.property_id,
        dimensions=args.dimensions,
        metrics=args.metrics,
        start_date=date.fromisoformat(args.start_date),
        end_date=date.fromisoformat(args.end_date),
    )

    result = extract_and_save(
        config=report_config,
        output_path=Path(args.output),
        incremental=not args.no_incremental,
    )
    print(f"Extracted {result.row_count} rows")
