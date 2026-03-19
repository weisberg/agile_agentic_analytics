"""Search term analysis for paid media campaigns.

Identifies wasted ad spend from irrelevant or underperforming search terms
and generates negative keyword recommendations with match type suggestions
and waste savings estimates.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_CPA_MULTIPLIER: float = 3.0
DEFAULT_MIN_IMPRESSIONS: int = 50
DEFAULT_MIN_SPEND: Decimal = Decimal("5.00")


@dataclass
class WastedTerm:
    """A search term identified as generating waste."""

    search_term: str
    campaign_id: str
    ad_group_id: str
    impressions: int
    clicks: int
    spend: Decimal
    conversions: int
    cpa: Optional[Decimal]
    waste_reason: str


@dataclass
class NegativeKeywordRecommendation:
    """A recommended negative keyword with estimated savings."""

    keyword: str
    match_type: str  # "exact" or "phrase"
    campaign_id: str
    cluster_label: str
    estimated_monthly_waste: Decimal
    term_count: int
    contributing_terms: list[str]


# ---------------------------------------------------------------------------
# Waste identification
# ---------------------------------------------------------------------------


def load_search_terms(
    file_path: str,
    platform: str,
) -> pd.DataFrame:
    """Load a platform-specific search term report CSV.

    Parameters
    ----------
    file_path:
        Path to the search term CSV
        (e.g., ``workspace/raw/search_terms_google.csv``).
    platform:
        Platform identifier (``google`` or ``microsoft``).

    Returns
    -------
    pd.DataFrame
        Search term data with normalized column names.
    """
    # TODO: load CSV, normalize column names per platform
    raise NotImplementedError


def flag_zero_conversion_terms(
    df: pd.DataFrame,
    min_impressions: int = DEFAULT_MIN_IMPRESSIONS,
    min_spend: Decimal = DEFAULT_MIN_SPEND,
) -> pd.DataFrame:
    """Flag search terms with significant spend but zero conversions.

    Parameters
    ----------
    df:
        Search term DataFrame with ``impressions``, ``spend``, and
        ``conversions`` columns.
    min_impressions:
        Minimum impression threshold to consider a term significant.
    min_spend:
        Minimum spend threshold (Decimal) to consider a term significant.

    Returns
    -------
    pd.DataFrame
        Subset of *df* where conversions == 0 and both impression and spend
        thresholds are met.
    """
    # TODO: filter to zero-conversion terms exceeding thresholds
    raise NotImplementedError


def flag_high_cpa_terms(
    df: pd.DataFrame,
    campaign_avg_cpa: Decimal,
    cpa_multiplier: float = DEFAULT_CPA_MULTIPLIER,
) -> pd.DataFrame:
    """Flag search terms with CPA exceeding a multiple of campaign average.

    Parameters
    ----------
    df:
        Search term DataFrame with ``spend`` and ``conversions`` columns.
    campaign_avg_cpa:
        The campaign-level average CPA for comparison.
    cpa_multiplier:
        Threshold multiplier. Terms with CPA > campaign_avg_cpa * multiplier
        are flagged.

    Returns
    -------
    pd.DataFrame
        Subset of *df* where term-level CPA exceeds the threshold.
    """
    # TODO: compute per-term CPA, filter by threshold
    raise NotImplementedError


def flag_irrelevant_terms(
    df: pd.DataFrame,
    brand_terms: list[str] | None = None,
    competitor_terms: list[str] | None = None,
) -> pd.DataFrame:
    """Flag semantically irrelevant search terms.

    Identifies brand misspellings and unwanted competitor terms using
    fuzzy string matching.

    Parameters
    ----------
    df:
        Search term DataFrame with a ``search_term`` column.
    brand_terms:
        Known brand terms for misspelling detection.
    competitor_terms:
        Competitor brand terms to flag if appearing in search queries
        (when competitor targeting is not desired).

    Returns
    -------
    pd.DataFrame
        Subset of *df* containing semantically irrelevant terms.
    """
    # TODO: fuzzy match against brand/competitor lists
    raise NotImplementedError


def identify_wasted_terms(
    df: pd.DataFrame,
    campaign_avg_cpa: Decimal,
    min_impressions: int = DEFAULT_MIN_IMPRESSIONS,
    min_spend: Decimal = DEFAULT_MIN_SPEND,
    cpa_multiplier: float = DEFAULT_CPA_MULTIPLIER,
    brand_terms: list[str] | None = None,
    competitor_terms: list[str] | None = None,
) -> list[WastedTerm]:
    """Run all waste identification checks and return flagged terms.

    Combines zero-conversion, high-CPA, and irrelevant-term checks into a
    deduplicated list of wasted terms.

    Parameters
    ----------
    df:
        Full search term DataFrame.
    campaign_avg_cpa:
        Campaign-level average CPA for high-CPA comparison.
    min_impressions:
        Minimum impressions for zero-conversion flagging.
    min_spend:
        Minimum spend for zero-conversion flagging.
    cpa_multiplier:
        CPA multiplier threshold.
    brand_terms:
        Known brand terms for misspelling detection.
    competitor_terms:
        Competitor terms to flag.

    Returns
    -------
    list[WastedTerm]
        Deduplicated list of wasted terms sorted by spend descending.
    """
    # TODO: union all flag methods, deduplicate, build WastedTerm objects
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Negative keyword extraction
# ---------------------------------------------------------------------------


def cluster_terms(
    terms: list[str],
    n_clusters: int | None = None,
) -> dict[str, list[str]]:
    """Group flagged search terms into thematic clusters.

    Uses TF-IDF vectorization and agglomerative clustering to group
    semantically similar terms together.

    Parameters
    ----------
    terms:
        List of search term strings to cluster.
    n_clusters:
        Number of clusters. If ``None``, determined automatically using
        silhouette scoring.

    Returns
    -------
    dict[str, list[str]]
        Mapping of cluster label to list of terms in that cluster.
    """
    # TODO: TF-IDF vectorize, agglomerative cluster, label clusters
    raise NotImplementedError


def recommend_match_type(term: str) -> str:
    """Recommend negative keyword match type based on term specificity.

    Single-word terms get phrase match (broader exclusion). Multi-word
    specific terms get exact match (targeted exclusion).

    Parameters
    ----------
    term:
        The candidate negative keyword.

    Returns
    -------
    str
        ``"exact"`` or ``"phrase"``.
    """
    # TODO: heuristic based on word count and specificity
    raise NotImplementedError


def estimate_monthly_waste(
    terms: list[WastedTerm],
    lookback_days: int = 30,
) -> Decimal:
    """Estimate monthly waste savings from adding negative keywords.

    Extrapolates observed waste over the lookback period to a 30-day estimate.

    Parameters
    ----------
    terms:
        Wasted terms in the cluster.
    lookback_days:
        Number of days covered by the input data.

    Returns
    -------
    Decimal
        Estimated monthly spend savings.
    """
    # TODO: sum spend from terms, scale to 30 days
    raise NotImplementedError


def generate_negative_keywords(
    wasted_terms: list[WastedTerm],
    lookback_days: int = 30,
) -> list[NegativeKeywordRecommendation]:
    """Generate negative keyword recommendations from wasted terms.

    Clusters terms, selects representative keywords per cluster, recommends
    match types, and estimates waste savings.

    Parameters
    ----------
    wasted_terms:
        Output of ``identify_wasted_terms``.
    lookback_days:
        Days covered by the source data, for waste extrapolation.

    Returns
    -------
    list[NegativeKeywordRecommendation]
        Recommendations sorted by estimated monthly waste descending.
    """
    # TODO: cluster -> representative keyword -> match type -> waste estimate
    raise NotImplementedError
