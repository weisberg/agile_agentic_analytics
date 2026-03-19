"""
Archival Tagger for Compliance-Aware Content Review

Tags reviewed content with archival metadata per SEC Rule 17a-4 and FINRA
retention requirements. Produces metadata compatible with common compliance
archival systems (Smarsh, Global Relay, Bloomberg Vault).

ADVISORY NOTICE: This tagger provides automated metadata generation for a
first-pass review only. It does NOT constitute compliance certification.
All archival decisions require confirmation by a qualified compliance officer.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class CommunicationType(Enum):
    """FINRA communication type classification."""
    RETAIL = "RETAIL"
    INSTITUTIONAL = "INSTITUTIONAL"
    CORRESPONDENCE = "CORRESPONDENCE"


class ContentCategory(Enum):
    """Content category for archival classification."""
    ADVERTISEMENT = "ADVERTISEMENT"
    SALES_LITERATURE = "SALES_LITERATURE"
    RESEARCH = "RESEARCH"
    COMMENTARY = "COMMENTARY"
    EDUCATIONAL = "EDUCATIONAL"
    PROMOTIONAL = "PROMOTIONAL"


class FilingType(Enum):
    """FINRA filing requirement type."""
    PRE_USE = "PRE_USE"
    POST_USE = "POST_USE"
    NONE = "NONE"


class FilingStatus(Enum):
    """Current status of FINRA filing."""
    PENDING = "PENDING"
    FILED = "FILED"
    NOT_REQUIRED = "NOT_REQUIRED"


class StorageFormat(Enum):
    """Storage format classification."""
    WORM = "WORM"
    STANDARD = "STANDARD"


@dataclass
class RetentionPolicy:
    """Retention policy derived from regulatory requirements."""
    period_years: int
    start_date: date
    end_date: date
    rule_citation: str
    worm_required: bool


@dataclass
class FilingMetadata:
    """FINRA filing requirement metadata."""
    finra_filing_required: bool
    filing_type: FilingType
    filing_deadline: Optional[date]
    filing_status: FilingStatus


@dataclass
class StorageMetadata:
    """Storage location and format metadata."""
    primary_location: str
    duplicate_location: str
    index_reference: str
    format: StorageFormat


@dataclass
class ArchivalTag:
    """Complete archival metadata tag for a reviewed content piece."""
    content_id: str
    content_hash: str
    original_file_path: str
    review_id: str
    created_timestamp: str
    review_timestamp: str
    archival_timestamp: str
    reviewer_type: str  # "AUTOMATED_FIRST_PASS" or "HUMAN_COMPLIANCE_OFFICER"
    reviewer_identity: str
    jurisdictions: list[str]
    communication_type: CommunicationType
    content_category: ContentCategory
    product_type: Optional[str]
    retention: RetentionPolicy
    filing: FilingMetadata
    storage: StorageMetadata


@dataclass
class ArchivalManifest:
    """A collection of archival tags for batch processing."""
    manifest_id: str
    generated_timestamp: str
    tags: list[ArchivalTag] = field(default_factory=list)
    advisory_notice: str = (
        "This is an advisory first-pass review, not compliance certification. "
        "All archival tags require confirmation by a qualified compliance officer."
    )


def compute_content_hash(content: str) -> str:
    """Compute a SHA-256 hash of the content for integrity verification.

    The hash serves as a tamper-detection mechanism for archived content.
    Any modification to the content after archival will produce a different
    hash, alerting to potential integrity issues.

    Args:
        content: The content to hash.

    Returns:
        str: Hex-encoded SHA-256 hash of the content.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def determine_retention_policy(
    communication_type: CommunicationType,
    content_category: ContentCategory,
    jurisdictions: list[str],
    is_complaint_related: bool = False,
) -> RetentionPolicy:
    """Determine the retention policy based on content classification.

    Applies SEC Rule 17a-4 and FINRA retention schedules to determine the
    required retention period, start date, end date, and whether WORM
    storage is required.

    Args:
        communication_type: FINRA communication type (RETAIL, INSTITUTIONAL,
            CORRESPONDENCE).
        content_category: Content category (ADVERTISEMENT, SALES_LITERATURE,
            etc.).
        jurisdictions: Applicable regulatory jurisdictions.
        is_complaint_related: Whether the content relates to a customer
            complaint (triggers extended 4-year retention under FINRA).

    Returns:
        RetentionPolicy: The applicable retention policy with period,
            dates, rule citation, and WORM requirement.
    """
    # TODO: Implement retention policy determination.
    # 1. Look up base retention period from SEC 17a-4 schedule.
    # 2. Check FINRA-specific extensions (e.g., complaint-related = 4 years).
    # 3. Apply the longest applicable period across jurisdictions.
    # 4. Set WORM requirement per 17a-4(f).
    # 5. Calculate start date (today) and end date.
    today = date.today()
    return RetentionPolicy(
        period_years=3,
        start_date=today,
        end_date=today + timedelta(days=3 * 365),
        rule_citation="17a-4(b)(4)",
        worm_required=True,
    )


