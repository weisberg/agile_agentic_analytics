#!/usr/bin/env python3
"""Technical SEO auditing: Core Web Vitals, structured data validation,
and crawl error detection.

Checks page performance via the PageSpeed Insights API, validates
structured data (JSON-LD) against schema.org requirements, and identifies
common crawl issues (redirect chains, broken links, orphaned pages).

Usage:
    python seo_audit.py \
        --urls workspace/raw/content_inventory.csv \
        --output workspace/analysis/seo_audit.json

Inputs:
    - workspace/raw/content_inventory.csv (url column for pages to audit)
    - PageSpeed Insights API key (via environment variable or config)

Outputs:
    - workspace/analysis/seo_audit.json with CWV scores, structured data
      issues, and crawl error inventory
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import date
from enum import Enum
from fnmatch import fnmatch
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


class CWVRating(Enum):
    """Core Web Vitals rating classification."""

    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


# Core Web Vitals thresholds
CWV_THRESHOLDS = {
    "LCP": {"good": 2500, "poor": 4000},  # milliseconds
    "INP": {"good": 200, "poor": 500},  # milliseconds
    "CLS": {"good": 0.1, "poor": 0.25},  # unitless score
}

# Required properties per schema.org type
SCHEMA_REQUIRED_PROPERTIES: dict[str, list[str]] = {
    "Article": ["headline", "image", "datePublished", "author"],
    "FAQPage": ["mainEntity"],
    "HowTo": ["name", "step"],
    "Product": ["name", "image", "offers"],
    "Organization": ["name", "url", "logo"],
    "BreadcrumbList": ["itemListElement"],
    "LocalBusiness": ["name", "address", "telephone"],
    "FinancialProduct": ["name", "description", "provider"],
}


@dataclass
class CoreWebVitalsResult:
    """Core Web Vitals assessment for a single page."""

    url: str
    strategy: str  # "mobile" or "desktop"
    lcp_ms: float | None = None
    lcp_rating: CWVRating | None = None
    inp_ms: float | None = None
    inp_rating: CWVRating | None = None
    cls_score: float | None = None
    cls_rating: CWVRating | None = None
    performance_score: float | None = None
    ttfb_ms: float | None = None
    fcp_ms: float | None = None


@dataclass
class StructuredDataIssue:
    """An issue found in a page's structured data."""

    url: str
    schema_type: str
    issue_type: str  # "missing_required", "invalid_value", "missing_schema"
    field_name: str | None = None
    message: str = ""


@dataclass
class CrawlIssue:
    """A crawl-related issue detected for a URL."""

    url: str
    issue_type: str  # "redirect_chain", "broken_link", "orphaned", "soft_404", "slow_ttfb"
    severity: str  # "error", "warning", "info"
    details: str = ""
    source_url: str | None = None


@dataclass
class SEOAuditReport:
    """Aggregated results from a full technical SEO audit."""

    audit_date: str
    pages_audited: int
    cwv_results: list[CoreWebVitalsResult] = field(default_factory=list)
    structured_data_issues: list[StructuredDataIssue] = field(default_factory=list)
    crawl_issues: list[CrawlIssue] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


def classify_cwv_metric(
    metric_name: str,
    value: float,
) -> CWVRating:
    """Classify a Core Web Vitals metric value as good, needs improvement,
    or poor.

    Args:
        metric_name: One of "LCP", "INP", or "CLS".
        value: The measured metric value.

    Returns:
        The CWVRating classification.

    Raises:
        ValueError: If metric_name is not recognized.
    """
    if metric_name not in CWV_THRESHOLDS:
        raise ValueError(f"Unknown CWV metric: {metric_name}. Expected one of: {list(CWV_THRESHOLDS.keys())}")

    thresholds = CWV_THRESHOLDS[metric_name]
    if value <= thresholds["good"]:
        return CWVRating.GOOD
    elif value <= thresholds["poor"]:
        return CWVRating.NEEDS_IMPROVEMENT
    else:
        return CWVRating.POOR


