"""Tests for audience-segmentation / rfm_scoring.py

Covers RFM computation, quintile assignment, segment labelling, and the
end-to-end pipeline.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Make the scripts directory importable.
_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "marketing-analytics"
    / "skills"
    / "audience-segmentation"
    / "scripts"
)
sys.path.insert(0, str(_SCRIPTS_DIR))

from rfm_scoring import (
    assign_quintiles,
    compute_rfm,
    label_segments,
    load_transactions,
    run_rfm_pipeline,
    SEGMENT_RULES,
)

# Import the helper -- conftest.py is at tests/ root and auto-loaded by pytest.
# We also add the tests directory to sys.path for direct invocation.
_TESTS_DIR = Path(__file__).resolve().parents[1]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))
from conftest import write_fixture_csv


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ANALYSIS_DATE = datetime(2025, 1, 1)


def _make_minimal_transactions(n_customers: int = 50) -> pd.DataFrame:
    """Build a small but varied transaction DataFrame."""
    rng = np.random.default_rng(0)
    rows = []
    for cid in range(1, n_customers + 1):
        n_txns = rng.integers(1, 20)
        for _ in range(n_txns):
            rows.append(
                {
                    "customer_id": f"C-{cid:03d}",
                    "date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 365))),
                    "amount": round(float(rng.lognormal(3, 1)), 2),
                }
            )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# test_compute_rfm_basic
# ---------------------------------------------------------------------------


class TestComputeRfmBasic:
    """Validates that compute_rfm produces the expected columns."""

    def test_output_columns(self):
        txns = _make_minimal_transactions()
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)

        assert "recency" in rfm.columns
        assert "frequency" in rfm.columns
        assert "monetary" in rfm.columns

    def test_no_negative_values(self):
        txns = _make_minimal_transactions()
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)

        assert (rfm["recency"] >= 0).all()
        assert (rfm["frequency"] >= 1).all()
        assert (rfm["monetary"] > 0).all()

    def test_customer_count(self):
        txns = _make_minimal_transactions(n_customers=30)
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)
        assert len(rfm) == 30

    def test_recency_is_integer_days(self):
        txns = _make_minimal_transactions()
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)
        assert rfm["recency"].dtype in (np.int64, np.int32, int)


# ---------------------------------------------------------------------------
# test_assign_quintiles
# ---------------------------------------------------------------------------


class TestAssignQuintiles:
    """Validates quintile scoring produces scores 1-5."""

    def test_scores_in_range(self):
        txns = _make_minimal_transactions(n_customers=100)
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)
        scored = assign_quintiles(rfm)

        for col in ("r_score", "f_score", "m_score"):
            assert scored[col].min() >= 1, f"{col} has values below 1"
            assert scored[col].max() <= 5, f"{col} has values above 5"

    def test_composite_string_format(self):
        txns = _make_minimal_transactions(n_customers=100)
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)
        scored = assign_quintiles(rfm)

        assert scored["rfm_composite"].str.len().eq(3).all()
        assert scored["rfm_composite"].str.match(r"^[1-5]{3}$").all()

    def test_weighted_score_bounds(self):
        txns = _make_minimal_transactions(n_customers=100)
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)
        scored = assign_quintiles(rfm)

        # Weighted score = 0.4*R + 0.3*F + 0.3*M  =>  min=1.0, max=5.0
        assert scored["rfm_weighted"].min() >= 1.0
        assert scored["rfm_weighted"].max() <= 5.0

    def test_all_customers_scored(self):
        txns = _make_minimal_transactions(n_customers=60)
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)
        scored = assign_quintiles(rfm)

        assert len(scored) == len(rfm)
        assert scored[["r_score", "f_score", "m_score"]].notna().all().all()


# ---------------------------------------------------------------------------
# test_label_segments
# ---------------------------------------------------------------------------


class TestLabelSegments:
    """Validates all customers get exactly one named segment."""

    def test_all_customers_labelled(self):
        txns = _make_minimal_transactions(n_customers=100)
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)
        scored = assign_quintiles(rfm)
        labelled = label_segments(scored)

        assert "segment" in labelled.columns
        assert labelled["segment"].notna().all()

    def test_known_segment_names(self):
        txns = _make_minimal_transactions(n_customers=100)
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)
        scored = assign_quintiles(rfm)
        labelled = label_segments(scored)

        valid_names = {rule["name"] for rule in SEGMENT_RULES} | {"Lost"}
        assert labelled["segment"].isin(valid_names).all()

    def test_single_segment_per_customer(self):
        txns = _make_minimal_transactions(n_customers=100)
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)
        scored = assign_quintiles(rfm)
        labelled = label_segments(scored)

        # Each customer should appear exactly once (index is unique)
        assert not labelled.index.duplicated().any()

    def test_custom_rules(self):
        """Custom rules that cover all possible score combos."""
        custom_rules = [
            {"name": "VIP", "R": (3, 5), "F": (3, 5), "M": (3, 5)},
            {"name": "Regular", "R": (1, 5), "F": (1, 5), "M": (1, 5)},
        ]
        txns = _make_minimal_transactions(n_customers=50)
        rfm = compute_rfm(txns, analysis_date=ANALYSIS_DATE)
        scored = assign_quintiles(rfm)
        labelled = label_segments(scored, rules=custom_rules)

        assert labelled["segment"].isin({"VIP", "Regular"}).all()


# ---------------------------------------------------------------------------
# test_rfm_pipeline_end_to_end
# ---------------------------------------------------------------------------


class TestRfmPipelineEndToEnd:
    """Full pipeline from CSV to segment output."""

    def test_pipeline_produces_output_files(self, tmp_path):
        txns = _make_minimal_transactions(n_customers=80)
        csv_path = write_fixture_csv(tmp_path, "transactions.csv", txns)
        output_dir = tmp_path / "output"

        result = run_rfm_pipeline(
            transactions_path=csv_path,
            output_dir=output_dir,
            analysis_date=ANALYSIS_DATE,
        )

        assert (output_dir / "rfm_segments.csv").exists()
        assert (output_dir / "rfm_boundaries.json").exists()

    def test_pipeline_result_has_segment_column(self, tmp_path):
        txns = _make_minimal_transactions(n_customers=80)
        csv_path = write_fixture_csv(tmp_path, "transactions.csv", txns)
        output_dir = tmp_path / "output"

        result = run_rfm_pipeline(
            transactions_path=csv_path,
            output_dir=output_dir,
            analysis_date=ANALYSIS_DATE,
        )

        assert "segment" in result.columns
        assert result["segment"].notna().all()

    def test_pipeline_roundtrip_csv(self, tmp_path):
        """Written CSV can be read back and has expected columns."""
        txns = _make_minimal_transactions(n_customers=80)
        csv_path = write_fixture_csv(tmp_path, "transactions.csv", txns)
        output_dir = tmp_path / "output"

        run_rfm_pipeline(
            transactions_path=csv_path,
            output_dir=output_dir,
            analysis_date=ANALYSIS_DATE,
        )

        reloaded = pd.read_csv(output_dir / "rfm_segments.csv")
        expected_cols = {
            "recency",
            "frequency",
            "monetary",
            "r_score",
            "f_score",
            "m_score",
            "rfm_composite",
            "rfm_weighted",
            "segment",
        }
        assert expected_cols.issubset(set(reloaded.columns))

    def test_load_transactions_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_transactions("/nonexistent/path.csv")

    def test_load_transactions_missing_columns(self, tmp_path):
        bad_df = pd.DataFrame({"a": [1], "b": [2]})
        csv_path = write_fixture_csv(tmp_path, "bad.csv", bad_df)
        with pytest.raises(ValueError, match="Missing required columns"):
            load_transactions(csv_path)
