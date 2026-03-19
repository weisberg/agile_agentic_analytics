"""
Content Scanner for Compliance-Aware Content Review

Rule-based scanning for regulatory violations using keyword and pattern matching.
Screens marketing content against SEC Marketing Rule 206(4)-1, FINRA Rule 2210,
and FCA financial promotions requirements.

ADVISORY NOTICE: This scanner provides an automated first-pass review only.
It does NOT constitute compliance certification. All findings require confirmation
by a qualified human compliance officer.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class Severity(Enum):
    """Severity levels for compliance findings."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Jurisdiction(Enum):
    """Regulatory jurisdiction for a finding."""
    SEC = "SEC"
    FINRA = "FINRA"
    FCA = "FCA"


@dataclass
class ComplianceFinding:
    """A single compliance finding from content scanning."""
    issue_id: str
    severity: Severity
    jurisdiction: Jurisdiction
    rule_citation: str
    description: str
    matched_text: str
    location: str
    remediation: str
    requires_human_review: bool = True


@dataclass
class ScanResult:
    """Complete result of a compliance content scan."""
    scan_id: str
    scan_timestamp: str
    content_source: str
    overall_status: str  # "PASS", "FAIL", or "WARNING"
    advisory_notice: str = (
        "This is an advisory first-pass review, not compliance certification."
    )
    findings: list[ComplianceFinding] = field(default_factory=list)


@dataclass
class ScanRule:
    """A single scanning rule with pattern and metadata."""
    rule_id: str
    pattern: re.Pattern[str]
    severity: Severity
    jurisdiction: Jurisdiction
    rule_citation: str
    description: str
    remediation: str


def load_default_rules() -> list[ScanRule]:
    """Load the default set of compliance scanning rules.

    Returns a list of ScanRule objects covering SEC general prohibitions,
    FINRA fair-and-balanced requirements, and FCA clear/fair/not-misleading
    standards.

    Returns:
        list[ScanRule]: The default scanning rules ordered by severity
            (HIGH first).
    """
    # TODO: Implement default rule loading from references/ directory.
    # Rules should be loaded from versioned reference files so they can be
    # updated without modifying this script.
    return []


def load_custom_rules(rules_path: Path) -> list[ScanRule]:
    """Load custom scanning rules from a firm-specific rules file.

    Args:
        rules_path: Path to a JSON or YAML file containing custom scanning
            rules. Each rule must include: rule_id, pattern (regex string),
            severity, jurisdiction, rule_citation, description, remediation.

    Returns:
        list[ScanRule]: Custom rules parsed from the file.

    Raises:
        FileNotFoundError: If the rules file does not exist.
        ValueError: If the rules file contains invalid rule definitions.
    """
    # TODO: Implement custom rule loading with validation.
    return []


def scan_content(
    content: str,
    rules: list[ScanRule],
    content_source: str = "unknown",
) -> ScanResult:
    """Scan content against a set of compliance rules.

    Applies each rule's regex pattern against the content and collects all
    matches as ComplianceFinding objects. Determines overall status based on
    the highest severity finding.

    Args:
        content: The full text content to scan for compliance violations.
        rules: List of ScanRule objects to apply. Use load_default_rules()
            and/or load_custom_rules() to obtain these.
        content_source: Identifier for the source file or content piece
            being scanned (used in the scan report).

    Returns:
        ScanResult: Contains all findings, overall pass/fail status, and
            the advisory notice.
    """
    # TODO: Implement rule-based scanning logic.
    # 1. Iterate over each rule and apply its pattern to the content.
    # 2. For each match, create a ComplianceFinding with location info.
    # 3. Determine overall_status: FAIL if any HIGH finding, WARNING if
    #    MEDIUM, PASS otherwise.
    # 4. Always include the advisory notice.
    return ScanResult(
        scan_id=str(uuid.uuid4()),
        scan_timestamp=datetime.now(timezone.utc).isoformat(),
        content_source=content_source,
        overall_status="PASS",
        findings=[],
    )


def scan_for_superlatives(content: str) -> list[ComplianceFinding]:
    """Detect superlative and promissory language prohibited by SEC and FINRA.

    Scans for terms like 'guaranteed,' 'risk-free,' 'best,' 'safe,' 'no risk,'
    'will achieve,' 'certain to,' and similar language that violates SEC Rule
    206(4)-1 general prohibitions and FINRA Rule 2210(d).

    Args:
        content: The text content to scan.

    Returns:
        list[ComplianceFinding]: Findings for each superlative or promissory
            term detected, with HIGH severity.
    """
    # TODO: Implement superlative detection with context-aware matching.
    # Should avoid false positives from quoted text, negations, and
    # conditional language.
    return []