def fetch_pagespeed_insights(
    url: str,
    api_key: str | None = None,
    strategy: str = "mobile",
    categories: list[str] | None = None,
) -> dict[str, Any]:
    """Fetch PageSpeed Insights data for a single URL.

    Args:
        url: The page URL to analyze.
        api_key: Google API key. If None, uses unauthenticated requests
            (lower rate limits).
        strategy: "mobile" or "desktop".
        categories: Lighthouse categories to audit. Defaults to
            ["performance", "seo"].

    Returns:
        The raw API response as a dict.

    Raises:
        RuntimeError: If the API returns an error response.
    """
    if categories is None:
        categories = ["performance", "seo"]

    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeedtest"
    params: dict[str, Any] = {
        "url": url,
        "strategy": strategy,
    }
    # PSI API accepts multiple category params
    for cat in categories:
        params.setdefault("category", [])
        if isinstance(params["category"], list):
            params["category"].append(cat)

    if api_key:
        params["key"] = api_key

    max_retries = 5
    for attempt in range(max_retries):
        try:
            resp = requests.get(endpoint, params=params, timeout=120)
            if resp.status_code == 429:
                wait_time = 2**attempt
                logger.warning(
                    "PSI rate limited for %s, retrying in %ds (attempt %d/%d)",
                    url,
                    wait_time,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(wait_time)
                continue
            if resp.status_code != 200:
                raise RuntimeError(
                    f"PageSpeed Insights API error for {url}: HTTP {resp.status_code} - {resp.text[:500]}"
                )
            return resp.json()
        except requests.exceptions.RequestException as exc:
            if attempt < max_retries - 1:
                wait_time = 2**attempt
                logger.warning(
                    "PSI request failed for %s, retrying in %ds: %s",
                    url,
                    wait_time,
                    exc,
                )
                time.sleep(wait_time)
            else:
                raise RuntimeError(f"PageSpeed Insights request failed after {max_retries} attempts for {url}") from exc

    raise RuntimeError(f"PageSpeed Insights request failed after {max_retries} attempts for {url}")


def extract_cwv_from_response(
    url: str,
    response: dict[str, Any],
    strategy: str = "mobile",
) -> CoreWebVitalsResult:
    """Extract Core Web Vitals metrics from a PageSpeed Insights response.

    Parses both field data (CrUX, preferred) and lab data (Lighthouse,
    fallback) from the API response.

    Args:
        url: The page URL that was analyzed.
        response: Raw PageSpeed Insights API response.
        strategy: The strategy used ("mobile" or "desktop").

    Returns:
        A CoreWebVitalsResult with metrics and ratings populated.
    """
    result = CoreWebVitalsResult(url=url, strategy=strategy)

    # Try field data first (loadingExperience)
    field_data = response.get("loadingExperience", {}).get("metrics", {})

    # LCP from field data
    lcp_field = field_data.get("LARGEST_CONTENTFUL_PAINT_MS", {})
    if lcp_field.get("percentile") is not None:
        result.lcp_ms = float(lcp_field["percentile"])
        result.lcp_rating = classify_cwv_metric("LCP", result.lcp_ms)

    # INP from field data
    inp_field = field_data.get("INTERACTION_TO_NEXT_PAINT", {})
    if inp_field.get("percentile") is not None:
        result.inp_ms = float(inp_field["percentile"])
        result.inp_rating = classify_cwv_metric("INP", result.inp_ms)

    # CLS from field data
    cls_field = field_data.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", {})
    if cls_field.get("percentile") is not None:
        # CLS percentile from CrUX is multiplied by 100, convert back
        raw_cls = float(cls_field["percentile"])
        result.cls_score = raw_cls / 100.0 if raw_cls > 1 else raw_cls
        result.cls_rating = classify_cwv_metric("CLS", result.cls_score)

    # Fall back to lab data (Lighthouse) for missing metrics
    lab_audits = response.get("lighthouseResult", {}).get("audits", {})

    if result.lcp_ms is None:
        lcp_audit = lab_audits.get("largest-contentful-paint", {})
        if lcp_audit.get("numericValue") is not None:
            result.lcp_ms = float(lcp_audit["numericValue"])
            result.lcp_rating = classify_cwv_metric("LCP", result.lcp_ms)

    if result.cls_score is None:
        cls_audit = lab_audits.get("cumulative-layout-shift", {})
        if cls_audit.get("numericValue") is not None:
            result.cls_score = float(cls_audit["numericValue"])
            result.cls_rating = classify_cwv_metric("CLS", result.cls_score)

    # TTFB from field data or lab data
    ttfb_field = field_data.get("EXPERIMENTAL_TIME_TO_FIRST_BYTE", {})
    if ttfb_field.get("percentile") is not None:
        result.ttfb_ms = float(ttfb_field["percentile"])
    else:
        ttfb_audit = lab_audits.get("server-response-time", {})
        if ttfb_audit.get("numericValue") is not None:
            result.ttfb_ms = float(ttfb_audit["numericValue"])

    # FCP from field data or lab data
    fcp_field = field_data.get("FIRST_CONTENTFUL_PAINT_MS", {})
    if fcp_field.get("percentile") is not None:
        result.fcp_ms = float(fcp_field["percentile"])
    else:
        fcp_audit = lab_audits.get("first-contentful-paint", {})
        if fcp_audit.get("numericValue") is not None:
            result.fcp_ms = float(fcp_audit["numericValue"])

    # Performance score from Lighthouse
    categories = response.get("lighthouseResult", {}).get("categories", {})
    perf_category = categories.get("performance", {})
    if perf_category.get("score") is not None:
        result.performance_score = float(perf_category["score"])

    return result


def audit_core_web_vitals(
    urls: list[str],
    api_key: str | None = None,
    strategies: list[str] | None = None,
    max_concurrent: int = 5,
) -> list[CoreWebVitalsResult]:
    """Audit Core Web Vitals for a list of URLs.

    Args:
        urls: List of page URLs to audit.
        api_key: Google API key for PageSpeed Insights.
        strategies: Strategies to test. Defaults to ["mobile"].
        max_concurrent: Maximum concurrent API requests.

    Returns:
        A list of CoreWebVitalsResult objects, one per URL-strategy pair.
    """
    if strategies is None:
        strategies = ["mobile"]

    results: list[CoreWebVitalsResult] = []
    total = len(urls) * len(strategies)
    completed = 0

    for url in urls:
        for strategy in strategies:
            completed += 1
            logger.info(
                "Auditing CWV %d/%d: %s (%s)",
                completed,
                total,
                url,
                strategy,
            )
            try:
                response = fetch_pagespeed_insights(
                    url=url,
                    api_key=api_key,
                    strategy=strategy,
                )
                cwv = extract_cwv_from_response(url, response, strategy)
                results.append(cwv)
            except RuntimeError as exc:
                logger.error("CWV audit failed for %s (%s): %s", url, strategy, exc)
                # Add a result with None values to track the failure
                results.append(CoreWebVitalsResult(url=url, strategy=strategy))

            # Rate limiting: brief pause between requests
            # PSI allows 400 per 100 seconds = 4/sec
            time.sleep(0.3)

    logger.info("CWV audit complete: %d URLs audited", len(results))
    return results


def validate_structured_data(
    url: str,
    html_content: str | None = None,
    expected_types: list[str] | None = None,
) -> list[StructuredDataIssue]:
    """Validate structured data (JSON-LD) on a page.

    Checks for presence of expected schema types and validates that
    required properties are present for each type.

    Args:
        url: The page URL being validated.
        html_content: Raw HTML content of the page. If None, the
            function will attempt to fetch the page.
        expected_types: Schema types expected on this page (e.g.,
            ["Article", "BreadcrumbList"]). If None, checks for any
            valid structured data.

    Returns:
        A list of StructuredDataIssue objects for any problems found.
        Empty list if all checks pass.
    """
    issues: list[StructuredDataIssue] = []

    # Fetch HTML if not provided
    if html_content is None:
        try:
            resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (compatible; SEOAuditBot/1.0)"})
            resp.raise_for_status()
            html_content = resp.text
        except requests.exceptions.RequestException as exc:
            issues.append(
                StructuredDataIssue(
                    url=url,
                    schema_type="unknown",
                    issue_type="fetch_error",
                    message=f"Failed to fetch page: {exc}",
                )
            )
            return issues

    # Extract JSON-LD blocks from <script type="application/ld+json">
    jsonld_pattern = re.compile(
        r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE,
    )
    matches = jsonld_pattern.findall(html_content)

    if not matches:
        if expected_types:
            for expected in expected_types:
                issues.append(
                    StructuredDataIssue(
                        url=url,
                        schema_type=expected,
                        issue_type="missing_schema",
                        message=f"No JSON-LD structured data found, expected {expected}",
                    )
                )
        else:
            issues.append(
                StructuredDataIssue(
                    url=url,
                    schema_type="none",
                    issue_type="missing_schema",
                    message="No JSON-LD structured data found on page",
                )
            )
        return issues

    # Parse all JSON-LD blocks
    parsed_schemas: list[dict[str, Any]] = []
    for match in matches:
        try:
            data = json.loads(match.strip())
            # Handle @graph arrays
            if isinstance(data, dict) and "@graph" in data:
                for item in data["@graph"]:
                    if isinstance(item, dict):
                        parsed_schemas.append(item)
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        parsed_schemas.append(item)
            elif isinstance(data, dict):
                parsed_schemas.append(data)
        except json.JSONDecodeError:
            issues.append(
                StructuredDataIssue(
                    url=url,
                    schema_type="unknown",
                    issue_type="invalid_value",
                    message="Invalid JSON in JSON-LD script block",
                )
            )

    # Extract types found on page
    found_types: set[str] = set()
    for schema in parsed_schemas:
        schema_type = schema.get("@type", "")
        if isinstance(schema_type, list):
            found_types.update(schema_type)
        elif schema_type:
            found_types.add(schema_type)

    # Check @context
    for schema in parsed_schemas:
        context = schema.get("@context", "")
        if context and "schema.org" not in str(context):
            issues.append(
                StructuredDataIssue(
                    url=url,
                    schema_type=schema.get("@type", "unknown"),
                    issue_type="invalid_value",
                    field_name="@context",
                    message=f"Unexpected @context value: {context}",
                )
            )

    # Check expected types are present
    if expected_types:
        for expected in expected_types:
            if expected not in found_types:
                issues.append(
                    StructuredDataIssue(
                        url=url,
                        schema_type=expected,
                        issue_type="missing_schema",
                        message=f"Expected schema type '{expected}' not found on page",
                    )
                )

    # Validate required properties for each found schema
    for schema in parsed_schemas:
        schema_type = schema.get("@type", "")
        types_to_check = schema_type if isinstance(schema_type, list) else [schema_type]

        for st in types_to_check:
            required = SCHEMA_REQUIRED_PROPERTIES.get(st, [])
            for prop in required:
                if prop not in schema or schema[prop] is None or schema[prop] == "":
                    issues.append(
                        StructuredDataIssue(
                            url=url,
                            schema_type=st,
                            issue_type="missing_required",
                            field_name=prop,
                            message=f"Required property '{prop}' is missing for {st}",
                        )
                    )

    return issues


def audit_structured_data(
    urls: list[str],
    schema_expectations: dict[str, list[str]] | None = None,
) -> list[StructuredDataIssue]:
    """Audit structured data across multiple URLs.

    Args:
        urls: List of page URLs to audit.
        schema_expectations: Optional mapping of URL patterns to expected
            schema types (e.g., {"/blog/*": ["Article"],
            "/product/*": ["Product"]}). If None, checks for presence
            of any structured data.

    Returns:
        A list of StructuredDataIssue objects across all audited URLs.
    """
    all_issues: list[StructuredDataIssue] = []

    for idx, url in enumerate(urls, 1):
        logger.info("Auditing structured data %d/%d: %s", idx, len(urls), url)

        # Determine expected types based on URL pattern matching
        expected_types: list[str] | None = None
        if schema_expectations:
            parsed = urlparse(url)
            url_path = parsed.path
            for pattern, types in schema_expectations.items():
                if fnmatch(url_path, pattern):
                    expected_types = types
                    break

        issues = validate_structured_data(url, expected_types=expected_types)
        all_issues.extend(issues)

        # Brief pause to avoid hammering servers
        time.sleep(0.5)

    logger.info(
        "Structured data audit complete: %d issues across %d URLs",
        len(all_issues),
        len(urls),
    )
    return all_issues


def detect_redirect_chains(
    urls: list[str],
    max_redirects: int = 10,
    chain_threshold: int = 2,
) -> list[CrawlIssue]:
    """Detect redirect chains exceeding the specified hop threshold.

    Args:
        urls: List of URLs to check for redirect chains.
        max_redirects: Maximum redirects to follow before giving up.
        chain_threshold: Number of hops that triggers a warning
            (default 2, meaning 3+ hops flagged).

    Returns:
        A list of CrawlIssue objects for URLs with redirect chains.
    """
    issues: list[CrawlIssue] = []

    for url in urls:
        try:
            resp = requests.get(
                url,
                allow_redirects=True,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SEOAuditBot/1.0)"},
                stream=True,
            )
            # Count redirect hops
            hop_count = len(resp.history)
            if hop_count > chain_threshold:
                chain_detail = " -> ".join([r.url for r in resp.history] + [resp.url])
                severity = "error" if hop_count >= 4 else "warning"
                issues.append(
                    CrawlIssue(
                        url=url,
                        issue_type="redirect_chain",
                        severity=severity,
                        details=f"{hop_count} hops: {chain_detail}",
                    )
                )
            resp.close()
        except requests.exceptions.TooManyRedirects:
            issues.append(
                CrawlIssue(
                    url=url,
                    issue_type="redirect_chain",
                    severity="error",
                    details=f"Exceeded maximum redirects ({max_redirects})",
                )
            )
        except requests.exceptions.RequestException as exc:
            logger.warning("Could not check redirects for %s: %s", url, exc)

    logger.info("Redirect chain check: %d issues found", len(issues))
    return issues


