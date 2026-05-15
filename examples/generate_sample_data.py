#!/usr/bin/env python3
"""
Generate synthetic sample datasets for the marketing-analytics plugin.

All data is purely synthetic -- no real company data or PII.
Uses random.seed(42) for full reproducibility.

Usage:
    python examples/generate_sample_data.py

Outputs CSVs into examples/data/.
"""

import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def write_csv(filename: str, rows: list[dict]) -> None:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {filename}: {len(rows)} rows")


def date_range(start: str, days: int) -> list[str]:
    base = datetime.strptime(start, "%Y-%m-%d")
    return [(base + timedelta(days=d)).strftime("%Y-%m-%d") for d in range(days)]


def random_timestamp(date_str: str) -> str:
    """Return an ISO timestamp at a random time on the given date."""
    h = random.randint(0, 23)
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return f"{date_str}T{h:02d}:{m:02d}:{s:02d}"


# ---------------------------------------------------------------------------
# 1. campaign_spend_google.csv  (180 rows = 3 campaigns x 60 days each? No,
#    6 months daily = ~180 days, 3 campaigns = 540 rows.  Issue says "180 rows
#    (6 months daily)" so 180 days x 1 row per day?  We'll interpret it as
#    180 rows total: 3 campaigns x 60 days each.)
#    Re-reading: "180 rows (6 months daily)" => 180 days, 3 campaigns =>
#    actually the issue says "3 campaigns with realistic Google Ads metrics"
#    so 180 rows total means ~60 days each, or 180 days with 1 campaign.
#    Most natural: 180 total rows, so 60 days x 3 campaigns.
#    BUT 6 months ~= 180 days.  Let's do 180 days x 3 campaigns = 540 rows
#    because the parenthetical "(6 months daily)" clearly means 180 days.
#    We'll treat "180 rows" loosely and generate the full 180-day x 3-campaign
#    dataset.
# ---------------------------------------------------------------------------


def generate_campaign_spend_google() -> None:
    campaigns = {
        "G-BRAND-001": {"base_spend": 120, "cpc": 1.20, "cvr": 0.08, "aov": 65},
        "G-PERF-002": {"base_spend": 200, "cpc": 2.50, "cvr": 0.04, "aov": 85},
        "G-DISCO-003": {"base_spend": 80, "cpc": 0.60, "cvr": 0.02, "aov": 45},
    }
    dates = date_range("2025-07-01", 180)
    rows = []
    for d in dates:
        dow = datetime.strptime(d, "%Y-%m-%d").weekday()
        weekend_factor = 0.7 if dow >= 5 else 1.0
        for cid, cfg in campaigns.items():
            spend = round(cfg["base_spend"] * weekend_factor * random.uniform(0.8, 1.3), 2)
            clicks = max(1, int(spend / cfg["cpc"] * random.uniform(0.85, 1.15)))
            impressions = int(clicks / random.uniform(0.02, 0.06))
            conversions = max(0, int(clicks * cfg["cvr"] * random.uniform(0.6, 1.5)))
            revenue = round(conversions * cfg["aov"] * random.uniform(0.8, 1.2), 2)
            rows.append(
                {
                    "campaign_id": cid,
                    "date": d,
                    "spend": spend,
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "revenue": revenue,
                }
            )
    write_csv("campaign_spend_google.csv", rows)


# ---------------------------------------------------------------------------
# 2. campaign_spend_meta.csv
# ---------------------------------------------------------------------------


def generate_campaign_spend_meta() -> None:
    campaigns = {
        "META-RETARGET-001": {"base_spend": 150, "cpc": 0.90, "cvr": 0.06, "aov": 72},
        "META-PROSPECT-002": {"base_spend": 250, "cpc": 1.80, "cvr": 0.015, "aov": 55},
        "META-LOOKALIKE-003": {"base_spend": 100, "cpc": 1.10, "cvr": 0.035, "aov": 90},
    }
    dates = date_range("2025-07-01", 180)
    rows = []
    for d in dates:
        dow = datetime.strptime(d, "%Y-%m-%d").weekday()
        weekend_factor = 1.15 if dow >= 5 else 1.0  # Meta does better weekends
        for cid, cfg in campaigns.items():
            spend = round(cfg["base_spend"] * weekend_factor * random.uniform(0.75, 1.25), 2)
            clicks = max(1, int(spend / cfg["cpc"] * random.uniform(0.8, 1.2)))
            impressions = int(clicks / random.uniform(0.008, 0.025))
            conversions = max(0, int(clicks * cfg["cvr"] * random.uniform(0.5, 1.6)))
            revenue = round(conversions * cfg["aov"] * random.uniform(0.7, 1.3), 2)
            rows.append(
                {
                    "campaign_id": cid,
                    "date": d,
                    "spend": spend,
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "revenue": revenue,
                }
            )
    write_csv("campaign_spend_meta.csv", rows)


# ---------------------------------------------------------------------------
# 3. transactions.csv — 5000 rows, 500 unique customers, 2 years
# ---------------------------------------------------------------------------


