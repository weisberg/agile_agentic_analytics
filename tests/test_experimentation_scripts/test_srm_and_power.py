"""Golden-value tests for experimentation srm_check.py and power_analysis.py."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "plugins" / "marketing-analytics" / "skills" / "experimentation" / "scripts"
)
sys.path.insert(0, str(_SCRIPTS))

from srm_check import run_srm_check  # noqa: E402
from power_analysis import (  # noqa: E402
    calculate_sample_size_proportion,
    calculate_sample_size_continuous,
    calculate_mde,
    estimate_duration,
)


# ---------------------------------------------------------------------------
# SRM detection
# ---------------------------------------------------------------------------
class TestSRM:
    def test_balanced_no_mismatch(self):
        res = run_srm_check({"A": 5000, "B": 5000})
        assert res.chi_squared_statistic == pytest.approx(0.0, abs=1e-12)
        assert res.has_mismatch is False

    def test_five_percent_imbalance_flags(self):
        # 5250/4750 vs expected 5000/5000 -> chi-square 25.0 (hand-computed)
        res = run_srm_check({"A": 5250, "B": 4750})
        # (250^2/5000)*2 = 25.0 ; cross-checked with scipy.stats.chisquare
        chi_ref = stats.chisquare([5250, 4750], [5000, 5000]).statistic
        assert res.chi_squared_statistic == pytest.approx(25.0, abs=1e-9)
        assert res.chi_squared_statistic == pytest.approx(chi_ref, abs=1e-9)
        assert res.p_value < 0.001
        assert res.has_mismatch is True

    def test_small_imbalance_not_flagged(self):
        # 5020/4980 -> chi-square 0.16, p ~ 0.69, no SRM
        res = run_srm_check({"A": 5020, "B": 4980})
        chi_ref = stats.chisquare([5020, 4980], [5000, 5000]).statistic
        assert res.chi_squared_statistic == pytest.approx(chi_ref, abs=1e-9)
        assert res.has_mismatch is False

    def test_pvalue_approx_matches_scipy(self):
        # Wilson-Hilferty approximation should track the true chi-square tail closely.
        res = run_srm_check({"A": 5150, "B": 4850})
        _, p_ref = stats.chisquare([5150, 4850], [5000, 5000])
        assert res.p_value == pytest.approx(p_ref, abs=5e-3)

    def test_custom_ratios_flag(self):
        # Expected 90/10 split, observed 8000/2000 -> strong mismatch
        res = run_srm_check({"A": 8000, "B": 2000}, expected_ratios={"A": 0.9, "B": 0.1})
        assert res.has_mismatch is True

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            run_srm_check({})

    def test_bad_ratios_raise(self):
        with pytest.raises(ValueError, match="sum to 1"):
            run_srm_check({"A": 10, "B": 10}, expected_ratios={"A": 0.4, "B": 0.4})


# ---------------------------------------------------------------------------
# Power / sample size
# ---------------------------------------------------------------------------
class TestPowerAnalysis:
    def test_proportion_sample_size_closed_form(self):
        # baseline 10%, relative MDE 0.2 (=> +2pp), alpha 0.05, power 0.8
        res = calculate_sample_size_proportion(0.10, 0.2, alpha=0.05, power=0.80)
        assert res.mde_absolute == pytest.approx(0.02, abs=1e-12)

        # Independent replication of the exact closed form the script uses.
        z_alpha = stats.norm.ppf(1 - 0.05 / 2)
        z_beta = stats.norm.ppf(0.80)
        p1, p2 = 0.10, 0.12
        p_bar = 0.11
        num = (z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
        n_ref = int(np.ceil(num / 0.02**2))
        assert res.sample_size_per_group == n_ref == 3841
        assert res.total_sample_size == n_ref * 2

    def test_proportion_in_statsmodels_ballpark(self):
        # Cohen's-h based statsmodels estimate should agree within ~3%.
        res = calculate_sample_size_proportion(0.10, 0.2, alpha=0.05, power=0.80)
        es = proportion_effectsize(0.12, 0.10)
        n_sm = NormalIndPower().solve_power(effect_size=es, alpha=0.05, power=0.80, ratio=1, alternative="two-sided")
        assert res.sample_size_per_group == pytest.approx(n_sm, rel=0.03)

    def test_continuous_sample_size_closed_form(self):
        # mean 100, std 20, relative MDE 0.05 (=> delta 5)
        res = calculate_sample_size_continuous(100.0, 20.0, 0.05, alpha=0.05, power=0.80)
        z_alpha = stats.norm.ppf(1 - 0.05 / 2)
        z_beta = stats.norm.ppf(0.80)
        delta = 5.0
        n_ref = int(np.ceil((z_alpha + z_beta) ** 2 * 2 * 20.0**2 / delta**2))
        assert res.sample_size_per_group == n_ref

    def test_mde_roundtrips_with_sample_size(self):
        # Feed the sample size back in; recovered relative MDE ~= input.
        # NOTE: calculate_mde uses a simpler single-variance formula than the
        # pooled+unpooled sample-size formula, so the round-trip is close but
        # not exact (recovers ~0.192 vs the 0.20 input, i.e. slightly more
        # conservative). This documents current behavior; ~4% gap is expected.
        res = calculate_sample_size_proportion(0.10, 0.2, alpha=0.05, power=0.80)
        mde = calculate_mde(res.sample_size_per_group, baseline_rate=0.10, alpha=0.05, power=0.80)
        assert mde == pytest.approx(0.192, abs=0.005)
        assert mde <= 0.2  # never over-optimistic about detectable effect

    def test_duration_rounds_to_weeks(self):
        # 10000 total / 1000 per day = 10 days -> rounds up to 14 (2 weeks)
        assert estimate_duration(10000, 1000, round_to_weeks=True) == 14
        # without week rounding, exactly 10 days
        assert estimate_duration(10000, 1000, round_to_weeks=False) == 10

    def test_invalid_inputs_raise(self):
        with pytest.raises(ValueError):
            calculate_sample_size_proportion(1.5, 0.2)  # baseline out of (0,1)
        with pytest.raises(ValueError):
            calculate_sample_size_proportion(0.1, -0.2)  # negative MDE
