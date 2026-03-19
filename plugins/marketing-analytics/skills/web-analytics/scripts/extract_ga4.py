"""GA4 report builder with configurable dimensions and metrics.

Connects to the Google Analytics 4 Data API to extract report data with
user-specified dimensions, metrics, date ranges, and filters. Supports
incremental loading by appending new date ranges to existing data files.

Dependencies:
    - google-analytics-data (google.analytics.data_v1beta)
    - pandas
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


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


def build_report_request(config: GA4ReportConfig) -> dict[str, Any]:
    """Build a GA4 Data API RunReport request body from a config.

    Args:
        config: Report configuration specifying dimensions, metrics, dates,
            and optional filters.

    Returns:
        Dict matching the GA4 Data API RunReport JSON request schema.
    """
    # TODO: Construct the request body dict from config fields.
    # Include dateRanges, dimensions, metrics, dimensionFilter, metricFilter,
    # orderBys, limit, and offset.
    raise NotImplementedError("build_report_request not yet implemented")


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
    # TODO: Initialize the BetaAnalyticsDataClient, call run_report,
    # parse the response rows into dicts, and populate GA4ReportResult.
    raise NotImplementedError("execute_report not yet implemented")


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
    # TODO: Lowercase, strip whitespace, decode percent-encoded chars,
    # apply known alias mappings (e.g., "google.com" -> "google").
    raise NotImplementedError("normalize_utm_parameters not yet implemented")


def load_existing_data(output_path: Path) -> list[dict[str, Any]]:
    """Load previously extracted data for incremental appending.

    Args:
        output_path: Path to the existing CSV or JSON data file.

    Returns:
        List of row dicts from the existing file. Empty list if the file
        does not exist.
    """
    # TODO: Read existing file, parse rows, return as list of dicts.
    # Support both CSV and JSON formats based on file extension.
    raise NotImplementedError("load_existing_data not yet implemented")


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
    # TODO: Call execute_report, optionally merge with existing data,
    # deduplicate, and write to output_path.
    raise NotImplementedError("extract_and_save not yet implemented")


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