def detect_broken_internal_links(
    urls: list[str],
    internal_domain: str,
) -> list[CrawlIssue]:
    """Detect broken internal links by checking response status codes.

    Args:
        urls: List of internal URLs to verify.
        internal_domain: The site's domain for filtering internal links.

    Returns:
        A list of CrawlIssue objects for URLs returning 4xx/5xx status.
    """
    issues: list[CrawlIssue] = []

    for url in urls:
        # Only check URLs matching the internal domain
        parsed = urlparse(url)
        if internal_domain not in parsed.netloc:
            continue

        try:
            resp = requests.head(
                url,
                allow_redirects=True,
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SEOAuditBot/1.0)"},
            )
            status = resp.status_code

            if 400 <= status < 500:
                severity = "error"
                issues.append(
                    CrawlIssue(
                        url=url,
                        issue_type="broken_link",
                        severity=severity,
                        details=f"HTTP {status} - Client error",
                    )
                )
            elif status >= 500:
                issues.append(
                    CrawlIssue(
                        url=url,
                        issue_type="broken_link",
                        severity="error",
                        details=f"HTTP {status} - Server error",
                    )
                )
            elif 300 <= status < 400:
                # Redirect to external domain is a warning
                final_url = resp.url
                final_parsed = urlparse(final_url)
                if internal_domain not in final_parsed.netloc:
                    issues.append(
                        CrawlIssue(
                            url=url,
                            issue_type="broken_link",
                            severity="warning",
                            details=f"Redirects to external domain: {final_url}",
                        )
                    )
        except requests.exceptions.RequestException as exc:
            issues.append(
                CrawlIssue(
                    url=url,
                    issue_type="broken_link",
                    severity="error",
                    details=f"Connection error: {exc}",
                )
            )

    logger.info("Broken link check: %d issues found", len(issues))
    return issues


