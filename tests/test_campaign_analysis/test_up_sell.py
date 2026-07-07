"""Golden-value tests for campaign-analysis / analyze_upsell.py.

Assertions are checked against scipy references and hand-computed values.
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

_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "campaign-analysis"
    / "skills"
    / "up-sell-analysis"
    / "scripts"
    / "analyze_upsell.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("analyze_upsell", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


up = _load_module()


# ---------------------------------------------------------------------------
# value_lift -- pure arithmetic, hand-computed
# ---------------------------------------------------------------------------
class TestValueLift:
    def test_known_deltas(self):
        deltas = np.array([10.0, 20.0, 30.0])
        out = up.value_lift(deltas, pre_mean=100.0)
        assert out["n"] == 3
        assert out["mean_delta"] == pytest.approx(20.0)
        assert out["median_delta"] == pytest.approx(20.0)
        assert out["total_absolute_lift"] == pytest.approx(60.0)
        # percent lift = mean_delta / pre_mean = 20/100
        assert out["percent_lift_vs_pre_mean"] == pytest.approx(0.20)

    def test_nan_dropped(self):
        deltas = np.array([10.0, np.nan, 30.0])
        out = up.value_lift(deltas, pre_mean=100.0)
        assert out["n"] == 2
        assert out["mean_delta"] == pytest.approx(20.0)

    def test_empty(self):
        assert up.value_lift(np.array([]), pre_mean=100.0) == {"n": 0}

    def test_zero_pre_mean_gives_none_pct(self):
        out = up.value_lift(np.array([5.0, 5.0]), pre_mean=0.0)
        assert out["percent_lift_vs_pre_mean"] is None


# ---------------------------------------------------------------------------
# holdout_comparison -- Welch t, Mann-Whitney, bootstrap CI vs scipy
# ---------------------------------------------------------------------------
class TestHoldoutComparison:
    def test_matches_scipy(self):
        rng = np.random.default_rng(3)
        treated = rng.normal(50, 10, 400)  # +8 vs holdout
        holdout = rng.normal(42, 10, 400)
        out = up.holdout_comparison(treated, holdout)

        welch_ref = stats.ttest_ind(treated, holdout, equal_var=False)
        mw_ref = stats.mannwhitneyu(treated, holdout, alternative="two-sided")

        assert out["incremental_per_customer"] == pytest.approx(float(treated.mean() - holdout.mean()), abs=1e-9)
        assert out["welch_t_pvalue"] == pytest.approx(welch_ref.pvalue, rel=1e-9)
        assert out["mann_whitney_pvalue"] == pytest.approx(mw_ref.pvalue, rel=1e-9)
        assert out["welch_significant_at_0_05"] is True
        assert out["mann_whitney_significant_at_0_05"] is True

    def test_incremental_total_estimate(self):
        treated = np.array([10.0] * 100)  # mean 10
        holdout = np.array([4.0] * 100)  # mean 4 -> incremental 6
        out = up.holdout_comparison(treated, holdout)
        assert out["incremental_per_customer"] == pytest.approx(6.0)
        # total = incremental * n_treated = 6 * 100
        assert out["incremental_total_estimate"] == pytest.approx(600.0)
        assert out["n_treated"] == 100
        assert out["n_holdout"] == 100

    def test_bootstrap_ci_covers_true_effect(self):
        rng = np.random.default_rng(5)
        treated = rng.normal(50, 8, 300)
        holdout = rng.normal(45, 8, 300)
        out = up.holdout_comparison(treated, holdout)
        lo, hi = out["ci_95"]
        true_diff = float(treated.mean() - holdout.mean())
        assert lo < true_diff < hi

    def test_no_effect_not_significant(self):
        rng = np.random.default_rng(7)
        treated = rng.normal(30, 5, 500)
        holdout = rng.normal(30, 5, 500)
        out = up.holdout_comparison(treated, holdout)
        # near-zero incremental, high p-values
        assert abs(out["incremental_per_customer"]) < 1.0
        assert out["welch_t_pvalue"] > 0.05
        assert out["welch_significant_at_0_05"] is False


# ---------------------------------------------------------------------------
# bootstrap_ci_diff -- deterministic under fixed seed, brackets the point diff
# ---------------------------------------------------------------------------
class TestBootstrapCI:
    def test_deterministic_and_ordered(self):
        rng = np.random.default_rng(11)
        t = rng.normal(10, 2, 200)
        h = rng.normal(8, 2, 200)
        ci1 = up.bootstrap_ci_diff(t, h, n_boot=1000, seed=7)
        ci2 = up.bootstrap_ci_diff(t, h, n_boot=1000, seed=7)
        assert ci1 == ci2  # same seed -> identical
        assert ci1[0] < ci1[1]


# ---------------------------------------------------------------------------
# CLI: overlap error + golden end-to-end
# ---------------------------------------------------------------------------
class TestCLI:
    def _write(self, tmp_path, name, df):
        p = tmp_path / name
        df.to_csv(p, index=False)
        return p

    def test_overlap_errors(self, tmp_path):
        treated = self._write(tmp_path, "treated.csv", pd.DataFrame({"customer_id": [1, 2, 3]}))
        holdout = self._write(tmp_path, "holdout.csv", pd.DataFrame({"customer_id": [3, 4]}))
        metric = self._write(
            tmp_path,
            "metric.csv",
            pd.DataFrame({"customer_id": [1, 2, 3, 4], "metric_pre": [1, 1, 1, 1], "metric_post": [2, 2, 2, 2]}),
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
                "--metric",
                str(metric),
                "--out",
                str(out),
            ],
            capture_output=True,
            text=True,
        )
        assert res.returncode != 0
        assert "BOTH treated and holdout" in res.stderr

    def test_missing_metric_column_errors(self, tmp_path):
        treated = self._write(tmp_path, "treated.csv", pd.DataFrame({"customer_id": [1, 2]}))
        metric = self._write(
            tmp_path,
            "metric.csv",
            pd.DataFrame({"customer_id": [1, 2], "metric_pre": [1, 1]}),  # no metric_post
        )
        out = tmp_path / "out"
        res = subprocess.run(
            [sys.executable, str(_SCRIPT), "--treated", str(treated), "--metric", str(metric), "--out", str(out)],
            capture_output=True,
            text=True,
        )
        assert res.returncode != 0
        assert "metric_post" in res.stderr

    def test_golden_end_to_end(self, tmp_path):
        # Treated grow +6 on average (post-pre), holdout +1 -> incremental ~5
        treated_ids = list(range(1, 101))
        holdout_ids = list(range(1001, 1101))
        treated = self._write(tmp_path, "treated.csv", pd.DataFrame({"customer_id": treated_ids}))
        holdout = self._write(tmp_path, "holdout.csv", pd.DataFrame({"customer_id": holdout_ids}))
        rows = []
        for c in treated_ids:
            rows.append({"customer_id": c, "metric_pre": 100.0, "metric_post": 106.0})
        for c in holdout_ids:
            rows.append({"customer_id": c, "metric_pre": 100.0, "metric_post": 101.0})
        metric = self._write(tmp_path, "metric.csv", pd.DataFrame(rows))
        out = tmp_path / "out"
        res = subprocess.run(
            [
                sys.executable,
                str(_SCRIPT),
                "--treated",
                str(treated),
                "--holdout",
                str(holdout),
                "--metric",
                str(metric),
                "--out",
                str(out),
            ],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, res.stderr
        summary = json.loads((out / "summary.json").read_text())
        assert summary["value_lift_treated"]["mean_delta"] == pytest.approx(6.0)
        assert summary["holdout_comparison"]["incremental_per_customer"] == pytest.approx(5.0)
