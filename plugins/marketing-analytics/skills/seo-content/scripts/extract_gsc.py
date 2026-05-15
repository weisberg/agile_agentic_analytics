#!/usr/bin/env python3
"""Google Search Console data extraction with automated date range handling.

Extracts search performance data from the Google Search Console API,
handling pagination for high-volume sites (25,000 row limit per request)
and optional date range chunking for very large datasets.

Usage:
    python extract_gsc.py --site-url https://example.com \
        --start-date 2025-01-01 --end-date 2025-03-31 \
        --output workspace/raw/search_console.csv

Inputs:
    - Google Search Console API credentials (service account JSON)
    - Site URL registered in GSC
    - Date range for extraction

Outputs:
    - workspace/raw/search_console.csv with columns:
      query, page, clicks, impressions, ctr, position, date, device, country
"""

from __future__ import annotations

import csv
import json
import logging
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def authenticate_gsc(credentials_path: str) -> Any:
    """Authenticate with Google Search Console API using a service account.

    Args:
        credentials_path: Path to the service account JSON key file.

    Returns:
        An authenticated GSC service resource object.

    Raises:
        FileNotFoundError: If the credentials file does not exist.
        ValueError: If the credentials file is malformed.
    """
    cred_path = Path(credentials_path)
    if not cred_path.exists():
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError(
            "google-auth and google-api-python-client are required. "
            "Install with: pip install google-auth google-api-python-client"
        )

    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        raise ValueError(f"Malformed credentials file: {credentials_path}") from exc

    service = build("webmasters", "v3", credentials=credentials)
    logger.info("Successfully authenticated with Google Search Console API")
    return service


def build_query_request(
    start_date: date,
    end_date: date,
    dimensions: list[str] | None = None,
    search_type: str = "web",
    row_limit: int = 25_000,
    start_row: int = 0,
    dimension_filters: list[dict[str, Any]] | None = None,
    data_state: str = "final",
    aggregation_type: str = "auto",
) -> dict[str, Any]:
    """Build a Search Analytics query request payload.

    Args:
        start_date: Inclusive start date for the query.
        end_date: Inclusive end date for the query.
        dimensions: Grouping dimensions. Defaults to
            ["query", "page", "date"].
        search_type: Search type filter: "web", "image", "video", "news",
            "discover", or "googleNews".
        row_limit: Maximum rows per response (max 25,000).
        start_row: Zero-based row offset for pagination.
        dimension_filters: Optional list of dimension filter group dicts.
        data_state: "final" for stable data, "all" to include preliminary.
        aggregation_type: "auto", "byPage", or "byProperty".

    Returns:
        A dict representing the API request body.
    """
    if dimensions is None:
        dimensions = ["query", "page", "date"]

    row_limit = min(row_limit, 25_000)

    request_body: dict[str, Any] = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "dimensions": dimensions,
        "type": search_type,
        "rowLimit": row_limit,
        "startRow": start_row,
        "dataState": data_state,
        "aggregationType": aggregation_type,
    }

    if dimension_filters:
        request_body["dimensionFilterGroups"] = dimension_filters

    return request_body