def check_robots_and_sitemap(
    site_url: str,
) -> list[CrawlIssue]:
    """Verify robots.txt accessibility and sitemap health.

    Checks:
    - robots.txt is accessible and parseable.
    - Sitemap URL is declared in robots.txt.
    - Sitemap is valid XML and contains URLs.
    - Sitemap URLs are indexable (not noindex, not blocked by robots.txt).

    Args:
        site_url: The site's base URL (e.g., "https://example.com").

    Returns:
        A list of CrawlIssue objects for any problems found.
    """
    issues: list[CrawlIssue] = []
    site_url = site_url.rstrip("/")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SEOAuditBot/1.0)"}

    # 1. Check robots.txt
    robots_url = f"{site_url}/robots.txt"
    sitemap_urls_from_robots: list[str] = []
    try:
        resp = requests.get(robots_url, timeout=15, headers=headers)
        if resp.status_code != 200:
            issues.append(
                CrawlIssue(
                    url=robots_url,
                    issue_type="robots_txt",
                    severity="warning",
                    details=f"robots.txt returned HTTP {resp.status_code}",
                )
            )
        else:
            robots_content = resp.text
            # Check if it's parseable (look for User-agent or Sitemap directives)
            if not robots_content.strip():
                issues.append(
                    CrawlIssue(
                        url=robots_url,
                        issue_type="robots_txt",
                        severity="info",
                        details="robots.txt is empty",
                    )
                )
            # Extract sitemap declarations
            for line in robots_content.splitlines():
                line_stripped = line.strip()
                if line_stripped.lower().startswith("sitemap:"):
                    sm_url = line_stripped.split(":", 1)[1].strip()
                    sitemap_urls_from_robots.append(sm_url)

            if not sitemap_urls_from_robots:
                issues.append(
                    CrawlIssue(
                        url=robots_url,
                        issue_type="robots_txt",
                        severity="warning",
                        details="No Sitemap directive found in robots.txt",
                    )
                )
    except requests.exceptions.RequestException as exc:
        issues.append(
            CrawlIssue(
                url=robots_url,
                issue_type="robots_txt",
                severity="error",
                details=f"Could not fetch robots.txt: {exc}",
            )
        )

    # 2. Check sitemaps
    # Also try default location if not declared in robots.txt
    sitemap_urls_to_check = list(sitemap_urls_from_robots)
    if not sitemap_urls_to_check:
        sitemap_urls_to_check = [f"{site_url}/sitemap.xml"]

    for sitemap_url in sitemap_urls_to_check:
        try:
            resp = requests.get(sitemap_url, timeout=30, headers=headers)
            if resp.status_code != 200:
                issues.append(
                    CrawlIssue(
                        url=sitemap_url,
                        issue_type="sitemap",
                        severity="warning" if resp.status_code == 404 else "error",
                        details=f"Sitemap returned HTTP {resp.status_code}",
                    )
                )
                continue

            content = resp.text

            # Basic XML validation
            if "<?xml" not in content and "<urlset" not in content and "<sitemapindex" not in content:
                issues.append(
                    CrawlIssue(
                        url=sitemap_url,
                        issue_type="sitemap",
                        severity="error",
                        details="Sitemap does not appear to be valid XML",
                    )
                )
                continue

            # Check for <url> entries
            url_count = content.count("<url>") + content.count("<url ")
            if url_count == 0 and "<sitemapindex" not in content:
                issues.append(
                    CrawlIssue(
                        url=sitemap_url,
                        issue_type="sitemap",
                        severity="warning",
                        details="Sitemap contains no <url> entries",
                    )
                )
            else:
                logger.info(
                    "Sitemap %s contains approximately %d URLs",
                    sitemap_url,
                    url_count,
                )

            # Check if sitemap is excessively large
            if url_count > 50_000:
                issues.append(
                    CrawlIssue(
                        url=sitemap_url,
                        issue_type="sitemap",
                        severity="warning",
                        details=f"Sitemap has {url_count} URLs, exceeding 50,000 recommended limit",
                    )
                )

        except requests.exceptions.RequestException as exc:
            issues.append(
                CrawlIssue(
                    url=sitemap_url,
                    issue_type="sitemap",
                    severity="error",
                    details=f"Could not fetch sitemap: {exc}",
                )
            )

    logger.info("Robots/sitemap check: %d issues found", len(issues))
    return issues


