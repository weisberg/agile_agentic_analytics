"""Tests for funnel-analysis / funnel_stats.py

Covers Wilson score intervals, edge cases, bottleneck ranking, and
chi-squared cohort comparison.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

# Make the scripts directory importable.
_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2] / "plugins" / "marketing-analytics" / "skills" / "funnel-analysis" / "scripts"
)
sys.path.insert(0, str(_SCRIPTS_DIR))

from funnel_stats import (
    FunnelStats,
    StageStats,
    WilsonInterval,
    chi_squared_comparison,
    rank_bottlenecks,
    wilson_score_interval,
)


# ---------------------------------------------------------------------------
# test_wilson_score_interval  -- validates against known values
# ---------------------------------------------------------------------------


class TestWilsonScoreInterval:
    """Validate the Wilson score CI against analytically known values."""

    def test_known_50_percent(self):
        """50/100 at 95% CI should produce a narrow interval around 0.5."""
        wi = wilson_score_interval(k=50, n=100, confidence_level=0.95)

        assert wi.point_estimate == pytest.approx(0.5, abs=1e-9)
        assert wi.lower < 0.5
        assert wi.upper > 0.5
        # Known Wilson interval for 50/100 at 95%: ~[0.401, 0.599]
        assert wi.lower == pytest.approx(0.4013, abs=0.005)
        assert wi.upper == pytest.approx(0.5987, abs=0.005)

    def test_high_conversion(self):
        """90/100 -- interval should be mostly above 0.8."""
        wi = wilson_score_interval(k=90, n=100)
        assert wi.point_estimate == pytest.approx(0.9, abs=1e-9)
        assert wi.lower > 0.80
        assert wi.upper <= 1.0

    def test_low_conversion(self):
        """5/100 -- interval should be entirely below 0.15."""
        wi = wilson_score_interval(k=5, n=100)
        assert wi.point_estimate == pytest.approx(0.05, abs=1e-9)
        assert wi.lower >= 0.0
        assert wi.upper < 0.15

    def test_small_sample(self):
        """3/10 at 95% -- interval should still be valid."""
        wi = wilson_score_interval(k=3, n=10)
        assert 0.0 <= wi.lower <= wi.point_estimate
        assert wi.point_estimate <= wi.upper <= 1.0

    def test_confidence_level_99(self):
        """99% CI should be wider than 95% CI."""
        wi_95 = wilson_score_interval(k=50, n=100, confidence_level=0.95)
        wi_99 = wilson_score_interval(k=50, n=100, confidence_level=0.99)

        width_95 = wi_95.upper - wi_95.lower
        width_99 = wi_99.upper - wi_99.lower
        assert width_99 > width_95

    def test_metadata_fields(self):
        wi = wilson_score_interval(k=25, n=200, confidence_level=0.90)
        assert wi.n == 200
        assert wi.k == 25
        assert wi.confidence_level == 0.90


# ---------------------------------------------------------------------------
# test_wilson_edge_cases  -- 0% and 100% conversion
# ---------------------------------------------------------------------------


class TestWilsonEdgeCases:
    """Edge case handling for boundary proportions."""

    def test_zero_conversions(self):
        """0/100 should produce a valid interval starting at 0."""
        wi = wilson_score_interval(k=0, n=100)
        assert wi.point_estimate == 0.0
        assert wi.lower == 0.0
        assert wi.upper > 0.0  # Wilson gives a nonzero upper bound
        assert wi.upper < 0.05  # but it should be small

    def test_all_conversions(self):
        """100/100 should produce a valid interval ending at 1."""
        wi = wilson_score_interval(k=100, n=100)
        assert wi.point_estimate == 1.0
        assert wi.upper == 1.0
        assert wi.lower < 1.0  # Wilson gives a lower bound below 1.0
        assert wi.lower > 0.95

    def test_invalid_k_greater_than_n(self):
        with pytest.raises(ValueError, match="cannot exceed"):
            wilson_score_interval(k=101, n=100)

    def test_invalid_negative_k(self):
        with pytest.raises(ValueError, match="non-negative"):
            wilson_score_interval(k=-1, n=100)

    def test_invalid_zero_n(self):
        with pytest.raises(ValueError, match="positive"):
            wilson_score_interval(k=0, n=0)

    def test_single_trial_success(self):
        """1/1 -- extreme small sample."""
        wi = wilson_score_interval(k=1, n=1)
        assert wi.point_estimate == 1.0
        assert 0.0 <= wi.lower <= 1.0
        assert wi.upper == 1.0

    def test_single_trial_failure(self):
        """0/1 -- extreme small sample."""
        wi = wilson_score_interval(k=0, n=1)
        assert wi.point_estimate == 0.0
        assert wi.lower == 0.0
        assert 0.0 < wi.upper <= 1.0


# ---------------------------------------------------------------------------
# test_bottleneck_ranking  -- validates scoring formula
# ---------------------------------------------------------------------------


def _make_funnel_stats(stage_data: list[tuple[str, int, int]]) -> FunnelStats:
    """Build a FunnelStats from a list of (name, entered, converted) tuples."""
    stages = []
    for i, (name, entered, converted) in enumerate(stage_data):
        dropped = entered - converted
        drop_rate = dropped / entered if entered > 0 else 0.0
        conv_rate = converted / entered if entered > 0 else 0.0
        stages.append(
            StageStats(
                stage_index=i,
                stage_name=name,
                entered=entered,
                converted=converted,
                dropped=dropped,
                conversion_rate=WilsonInterval(conv_rate, 0, 1, 0.95, entered, converted),
                drop_off_rate=WilsonInterval(drop_rate, 0, 1, 0.95, entered, dropped),
            )
        )

    total_entered = stage_data[0][1] if stage_data else 0
    total_completed = stage_data[-1][2] if stage_data else 0

    return FunnelStats(
        funnel_name="test_funnel",
        stages=stages,
        overall_conversion=WilsonInterval(0, 0, 1, 0.95, total_entered, total_completed),
        total_entered=total_entered,
        total_completed=total_completed,
    )


class TestBottleneckRanking:
    """Validates the composite bottleneck scoring formula."""

    def test_rank_ordering(self):
        """Stage with highest composite score should be rank 1."""
        fs = _make_funnel_stats(
            [
                ("Visit", 1000, 800),  # 20% drop-off
                ("Cart", 800, 400),  # 50% drop-off  <-- worst bottleneck
                ("Checkout", 400, 350),  # 12.5% drop-off
                ("Purchase", 350, 350),  # final stage, not ranked
            ]
        )
        bottlenecks = rank_bottlenecks(fs)

        assert bottlenecks[0].stage_name == "Cart"
        assert bottlenecks[0].rank == 1

    def test_composite_formula(self):
        """Verify the formula: drop_off * sqrt(volume) * revenue_proximity."""
        fs = _make_funnel_stats(
            [
                ("A", 1000, 600),  # drop_off=0.4, volume=1000, prox=1/3
                ("B", 600, 500),  # drop_off=0.167, volume=600, prox=1/2
                ("C", 500, 500),  # final stage
            ]
        )
        bottlenecks = rank_bottlenecks(fs)

        a_score = bottlenecks[0] if bottlenecks[0].stage_name == "A" else bottlenecks[1]

        expected = 0.4 * math.sqrt(1000) * (1.0 / 3)
        assert a_score.composite_score == pytest.approx(expected, rel=0.01)

    def test_single_stage_funnel(self):
        """Single-stage funnel should produce no bottlenecks."""
        fs = _make_funnel_stats([("Only", 100, 100)])
        bottlenecks = rank_bottlenecks(fs)
        assert len(bottlenecks) == 0

    def test_all_ranks_unique(self):
        fs = _make_funnel_stats(
            [
                ("A", 1000, 800),
                ("B", 800, 500),
                ("C", 500, 300),
                ("D", 300, 300),
            ]
        )
        bottlenecks = rank_bottlenecks(fs)
        ranks = [b.rank for b in bottlenecks]
        assert ranks == sorted(ranks)
        assert len(set(ranks)) == len(ranks)


# ---------------------------------------------------------------------------
# test_chi_squared_comparison
# ---------------------------------------------------------------------------


class TestChiSquaredComparison:
    """Validates significant vs. non-significant differences."""

    def test_significant_difference(self):
        """Large difference in conversion rates should be significant."""
        result = chi_squared_comparison(
            stage_name="Checkout",
            stage_index=2,
            cohort_a_name="Control",
            cohort_a_converted=100,
            cohort_a_total=1000,
            cohort_b_name="Variant",
            cohort_b_converted=200,
            cohort_b_total=1000,
        )
        assert result.significant is True
        assert result.p_value < 0.05
        assert result.cohort_a_rate == pytest.approx(0.1, abs=1e-9)
        assert result.cohort_b_rate == pytest.approx(0.2, abs=1e-9)
        assert result.relative_difference == pytest.approx(1.0, abs=0.01)

    def test_non_significant_difference(self):
        """Tiny difference should not be significant."""
        result = chi_squared_comparison(
            stage_name="Cart",
            stage_index=1,
            cohort_a_name="Control",
            cohort_a_converted=500,
            cohort_a_total=1000,
            cohort_b_name="Variant",
            cohort_b_converted=510,
            cohort_b_total=1000,
        )
        assert result.significant is False
        assert result.p_value > 0.05

    def test_identical_cohorts(self):
        """Identical conversion rates should not be significant."""
        result = chi_squared_comparison(
            stage_name="Visit",
            stage_index=0,
            cohort_a_name="A",
            cohort_a_converted=300,
            cohort_a_total=1000,
            cohort_b_name="B",
            cohort_b_converted=300,
            cohort_b_total=1000,
        )
        assert result.significant is False
        assert result.relative_difference == pytest.approx(0.0, abs=1e-9)

    def test_validation_errors(self):
        with pytest.raises(ValueError):
            chi_squared_comparison(
                stage_name="X",
                stage_index=0,
                cohort_a_name="A",
                cohort_a_converted=200,
                cohort_a_total=100,
                cohort_b_name="B",
                cohort_b_converted=50,
                cohort_b_total=100,
            )

    def test_small_sample_yates_correction(self):
        """Small expected cell counts should trigger Yates correction."""
        result = chi_squared_comparison(
            stage_name="Signup",
            stage_index=0,
            cohort_a_name="A",
            cohort_a_converted=2,
            cohort_a_total=10,
            cohort_b_name="B",
            cohort_b_converted=8,
            cohort_b_total=10,
        )
        # Should still return a valid result
        assert isinstance(result.p_value, float)
        assert 0.0 <= result.p_value <= 1.0
