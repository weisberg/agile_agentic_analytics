"""Golden-value tests for experimentation bayesian_test.py and sequential_test.py."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "plugins" / "marketing-analytics" / "skills" / "experimentation" / "scripts"
)
sys.path.insert(0, str(_SCRIPTS))

from bayesian_test import (  # noqa: E402
    compute_beta_posterior,
    probability_of_being_best,
    compute_lift_distribution,
)
from sequential_test import (  # noqa: E402
    obrien_fleming_spending,
    pocock_spending,
    compute_conditional_power,
    run_sequential_analysis,
)


# ---------------------------------------------------------------------------
# Bayesian
# ---------------------------------------------------------------------------
class TestBayesian:
    def test_beta_posterior_moments_exact(self):
        # Uniform prior (1,1) + 100/1000 -> Beta(101, 901)
        post = compute_beta_posterior(100, 1000, prior_alpha=1.0, prior_beta=1.0)
        assert post.alpha == 101
        assert post.beta == 901
        a, b = 101, 901
        assert post.mean == pytest.approx(a / (a + b), abs=1e-12)
        var_ref = (a * b) / ((a + b) ** 2 * (a + b + 1))
        assert post.variance == pytest.approx(var_ref, abs=1e-12)
        # 95% credible interval brackets the mean
        lo, hi = post.credible_interval_95
        assert lo < post.mean < hi

    def test_probability_best_direction(self):
        # Treatment 150/1000 clearly beats control 100/1000.
        control = compute_beta_posterior(100, 1000)
        treatment = compute_beta_posterior(150, 1000)
        probs = probability_of_being_best(
            {"control": control, "treatment": treatment},
            n_simulations=20000,
            random_seed=42,
        )
        assert probs["treatment"] > 0.99
        assert probs["control"] < 0.01
        assert probs["treatment"] + probs["control"] == pytest.approx(1.0, abs=1e-9)

    def test_probability_best_symmetric_when_equal(self):
        a = compute_beta_posterior(120, 1000)
        b = compute_beta_posterior(120, 1000)
        probs = probability_of_being_best({"a": a, "b": b}, n_simulations=20000, random_seed=1)
        # Roughly 50/50 for identical arms.
        assert probs["a"] == pytest.approx(0.5, abs=0.05)

    def test_lift_distribution_positive_for_better_treatment(self):
        control = compute_beta_posterior(100, 1000)
        treatment = compute_beta_posterior(150, 1000)
        summary = compute_lift_distribution(control, treatment, n_simulations=20000, random_seed=7)
        # relative lift ~ (0.15-0.10)/0.10 = 0.5, and firmly positive
        assert summary["median"] > 0.3
        assert summary["p5"] > 0.0

    def test_invalid_successes_raise(self):
        with pytest.raises(ValueError):
            compute_beta_posterior(1100, 1000)


# ---------------------------------------------------------------------------
# Sequential testing
# ---------------------------------------------------------------------------
class TestSequential:
    def test_obrien_fleming_spending_closed_form(self):
        # At full information (t=1), cumulative spend == nominal alpha.
        assert obrien_fleming_spending(1.0, alpha=0.05) == pytest.approx(0.05, abs=1e-9)
        # Independent replication of the OBF formula at t=0.5.
        z_alpha = stats.norm.ppf(1 - 0.05 / 2)
        ref = 2 * (1 - stats.norm.cdf(z_alpha / np.sqrt(0.5)))
        assert obrien_fleming_spending(0.5, alpha=0.05) == pytest.approx(ref, abs=1e-12)
        # OBF spends very little alpha early.
        assert obrien_fleming_spending(0.25, alpha=0.05) < 0.005

    def test_pocock_spending_closed_form(self):
        assert pocock_spending(0.0, alpha=0.05) == pytest.approx(0.0, abs=1e-12)
        ref = 0.05 * np.log(1 + (np.e - 1) * 0.5)
        assert pocock_spending(0.5, alpha=0.05) == pytest.approx(ref, abs=1e-12)

    def test_conditional_power_monotonic_in_effect(self):
        low = compute_conditional_power(0.5, 500, 1000, 4.0)
        high = compute_conditional_power(2.0, 500, 1000, 4.0)
        assert 0.0 <= low <= 1.0 and 0.0 <= high <= 1.0
        assert high > low

    def test_no_effect_rarely_rejects(self):
        # Same distribution for both arms, fixed seed -> should not reject H0.
        rng = np.random.default_rng(123)
        control = rng.normal(0, 1, 1000).tolist()
        treatment = rng.normal(0, 1, 1000).tolist()
        res = run_sequential_analysis(control, treatment, planned_n_per_group=1000)
        assert res.reject_null is False
        # Always-valid CI should contain 0 under the null.
        lo, hi = res.always_valid_ci
        assert lo < 0.0 < hi

    def test_large_effect_rejects(self):
        rng = np.random.default_rng(321)
        control = rng.normal(0, 1, 1000).tolist()
        treatment = rng.normal(1.0, 1, 1000).tolist()  # strong effect
        res = run_sequential_analysis(control, treatment, planned_n_per_group=1000)
        assert res.reject_null is True
        assert res.effect_estimate == pytest.approx(1.0, abs=0.15)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            run_sequential_analysis([], [1.0], planned_n_per_group=10)