def determine_filing_requirements(
    communication_type: CommunicationType,
    content_category: ContentCategory,
    is_new_member: bool = False,
    is_options_related: bool = False,
    is_cmo_related: bool = False,
    is_investment_company: bool = False,
) -> FilingMetadata:
    """Determine FINRA filing requirements for the content.

    Evaluates whether the content requires pre-use or post-use filing with
    FINRA based on communication type, content category, and firm status.

    Args:
        communication_type: FINRA communication type.
        content_category: Content category.
        is_new_member: Whether the firm is in its first year of FINRA
            membership (triggers pre-use filing for all retail).
        is_options_related: Whether content concerns options (pre-use with OCC).
        is_cmo_related: Whether content concerns CMOs (pre-use filing).
        is_investment_company: Whether content concerns registered investment
            companies (filing requirements vary).

    Returns:
        FilingMetadata: Filing requirement details including type, deadline,
            and current status.
    """
    # TODO: Implement filing requirement determination.
    # 1. Check new member status -> pre-use for all retail.
    # 2. Check product-specific requirements (options, CMOs, RICs).
    # 3. Default filing type for retail vs institutional.
    # 4. Calculate filing deadline (10 business days for pre/post-use).
    return FilingMetadata(
        finra_filing_required=False,
        filing_type=FilingType.NONE,
        filing_deadline=None,
        filing_status=FilingStatus.NOT_REQUIRED,
    )


def create_archival_tag(
    content: str,
    original_file_path: str,
    review_id: str,
    review_timestamp: str,
    jurisdictions: list[str],
    communication_type: CommunicationType,
    content_category: ContentCategory,
    product_type: Optional[str] = None,
    is_complaint_related: bool = False,
    is_new_member: bool = False,
    is_options_related: bool = False,
    is_cmo_related: bool = False,
    is_investment_company: bool = False,
    storage_primary: str = "",
    storage_duplicate: str = "",
) -> ArchivalTag:
    """Create a complete archival metadata tag for a content piece.

    Assembles all archival metadata including content hash, classification,
    retention policy, filing requirements, and storage references.

    Args:
        content: The reviewed content (used for hash computation).
        original_file_path: Path to the original content file.
        review_id: UUID of the associated compliance review.
        review_timestamp: ISO 8601 timestamp of the compliance review.
        jurisdictions: Applicable regulatory jurisdictions.
        communication_type: FINRA communication type classification.
        content_category: Content category classification.
        product_type: Optional product type (e.g., "mutual_fund", "etf").
        is_complaint_related: Whether related to a customer complaint.
        is_new_member: Whether the firm is a new FINRA member.
        is_options_related: Whether the content concerns options.
        is_cmo_related: Whether the content concerns CMOs.
        is_investment_company: Whether the content concerns RICs.
        storage_primary: Primary storage location reference.
        storage_duplicate: Duplicate storage location reference.

    Returns:
        ArchivalTag: Complete archival metadata for the content piece.
    """
    # TODO: Implement full archival tag creation.
    # 1. Compute content hash.
    # 2. Determine retention policy.
    # 3. Determine filing requirements.
    # 4. Assemble the complete ArchivalTag.
    now = datetime.now(timezone.utc).isoformat()
    content_hash = compute_content_hash(content)
    retention = determine_retention_policy(
        communication_type, content_category, jurisdictions, is_complaint_related
    )
    filing = determine_filing_requirements(
        communication_type, content_category,
        is_new_member, is_options_related, is_cmo_related, is_investment_company
    )
    content_id = str(uuid.uuid4())
    return ArchivalTag(
        content_id=content_id,
        content_hash=content_hash,
        original_file_path=original_file_path,
        review_id=review_id,
        created_timestamp=now,
        review_timestamp=review_timestamp,
        archival_timestamp=now,
        reviewer_type="AUTOMATED_FIRST_PASS",
        reviewer_identity="compliance-review-skill-v1",
        jurisdictions=jurisdictions,
        communication_type=communication_type,
        content_category=content_category,
        product_type=product_type,
        retention=retention,
        filing=filing,
        storage=StorageMetadata(
            primary_location=storage_primary,
            duplicate_location=storage_duplicate,
            index_reference=f"idx-{content_id}",
            format=StorageFormat.WORM if retention.worm_required else StorageFormat.STANDARD,
        ),
    )


