"""Golden-value tests for campaign-analysis / analyze_cross_sell.py.

Every statistical assertion here is checked against an *independent* reference
(scipy / statsmodels / hand-computed), not merely "runs without error".
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest

_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "campaign-analysis"
    / "skills"
    / "cross-sell-analysis"
    / "scripts"
    / "analyze_cross_sell.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("analyze_cross_sell", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


xs = _load_module()


def _conv_frame(n_conv: int, n_total: int, funded=None) -> pd.DataFrame:
    """Build a per-eligible attach frame with `n_conv` converters out of n_total."""
    converted = np.array([True] * n_conv + [False] * (n_total - n_conv))
    if funded is None:
        funded_value = np.full(n_total, np.nan)
    else:
        funded_value = np.asarray(funded, dtype=float)
    return pd.DataFrame({"converted": converted, "funded_value": funded_value})


# ---------------------------------------------------------------------------
# wilson_ci -- against the closed-form Wilson interval
# ---------------------------------------------------------------------------
class TestWilsonCI:
    def test_known_50_of_100(self):
        low, high = xs.wilson_ci(50, 100, alpha=0.05)
        # Independent closed-form Wilson reference.
        z = stats.norm.ppf(0.975)
        n, phat = 100, 0.5
        denom = 1 + z**2 / n
        center = (phat + z**2 / (2 * n)) / denom
        half = z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2)) / denom
        assert low == pytest.approx(center - half, abs=1e-9)
        assert high == pytest.approx(center + half, abs=1e-9)
        # Symmetric around ~0.509 for 50/100 (Wilson center is pulled toward 0.5).
        assert low == pytest.approx(0.4038, abs=0.001)

    def test_zero_n(self):
        assert xs.wilson_ci(0, 0) == (0.0, 0.0)

    def test_bounds_clamped(self):
        low, high = xs.wilson_ci(100, 100)
        assert low >= 0.0 and high <= 1.0


# ---------------------------------------------------------------------------
# holdout_tests -- two-proportion z, Fisher's exact, bootstrap CI, sign/magnitude
# ---------------------------------------------------------------------------
class TestHoldoutTests:
    def test_lift_sign_and_magnitude(self):
        # treated 100/1000 (10%) vs holdout 50/1000 (5%): true lift = +0.05
        t = _conv_frame(100, 1000)
        h = _conv_frame(50, 1000)
        out = xs.holdout_tests(t, h)
        assert out["absolute_lift_pp"] == pytest.approx(0.05, abs=1e-12)
        # relative lift = 0.05 / 0.05 = 1.0 (100%)
        assert out["relative_lift"] == pytest.approx(1.0, abs=1e-9)
        # incremental opens = 0.05 * 1000 = 50
        assert out["incremental_opens_estimated"] == pytest.approx(50.0, abs=1e-9)

    def test_two_proportion_z_matches_statsmodels(self):
        t = _conv_frame(100, 1000)
        h = _conv_frame(50, 1000)
        out = xs.holdout_tests(t, h)
        # statsmodels pooled two-proportion z (same formula the script uses)
        z_ref, p_ref = proportions_ztest([100, 50], [1000, 1000])
        assert out["two_proportion_z_pvalue"] == pytest.approx(p_ref, rel=1e-6)
        assert out["two_proportion_z_pvalue"] == pytest.approx(2.1882e-05, rel=1e-3)

    def test_fisher_matches_scipy(self):
        t = _conv_frame(100, 1000)
        h = _conv_frame(50, 1000)
        out = xs.holdout_tests(t, h)
        _, p_ref = stats.fisher_exact([[100, 900], [50, 950]])
        assert out["fisher_exact_pvalue"] == pytest.approx(p_ref, rel=1e-9)

    def test_bootstrap_ci_covers_true_effect(self):
        t = _conv_frame(100, 1000)
        h = _conv_frame(50, 1000)
        out = xs.holdout_tests(t, h)
        lo, hi = out["absolute_lift_ci_95"]
        assert lo < 0.05 < hi
        # CI is a proper interval and reasonably tight for n=1000/arm
        assert hi - lo < 0.06

    def test_significant_flag_true(self):
        out = xs.holdout_tests(_conv_frame(100, 1000), _conv_frame(50, 1000))
        assert out["significant_at_0_05"] is True

    def test_no_effect_not_significant(self):
        # 50/1000 vs 50/1000: zero lift, must not be significant
        out = xs.holdout_tests(_conv_frame(50, 1000), _conv_frame(50, 1000))
        assert out["absolute_lift_pp"] == pytest.approx(0.0, abs=1e-12)
        assert out["significant_at_0_05"] is False
        assert out["fisher_exact_pvalue"] == pytest.approx(1.0, rel=1e-6)

    def test_value_tests_match_scipy(self):
        rng = np.random.default_rng(0)
        # treated funded values shifted +5 vs holdout
        t_vals = rng.normal(20, 5, 500)
        h_vals = rng.normal(15, 5, 500)
        t = _conv_frame(500, 500, funded=t_vals)
        h = _conv_frame(500, 500, funded=h_vals)
        out = xs.holdout_tests(t, h)
        welch_ref = stats.ttest_ind(t_vals, h_vals, equal_var=False)
        mw_ref = stats.mannwhitneyu(t_vals, h_vals, alternative="two-sided")
        assert out["value_welch_t_pvalue"] == pytest.approx(welch_ref.pvalue, rel=1e-9)
        assert out["value_mann_whitney_pvalue"] == pytest.approx(mw_ref.pvalue, rel=1e-9)
        assert out["value_per_eligible_lift"] == pytest.approx(float(t_vals.mean() - h_vals.mean()), abs=1e-9)

    # -- degenerate inputs -------------------------------------------------
    def test_zero_eligible_skips(self):
        out = xs.holdout_tests(_conv_frame(0, 0), _conv_frame(50, 1000))
        assert out.get("skipped") is True

    def test_both_zero_conversions(self):
        # No conversions at all -> z undefined (None), Fisher p == 1
        out = xs.holdout_tests(_conv_frame(0, 500), _conv_frame(0, 500))
        assert out["absolute_lift_pp"] == pytest.approx(0.0, abs=1e-12)
        assert out["two_proportion_z_pvalue"] is None
        assert out["fisher_exact_pvalue"] == pytest.approx(1.0, rel=1e-9)
        assert out["significant_at_0_05"] is False


# ---------------------------------------------------------------------------
# apply_eligibility -- prior-holder exclusion
# ---------------------------------------------------------------------------
class TestEligibility:
    def test_excludes_prior_holders(self):
        arm = pd.DataFrame({"customer_id": [1, 2, 3, 4]})
        prior = pd.DataFrame({"customer_id": [2, 4], "product_code": ["SAV", "SAV"]})
        elig, excluded = xs.apply_eligibility(arm, prior, "SAV")
        assert excluded == 2
        assert sorted(elig["customer_id"]) == [1, 3]

    def test_only_target_product_excluded(self):
        arm = pd.DataFrame({"customer_id": [1, 2, 3]})
        prior = pd.DataFrame({"customer_id": [2, 3], "product_code": ["CHK", "SAV"]})
        elig, excluded = xs.apply_eligibility(arm, prior, "SAV")
        # only customer 3 holds SAV
        assert excluded == 1
        assert sorted(elig["customer_id"]) == [1, 2]

    def test_no_prior_holdings_is_noop(self):
        arm = pd.DataFrame({"customer_id": [1, 2, 3]})
        elig, excluded = xs.apply_eligibility(arm, None, "SAV")
        assert excluded == 0
        assert len(elig) == 3

    def test_missing_columns_raises(self):
        arm = pd.DataFrame({"customer_id": [1]})
        bad = pd.DataFrame({"customer_id": [1]})  # no product_code
        with pytest.raises(ValueError, match="missing required columns"):
            xs.apply_eligibility(arm, bad, "SAV")


# ---------------------------------------------------------------------------
# arm_summary -- conversion rate arithmetic
# ---------------------------------------------------------------------------
class TestArmSummary:
    def test_conversion_rate(self):
        s = xs.arm_summary("treated", _conv_frame(25, 100))
        assert s["eligible"] == 100
        assert s["converters"] == 25
        assert s["conversion_rate"] == pytest.approx(0.25, abs=1e-12)

    def test_value_metrics(self):
        funded = [10.0] * 20 + [0.0] * 80  # 20 converters each funded 10
        df = _conv_frame(20, 100, funded=funded)
        s = xs.arm_summary("treated", df)
        assert s["total_funded_value"] == pytest.approx(200.0)
        assert s["value_per_eligible_mean"] == pytest.approx(2.0)
        assert s["funded_value_per_converter_mean"] == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# CLI end-to-end: overlap must error; golden run produces summary.json
# ---------------------------------------------------------------------------
class TestCLI:
    def _write(self, tmp_path, name, df):
        p = tmp_path / name
        df.to_csv(p, index=False)
        return p

    def test_overlap_between_arms_errors(self, tmp_path):
        treated = self._write(
            tmp_path,
            "treated.csv",
            pd.DataFrame({"customer_id": [1, 2, 3], "treatment_date": ["2024-01-01"] * 3}),
        )
        # customer 3 appears in BOTH arms -> must raise/exit non-zero
        holdout = self._write(
            tmp_path,
            "holdout.csv",
            pd.DataFrame({"customer_id": [3, 4, 5], "treatment_date": ["2024-01-01"] * 3}),
        )
        opens = self._write(
            tmp_path,
            "opens.csv",
            pd.DataFrame({"customer_id": [1], "product_code": ["SAV"], "open_date": ["2024-01-05"]}),
        )
        out = tmp_path / "out"
        res = subprocess.run(
            [
                sys.executable,
                str(_SCRIPT),
                "--treated",
                str(treated),
                "--holdout",
                str(holdout),
                "--product-opens",
                str(opens),
                "--target-product",
                "SAV",
                "--out",
                str(out),
            ],
            capture_output=True,
            text=True,
        )
        assert res.returncode != 0
        assert "both treated and holdout" in res.stderr

    def test_golden_end_to_end(self, tmp_path):
        rng = np.random.default_rng(1)
        # 200 treated, ~30% convert; 200 holdout, ~10% convert
        treated_ids = list(range(1, 201))
        holdout_ids = list(range(1001, 1201))
        treated = self._write(
            tmp_path,
            "treated.csv",
            pd.DataFrame({"customer_id": treated_ids, "treatment_date": ["2024-01-01"] * 200}),
        )
        holdout = self._write(
            tmp_path,
            "holdout.csv",
            pd.DataFrame({"customer_id": holdout_ids, "treatment_date": ["2024-01-01"] * 200}),
        )
        t_conv = rng.choice(treated_ids, size=60, replace=False)
        h_conv = rng.choice(holdout_ids, size=20, replace=False)
        opens_rows = [
            {"customer_id": c, "product_code": "SAV", "open_date": "2024-01-10"} for c in list(t_conv) + list(h_conv)
        ]
        opens = self._write(tmp_path, "opens.csv", pd.DataFrame(opens_rows))
        out = tmp_path / "out"
        res = subprocess.run(
            [
                sys.executable,
                str(_SCRIPT),
                "--treated",
                str(treated),
                "--holdout",
                str(holdout),
                "--product-opens",
                str(opens),
                "--target-product",
                "SAV",
                "--attribution-window",
                "30",
                "--out",
                str(out),
            ],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, res.stderr
        summary = json.loads((out / "summary.json").read_text())
        assert summary["treated_summary"]["converters"] == 60
        assert summary["holdout_summary"]["converters"] == 20
        assert summary["treated_summary"]["conversion_rate"] == pytest.approx(0.30)
        assert summary["holdout_tests"]["absolute_lift_pp"] == pytest.approx(0.20)
