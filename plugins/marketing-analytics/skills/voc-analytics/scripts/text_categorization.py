"""
Theme extraction from open-text survey responses using LLM API calls.

This module categorizes free-text customer feedback into predefined and
emergent themes using Claude API with structured output. It also performs
sentiment scoring (positive/neutral/negative with intensity) on each
response.

Usage:
    python text_categorization.py \
        --input workspace/raw/survey_responses.csv \
        --taxonomy references/theme_taxonomy.json \
        --output workspace/analysis/text_themes.json \
        --batch-size 30

Dependencies:
    anthropic, pandas, json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ThemeClassification:
    """A single theme assigned to a response."""

    theme_name: str
    is_predefined: bool
    confidence: float  # 0.0 to 1.0


@dataclass
class SentimentScore:
    """Sentiment assessment for a single response."""

    polarity: str  # "positive", "neutral", "negative"
    intensity: float  # 0.0 to 1.0
    mixed: bool = False  # True if response contains conflicting sentiment


@dataclass
class ResponseClassification:
    """Complete classification result for a single survey response."""

    respondent_id: str
    response_text: str
    themes: list[ThemeClassification]
    sentiment: SentimentScore
    language: str  # ISO 639-1 code


@dataclass
class ThemeSummary:
    """Aggregated theme statistics across all responses."""

    theme_name: str
    count: int
    pct_of_responses: float
    net_sentiment: float  # -1.0 to 1.0
    is_emergent: bool
    first_detected: Optional[str] = None  # ISO date string


@dataclass
class CategorizationResult:
    """Complete output of the text categorization pipeline."""

    total_responses: int
    classifications: list[ResponseClassification]
    theme_summaries: list[ThemeSummary]
    emergent_themes: list[ThemeSummary]


# ---------------------------------------------------------------------------
# Theme taxonomy
# ---------------------------------------------------------------------------

DEFAULT_THEME_TAXONOMY: list[str] = [
    "Product Quality",
    "Customer Service",
    "Pricing & Value",
    "Digital Experience",
    "Onboarding",
    "Communication",
    "Trust & Security",
    "Speed & Efficiency",
]


def load_theme_taxonomy(taxonomy_path: Optional[Path] = None) -> list[str]:
    """Load predefined theme taxonomy from a JSON file.

    If no path is provided, returns the default taxonomy.

    Args:
        taxonomy_path: Optional path to a JSON file containing a list of
            theme name strings.

    Returns:
        List of predefined theme names.

    Raises:
        FileNotFoundError: If the specified taxonomy file does not exist.
        ValueError: If the file does not contain a valid JSON list of strings.
    """
    # TODO: Implement taxonomy loading
    raise NotImplementedError("load_theme_taxonomy not yet implemented")


# ---------------------------------------------------------------------------
# LLM-based classification
# ---------------------------------------------------------------------------

def build_classification_prompt(
    responses: list[dict[str, str]],
    taxonomy: list[str],
) -> list[dict[str, str]]:
    """Build the message list for the Claude API classification call.

    Constructs a system prompt defining the analyst role and output schema,
    and a user prompt containing the theme taxonomy and batch of responses
    to classify.

    Args:
        responses: List of dicts with keys "respondent_id" and
            "response_text".
        taxonomy: List of predefined theme names.

    Returns:
        List of message dicts suitable for the Anthropic messages API,
        with "role" and "content" keys.
    """
    # TODO: Implement prompt construction per references/text_analytics.md
    raise NotImplementedError("build_classification_prompt not yet implemented")


def call_llm_classification(
    messages: list[dict[str, str]],
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 4096,
    api_key: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Call the Claude API to classify a batch of responses.

    Sends the classification prompt to the Anthropic messages API and
    parses the structured JSON output.

    Args:
        messages: Message list from build_classification_prompt.
        model: Anthropic model identifier.
        max_tokens: Maximum tokens in the response.
        api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY
            environment variable.

    Returns:
        List of classification dicts parsed from the LLM JSON response.
        Each dict contains: respondent_id, themes, sentiment, language.

    Raises:
        RuntimeError: If the API call fails or the response is not valid JSON.
    """
    # TODO: Implement API call with structured output parsing
    raise NotImplementedError("call_llm_classification not yet implemented")


def parse_llm_response(
    raw_classifications: list[dict[str, Any]],
    response_texts: dict[str, str],
) -> list[ResponseClassification]:
    """Parse raw LLM classification output into typed dataclasses.

    Validates theme names, sentiment values, and confidence scores.
    Logs warnings for any malformed entries.

    Args:
        raw_classifications: List of classification dicts from the LLM.
        response_texts: Mapping of respondent_id to original response text.

    Returns:
        List of validated ResponseClassification objects.
    """
    # TODO: Implement parsing and validation
    raise NotImplementedError("parse_llm_response not yet implemented")


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

