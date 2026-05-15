"""Integration test: RFM segments feeding into email engagement analysis.

Validates that the output of audience-segmentation (RFM segments) can be
consumed by email-analytics (segment-level CTDR) without data contract
mismatches.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Make both skill script directories importable.
_SEG_SCRIPTS = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "marketing-analytics"
    / "skills"
    / "audience-segmentation"
    / "scripts"
)
_EMAIL_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "plugins" / "marketing-analytics" / "skills" / "email-analytics" / "scripts"
)
sys.path.insert(0, str(_SEG_SCRIPTS))
sys.path.insert(0, str(_EMAIL_SCRIPTS))

from rfm_scoring import compute_rfm, assign_quintiles, label_segments
from engagement_analysis import calculate_segment_ctdr

# Import the helper -- conftest.py is at tests/ root.
_TESTS_DIR = Path(__file__).resolve().parents[1]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))
from conftest import write_fixture_csv


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_rfm_segments(n_customers: int = 100) -> pd.DataFrame:
    """Run the RFM pipeline on synthetic data and return labelled segments."""
    rng = np.random.default_rng(77)
    rows = []
    for cid in range(1, n_customers + 1):
        for _ in range(rng.integers(1, 15)):
            rows.append(
                {
                    "customer_id": f"CUST-{cid:04d}",
                    "date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 365))),
                    "amount": round(float(rng.lognormal(3, 1)), 2),
                }
            )
    txns = pd.DataFrame(rows)
    rfm = compute_rfm(txns, analysis_date=datetime(2025, 1, 1))
    scored = assign_quintiles(rfm)
    labelled = label_segments(scored)
    return labelled.reset_index()  # customer_id becomes a column


def _build_email_sends(customer_ids: list[str], n_sends: int = 500) -> pd.DataFrame:
    """Build email sends data referencing the given customer IDs."""
    rng = np.random.default_rng(88)
    recipients = rng.choice(customer_ids, size=n_sends)
    delivered = rng.choice([0, 1], size=n_sends, p=[0.02, 0.98]).astype(int)
    clicked = (delivered & rng.choice([0, 1], size=n_sends, p=[0.7, 0.3])).astype(int)
    converted = (clicked & rng.choice([0, 1], size=n_sends, p=[0.8, 0.2])).astype(int)
    revenue = np.where(converted, np.round(rng.lognormal(3, 0.5, size=n_sends), 2), 0.0)

    return pd.DataFrame(
        {
            "campaign_id": rng.choice(["CAMP-1", "CAMP-2", "CAMP-3"], size=n_sends),
            "send_time": pd.date_range("2024-06-01", periods=n_sends, freq="30min"),
            "recipient": recipients,
            "delivered": delivered,
            "clicked": clicked,
            "opened": delivered,  # simplified
            "converted": converted,
            "unsubscribed": np.zeros(n_sends, dtype=int),
            "revenue": revenue,
        }
    )


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------


class TestSegmentsFeedEmailTargeting:
    """RFM segments can be loaded by email analytics for segment-level CTDR."""

    def test_segment_ctdr_integration(self, tmp_path):
        """Full integration: RFM segments -> JSON -> email segment CTDR."""
        # Step 1: Generate RFM segments
        segments_df = _build_rfm_segments(n_customers=100)
        customer_ids = segments_df["customer_id"].tolist()

        # Step 2: Write segments as JSON (email-analytics expected format)
        segments_json = [
            {
                "customer_id": row["customer_id"],
                "segment_name": row["segment"],
                "segment_id": row["segment"],
            }
            for _, row in segments_df.iterrows()
        ]
        segments_path = tmp_path / "segments.json"
        segments_path.write_text(json.dumps(segments_json, indent=2))

        # Step 3: Generate email sends referencing the same customer IDs
        email_df = _build_email_sends(customer_ids)
        sends_path = write_fixture_csv(tmp_path, "email_sends.csv", email_df)

        # Step 4: Run segment-level CTDR
        results = calculate_segment_ctdr(sends_path, segments_path)

        # Assertions
        assert len(results) > 0, "Should produce at least one segment result"

        segment_names = {r.segment_name for r in results}
        # At least some RFM segment names should appear
        rfm_names = set(segments_df["segment"].unique())
        assert segment_names.issubset(rfm_names), f"Unexpected segments: {segment_names - rfm_names}"

        for r in results:
            assert r.total_delivered > 0
            assert 0.0 <= r.ctdr <= 100.0
            assert r.total_clicks >= 0
            assert r.total_revenue >= 0.0

    def test_segment_schema_compatibility(self, tmp_path):
        """Verify RFM output schema has the columns email-analytics expects."""
        segments_df = _build_rfm_segments(n_customers=50)

        # email-analytics expects: customer_id, segment_name
        assert "customer_id" in segments_df.columns
        assert "segment" in segments_df.columns  # used as segment_name

    def test_no_data_loss_on_join(self, tmp_path):
        """Email sends for known customers should not be lost during join."""
        segments_df = _build_rfm_segments(n_customers=50)
        customer_ids = segments_df["customer_id"].tolist()

        email_df = _build_email_sends(customer_ids, n_sends=200)
        sends_path = write_fixture_csv(tmp_path, "email_sends.csv", email_df)

        segments_json = [
            {"customer_id": row["customer_id"], "segment_name": row["segment"]} for _, row in segments_df.iterrows()
        ]
        segments_path = tmp_path / "segments.json"
        segments_path.write_text(json.dumps(segments_json, indent=2))

        results = calculate_segment_ctdr(sends_path, segments_path)

        total_delivered_in_results = sum(r.total_delivered for r in results)
        total_delivered_in_source = email_df["delivered"].sum()

        # All delivered emails should be accounted for (since all recipients
        # are in the segment list)
        assert total_delivered_in_results == total_delivered_in_source
