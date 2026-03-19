"""
Performance Validator for Compliance-Aware Content Review

Validates performance presentation in marketing content for SEC and FINRA
compliance. Checks gross/net balance, time period completeness, benchmark
inclusion, and hypothetical performance disclosure requirements.

ADVISORY NOTICE: This validator provides an automated first-pass review only.
It does NOT constitute compliance certification. All findings require confirmation
by a qualified human compliance officer.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional


class ValidationSeverity(Enum):
    """Severity levels for performance validation findings."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class PerformanceClaim:
    """A parsed performance claim extracted from content."""
    raw_text: str
    percentage: Optional[float]
    time_period: Optional[str]
    is_gross: Optional[bool]
    is_net: Optional[bool]
    is_annualized: Optional[bool]
    benchmark_name: Optional[str]
    location: str


@dataclass
class ValidationFinding:
    """A single finding from performance validation."""
    finding_id: str
    severity: ValidationSeverity
    rule_citation: str
    description: str
    related_claim: Optional[PerformanceClaim]
    remediation: str
    requires_human_review: bool = True


@dataclass
class PerformanceValidationResult:
    """Complete result of performance validation."""
    validation_id: str
    validation_timestamp: str
    content_source: str
    claims_found: list[PerformanceClaim]
    findings: list[ValidationFinding]
    gross_net_balanced: Optional[bool]
    time_periods_complete: Optional[bool]
    benchmarks_included: Optional[bool]
    advisory_notice: str = (
        "This is an advisory first-pass review, not compliance certification."
    )


def extract_performance_claims(content: str) -> list[PerformanceClaim]:
    """Extract all performance claims from marketing content.

    Parses the content to identify statements that present investment
    performance data, including percentage returns, time periods, gross/net
    designations, and benchmark references.

    Args:
        content: The full text content to parse for performance claims.

    Returns:
        list[PerformanceClaim]: All performance claims found in the content,
            with parsed components (percentage, time period, gross/net status).
    """
    # TODO: Implement performance claim extraction.
    # 1. Use regex to find percentage patterns (e.g., "+12.5%", "12.5 percent").
    # 2. Parse surrounding context for time period (1-year, 5-year, etc.).
    # 3. Detect gross/net designation.
    # 4. Identify associated benchmark references.
    return []


def validate_gross_net_balance(
    claims: list[PerformanceClaim],
) -> list[ValidationFinding]:
    """Validate that gross and net performance receive equal prominence.

    SEC Marketing Rule requires that if gross performance is shown, net
    performance must also be shown with at least equal prominence. This
    validator checks for the presence and balance of gross/net claims.

    Args:
        claims: List of PerformanceClaim objects extracted from content.

    Returns:
        list[ValidationFinding]: Findings for any gross/net imbalances.
            HIGH severity if gross is shown without net. MEDIUM severity
            if net appears less prominent than gross.
    """
    # TODO: Implement gross/net balance validation.
    # 1. Identify claims marked as gross and claims marked as net.
    # 2. If gross is present but net is absent, flag as HIGH.
    # 3. If both present, check for equal prominence (position, formatting).
    # 4. Verify net deductions are properly disclosed.
    return []


def validate_time_period_completeness(
    claims: list[PerformanceClaim],
    inception_date: Optional[date] = None,
) -> list[ValidationFinding]:
    """Validate that all required time periods are presented.

    SEC Marketing Rule requires performance to include 1-year, 5-year, and
    10-year (or since-inception) periods. Performance for periods less than
    one year must not be annualized.

    Args:
        claims: List of PerformanceClaim objects extracted from content.
        inception_date: Optional date of fund/strategy inception. Used to
            determine whether since-inception should replace 10-year period.

    Returns:
        list[ValidationFinding]: Findings for missing time periods or
            improperly annualized short-period returns.
    """
    # TODO: Implement time period completeness validation.
    # 1. Collect all time periods mentioned in claims.
    # 2. Check for presence of 1-year, 5-year, and 10-year (or since-inception).
    # 3. Flag missing required periods as HIGH severity.
    # 4. Check for annualized returns on sub-1-year periods (violation).
    # 5. Verify all periods end on a consistent, recent date.
    return []