def execute_paginated_query(
    service: Any,
    site_url: str,
    start_date: date,
    end_date: date,
    dimensions: list[str] | None = None,
    search_type: str = "web",
    dimension_filters: list[dict[str, Any]] | None = None,
    max_rows: int | None = None,
) -> list[dict[str, Any]]:
    """Execute a Search Console query with automatic pagination.

    Handles the 25,000 row limit by issuing sequential requests with
    incrementing startRow until all data is retrieved.

    Args:
        service: Authenticated GSC service resource.
        site_url: The site URL as registered in GSC (including protocol).
        start_date: Inclusive start date.
        end_date: Inclusive end date.
        dimensions: Grouping dimensions.
        search_type: Type of search results to query.
        dimension_filters: Optional filters to apply.
        max_rows: Optional cap on total rows to retrieve.

    Returns:
        A list of row dicts with keys matching the requested dimensions
        plus clicks, impressions, ctr, and position.

    Raises:
        RuntimeError: If the API returns an error response.
    """
    if dimensions is None:
        dimensions = ["query", "page", "date"]

    all_rows: list[dict[str, Any]] = []
    row_limit = 25_000
    start_row = 0
    max_retries = 5

    while True:
        request_body = build_query_request(
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions,
            search_type=search_type,
            row_limit=row_limit,
            start_row=start_row,
            dimension_filters=dimension_filters,
        )

        response = None
        for attempt in range(max_retries):
            try:
                response = service.searchanalytics().query(siteUrl=site_url, body=request_body).execute()
                break
            except Exception as exc:
                exc_str = str(exc)
                # Handle rate limiting (HTTP 429) with exponential backoff
                if "429" in exc_str or "rate" in exc_str.lower():
                    wait_time = 2**attempt
                    logger.warning(
                        "Rate limited, retrying in %ds (attempt %d/%d)",
                        wait_time,
                        attempt + 1,
                        max_retries,
                    )
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(f"GSC API error: {exc}") from exc

        if response is None:
            raise RuntimeError("GSC API request failed after all retries")

        rows = response.get("rows", [])
        all_rows.extend(rows)

        logger.info(
            "Fetched %d rows (startRow=%d, total so far=%d)",
            len(rows),
            start_row,
            len(all_rows),
        )

        # Stop conditions
        if len(rows) < row_limit:
            break

        start_row += row_limit

        if max_rows is not None and len(all_rows) >= max_rows:
            all_rows = all_rows[:max_rows]
            break

    return all_rows