def serialize_archival_tag(tag: ArchivalTag) -> dict:
    """Serialize an ArchivalTag to a JSON-compatible dictionary.

    Converts all enum values, date objects, and nested dataclasses to
    JSON-serializable types matching the schema defined in
    references/archival_requirements.md.

    Args:
        tag: The ArchivalTag to serialize.

    Returns:
        dict: JSON-serializable dictionary matching the archival metadata
            schema.
    """
    # TODO: Implement serialization with proper type conversion.
    # Convert enums to .value, dates to ISO format strings, etc.
    return {}


def create_manifest(tags: list[ArchivalTag]) -> ArchivalManifest:
    """Create an archival manifest from a list of archival tags.

    Bundles multiple archival tags into a single manifest for batch
    processing and export to archival systems.

    Args:
        tags: List of ArchivalTag objects to include in the manifest.

    Returns:
        ArchivalManifest: The manifest containing all tags and the
            advisory notice.
    """
    return ArchivalManifest(
        manifest_id=str(uuid.uuid4()),
        generated_timestamp=datetime.now(timezone.utc).isoformat(),
        tags=tags,
    )


def export_manifest(
    manifest: ArchivalManifest,
    output_path: Path,
    format: str = "json",
) -> Path:
    """Export an archival manifest to a file.

    Writes the manifest to the specified path in JSON or CSV format for
    ingestion by external archival systems.

    Args:
        manifest: The ArchivalManifest to export.
        output_path: Path to write the manifest file.
        format: Output format, either "json" or "csv". Defaults to "json".

    Returns:
        Path: The path to the written manifest file.

    Raises:
        ValueError: If format is not "json" or "csv".
    """
    # TODO: Implement manifest export.
    # 1. Serialize all tags.
    # 2. Write to output_path in specified format.
    # 3. Include advisory_notice in the output.
    return output_path


def append_to_review_log(
    tag: ArchivalTag,
    log_path: Path,
) -> None:
    """Append an archival tag entry to the immutable review log.

    The review log is an append-only audit trail. Each entry records the
    archival tagging event for regulatory examination readiness.

    Args:
        tag: The ArchivalTag to log.
        log_path: Path to the review log file
            (workspace/compliance/review_log.json).

    Raises:
        IOError: If the log file cannot be written.
    """
    # TODO: Implement append-only logging.
    # 1. Read existing log entries (if file exists).
    # 2. Append new entry with timestamp and tag summary.
    # 3. Write back to file.
    # IMPORTANT: This must be append-only. Never overwrite or modify
    # existing entries.
    pass