def validate_benchmark_inclusion(
    claims: list[PerformanceClaim],
) -> list[ValidationFinding]:
    """Validate that performance comparisons include appropriate benchmarks.

    When performance is compared to a benchmark, the benchmark must be clearly
    identified and results shown for the same time periods. This validator
    checks for benchmark presence and consistency.

    Args:
        claims: List of PerformanceClaim objects extracted from content.

    Returns:
        list[ValidationFinding]: Findings for missing or improperly
            presented benchmarks. MEDIUM severity if performance is shown
            without benchmark context. HIGH if benchmark comparison is
            made but benchmark is not identified.
    """
    # TODO: Implement benchmark validation.
    # 1. Check if any claims reference a benchmark.
    # 2. If performance data exists without benchmark, flag as MEDIUM.
    # 3. If benchmark is referenced but not clearly identified, flag as HIGH.
    # 4. Verify benchmark periods match the adviser's performance periods.
    return []


def validate_hypothetical_performance(
    content: str,
    claims: list[PerformanceClaim],
) -> list[ValidationFinding]:
    """Validate hypothetical performance presentation requirements.

    Hypothetical performance (back-tested, model, projected) has additional
    disclosure requirements under the SEC Marketing Rule. This validator
    checks for required disclosures when hypothetical performance is detected.

    Args:
        content: The full text content (for disclosure checking).
        claims: List of PerformanceClaim objects extracted from content.

    Returns:
        list[ValidationFinding]: Findings for hypothetical performance
            missing required disclosures (criteria, assumptions, risks,
            limitations). HIGH severity for missing disclosures.
    """
    # TODO: Implement hypothetical performance validation.
    # 1. Detect hypothetical/back-tested/model performance indicators.
    # 2. Check for required methodology description.
    # 3. Check for required risk/limitation disclosures.
    # 4. Verify audience-appropriateness policies are referenced.
    return []


def validate_extracted_performance(
    content: str,
    claims: list[PerformanceClaim],
) -> list[ValidationFinding]:
    """Validate extracted performance includes total portfolio results.

    When showing performance of a subset of investments (extracted
    performance), the SEC Marketing Rule requires that total portfolio
    performance also be shown.

    Args:
        content: The full text content (for context analysis).
        claims: List of PerformanceClaim objects extracted from content.

    Returns:
        list[ValidationFinding]: Findings if extracted performance is
            detected without total portfolio performance. HIGH severity.
    """
    # TODO: Implement extracted performance detection and validation.
    # 1. Detect indicators of extracted/partial portfolio performance.
    # 2. Check if total portfolio performance is also presented.
    # 3. Flag if extracted performance shown without total portfolio.
    return []


def run_full_validation(
    content: str,
    content_source: str = "unknown",
    inception_date: Optional[date] = None,
) -> PerformanceValidationResult:
    """Run all performance validations on the given content.

    Extracts performance claims from the content and runs all validators:
    gross/net balance, time period completeness, benchmark inclusion,
    hypothetical performance, and extracted performance.

    Args:
        content: The full text content to validate.
        content_source: Identifier for the source file or content piece.
        inception_date: Optional inception date for the fund/strategy.

    Returns:
        PerformanceValidationResult: Aggregated results from all validators
            including all claims found, all findings, and summary flags.
    """
    # TODO: Implement full validation pipeline.
    # 1. Extract claims via extract_performance_claims().
    # 2. Run each validator and collect findings.
    # 3. Set summary flags (gross_net_balanced, time_periods_complete, etc.).
    # 4. Always include advisory_notice in the result.
    claims = extract_performance_claims(content)
    return PerformanceValidationResult(
        validation_id=str(uuid.uuid4()),
        validation_timestamp=datetime.now(timezone.utc).isoformat(),
        content_source=content_source,
        claims_found=claims,
        findings=[],
        gross_net_balanced=None,
        time_periods_complete=None,
        benchmarks_included=None,
    )
