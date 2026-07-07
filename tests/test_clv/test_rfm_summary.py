"""Golden-value tests for clv-modeling / rfm_summary.py deterministic components.

RFM summary construction from transactions with hand-computed known answers,
plus the transaction data-quality validator.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "plugins" / "marketing-analytics" / "skills" / "clv-modeling" / "scripts"
)
sys.path.insert(0, str(_SCRIPTS))

from rfm_summary import build_rfm_summary, validate_transactions, load_transactions  # noqa: E402


def _txns(records):
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df["customer_id"] = df["customer_id"].astype(str)
    return df


# ---------------------------------------------------------------------------
# build_rfm_summary -- exact hand-computed RFM values
# ---------------------------------------------------------------------------
class TestBuildRFM:
    def test_known_answer(self):
        txns = _txns(
            [
                # C1: 3 purchases spanning 20 days
                {"customer_id": "C1", "date": "2024-01-01", "amount": 100.0},
                {"customer_id": "C1", "date": "2024-01-11", "amount": 50.0},
                {"customer_id": "C1", "date": "2024-01-21", "amount": 70.0},
                # C2: single purchase (one-time buyer)
                {"customer_id": "C2", "date": "2024-01-05", "amount": 200.0},
            ]
        )
        rfm = build_rfm_summary(txns, observation_end="2024-01-31", time_unit="D")
        rfm = rfm.set_index("customer_id")

        # C1: frequency = 3-1 = 2 repeat purchases
        assert rfm.loc["C1", "frequency"] == 2
        # recency = last - first = Jan 21 - Jan 1 = 20 days
        assert rfm.loc["C1", "recency"] == pytest.approx(20.0)
        # T = obs_end - first = Jan 31 - Jan 1 = 30 days
        assert rfm.loc["C1", "T"] == pytest.approx(30.0)
        # monetary (repeat only) = mean(50, 70) = 60
        assert rfm.loc["C1", "monetary_value"] == pytest.approx(60.0)

        # C2: one-time buyer -> frequency 0, recency 0, monetary NaN
        assert rfm.loc["C2", "frequency"] == 0
        assert rfm.loc["C2", "recency"] == pytest.approx(0.0)
        assert rfm.loc["C2", "T"] == pytest.approx(26.0)  # Jan 31 - Jan 5
        assert np.isnan(rfm.loc["C2", "monetary_value"])

    def test_weekly_time_unit(self):
        txns = _txns(
            [
                {"customer_id": "C1", "date": "2024-01-01", "amount": 10.0},
                {"customer_id": "C1", "date": "2024-01-15", "amount": 20.0},  # 14 days later
            ]
        )
        rfm = build_rfm_summary(txns, observation_end="2024-01-29", time_unit="W").set_index("customer_id")
        # recency 14 days = 2 weeks; T = 28 days = 4 weeks
        assert rfm.loc["C1", "recency"] == pytest.approx(2.0)
        assert rfm.loc["C1", "T"] == pytest.approx(4.0)

    def test_monetary_all_when_not_repeat_only(self):
        txns = _txns(
            [
                {"customer_id": "C1", "date": "2024-01-01", "amount": 100.0},
                {"customer_id": "C1", "date": "2024-01-11", "amount": 50.0},
            ]
        )
        rfm = build_rfm_summary(txns, observation_end="2024-01-31", monetary_repeat_only=False).set_index("customer_id")
        # includes the first purchase: mean(100, 50) = 75
        assert rfm.loc["C1", "monetary_value"] == pytest.approx(75.0)

    def test_observation_end_defaults_to_max_date(self):
        txns = _txns(
            [
                {"customer_id": "C1", "date": "2024-01-01", "amount": 10.0},
                {"customer_id": "C1", "date": "2024-01-11", "amount": 10.0},
            ]
        )
        rfm = build_rfm_summary(txns).set_index("customer_id")
        # obs_end defaults to max date (Jan 11) -> T == recency == 10
        assert rfm.loc["C1", "T"] == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# validate_transactions -- known defect counts
# ---------------------------------------------------------------------------
class TestValidate:
    def test_clean_data(self):
        txns = _txns(
            [
                {"customer_id": "C1", "date": "2024-01-01", "amount": 10.0},
                {"customer_id": "C1", "date": "2024-01-02", "amount": 20.0},
                {"customer_id": "C2", "date": "2024-01-03", "amount": 30.0},
            ]
        )
        report = validate_transactions(txns)
        assert report["duplicate_count"] == 0
        assert report["negative_amount_count"] == 0
        assert report["future_date_count"] == 0
        assert report["total_transactions"] == 3
        assert report["unique_customers"] == 2
        assert report["is_clean"] is True

    def test_counts_defects(self):
        txns = _txns(
            [
                {"customer_id": "C1", "date": "2024-01-01", "amount": 10.0},
                {"customer_id": "C1", "date": "2024-01-01", "amount": 10.0},  # exact duplicate
                {"customer_id": "C2", "date": "2024-01-02", "amount": -5.0},  # negative
                {"customer_id": "C3", "date": "2024-01-03", "amount": 0.0},  # zero (<=0)
            ]
        )
        report = validate_transactions(txns)
        assert report["duplicate_count"] == 1
        assert report["negative_amount_count"] == 2  # -5 and 0
        assert report["future_date_count"] == 0
        assert report["is_clean"] is False

    def test_future_dates_flagged(self):
        future = (pd.Timestamp.now() + pd.Timedelta(days=365)).strftime("%Y-%m-%d")
        txns = _txns(
            [
                {"customer_id": "C1", "date": "2024-01-01", "amount": 10.0},
                {"customer_id": "C2", "date": future, "amount": 20.0},
            ]
        )
        report = validate_transactions(txns)
        assert report["future_date_count"] == 1
        assert report["is_clean"] is False


# ---------------------------------------------------------------------------
# load_transactions -- CSV round trip, column validation
# ---------------------------------------------------------------------------
class TestLoad:
    def test_loads_and_standardizes(self, tmp_path):
        csv = tmp_path / "t.csv"
        pd.DataFrame(
            {
                "cust": ["A", "B"],
                "when": ["2024-01-02", "2024-01-01"],
                "spend": [10.0, 20.0],
            }
        ).to_csv(csv, index=False)
        df = load_transactions(csv, customer_col="cust", date_col="when", amount_col="spend")
        assert list(df.columns[:3]) == ["customer_id", "date", "amount"]
        # sorted by date ascending -> B (Jan 1) first
        assert df.iloc[0]["customer_id"] == "B"

    def test_missing_column_raises(self, tmp_path):
        csv = tmp_path / "t.csv"
        pd.DataFrame({"customer_id": ["A"], "date": ["2024-01-01"]}).to_csv(csv, index=False)
        with pytest.raises(ValueError, match="Missing required columns"):
            load_transactions(csv)

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_transactions(tmp_path / "nope.csv")
