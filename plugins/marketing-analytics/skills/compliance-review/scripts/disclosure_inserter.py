"""
Disclosure Inserter for Compliance-Aware Content Review

Inserts required disclosures into marketing content based on content type
classification. Supports performance disclaimers, testimonial disclosures,
risk warnings, fee disclosures, and regulatory status statements.

ADVISORY NOTICE: This inserter provides an automated first-pass review only.
It does NOT constitute compliance certification. All inserted disclosures
require review and approval by a qualified human compliance officer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class ContentType(Enum):
    """Content type classification for disclosure requirements."""
    PERFORMANCE = "PERFORMANCE"
    TESTIMONIAL = "TESTIMONIAL"
    ENDORSEMENT = "ENDORSEMENT"
    HYPOTHETICAL = "HYPOTHETICAL"
    THIRD_PARTY_RATING = "THIRD_PARTY_RATING"
    FEE_REFERENCE = "FEE_REFERENCE"
    RISK_STATEMENT = "RISK_STATEMENT"
    GENERAL = "GENERAL"


class DisclosureType(Enum):
    """Types of disclosures that can be inserted."""
    PAST_PERFORMANCE_US = "PAST_PERFORMANCE_US"
    PAST_PERFORMANCE_UK = "PAST_PERFORMANCE_UK"
    GROSS_NET = "GROSS_NET"
    HYPOTHETICAL = "HYPOTHETICAL"
    BACK_TESTED = "BACK_TESTED"
    BENCHMARK = "BENCHMARK"
    TESTIMONIAL_COMPENSATED = "TESTIMONIAL_COMPENSATED"
    TESTIMONIAL_UNCOMPENSATED = "TESTIMONIAL_UNCOMPENSATED"
    ENDORSEMENT = "ENDORSEMENT"
    THIRD_PARTY_RATING = "THIRD_PARTY_RATING"
    GENERAL_RISK_US = "GENERAL_RISK_US"
    GENERAL_RISK_UK = "GENERAL_RISK_UK"
    ADVISORY_FEE = "ADVISORY_FEE"
    TOTAL_COST = "TOTAL_COST"
    SEC_REGISTRATION = "SEC_REGISTRATION"
    FINRA_MEMBERSHIP = "FINRA_MEMBERSHIP"
    FCA_AUTHORIZATION = "FCA_AUTHORIZATION"
    HIGH_RISK_INVESTMENT = "HIGH_RISK_INVESTMENT"
    CAPITAL_AT_RISK = "CAPITAL_AT_RISK"


@dataclass
class DisclosureTemplate:
    """A disclosure template with placeholder support."""
    disclosure_type: DisclosureType
    template_text: str
    placeholders: list[str]
    jurisdiction: str  # "US", "UK", or "BOTH"
    is_firm_customized: bool = False


@dataclass
class InsertionPoint:
    """A location in the content where a disclosure should be inserted."""
    position: int  # Character offset in the content
    anchor_text: str  # Nearby text for human reference
    placement: str  # "AFTER", "BEFORE", "FOOTER", "INLINE"


@dataclass
class DisclosureInsertion:
    """A disclosure to be inserted at a specific location."""
    disclosure_type: DisclosureType
    disclosure_text: str
    insertion_point: InsertionPoint
    is_required: bool
    rule_citation: str
    status: str = "PENDING"  # "PENDING", "INSERTED", "SKIPPED"


@dataclass
class InsertionResult:
    """Result of a disclosure insertion operation."""
    result_id: str
    timestamp: str
    content_source: str
    original_content_hash: str
    modified_content: Optional[str]
    insertions: list[DisclosureInsertion]
    disclosures_required: list[DisclosureType]
    disclosures_present: list[DisclosureType]
    disclosures_missing: list[DisclosureType]
    advisory_notice: str = (
        "This is an advisory first-pass review, not compliance certification. "
        "All inserted disclosures require human compliance officer approval."
    )


def load_default_templates() -> dict[DisclosureType, DisclosureTemplate]:
    """Load default disclosure templates from the references directory.

    Reads standard regulatory disclosure language from
    references/disclosure_templates.md and parses each template into
    a DisclosureTemplate object.

    Returns:
        dict[DisclosureType, DisclosureTemplate]: Mapping of disclosure
            type to its template. Templates contain placeholder markers
            (e.g., [Firm Name], [X]%) for firm-specific customization.
    """
    # TODO: Implement template loading from references/disclosure_templates.md.
    # Parse the markdown file to extract each template section.
    return {}


def load_firm_templates(
    firm_templates_path: Path,
) -> dict[DisclosureType, DisclosureTemplate]:
    """Load firm-specific disclosure templates that override defaults.

    Args:
        firm_templates_path: Path to the firm's custom disclosure templates
            file (typically workspace/config/firm_disclosures.md).

    Returns:
        dict[DisclosureType, DisclosureTemplate]: Firm-customized templates.
            These take priority over default templates.

    Raises:
        FileNotFoundError: If the firm templates file does not exist.
        ValueError: If templates contain unresolved required placeholders.
    """
    # TODO: Implement firm-specific template loading.
    return {}


def determine_required_disclosures(
    content: str,
    content_types: list[ContentType],
    jurisdictions: list[str],
) -> list[DisclosureType]:
    """Determine which disclosures are required based on content classification.

    Maps content types and jurisdictions to the set of required disclosures.
    For example, PERFORMANCE content in a US jurisdiction requires
    PAST_PERFORMANCE_US and potentially GROSS_NET and BENCHMARK disclosures.

    Args:
        content: The text content (used for additional context analysis).
        content_types: List of ContentType classifications for the content.
        jurisdictions: List of applicable jurisdictions ("US", "UK").

    Returns:
        list[DisclosureType]: All disclosure types required for this content.
    """
    # TODO: Implement disclosure requirement mapping.
    # Use the mapping table from SKILL.md to determine requirements.
    return []


def detect_existing_disclosures(
    content: str,
    templates: dict[DisclosureType, DisclosureTemplate],
) -> list[DisclosureType]:
    """Detect which required disclosures are already present in the content.

    Scans the content for text matching known disclosure templates (both
    default and firm-specific). Uses fuzzy matching to account for minor
    variations in wording.

    Args:
        content: The text content to scan for existing disclosures.
        templates: Available disclosure templates to match against.

    Returns:
        list[DisclosureType]: Disclosure types already present in the content.
    """
    # TODO: Implement existing disclosure detection.
    # 1. For each template, check if key phrases appear in the content.
    # 2. Use fuzzy matching to catch paraphrased versions.
    # 3. Return the list of disclosure types found.
    return []


def find_insertion_points(
    content: str,
    disclosures_to_insert: list[DisclosureType],
) -> dict[DisclosureType, InsertionPoint]:
    """Determine optimal insertion points for each missing disclosure.

    Analyzes the content structure to find appropriate locations for each
    disclosure. Follows placement rules: performance disclosures near
    performance data, risk warnings prominent and not buried, regulatory
    status at document footer.

    Args:
        content: The text content to analyze for insertion points.
        disclosures_to_insert: List of disclosure types that need insertion.

    Returns:
        dict[DisclosureType, InsertionPoint]: Mapping of each disclosure
            type to its recommended insertion point in the content.
    """
    # TODO: Implement insertion point analysis.
    # 1. Parse content structure (sections, paragraphs, footers).
    # 2. For each disclosure type, apply placement rules.
    # 3. Performance disclosures: immediately after performance data.
    # 4. Risk warnings: prominent position, not footnotes.
    # 5. Regulatory status: document footer.
    return {}


def insert_disclosures(
    content: str,
    disclosures: list[DisclosureInsertion],
) -> str:
    """Insert disclosure text into content at the specified positions.

    Modifies the content by inserting disclosure text at each specified
    insertion point. Handles formatting to ensure disclosures are visually
    distinct (e.g., wrapped in appropriate HTML tags for HTML content).

    Args:
        content: The original text content.
        disclosures: List of DisclosureInsertion objects specifying what
            to insert and where.

    Returns:
        str: The modified content with disclosures inserted.
    """
    # TODO: Implement disclosure insertion.
    # 1. Sort insertions by position (reverse order to preserve offsets).
    # 2. Insert each disclosure at its specified position.
    # 3. Wrap in appropriate formatting tags.
    # 4. Update insertion status to "INSERTED".
    return content


def validate_disclosure_placement(
    content: str,
    disclosures: list[DisclosureInsertion],
) -> list[dict[str, str]]:
    """Validate that inserted disclosures meet prominence requirements.

    Checks that disclosures are not buried in footnotes, small print, or
    otherwise obscured. Verifies that key disclosures (risk warnings,
    past performance) are in prominent positions.

    Args:
        content: The content with disclosures inserted.
        disclosures: The list of insertions that were made.

    Returns:
        list[dict[str, str]]: Validation issues, each with 'disclosure_type',
            'issue', and 'remediation' keys. Empty list if all placements
            are satisfactory.
    """
    # TODO: Implement placement validation.
    # Check for footnote-only placement of required prominent disclosures.
    return []


def run_disclosure_pipeline(
    content: str,
    content_source: str,
    content_types: list[ContentType],
    jurisdictions: list[str],
    firm_templates_path: Optional[Path] = None,
) -> InsertionResult:
    """Run the full disclosure insertion pipeline.

    Determines required disclosures, detects existing ones, finds insertion
    points for missing disclosures, inserts them, and validates placement.

    Args:
        content: The text content to process.
        content_source: Identifier for the source file.
        content_types: Content type classifications.
        jurisdictions: Applicable jurisdictions.
        firm_templates_path: Optional path to firm-specific templates.
            If not provided, default templates are used.

    Returns:
        InsertionResult: Complete result including modified content,
            insertion details, and disclosure gap analysis.
    """
    # TODO: Implement full pipeline.
    # 1. Load templates (firm-specific overriding defaults).
    # 2. Determine required disclosures.
    # 3. Detect existing disclosures.
    # 4. Compute missing disclosures.
    # 5. Find insertion points.
    # 6. Create DisclosureInsertion objects.
    # 7. Insert disclosures.
    # 8. Validate placement.
    # 9. Always include advisory_notice.
    import hashlib
    return InsertionResult(
        result_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        content_source=content_source,
        original_content_hash=hashlib.sha256(content.encode()).hexdigest(),
        modified_content=content,
        insertions=[],
        disclosures_required=[],
        disclosures_present=[],
        disclosures_missing=[],
    )
