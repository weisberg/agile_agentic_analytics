"""Golden-value tests for experimentation cuped.py and frequentist_test.py."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest

_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "plugins" / "marketing-analytics" / "skills" / "experimentation" / "scripts"
)
sys.path.insert(0, str(_SCRIPTS))

from cuped import estimate_theta, compute_adjusted_metric, run_cuped_adjustment  # noqa: E402
from frequentist_test import run_proportion_z_test, run_t_test, run_chi_squared_test  # noqa: E402


# ---------------------------------------------------------------------------
# CUPED: variance reduction ratio ~= 1 - rho^2
# ---------------------------------------------------------------------------
class TestCUPED:
    def _synth(self, rho, n=20000, seed=1):
        rng = np.random.default_rng(seed)
        pre = rng.normal(0, 1, n)
        noise = rng.normal(0, 1, n)
        post = rho * pre + np.sqrt(1 - rho**2) * noise
        return pre.tolist(), post.tolist()

    def test_theta_and_correlation(self):
        pre, post = self._synth(0.7)
        theta, corr = estimate_theta(post, pre)
        # correlation should recover rho; theta = cov/var(pre) ~ rho (since var(pre)=1)
        assert corr == pytest.approx(0.7, abs=0.02)
        assert theta == pytest.approx(0.7, abs=0.03)

    def test_variance_reduction_matches_1_minus_rho2(self):
        rho = 0.6
        pre, post = self._synth(rho)
        theta, corr = estimate_theta(post, pre)
        cov_mean = float(np.mean(pre))
        adjusted = compute_adjusted_metric(post, pre, theta, cov_mean)
        var_orig = np.var(post, ddof=1)
        var_adj = np.var(adjusted, ddof=1)
        ratio = var_adj / var_orig
        # Theoretical reduction: adjusted variance = original * (1 - corr^2)
        assert ratio == pytest.approx(1 - corr**2, abs=0.01)
        # And empirically close to 1 - rho^2 = 0.64
        assert ratio == pytest.approx(1 - rho**2, abs=0.03)

    def test_run_cuped_reduction_pct(self):
        rho = 0.8
        pre, post = self._synth(rho, n=15000, seed=2)
        results = run_cuped_adjustment(
            experiment_data={"metric": {"all": post}},
            covariate_data={"all": pre},
            metric_covariate_mapping={"metric": "cov"},
            winsorize_percentile=None,
        )
        r = results[0]
        # variance_reduction_pct ~ corr^2 * 100
        assert r.variance_reduction_pct == pytest.approx((r.correlation**2) * 100, abs=1.0)
        assert r.variance_reduction_pct == pytest.approx(64.0, abs=4.0)

    def test_zero_variance_covariate_raises(self):
        with pytest.raises(ValueError):
            estimate_theta([1.0, 2.0, 3.0], [5.0, 5.0, 5.0])


# ---------------------------------------------------------------------------
# Frequentist proportion z-test vs statsmodels
# ---------------------------------------------------------------------------
class TestProportionZ:
    def test_matches_statsmodels(self):
        # treatment 150/1000 vs control 100/1000
        res = run_proportion_z_test(100, 1000, 150, 1000)
        z_ref, p_ref = proportions_ztest([150, 100], [1000, 1000])
        assert res.test_statistic == pytest.approx(z_ref, rel=1e-6)
        assert res.p_value == pytest.approx(p_ref, rel=1e-4)
        assert res.effect_size_absolute == pytest.approx(0.05, abs=1e-12)
        assert res.effect_size_relative == pytest.approx(0.5, abs=1e-9)  # (0.15-0.10)/0.10
        assert res.is_significant is True

    def test_no_effect(self):
        res = run_proportion_z_test(100, 1000, 100, 1000)
        assert res.effect_size_absolute == pytest.approx(0.0, abs=1e-12)
        assert res.p_value == pytest.approx(1.0, abs=1e-9)
        assert res.is_significant is False

    def test_invalid_inputs_raise(self):
        with pytest.raises(ValueError):
            run_proportion_z_test(1100, 1000, 100, 1000)  # successes > total


# ---------------------------------------------------------------------------
# Welch t-test statistic vs scipy (script uses a normal-approx p-value,
# but the test statistic itself must match scipy's Welch t exactly).
# ---------------------------------------------------------------------------
class TestTTest:
    def test_statistic_matches_scipy_welch(self):
        rng = np.random.default_rng(9)
        control = rng.normal(50, 10, 300).tolist()
        treatment = rng.normal(55, 10, 300).tolist()
        res = run_t_test(control, treatment, equal_variance=False)
        ref = stats.ttest_ind(treatment, control, equal_var=False)
        assert res.test_statistic == pytest.approx(ref.statistic, rel=1e-9)
        # Welch-Satterthwaite dof, computed independently (scipy 1.10 doesn't
        # expose `.df` on the result object).
        c = np.array(control)
        t = np.array(treatment)
        vc, vt = c.var(ddof=1), t.var(ddof=1)
        nc, nt = len(c), len(t)
        df_ref = (vc / nc + vt / nt) ** 2 / ((vc / nc) ** 2 / (nc - 1) + (vt / nt) ** 2 / (nt - 1))
        assert res.degrees_of_freedom == pytest.approx(df_ref, rel=1e-9)

    def test_effect_direction(self):
        res = run_t_test([10.0] * 50, [12.0] * 50, equal_variance=True)
        assert res.effect_size_absolute == pytest.approx(2.0)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            run_t_test([], [1.0, 2.0])


# ---------------------------------------------------------------------------
# Chi-squared statistic vs scipy contingency
# ---------------------------------------------------------------------------
class TestChiSquared:
    def test_statistic_matches_scipy(self):
        table = [[90, 10], [70, 30]]
        res = run_chi_squared_test(table)
        chi2_ref, _, _, _ = stats.chi2_contingency(table, correction=False)
        assert res.test_statistic == pytest.approx(chi2_ref, rel=1e-9)
        assert res.degrees_of_freedom == 1