def extract_with_date_chunking(
    service: Any,
    site_url: str,
    start_date: date,
    end_date: date,
    chunk_days: int = 7,
    dimensions: list[str] | None = None,
    search_type: str = "web",
    dimension_filters: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Extract GSC data using date range chunking for very large sites.

    Splits the overall date range into smaller chunks (default 7 days)
    and runs paginated queries for each chunk. Reduces per-request result
    sizes and improves reliability.

    Args:
        service: Authenticated GSC service resource.
        site_url: The site URL as registered in GSC.
        start_date: Overall start date.
        end_date: Overall end date.
        chunk_days: Number of days per chunk (default 7).
        dimensions: Grouping dimensions.
        search_type: Type of search results to query.
        dimension_filters: Optional filters to apply.

    Returns:
        Combined list of row dicts across all date chunks.
    """
    # Generate date chunks
    chunks: list[tuple[date, date]] = []
    chunk_start = start_date
    while chunk_start <= end_date:
        chunk_end = min(chunk_start + timedelta(days=chunk_days - 1), end_date)
        chunks.append((chunk_start, chunk_end))
        chunk_start = chunk_end + timedelta(days=1)

    all_rows: list[dict[str, Any]] = []
    total_chunks = len(chunks)

    for idx, (cs, ce) in enumerate(chunks, 1):
        logger.info(
            "Processing chunk %d/%d: %s to %s",
            idx,
            total_chunks,
            cs.isoformat(),
            ce.isoformat(),
        )

        chunk_rows = execute_paginated_query(
            service=service,
            site_url=site_url,
            start_date=cs,
            end_date=ce,
            dimensions=dimensions,
            search_type=search_type,
            dimension_filters=dimension_filters,
        )
        all_rows.extend(chunk_rows)

        logger.info(
            "Chunk %d/%d complete: %d rows (total: %d)",
            idx,
            total_chunks,
            len(chunk_rows),
            len(all_rows),
        )

    return all_rows


def flatten_gsc_rows(
    rows: list[dict[str, Any]],
    dimensions: list[str],
) -> list[dict[str, Any]]:
    """Flatten GSC API response rows into a tabular format.

    The GSC API returns dimension values as an ordered list in a "keys"
    field. This function maps those positional values to named columns.

    Args:
        rows: Raw response rows from the GSC API.
        dimensions: The dimension names in the order they were requested.

    Returns:
        A list of flat dicts with dimension names as keys plus metric
        columns (clicks, impressions, ctr, position).
    """
    flat_rows: list[dict[str, Any]] = []
    for row in rows:
        flat: dict[str, Any] = {}
        keys = row.get("keys", [])
        for i, dim in enumerate(dimensions):
            flat[dim] = keys[i] if i < len(keys) else None
        flat["clicks"] = row.get("clicks", 0.0)
        flat["impressions"] = row.get("impressions", 0.0)
        flat["ctr"] = row.get("ctr", 0.0)
        flat["position"] = row.get("position", 0.0)
        flat_rows.append(flat)
    return flat_rows


def save_to_csv(
    rows: list[dict[str, Any]],
    output_path: str | Path,
    columns: list[str] | None = None,
) -> int:
    """Save extracted GSC data to a CSV file.

    Args:
        rows: Flattened row dicts to write.
        output_path: Destination file path.
        columns: Optional explicit column ordering. If None, uses keys
            from the first row.

    Returns:
        The number of rows written.

    Raises:
        ValueError: If rows is empty.
    """
    if not rows:
        raise ValueError("Cannot write CSV: rows list is empty")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if columns is None:
        columns = list(rows[0].keys())

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    logger.info("Wrote %d rows to %s", len(rows), output_path)
    return len(rows)


def extract_gsc_data(
    credentials_path: str,
    site_url: str,
    start_date: str,
    end_date: str,
    output_path: str = "workspace/raw/search_console.csv",
    dimensions: list[str] | None = None,
    search_type: str = "web",
    use_date_chunking: bool = False,
    chunk_days: int = 7,
) -> dict[str, Any]:
    """End-to-end Search Console data extraction pipeline.

    Orchestrates authentication, query execution (with optional date
    chunking), row flattening, and CSV export.

    Args:
        credentials_path: Path to service account JSON credentials.
        site_url: GSC site URL (e.g., "https://example.com").
        start_date: Start date as "YYYY-MM-DD" string.
        end_date: End date as "YYYY-MM-DD" string.
        output_path: Destination CSV file path.
        dimensions: Grouping dimensions. Defaults to
            ["query", "page", "date"].
        search_type: Search type filter.
        use_date_chunking: Whether to split into weekly chunks.
        chunk_days: Days per chunk if chunking is enabled.

    Returns:
        A summary dict with keys: row_count, date_range, output_path,
        extraction_duration_seconds.
    """
    pipeline_start = time.time()

    if dimensions is None:
        dimensions = ["query", "page", "date"]

    # 1. Authenticate
    service = authenticate_gsc(credentials_path)

    # 2. Parse date strings
    sd = date.fromisoformat(start_date)
    ed = date.fromisoformat(end_date)

    # 3. Execute query
    if use_date_chunking:
        raw_rows = extract_with_date_chunking(
            service=service,
            site_url=site_url,
            start_date=sd,
            end_date=ed,
            chunk_days=chunk_days,
            dimensions=dimensions,
            search_type=search_type,
        )
    else:
        raw_rows = execute_paginated_query(
            service=service,
            site_url=site_url,
            start_date=sd,
            end_date=ed,
            dimensions=dimensions,
            search_type=search_type,
        )

    # 4. Flatten rows
    flat_rows = flatten_gsc_rows(raw_rows, dimensions)

    # 5. Save to CSV
    row_count = save_to_csv(flat_rows, output_path)

    # 6. Return summary
    duration = time.time() - pipeline_start
    return {
        "row_count": row_count,
        "date_range": {"start": start_date, "end": end_date},
        "output_path": str(output_path),
        "extraction_duration_seconds": round(duration, 2),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract Google Search Console data")
    parser.add_argument("--credentials", required=True, help="Path to service account JSON")
    parser.add_argument("--site-url", required=True, help="GSC site URL")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", default="workspace/raw/search_console.csv", help="Output CSV path")
    parser.add_argument("--chunked", action="store_true", help="Use date chunking for large sites")
    parser.add_argument("--chunk-days", type=int, default=7, help="Days per chunk")

    args = parser.parse_args()

    result = extract_gsc_data(
        credentials_path=args.credentials,
        site_url=args.site_url,
        start_date=args.start_date,
        end_date=args.end_date,
        output_path=args.output,
        use_date_chunking=args.chunked,
        chunk_days=args.chunk_days,
    )
    print(json.dumps(result, indent=2))
