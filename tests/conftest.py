"""Shared pytest fixtures for marketing-analytics plugin tests.

Provides synthetic but realistic DataFrames and workspace directory
scaffolding used across all skill test modules.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def write_fixture_csv(tmp_path: Path, name: str, df: pd.DataFrame) -> Path:
    """Write a DataFrame to a CSV inside *tmp_path* and return the path.

    Parameters
    ----------
    tmp_path : Path
        Temporary directory (usually from ``tmp_path`` or ``tmp_workspace``).
    name : str
        Filename (e.g. ``"transactions.csv"``).  Sub-directories in *name*
        are created automatically.
    df : pd.DataFrame
        Data to persist.

    Returns
    -------
    Path
        Absolute path to the written CSV file.
    """
    dest = tmp_path / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False)
    return dest


# ---------------------------------------------------------------------------
# Workspace fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_workspace(tmp_path: Path) -> Path:
    """Create a temporary workspace with standard sub-directories.

    Structure::

        workspace/
            raw/
            processed/
            analysis/
            reports/

    Returns the *workspace* directory path.
    """
    workspace = tmp_path / "workspace"
    for sub in ("raw", "processed", "analysis", "reports"):
        (workspace / sub).mkdir(parents=True, exist_ok=True)
    return workspace


# ---------------------------------------------------------------------------
# Sample transaction data  (1 000 rows)
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_transactions() -> pd.DataFrame:
    """Synthetic transaction data with 1 000 rows.

    Columns: customer_id, date, amount
    - 200 unique customers
    - Dates spanning 2024-01-01 to 2024-12-31
    - Amounts drawn from a log-normal distribution (realistic spend)
    """
    rng = np.random.default_rng(42)
    n_rows = 1_000
    n_customers = 200

    customer_ids = rng.choice(
        [f"CUST-{i:04d}" for i in range(1, n_customers + 1)],
        size=n_rows,
    )
    dates = pd.date_range("2024-01-01", "2024-12-31", periods=n_rows)
    amounts = np.round(rng.lognormal(mean=3.5, sigma=1.0, size=n_rows), 2)

    return pd.DataFrame({
        "customer_id": customer_ids,
        "date": dates,
        "amount": amounts,
    })


# ---------------------------------------------------------------------------
# Campaign spend data  (3 platforms x 12 months)
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_campaign_spend() -> pd.DataFrame:
    """Campaign spend data across 3 platforms over 12 months.

    Columns: platform, month, spend, impressions, clicks, conversions
    """
    rng = np.random.default_rng(99)
    platforms = ["google_ads", "meta_ads", "linkedin_ads"]
    months = pd.date_range("2024-01-01", periods=12, freq="MS")
    rows = []
    for platform in platforms:
        base_spend = {"google_ads": 5000, "meta_ads": 3000, "linkedin_ads": 2000}[platform]
        for month in months:
            spend = round(base_spend * rng.uniform(0.8, 1.3), 2)
            impressions = int(spend * rng.uniform(80, 150))
            clicks = int(impressions * rng.uniform(0.01, 0.05))
            conversions = int(clicks * rng.uniform(0.02, 0.10))
            rows.append({
                "platform": platform,
                "month": month,
                "spend": spend,
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Web behavioural events  (5 000 rows)
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_events() -> pd.DataFrame:
    """Synthetic web behavioural events.

    Columns: user_id, event_name, timestamp, page, source, device
    """
    rng = np.random.default_rng(7)
    n_rows = 5_000
    n_users = 500

    user_ids = rng.choice(
        [f"U-{i:05d}" for i in range(1, n_users + 1)],
        size=n_rows,
    )
    event_names = rng.choice(
        ["page_view", "add_to_cart", "checkout_start", "purchase", "signup"],
        size=n_rows,
        p=[0.50, 0.20, 0.15, 0.10, 0.05],
    )
    timestamps = pd.date_range(
        "2024-06-01", "2024-06-30", periods=n_rows,
    )
    pages = rng.choice(["/home", "/product", "/cart", "/checkout", "/thank-you"], size=n_rows)
    sources = rng.choice(["organic", "paid", "email", "social", "direct"], size=n_rows)
    devices = rng.choice(["desktop", "mobile", "tablet"], size=n_rows, p=[0.5, 0.4, 0.1])

    return pd.DataFrame({
        "user_id": user_ids,
        "event_name": event_names,
        "timestamp": timestamps,
        "page": pages,
        "source": sources,
        "device": devices,
    })


# ---------------------------------------------------------------------------
# Email sends  (2 000 rows)
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_email_sends() -> pd.DataFrame:
    """Synthetic email send data.

    Columns: campaign_id, send_time, recipient, delivered, bounced, opened,
             clicked, converted, unsubscribed, revenue
    """
    rng = np.random.default_rng(123)
    n_rows = 2_000
    n_recipients = 400
    n_campaigns = 10

    campaign_ids = rng.choice(
        [f"CAMP-{i:03d}" for i in range(1, n_campaigns + 1)],
        size=n_rows,
    )
    send_times = pd.date_range("2024-03-01", "2024-06-30", periods=n_rows)
    recipients = rng.choice(
        [f"user-{i:04d}@example.com" for i in range(1, n_recipients + 1)],
        size=n_rows,
    )

    delivered = rng.choice([0, 1], size=n_rows, p=[0.03, 0.97]).astype(int)
    bounced = 1 - delivered
    opened = (delivered & rng.choice([0, 1], size=n_rows, p=[0.40, 0.60])).astype(int)
    clicked = (opened & rng.choice([0, 1], size=n_rows, p=[0.70, 0.30])).astype(int)
    converted = (clicked & rng.choice([0, 1], size=n_rows, p=[0.85, 0.15])).astype(int)
    unsubscribed = (delivered & rng.choice([0, 1], size=n_rows, p=[0.995, 0.005])).astype(int)
    revenue = np.where(converted, np.round(rng.lognormal(3.0, 0.8, size=n_rows), 2), 0.0)

    return pd.DataFrame({
        "campaign_id": campaign_ids,
        "send_time": send_times,
        "recipient": recipients,
        "delivered": delivered,
        "bounced": bounced,
        "opened": opened,
        "clicked": clicked,
        "converted": converted,
        "unsubscribed": unsubscribed,
        "revenue": revenue,
    })


# ---------------------------------------------------------------------------
# NPS survey responses  (500 rows)
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_survey_responses() -> pd.DataFrame:
    """Synthetic NPS survey data.

    Columns: respondent_id, score (0-10), open_text, timestamp
    Distribution mirrors typical B2B NPS (~30-40 NPS).
    """
    rng = np.random.default_rng(2024)
    n_rows = 500

    respondent_ids = [f"R-{i:04d}" for i in range(1, n_rows + 1)]

    # Weighted toward promoters to produce a positive NPS
    scores = rng.choice(
        range(0, 11),
        size=n_rows,
        p=[0.02, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.12, 0.18, 0.22, 0.18],
    )

    open_texts = []
    positive = ["Great product!", "Love it", "Very satisfied", "Keep it up"]
    neutral = ["It's okay", "Decent", "Average experience", "No comment"]
    negative = ["Needs improvement", "Too slow", "Poor support", "Disappointing"]
    for s in scores:
        if s >= 9:
            open_texts.append(rng.choice(positive))
        elif s >= 7:
            open_texts.append(rng.choice(neutral))
        else:
            open_texts.append(rng.choice(negative))

    timestamps = pd.date_range("2024-01-01", periods=n_rows, freq="4h")

    return pd.DataFrame({
        "respondent_id": respondent_ids,
        "score": scores,
        "open_text": open_texts,
        "timestamp": timestamps,
    })


# ---------------------------------------------------------------------------
# Segment assignments  (200 customers)
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_segments() -> pd.DataFrame:
    """Segment assignment table for 200 customers.

    Columns: customer_id, segment_name, segment_id
    Segments mirror RFM labels.
    """
    rng = np.random.default_rng(55)
    n_customers = 200
    segment_names = [
        "Champions", "Loyal Customers", "Potential Loyalists",
        "New Customers", "Promising", "Needs Attention",
        "At-Risk", "About to Sleep", "Hibernating", "Lost",
    ]
    customer_ids = [f"CUST-{i:04d}" for i in range(1, n_customers + 1)]
    segments = rng.choice(segment_names, size=n_customers)

    return pd.DataFrame({
        "customer_id": customer_ids,
        "segment_name": segments,
        "segment_id": segments,  # identical for simplicity
    })