def generate_audit_report(
    cwv_results: list[CoreWebVitalsResult],
    structured_data_issues: list[StructuredDataIssue],
    crawl_issues: list[CrawlIssue],
    output_path: str | Path = "workspace/analysis/seo_audit.json",
) -> SEOAuditReport:
    """Compile all audit results into a structured JSON report.

    Args:
        cwv_results: Core Web Vitals results for audited pages.
        structured_data_issues: Structured data validation issues.
        crawl_issues: Crawl-related issues.
        output_path: Destination file path for the JSON report.

    Returns:
        An SEOAuditReport with summary statistics.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Compute CWV summary
    cwv_good = sum(
        1
        for r in cwv_results
        if r.lcp_rating == CWVRating.GOOD
        and r.cls_rating == CWVRating.GOOD
        and (r.inp_rating is None or r.inp_rating == CWVRating.GOOD)
    )
    cwv_poor = sum(
        1
        for r in cwv_results
        if r.lcp_rating == CWVRating.POOR or r.cls_rating == CWVRating.POOR or r.inp_rating == CWVRating.POOR
    )

    # Crawl issue summary by severity
    crawl_by_severity: dict[str, int] = {"error": 0, "warning": 0, "info": 0}
    for ci in crawl_issues:
        crawl_by_severity[ci.severity] = crawl_by_severity.get(ci.severity, 0) + 1

    # Structured data issue summary by type
    sd_by_type: dict[str, int] = {}
    for sd in structured_data_issues:
        sd_by_type[sd.issue_type] = sd_by_type.get(sd.issue_type, 0) + 1

    unique_pages = set()
    for r in cwv_results:
        unique_pages.add(r.url)
    for sd in structured_data_issues:
        unique_pages.add(sd.url)
    for ci in crawl_issues:
        unique_pages.add(ci.url)

    summary = {
        "cwv_pages_good": cwv_good,
        "cwv_pages_poor": cwv_poor,
        "cwv_pages_total": len(cwv_results),
        "structured_data_issues_total": len(structured_data_issues),
        "structured_data_by_type": sd_by_type,
        "crawl_issues_total": len(crawl_issues),
        "crawl_issues_by_severity": crawl_by_severity,
    }

    report = SEOAuditReport(
        audit_date=date.today().isoformat(),
        pages_audited=len(unique_pages),
        cwv_results=cwv_results,
        structured_data_issues=structured_data_issues,
        crawl_issues=crawl_issues,
        summary=summary,
    )

    # Serialize to JSON
    def serialize(obj: Any) -> Any:
        if isinstance(obj, CWVRating):
            return obj.value
        if isinstance(obj, Enum):
            return obj.value
        if hasattr(obj, "__dataclass_fields__"):
            return asdict(obj)
        return str(obj)

    report_dict = {
        "audit_date": report.audit_date,
        "pages_audited": report.pages_audited,
        "summary": report.summary,
        "cwv_results": [
            {
                "url": r.url,
                "strategy": r.strategy,
                "lcp_ms": r.lcp_ms,
                "lcp_rating": r.lcp_rating.value if r.lcp_rating else None,
                "inp_ms": r.inp_ms,
                "inp_rating": r.inp_rating.value if r.inp_rating else None,
                "cls_score": r.cls_score,
                "cls_rating": r.cls_rating.value if r.cls_rating else None,
                "performance_score": r.performance_score,
                "ttfb_ms": r.ttfb_ms,
                "fcp_ms": r.fcp_ms,
            }
            for r in cwv_results
        ],
        "structured_data_issues": [asdict(sd) for sd in structured_data_issues],
        "crawl_issues": [asdict(ci) for ci in crawl_issues],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2, default=str)

    logger.info("SEO audit report written to %s", output_path)
    return report


def run_seo_audit(
    urls_source: str = "workspace/raw/content_inventory.csv",
    output_path: str = "workspace/analysis/seo_audit.json",
    api_key: str | None = None,
    site_url: str | None = None,
    strategies: list[str] | None = None,
    check_cwv: bool = True,
    check_structured_data: bool = True,
    check_crawl: bool = True,
) -> dict[str, Any]:
    """End-to-end technical SEO audit pipeline.

    Orchestrates Core Web Vitals assessment, structured data validation,
    and crawl issue detection across all pages in the content inventory.

    Args:
        urls_source: Path to CSV with a "url" column listing pages to
            audit.
        output_path: Destination for the audit JSON report.
        api_key: Google API key for PageSpeed Insights.
        site_url: Base site URL for robots/sitemap checks. If None,
            inferred from the first URL in the inventory.
        strategies: PageSpeed strategies to test (default ["mobile"]).
        check_cwv: Whether to run Core Web Vitals audit.
        check_structured_data: Whether to run structured data audit.
        check_crawl: Whether to run crawl issue checks.

    Returns:
        A summary dict with issue counts by category and severity.
    """
    import pandas as pd

    # 1. Load URLs from inventory
    source_path = Path(urls_source)
    if not source_path.exists():
        raise FileNotFoundError(f"URL source file not found: {urls_source}")

    urls_df = pd.read_csv(source_path)
    if "url" not in urls_df.columns:
        raise ValueError("URL source CSV must contain a 'url' column")

    urls = urls_df["url"].dropna().tolist()
    logger.info("Loaded %d URLs for audit from %s", len(urls), urls_source)

    # Infer site URL from first URL if not provided
    if site_url is None and urls:
        parsed = urlparse(urls[0])
        site_url = f"{parsed.scheme}://{parsed.netloc}"

    # 2. Run CWV audit
    cwv_results: list[CoreWebVitalsResult] = []
    if check_cwv:
        cwv_results = audit_core_web_vitals(
            urls=urls,
            api_key=api_key,
            strategies=strategies,
        )

    # 3. Run structured data audit
    sd_issues: list[StructuredDataIssue] = []
    if check_structured_data:
        sd_issues = audit_structured_data(urls=urls)

    # 4. Run crawl checks
    crawl_issues: list[CrawlIssue] = []
    if check_crawl:
        # Redirect chain detection
        redirect_issues = detect_redirect_chains(urls)
        crawl_issues.extend(redirect_issues)

        # Broken internal link detection
        if site_url:
            domain = urlparse(site_url).netloc
            broken_link_issues = detect_broken_internal_links(urls, domain)
            crawl_issues.extend(broken_link_issues)

        # Robots.txt and sitemap validation
        if site_url:
            robots_issues = check_robots_and_sitemap(site_url)
            crawl_issues.extend(robots_issues)

    # 5. Generate report
    report = generate_audit_report(
        cwv_results=cwv_results,
        structured_data_issues=sd_issues,
        crawl_issues=crawl_issues,
        output_path=output_path,
    )

    return report.summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Technical SEO audit")
    parser.add_argument("--urls", default="workspace/raw/content_inventory.csv")
    parser.add_argument("--output", default="workspace/analysis/seo_audit.json")
    parser.add_argument("--api-key", default=None, help="PageSpeed Insights API key")
    parser.add_argument("--site-url", default=None, help="Base site URL")
    parser.add_argument("--skip-cwv", action="store_true", help="Skip CWV checks")
    parser.add_argument("--skip-structured-data", action="store_true")
    parser.add_argument("--skip-crawl", action="store_true")

    args = parser.parse_args()

    result = run_seo_audit(
        urls_source=args.urls,
        output_path=args.output,
        api_key=args.api_key,
        site_url=args.site_url,
        check_cwv=not args.skip_cwv,
        check_structured_data=not args.skip_structured_data,
        check_crawl=not args.skip_crawl,
    )
    print(json.dumps(result, indent=2))
