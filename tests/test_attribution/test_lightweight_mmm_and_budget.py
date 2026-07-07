"""Golden-value tests for attribution-analysis deterministic components.

Full Bayesian MCMC fits are out of scope (heavy / require pymc-marketing).
We test the deterministic fallback model transforms and the greedy budget
optimizer on a concave toy whose optimum is known analytically.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

_SCRIPTS = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "marketing-analytics"
    / "skills"
    / "attribution-analysis"
    / "scripts"
)
sys.path.insert(0, str(_SCRIPTS))

from _lightweight_mmm import LightweightMMM, _quantile  # noqa: E402


def _load_optimizer():
    spec = importlib.util.spec_from_file_location("optimize_budget", _SCRIPTS / "optimize_budget.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ob = _load_optimizer()


def _toy_model(coef_a=1.0, coef_b=1.0, scale=1.0):
    """A 2-channel model with concave log1p response and known coefficients."""
    m = LightweightMMM(channel_columns=["a", "b"], control_columns=[])
    m.coefficients = {"a": coef_a, "b": coef_b}
    m.channel_scales = {"a": scale, "b": scale}
    m.intercept = 0.0
    m.training_allocation = {"a": 0.0, "b": 0.0}
    m.training_spend_totals = {"a": 0.0, "b": 0.0}
    m.feature_columns = ["a", "b"]
    m.feature_means = {"a": 0.0, "b": 0.0}
    m.feature_stds = {"a": 1.0, "b": 1.0}
    m.posterior_samples = {"intercept": [0.0], "a": [coef_a], "b": [coef_b]}
    return m


# ---------------------------------------------------------------------------
# response_value -- log1p saturation, hand-computed
# ---------------------------------------------------------------------------
class TestResponseValue:
    def test_log1p_transform(self):
        m = _toy_model(coef_a=2.0, scale=1.0)
        # response = coef * log1p(spend/scale) = 2 * ln(1 + 100)
        assert m.response_value("a", 100.0) == pytest.approx(2.0 * math.log1p(100.0), abs=1e-12)

    def test_scaled_transform(self):
        m = _toy_model(coef_a=1.0, scale=50.0)
        assert m.response_value("a", 100.0) == pytest.approx(math.log1p(2.0), abs=1e-12)

    def test_zero_spend_zero_response(self):
        m = _toy_model()
        assert m.response_value("a", 0.0) == pytest.approx(0.0, abs=1e-12)

    def test_negative_spend_clamped(self):
        m = _toy_model()
        assert m.response_value("a", -10.0) == pytest.approx(0.0, abs=1e-12)

    def test_concavity(self):
        # Diminishing returns: gain from 0->10 exceeds gain from 90->100.
        m = _toy_model()
        early = m.response_value("a", 10) - m.response_value("a", 0)
        late = m.response_value("a", 100) - m.response_value("a", 90)
        assert early > late


# ---------------------------------------------------------------------------
# _quantile helper -- linear interpolation, hand-computed
# ---------------------------------------------------------------------------
class TestQuantile:
    def test_median(self):
        assert _quantile([1, 2, 3, 4, 5], 0.5) == pytest.approx(3.0)

    def test_interpolated(self):
        # position = (4-1)*0.25 = 0.75 -> between index 0 (10) and 1 (20)
        assert _quantile([10, 20, 30, 40], 0.25) == pytest.approx(17.5)

    def test_empty(self):
        assert _quantile([], 0.5) == 0.0


# ---------------------------------------------------------------------------
# optimize_allocation -- concave toy with known analytic optimum
# ---------------------------------------------------------------------------
class TestBudgetOptimizer:
    def test_equal_channels_split_evenly(self):
        m = _toy_model(coef_a=1.0, coef_b=1.0, scale=1.0)
        res = ob.optimize_allocation(m, total_budget=100.0, channel_columns=["a", "b"])
        alloc = res["optimal_allocation"]
        # Symmetric concave channels -> near-equal split.
        assert alloc["a"] == pytest.approx(50.0, abs=2.0)
        assert alloc["b"] == pytest.approx(50.0, abs=2.0)
        assert alloc["a"] + alloc["b"] == pytest.approx(100.0, abs=1e-6)

    def test_stronger_channel_gets_more(self):
        # coef_a = 2, coef_b = 1, scale 1. Marginals equalize where
        # 2/(1+sa) = 1/(1+sb) with sa+sb=100  ->  sa = 2*sb + 1  ->  sb=33, sa=67.
        m = _toy_model(coef_a=2.0, coef_b=1.0, scale=1.0)
        res = ob.optimize_allocation(m, total_budget=100.0, channel_columns=["a", "b"])
        alloc = res["optimal_allocation"]
        assert alloc["a"] > alloc["b"]
        assert alloc["a"] == pytest.approx(67.0, abs=3.0)
        assert alloc["b"] == pytest.approx(33.0, abs=3.0)
        assert alloc["a"] + alloc["b"] == pytest.approx(100.0, abs=1e-6)

    def test_respects_upper_bounds(self):
        m = _toy_model(coef_a=1.0, coef_b=1.0)
        res = ob.optimize_allocation(
            m,
            total_budget=100.0,
            channel_columns=["a", "b"],
            budget_bounds={"a": (0.0, 20.0), "b": (0.0, 100.0)},
        )
        alloc = res["optimal_allocation"]
        assert alloc["a"] <= 20.0 + 1e-6
        # remaining budget forced into b
        assert alloc["b"] >= 80.0 - 1e-6

    def test_respects_lower_bounds(self):
        m = _toy_model(coef_a=1.0, coef_b=5.0)  # b much stronger
        res = ob.optimize_allocation(
            m,
            total_budget=100.0,
            channel_columns=["a", "b"],
            budget_bounds={"a": (30.0, 100.0), "b": (0.0, 100.0)},
        )
        alloc = res["optimal_allocation"]
        # a is forced to at least its floor even though b is stronger
        assert alloc["a"] >= 30.0 - 1e-6


# ---------------------------------------------------------------------------
# Fit sign recovery on a linear-in-log toy (fast: small n)
# ---------------------------------------------------------------------------
class TestFitSign:
    def test_positive_channel_positive_coefficient(self):
        import random

        random.seed(0)
        # y increases with channel 'a' spend; 'b' is noise-free zero.
        rows = [{"a": float(s), "b": 0.0, "date": str(i)} for i, s in enumerate(range(1, 41))]
        y = [math.log1p(row["a"]) * 3.0 for row in rows]  # y = 3*log1p(a)
        m = LightweightMMM(channel_columns=["a", "b"], control_columns=[])
        m.fit(rows, y)
        # Recovered coefficient for 'a' should be clearly positive.
        assert m.coefficients["a"] > 0.5