def scan_for_cherry_picked_performance(content: str) -> list[ComplianceFinding]:
    """Detect selective time-period presentation of performance data.

    Identifies performance claims that highlight favorable periods without
    including required standard periods (1-year, 5-year, 10-year or
    since-inception). Flags SEC Rule 206(4)-1 violation for cherry-picking.

    Args:
        content: The text content to scan.

    Returns:
        list[ComplianceFinding]: Findings for each instance of potentially
            cherry-picked performance data.
    """
    # TODO: Implement cherry-picking detection.
    # 1. Detect performance percentage patterns (e.g., "+15.3%").
    # 2. Check if standard reporting periods are present alongside.
    # 3. Flag if only favorable periods are shown.
    return []


def scan_for_missing_risk_disclosures(content: str) -> list[ComplianceFinding]:
    """Detect benefit claims that lack corresponding risk disclosures.

    FINRA Rule 2210(d)(1) requires fair and balanced presentation. Any
    statement of benefits must be balanced with associated risks. This
    scanner checks for benefit language without nearby risk language.

    Args:
        content: The text content to scan.

    Returns:
        list[ComplianceFinding]: Findings for each benefit claim lacking
            a corresponding risk disclosure.
    """
    # TODO: Implement benefit/risk balance detection.
    # 1. Identify benefit language (returns, growth, gains, outperformance).
    # 2. Check surrounding context for risk language.
    # 3. Flag imbalances as MEDIUM severity.
    return []


def scan_for_fca_violations(content: str) -> list[ComplianceFinding]:
    """Detect potential FCA financial promotion violations.

    Screens for issues under the FCA clear/fair/not-misleading standard
    including missing risk warnings, capital-at-risk disclosures, and
    past-performance disclaimers required for UK financial promotions.

    Args:
        content: The text content to scan.

    Returns:
        list[ComplianceFinding]: Findings specific to FCA requirements.
    """
    # TODO: Implement FCA-specific scanning.
    # 1. Check for capital-at-risk warnings.
    # 2. Check for past performance disclaimers (FCA-specific language).
    # 3. Flag high-risk investment promotions missing PS22/10 warnings.
    return []


def classify_content(
    content: str,
    metadata: Optional[dict[str, str]] = None,
) -> dict[str, str | list[str] | bool]:
    """Classify content by jurisdiction, audience, type, and filing requirement.

    Analyzes the content and any available metadata to determine the
    applicable regulatory jurisdictions, whether the audience is institutional
    or retail, the content type (performance, testimonial, etc.), and whether
    FINRA pre-use or post-use filing is required.

    Args:
        content: The text content to classify.
        metadata: Optional dict with keys like 'target_audience',
            'jurisdiction', 'product_type', 'firm_member_status' that
            inform classification.

    Returns:
        dict with keys:
            - jurisdiction: list[str] of applicable jurisdictions
            - audience: str ("INSTITUTIONAL", "RETAIL", or "CORRESPONDENCE")
            - content_type: str (e.g., "PERFORMANCE", "TESTIMONIAL")
            - filing_required: str ("PRE_USE", "POST_USE", or "NONE")
    """
    # TODO: Implement content classification logic.
    return {
        "jurisdiction": ["SEC", "FINRA"],
        "audience": "RETAIL",
        "content_type": "GENERAL",
        "filing_required": "NONE",
    }


def generate_scan_report(result: ScanResult) -> dict:
    """Convert a ScanResult into a JSON-serializable report dict.

    Produces the review_report.json output format specified in the skill's
    data contract. Always includes the advisory notice.

    Args:
        result: The ScanResult from a content scan.

    Returns:
        dict: JSON-serializable report matching the output schema defined
            in SKILL.md.
    """
    # TODO: Implement report generation.
    # Must always include: advisory_notice field.
    return {
        "scan_id": result.scan_id,
        "scan_timestamp": result.scan_timestamp,
        "content_source": result.content_source,
        "overall_status": result.overall_status,
        "advisory_notice": result.advisory_notice,
        "findings": [],
    }
