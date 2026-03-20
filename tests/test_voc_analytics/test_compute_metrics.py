"""Tests for voc-analytics / compute_metrics.py

Covers NPS computation, NPS bootstrap CI, CSAT, and CES calculations.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

# Make the scripts directory importable.
_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "marketing-analytics"
    / "skills"
    / "voc-analytics"
    / "scripts"
)
sys.path.insert(0, str(_SCRIPTS_DIR))

from compute_metrics import (
    bootstrap_nps_ci,
    compute_csat,
    compute_ces,
    compute_nps,
)


# ---------------------------------------------------------------------------
# test_nps_computation  -- known NPS calculation
# ---------------------------------------------------------------------------

class TestNpsComputation:
    """Known NPS calculations with hand-verified results."""

    def test_all_promoters(self):
        """All scores 9-10 => NPS = +100."""
        scores = np.array([9, 10, 9, 10, 10])
        result = compute_nps(scores)
        assert result.nps == 100.0
        assert result.promoters == 5
        assert result.detractors == 0

    def test_all_detractors(self):
        """All scores 0-6 => NPS = -100."""
        scores = np.array([0, 1, 2, 3, 4, 5, 6])
        result = compute_nps(scores)
        assert result.nps == -100.0
        assert result.promoters == 0
        assert result.detractors == 7

    def test_mixed_known_value(self):
        """Hand-calculated: 4 promoters, 3 passives, 3 detractors out of 10.
        NPS = (40% - 30%) = 10.0
        """
        scores = np.array([10, 9, 10, 9, 8, 7, 8, 5, 3, 1])
        result = compute_nps(scores)
        assert result.promoters == 4
        assert result.passives == 3
        assert result.detractors == 3
        assert result.nps == pytest.approx(10.0, abs=0.01)

    def test_all_passives(self):
        """All scores 7-8 => NPS = 0."""
        scores = np.array([7, 8, 7, 8])
        result = compute_nps(scores)
        assert result.nps == 0.0

    def test_empty_scores_raises(self):
        with pytest.raises(ValueError, match="not be empty"):
            compute_nps(np.array([]))

    def test_out_of_range_scores_raises(self):
        with pytest.raises(ValueError, match="0-10"):
            compute_nps(np.array([0, 5, 11]))

    def test_percentages_sum_to_100(self):
        scores = np.array([0, 3, 5, 7, 8, 9, 10])
        result = compute_nps(scores)
        total = result.pct_promoters + result.pct_passives + result.pct_detractors
        assert total == pytest.approx(100.0, abs=0.1)


# ---------------------------------------------------------------------------
# test_nps_bootstrap_ci  -- CI contains true NPS
# ---------------------------------------------------------------------------

class TestNpsBootstrapCi:
    """Validate bootstrap CI for NPS."""

    def test_ci_contains_point_estimate(self):
        """The CI should contain the observed NPS for a reasonably sized sample."""
        rng = np.random.default_rng(42)
        # Create a sample with known NPS around +20
        scores = rng.choice(
            range(0, 11), size=200,
            p=[0.02, 0.02, 0.03, 0.03, 0.05, 0.05, 0.10, 0.15, 0.15, 0.20, 0.20],
        )
        observed_nps = compute_nps(scores).nps
        ci = bootstrap_nps_ci(scores, n_bootstrap=5_000, random_seed=42)

        assert ci.lower <= observed_nps <= ci.upper

    def test_ci_width_shrinks_with_sample_size(self):
        """Larger samples should produce narrower CIs."""
        rng = np.random.default_rng(7)
        small = rng.choice(range(0, 11), size=50)
        large = rng.choice(range(0, 11), size=500)

        ci_small = bootstrap_nps_ci(small, n_bootstrap=5_000, random_seed=1)
        ci_large = bootstrap_nps_ci(large, n_bootstrap=5_000, random_seed=1)

        width_small = ci_small.upper - ci_small.lower
        width_large = ci_large.upper - ci_large.lower
        assert width_large < width_small

    def test_95_ci_is_narrower_than_99(self):
        scores = np.array([0, 3, 5, 7, 8, 9, 10] * 30)
        ci_95 = bootstrap_nps_ci(scores, confidence_level=0.95, n_bootstrap=5_000, random_seed=0)
        ci_99 = bootstrap_nps_ci(scores, confidence_level=0.99, n_bootstrap=5_000, random_seed=0)

        assert (ci_99.upper - ci_99.lower) > (ci_95.upper - ci_95.lower)

    def test_minimum_bootstrap_iterations(self):
        scores = np.array([5, 7, 9, 10])
        with pytest.raises(ValueError, match="1000"):
            bootstrap_nps_ci(scores, n_bootstrap=500)

    def test_invalid_confidence_level(self):
        scores = np.array([5, 7, 9, 10])
        with pytest.raises(ValueError):
            bootstrap_nps_ci(scores, confidence_level=1.5)


# ---------------------------------------------------------------------------
# test_csat_computation  -- basic CSAT calc
# ---------------------------------------------------------------------------

class TestCsatComputation:
    """Basic Customer Satisfaction Score tests."""

    def test_all_top_box(self):
        """All 5s on a 1-5 scale with top_box=2 => 100%."""
        scores = np.array([5, 5, 5, 5, 5])
        assert compute_csat(scores, scale_max=5, top_box=2) == 100.0

    def test_no_top_box(self):
        """All 1s on a 1-5 scale with top_box=2 => 0%."""
        scores = np.array([1, 1, 1, 1, 1])
        assert compute_csat(scores, scale_max=5, top_box=2) == 0.0

    def test_known_csat(self):
        """3 out of 5 respondents gave 4 or 5 => CSAT = 60%."""
        scores = np.array([5, 4, 3, 2, 4])
        result = compute_csat(scores, scale_max=5, top_box=2)
        assert result == pytest.approx(60.0, abs=0.1)

    def test_scale_max_7(self):
        """7-point scale with top_box=2: scores >= 6 count as satisfied."""
        scores = np.array([7, 6, 5, 4, 3, 2, 1, 6, 7, 5])
        # Satisfied: 7, 6, 6, 7 = 4 out of 10 = 40%
        result = compute_csat(scores, scale_max=7, top_box=2)
        assert result == pytest.approx(40.0, abs=0.1)

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="not be empty"):
            compute_csat(np.array([]))

    def test_top_box_exceeds_scale(self):
        with pytest.raises(ValueError, match="top_box"):
            compute_csat(np.array([1, 2, 3]), scale_max=3, top_box=3)


# ---------------------------------------------------------------------------
# test_ces_computation  -- basic CES calc
# ---------------------------------------------------------------------------

class TestCesComputation:
    """Basic Customer Effort Score tests."""

    def test_known_mean(self):
        """Mean of [1,2,3,4,5,6,7] = 4.0."""
        scores = np.array([1, 2, 3, 4, 5, 6, 7])
        assert compute_ces(scores) == pytest.approx(4.0, abs=1e-9)

    def test_all_same(self):
        """All 5s => CES = 5.0."""
        scores = np.array([5, 5, 5, 5])
        assert compute_ces(scores) == pytest.approx(5.0, abs=1e-9)

    def test_low_effort(self):
        """Low effort scores => low CES."""
        scores = np.array([1, 1, 2, 1, 2])
        assert compute_ces(scores) == pytest.approx(1.4, abs=1e-9)

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="not be empty"):
            compute_ces(np.array([]))

    def test_float_precision(self):
        """CES should handle float input cleanly."""
        scores = np.array([1.5, 2.5, 3.5])
        assert compute_ces(scores) == pytest.approx(2.5, abs=1e-9)