def extract_open_text_responses(df: pd.DataFrame) -> list[dict[str, str]]:
    """Extract open-text responses from the survey DataFrame.

    Filters to rows with non-empty text in the 'response' column and
    returns a list of dicts with respondent_id and response_text.

    Args:
        df: Survey response DataFrame with columns: respondent_id,
            question_id, response, score, timestamp.

    Returns:
        List of dicts, each with "respondent_id" and "response_text" keys.
    """
    # TODO: Implement response extraction and filtering
    raise NotImplementedError(
        "extract_open_text_responses not yet implemented"
    )


def classify_responses_in_batches(
    responses: list[dict[str, str]],
    taxonomy: list[str],
    batch_size: int = 30,
    model: str = "claude-sonnet-4-20250514",
    api_key: Optional[str] = None,
) -> list[ResponseClassification]:
    """Classify all responses by processing them in batches through the LLM.

    Batches responses into groups of batch_size, calls the LLM for each
    batch, and aggregates results. Handles rate limiting with exponential
    backoff.

    Args:
        responses: List of dicts with "respondent_id" and "response_text".
        taxonomy: List of predefined theme names.
        batch_size: Number of responses per LLM call (20-50 recommended).
        model: Anthropic model identifier.
        api_key: Anthropic API key.

    Returns:
        List of ResponseClassification objects for all responses.

    Raises:
        RuntimeError: If more than 3 consecutive batch calls fail.
    """
    # TODO: Implement batched classification with error handling
    raise NotImplementedError(
        "classify_responses_in_batches not yet implemented"
    )


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def compute_theme_summaries(
    classifications: list[ResponseClassification],
    taxonomy: list[str],
) -> tuple[list[ThemeSummary], list[ThemeSummary]]:
    """Aggregate theme frequencies and sentiment across all classifications.

    Args:
        classifications: List of per-response classification results.
        taxonomy: Predefined theme list, used to distinguish predefined
            from emergent themes.

    Returns:
        Tuple of (predefined_theme_summaries, emergent_theme_summaries).
        Each summary includes count, percentage, and net sentiment.
    """
    # TODO: Implement theme aggregation
    raise NotImplementedError("compute_theme_summaries not yet implemented")


def consolidate_emergent_themes(
    emergent_themes: list[ThemeSummary],
    similarity_threshold: float = 0.85,
) -> list[ThemeSummary]:
    """Merge similar emergent themes that may have been named differently
    across batches.

    Uses string similarity to identify near-duplicate theme names and
    consolidates their counts and sentiment scores.

    Args:
        emergent_themes: List of emergent ThemeSummary objects.
        similarity_threshold: Minimum similarity ratio (0-1) for merging.

    Returns:
        Deduplicated list of emergent ThemeSummary objects.
    """
    # TODO: Implement theme deduplication
    raise NotImplementedError(
        "consolidate_emergent_themes not yet implemented"
    )


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def write_results(result: CategorizationResult, output_path: Path) -> None:
    """Serialize categorization results to JSON.

    Args:
        result: Complete categorization result to serialize.
        output_path: Path for the output JSON file.
    """
    # TODO: Implement JSON serialization
    raise NotImplementedError("write_results not yet implemented")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Extract themes and sentiment from survey open-text."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to survey_responses.csv",
    )
    parser.add_argument(
        "--taxonomy",
        type=Path,
        default=None,
        help="Path to theme taxonomy JSON (optional, uses defaults)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path for output text_themes.json",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=30,
        help="Responses per LLM batch (default: 30)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4-20250514",
        help="Anthropic model identifier",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    """Main entry point for CLI execution.

    Args:
        argv: Optional argument list for testing.
    """
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO)

    logger.info("Loading survey data from %s", args.input)
    df = pd.read_csv(args.input)

    taxonomy = load_theme_taxonomy(args.taxonomy)
    logger.info("Using %d predefined themes", len(taxonomy))

    responses = extract_open_text_responses(df)
    logger.info("Found %d open-text responses to classify", len(responses))

    classifications = classify_responses_in_batches(
        responses,
        taxonomy=taxonomy,
        batch_size=args.batch_size,
        model=args.model,
    )

    predefined, emergent = compute_theme_summaries(classifications, taxonomy)
    emergent = consolidate_emergent_themes(emergent)

    result = CategorizationResult(
        total_responses=len(classifications),
        classifications=classifications,
        theme_summaries=predefined + emergent,
        emergent_themes=emergent,
    )

    write_results(result, args.output)
    logger.info("Done. Classified %d responses into themes.", len(classifications))


if __name__ == "__main__":
    main()
