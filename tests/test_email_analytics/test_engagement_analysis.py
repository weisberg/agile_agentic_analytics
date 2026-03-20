"""Tests for email-analytics / engagement_analysis.py

Covers CTDR calculation and engagement decay detection.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
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
    / "email-analytics"
    / "scripts"
)
sys.path.insert(0, str(_SCRIPTS_DIR))

from engagement_analysis import calculate_ctdr, detect_engagement_decay

# Import the helper -- conftest.py is at tests/ root.
_TESTS_DIR = Path(__file__).resolve().parents[1]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))
from conftest import write_fixture_csv


# ---------------------------------------------------------------------------
# test_ctdr_calculation  -- CTDR matches manual calc within 1%
# ---------------------------------------------------------------------------

class TestCtdrCalculation:
    """Validate click-to-delivered rate calculation."""

    def _make_email_csv(self, tmp_path: Path) -> Path:
        """Create a deterministic email sends CSV for CTDR testing."""
        rows = []
        # Campaign A: 100 delivered, 20 clicked => CTDR = 20%
        for i in range(100):
            rows.append({
                "campaign_id": "CAMP-A",
                "send_time": "2024-06-01",
                "recipient": f"user-{i}@test.com",
                "delivered": 1,
                "clicked": 1 if i < 20 else 0,
                "opened": 1 if i < 60 else 0,
                "converted": 1 if i < 5 else 0,
                "unsubscribed": 0,
                "revenue": 50.0 if i < 5 else 0.0,
            })
        # Campaign B: 200 delivered, 10 clicked => CTDR = 5%
        for i in range(200):
            rows.append({
                "campaign_id": "CAMP-B",
                "send_time": "2024-06-15",
                "recipient": f"user-{i + 100}@test.com",
                "delivered": 1,
                "clicked": 1 if i < 10 else 0,
                "opened": 1 if i < 80 else 0,
                "converted": 1 if i < 2 else 0,
                "unsubscribed": 0,
                "revenue": 30.0 if i < 2 else 0.0,
            })
        df = pd.DataFrame(rows)
        return write_fixture_csv(tmp_path, "email_sends.csv", df)

    def test_ctdr_matches_manual(self, tmp_path):
        """Campaign A CTDR should be 20%, Campaign B should be 5%."""
        csv_path = self._make_email_csv(tmp_path)
        results = calculate_ctdr(csv_path)

        by_campaign = {r.campaign_id: r for r in results}

        assert by_campaign["CAMP-A"].ctdr == pytest.approx(20.0, abs=1.0)
        assert by_campaign["CAMP-B"].ctdr == pytest.approx(5.0, abs=1.0)

    def test_delivered_and_clicks_correct(self, tmp_path):
        csv_path = self._make_email_csv(tmp_path)
        results = calculate_ctdr(csv_path)
        by_campaign = {r.campaign_id: r for r in results}

        assert by_campaign["CAMP-A"].delivered == 100
        assert by_campaign["CAMP-A"].unique_clicks == 20
        assert by_campaign["CAMP-B"].delivered == 200
        assert by_campaign["CAMP-B"].unique_clicks == 10

    def test_revenue_attribution(self, tmp_path):
        csv_path = self._make_email_csv(tmp_path)
        results = calculate_ctdr(csv_path)
        by_campaign = {r.campaign_id: r for r in results}

        assert by_campaign["CAMP-A"].attributed_revenue == pytest.approx(250.0, abs=0.01)
        assert by_campaign["CAMP-B"].attributed_revenue == pytest.approx(60.0, abs=0.01)

    def test_zero_delivered_campaign(self, tmp_path):
        """Campaign with zero delivered should have CTDR = 0."""
        df = pd.DataFrame([{
            "campaign_id": "CAMP-ZERO",
            "send_time": "2024-06-01",
            "recipient": "nobody@test.com",
            "delivered": 0,
            "clicked": 0,
            "opened": 0,
            "converted": 0,
            "unsubscribed": 0,
            "revenue": 0.0,
        }])
        csv_path = write_fixture_csv(tmp_path, "zero_sends.csv", df)
        results = calculate_ctdr(csv_path)

        assert len(results) == 1
        assert results[0].ctdr == 0.0


# ---------------------------------------------------------------------------
# test_engagement_decay_detection  -- detects declining engagement
# ---------------------------------------------------------------------------

class TestEngagementDecayDetection:
    """Validate detection of declining subscriber engagement."""

    def _make_decay_csv(self, tmp_path: Path) -> Path:
        """Create sends CSV where some subscribers show clear decay."""
        rows = []
        reference_date = datetime(2024, 7, 1)

        # Subscriber A: clicked every send in comparison window, none recently
        # Comparison window: 31-90 days before reference
        # Recent window: last 30 days
        for day_offset in range(31, 91):
            rows.append({
                "campaign_id": "CAMP-X",
                "send_time": reference_date - timedelta(days=day_offset),
                "recipient": "decay-user@test.com",
                "delivered": 1,
                "clicked": 1,  # clicked in old window
                "opened": 1,
            })
        for day_offset in range(0, 31):
            rows.append({
                "campaign_id": "CAMP-X",
                "send_time": reference_date - timedelta(days=day_offset),
                "recipient": "decay-user@test.com",
                "delivered": 1,
                "clicked": 0,  # stopped clicking recently
                "opened": 1,
            })

        # Subscriber B: consistent engagement (control -- should NOT be flagged)
        for day_offset in range(0, 91):
            rows.append({
                "campaign_id": "CAMP-X",
                "send_time": reference_date - timedelta(days=day_offset),
                "recipient": "steady-user@test.com",
                "delivered": 1,
                "clicked": 1,
                "opened": 1,
            })

        df = pd.DataFrame(rows)
        return write_fixture_csv(tmp_path, "decay_sends.csv", df)

    def test_decaying_subscriber_flagged(self, tmp_path):
        """Subscriber who stopped clicking should be detected."""
        csv_path = self._make_decay_csv(tmp_path)
        records = detect_engagement_decay(
            csv_path,
            recent_window_days=30,
            comparison_window_days=60,
            decay_threshold=0.5,
        )

        flagged_ids = {r.subscriber_id for r in records}
        assert "decay-user@test.com" in flagged_ids

    def test_steady_subscriber_not_flagged(self, tmp_path):
        """Subscriber with consistent engagement should not be flagged."""
        csv_path = self._make_decay_csv(tmp_path)
        records = detect_engagement_decay(
            csv_path,
            recent_window_days=30,
            comparison_window_days=60,
            decay_threshold=0.5,
        )

        flagged_ids = {r.subscriber_id for r in records}
        assert "steady-user@test.com" not in flagged_ids

    def test_decay_rate_value(self, tmp_path):
        """Decay rate for the decaying user should be 1.0 (100% decline)."""
        csv_path = self._make_decay_csv(tmp_path)
        records = detect_engagement_decay(
            csv_path,
            recent_window_days=30,
            comparison_window_days=60,
            decay_threshold=0.5,
        )

        decay_user = [r for r in records if r.subscriber_id == "decay-user@test.com"]
        assert len(decay_user) == 1
        assert decay_user[0].decay_rate == pytest.approx(1.0, abs=0.01)

    def test_risk_level_assignment(self, tmp_path):
        """A 100% decay should be classified as high risk."""
        csv_path = self._make_decay_csv(tmp_path)
        records = detect_engagement_decay(
            csv_path,
            recent_window_days=30,
            comparison_window_days=60,
            decay_threshold=0.5,
        )

        decay_user = [r for r in records if r.subscriber_id == "decay-user@test.com"]
        assert decay_user[0].risk_level == "high"
