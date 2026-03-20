# Worked Example: CLV Modeling + Segmentation Workflow

End-to-end walkthrough from raw transactions to actionable customer segments
with lifetime value predictions. Uses the synthetic `transactions.csv`
(5,000 rows, 500 customers, 2 years of history).

## Overview

| Step | Skill | Input | Output |
|------|-------|-------|--------|
| 1 | Data prep | `transactions.csv` | Validated, deduplicated file |
| 2 | CLV modeling | Transactions | Customer-level CLV predictions |
| 3 | Audience segmentation | CLV-enriched data | Labeled segments |
| 4 | Analysis | Segments + CLV | High-value at-risk list |

## Setup

```bash
python examples/generate_sample_data.py
mkdir -p workspace/raw
cp examples/data/transactions.csv workspace/raw/
```

---

## Step 1: Run CLV Modeling

```
/marketing-analytics:clv-modeling transactions.csv
```

The skill will:

1. **Parse and validate** the transaction data, confirming `customer_id`,
   `date`, and `amount` columns exist.
2. **Generate RFM summaries** -- for each customer, compute:
   - **Recency**: days since last purchase (relative to 2025-12-31).
   - **Frequency**: count of repeat purchases (excludes first transaction).
   - **Monetary**: average transaction value across all purchases.
   - **Tenure (T)**: days between first purchase and observation end.
3. **Fit a BG/NBD model** to predict expected future transactions per customer.
4. **Fit a Gamma-Gamma model** to predict expected average transaction value.
5. **Compute CLV** as `expected_transactions * expected_avg_value` over a
   configurable horizon (default: 12 months).

### Expected Output

**`workspace/output/clv_predictions.csv`** -- one row per customer:

```
customer_id | frequency | recency | T    | monetary | pred_transactions | pred_clv  | clv_rank
CUST-0023   | 42        | 5       | 710  | $187.30  | 28.4              | $5,319.42 | 1
CUST-0187   | 38        | 12      | 695  | $156.80  | 24.1              | $3,778.88 | 2
...
```

Key metrics printed to console:

```
Total customers:          500
Customers with repeat purchases: ~340
Median predicted 12-month CLV:   $285
Top 10% CLV threshold:           $1,450
Model fit (BG/NBD MAE):          2.3 transactions
```

### Interpreting the Results

- Customers with high frequency + low recency are your most reliable
  future revenue sources.
- The power-law distribution in the sample data means roughly 20% of
  customers drive 60-70% of predicted CLV -- a realistic pattern.

---

## Step 2: Run Audience Segmentation

With CLV predictions available, segmentation can use them as an input feature:

```
/marketing-analytics:audience-segmentation transactions.csv
```

The skill automatically detects `workspace/output/clv_predictions.csv` and
enriches the segmentation with predicted CLV as a clustering feature.

### Expected Segments

With CLV enrichment, the clustering typically produces 4-5 segments:

| Segment | Count | Avg CLV | Avg Frequency | Avg Recency | Profile |
|---------|-------|---------|---------------|-------------|---------|
| Champions | ~60 | $2,800 | 35 purchases | 15 days | High-value, highly active buyers |
| Loyal Regulars | ~100 | $980 | 18 purchases | 40 days | Consistent mid-frequency purchasers |
| Promising | ~90 | $420 | 8 purchases | 55 days | Growing engagement, moderate value |
| Needs Attention | ~120 | $195 | 4 purchases | 120 days | Previously active, slowing down |
| Dormant | ~130 | $75 | 2 purchases | 250 days | Low activity, low predicted value |

---

## Step 3: Identify High-Value At-Risk Customers

The critical insight comes from combining CLV with recency. Ask Claude:

> "Which customers have a predicted CLV above $1,000 but haven't purchased in
> the last 60 days?"

This cross-references the CLV predictions with the RFM data to surface
customers like:

```
customer_id | pred_clv  | days_since_last | frequency | segment
CUST-0412   | $2,140    | 78              | 22        | Needs Attention
CUST-0088   | $1,680    | 92              | 15        | Needs Attention
CUST-0334   | $1,520    | 65              | 19        | Needs Attention
```

These are your highest-priority retention targets: the model predicts they are
valuable, but their recent behavior suggests churn risk.

---

## Step 4: Generate Targeting Recommendations

The segmentation skill outputs recommended actions per segment. For the
at-risk high-value customers identified above:

- **Recommended channel**: Email win-back sequence + personalized offer.
- **Offer sizing**: The CLV prediction justifies a discount of up to 15-20%
  of predicted 12-month value to prevent churn.
- **Timing**: Act within 2 weeks -- the BG/NBD model's probability-alive
  score drops sharply after 90 days of inactivity for previously frequent
  buyers.

### Exporting for Campaign Activation

```
/marketing-analytics:audience-segmentation --export-list "Needs Attention" --min-clv 1000
```

This produces a targeted list suitable for upload to your email platform or
ad network for suppression/re-engagement campaigns.

---

## Key Takeaways

1. **CLV modeling before segmentation** produces more actionable segments
   because clusters incorporate forward-looking value, not just historical
   behavior.
2. **The "high-value at-risk" intersection** is the single most actionable
   output -- these customers represent disproportionate revenue risk.
3. **Reproducibility**: because the sample data uses `seed(42)`, you can
   re-run this workflow and get identical results, making it useful for
   testing pipeline changes or onboarding new team members.