def generate_transactions() -> None:
    customer_ids = [f"CUST-{i:04d}" for i in range(1, 501)]
    start = datetime.strptime("2024-01-01", "%Y-%m-%d")
    end = datetime.strptime("2025-12-31", "%Y-%m-%d")
    span_days = (end - start).days

    # Power-law spending: most purchases $10-80, long tail to $500
    def random_amount() -> float:
        # Pareto-ish distribution bounded [10, 500]
        u = random.random()
        amount = 10 / (u**0.35)  # shape gives nice right skew
        return round(min(amount, 500), 2)

    # Some customers buy more frequently than others
    customer_freq_weight = {c: random.paretovariate(1.5) for c in customer_ids}

    rows = []
    for _ in range(5000):
        # Weighted customer selection (some customers transact far more often)
        cid = random.choices(customer_ids, weights=[customer_freq_weight[c] for c in customer_ids])[0]
        day_offset = random.randint(0, span_days)
        d = (start + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        rows.append(
            {
                "customer_id": cid,
                "date": d,
                "amount": random_amount(),
            }
        )

    # Sort by date
    rows.sort(key=lambda r: r["date"])
    write_csv("transactions.csv", rows)


# ---------------------------------------------------------------------------
# 4. events.csv — 10000 rows with funnel drop-offs
# ---------------------------------------------------------------------------


def generate_events() -> None:
    """Realistic web-event funnel:
    page_view -> add_to_cart (30%) -> begin_checkout (50%) -> purchase (60%)
    Overall: ~9% of page_views convert to purchase.
    """
    pages = [
        "/",
        "/products",
        "/products/widget-pro",
        "/products/widget-lite",
        "/products/widget-max",
        "/pricing",
        "/about",
        "/blog",
        "/blog/how-to-choose",
        "/blog/widget-tips",
    ]
    checkout_pages = ["/cart", "/checkout", "/checkout/shipping", "/checkout/payment"]
    dates = date_range("2025-10-01", 90)

    user_ids = [f"U-{i:05d}" for i in range(1, 2001)]
    rows = []

    for _ in range(10000):
        uid = random.choice(user_ids)
        d = random.choice(dates)

        # Always a page_view
        rows.append(
            {
                "user_id": uid,
                "event_name": "page_view",
                "timestamp": random_timestamp(d),
                "page_url": random.choice(pages),
            }
        )

        # Funnel progression with drop-offs
        if random.random() < 0.30:
            rows.append(
                {
                    "user_id": uid,
                    "event_name": "add_to_cart",
                    "timestamp": random_timestamp(d),
                    "page_url": random.choice(pages[:5]),  # product pages
                }
            )
            if random.random() < 0.50:
                rows.append(
                    {
                        "user_id": uid,
                        "event_name": "begin_checkout",
                        "timestamp": random_timestamp(d),
                        "page_url": "/checkout",
                    }
                )
                if random.random() < 0.60:
                    rows.append(
                        {
                            "user_id": uid,
                            "event_name": "purchase",
                            "timestamp": random_timestamp(d),
                            "page_url": "/checkout/confirmation",
                        }
                    )

    # Sort by timestamp
    rows.sort(key=lambda r: r["timestamp"])
    # Trim to ~10000 rows (we over-generated because of funnel events)
    rows = rows[:10000]
    write_csv("events.csv", rows)


# ---------------------------------------------------------------------------
# 5. email_sends.csv — 2000 rows
# ---------------------------------------------------------------------------


def generate_email_sends() -> None:
    campaign_ids = [
        "EMAIL-WELCOME-01",
        "EMAIL-PROMO-02",
        "EMAIL-WINBACK-03",
        "EMAIL-NEWSLETTER-04",
        "EMAIL-ABANDON-05",
    ]
    recipient_ids = [f"R-{i:04d}" for i in range(1, 601)]
    dates = date_range("2025-09-01", 120)

    rows = []
    for _ in range(2000):
        delivered = random.random() < 0.97
        bounced = not delivered
        opened = delivered and random.random() < 0.20
        clicked = opened and random.random() < 0.15  # ~3% of all delivered
        converted = clicked and random.random() < 0.17  # ~0.5% of all delivered

        rows.append(
            {
                "campaign_id": random.choice(campaign_ids),
                "send_time": random_timestamp(random.choice(dates)),
                "recipient_id": random.choice(recipient_ids),
                "delivered": delivered,
                "bounced": bounced,
                "opened": opened,
                "clicked": clicked,
                "converted": converted,
            }
        )

    rows.sort(key=lambda r: r["send_time"])
    write_csv("email_sends.csv", rows)


# ---------------------------------------------------------------------------
# 6. survey_responses.csv — 500 rows with NPS
# ---------------------------------------------------------------------------


def generate_survey_responses() -> None:
    # NPS distribution skewing toward 8-9 (promoters dominate)
    # Roughly: 10% detractors (0-6), 20% passives (7-8), 70% promoters (9-10)
    nps_weights = {
        0: 1,
        1: 1,
        2: 1,
        3: 2,
        4: 2,
        5: 3,
        6: 4,
        7: 10,
        8: 15,
        9: 30,
        10: 20,
    }
    scores = list(nps_weights.keys())
    weights = list(nps_weights.values())

    segments = ["Enterprise", "Mid-Market", "SMB", "Startup"]

    feedback_templates = {
        "high": [
            "Great product, love the dashboard.",
            "Really easy to use. Saves us hours each week.",
            "Best analytics tool we've tried.",
            "The team loves it. Onboarding was smooth.",
            "Solid reporting features. Would recommend.",
            "Very intuitive interface.",
            "Excellent customer support.",
            "Exactly what we needed for our marketing team.",
            "Powerful and easy to learn.",
            "Love the funnel analysis feature.",
        ],
        "mid": [
            "Good overall, but the export feature needs work.",
            "Decent tool. Wish it had better integrations.",
            "It's fine for basic reporting.",
            "Useful but a bit slow with large datasets.",
            "Does what we need, nothing more.",
            "UI could be more modern.",
            "Adequate for our current needs.",
            "Some features are great, others feel half-baked.",
        ],
        "low": [
            "Too complex for our team.",
            "Pricing doesn't match the value.",
            "We had trouble getting data imported.",
            "Missing key integrations we need.",
            "Support response time is too slow.",
            "Crashed several times during setup.",
            "Not intuitive at all.",
            "We're considering switching to a competitor.",
        ],
    }

    dates = date_range("2025-06-01", 180)
    rows = []
    for i in range(500):
        score = random.choices(scores, weights=weights)[0]
        if score >= 9:
            text = random.choice(feedback_templates["high"])
        elif score >= 7:
            text = random.choice(feedback_templates["mid"])
        else:
            text = random.choice(feedback_templates["low"])

        rows.append(
            {
                "respondent_id": f"RESP-{i + 1:04d}",
                "nps_score": score,
                "open_text": text,
                "segment": random.choice(segments),
                "timestamp": random_timestamp(random.choice(dates)),
            }
        )

    rows.sort(key=lambda r: r["timestamp"])
    write_csv("survey_responses.csv", rows)


# ---------------------------------------------------------------------------
# 7. search_console.csv — 1000 rows of GSC keyword data
# ---------------------------------------------------------------------------


def generate_search_console() -> None:
    queries = [
        "marketing analytics tool",
        "marketing dashboard",
        "campaign analytics",
        "customer segmentation software",
        "clv calculator",
        "funnel analysis tool",
        "email marketing analytics",
        "attribution modeling",
        "marketing mix model",
        "ab testing platform",
        "conversion rate optimization",
        "cro tool",
        "paid media analytics",
        "google ads reporting",
        "meta ads dashboard",
        "seo analytics",
        "content performance tracking",
        "social media analytics",
        "marketing roi calculator",
        "customer lifetime value",
        "how to calculate clv",
        "best marketing analytics tools 2025",
        "marketing analytics for startups",
        "saas marketing metrics",
        "ecommerce analytics",
        "retention analytics",
        "churn prediction tool",
        "marketing data warehouse",
        "campaign performance report",
        "multi-touch attribution",
        "first-touch attribution",
        "incrementality testing",
        "marketing experimentation",
        "email deliverability analytics",
        "nps analysis tool",
        "voice of customer analytics",
        "competitive intelligence marketing",
        "marketing compliance",
        "gdpr marketing analytics",
        "marketing automation analytics",
        "lead scoring model",
        "ppc analytics",
        "sem reporting tool",
        "display ads analytics",
        "remarketing analytics",
        "lookalike audience optimization",
        "landing page optimization",
        "form conversion rate",
        "checkout abandonment analysis",
        "cart abandonment rate",
    ]

    pages = [
        "/",
        "/features",
        "/pricing",
        "/blog/clv-guide",
        "/blog/segmentation-101",
        "/blog/funnel-optimization",
        "/blog/attribution-explained",
        "/blog/ab-testing-guide",
        "/docs/getting-started",
        "/docs/api-reference",
        "/case-studies",
        "/integrations",
    ]

    dates = date_range("2025-10-01", 90)
    rows = []

    for _ in range(1000):
        query = random.choice(queries)
        page = random.choice(pages)
        impressions = max(1, int(random.paretovariate(1.0) * 20))
        position = round(random.uniform(1.0, 80.0), 1)
        # CTR inversely related to position
        base_ctr = max(0.005, 0.35 - position * 0.004)
        ctr = round(min(1.0, base_ctr * random.uniform(0.5, 1.5)), 4)
        clicks = max(0, int(impressions * ctr))

        rows.append(
            {
                "query": query,
                "page": page,
                "clicks": clicks,
                "impressions": impressions,
                "ctr": ctr,
                "position": position,
                "date": random.choice(dates),
            }
        )

    rows.sort(key=lambda r: r["date"])
    write_csv("search_console.csv", rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("Generating sample datasets...")
    generate_campaign_spend_google()
    generate_campaign_spend_meta()
    generate_transactions()
    generate_events()
    generate_email_sends()
    generate_survey_responses()
    generate_search_console()
    print("Done. All CSVs written to examples/data/")


if __name__ == "__main__":
    main()
