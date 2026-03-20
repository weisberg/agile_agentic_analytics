# Quick Start: Marketing Analytics Plugin

Get from zero to your first analysis in under 5 minutes.

## Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed
- Python 3.10+ (for data generation)

## Step 1: Install the Plugin

From the Claude Code marketplace:

```
/install-plugin marketing-analytics
```

Or, if working from this repository directly:

```bash
cd /path/to/agile_agentic_analytics
```

Claude Code will automatically detect the plugin definition in
`plugins/marketing-analytics/.claude-plugin/plugin.json`.

## Step 2: Generate the Sample Data

```bash
python examples/generate_sample_data.py
```

This creates seven CSV files in `examples/data/` with reproducible synthetic
data (seed 42). No real company data or PII is included.

| File | Rows | Description |
|------|------|-------------|
| `transactions.csv` | 5,000 | Customer purchase history (500 customers, 2 years) |
| `events.csv` | 10,000 | Web behavioral events with funnel structure |
| `campaign_spend_google.csv` | 540 | Google Ads daily spend across 3 campaigns |
| `campaign_spend_meta.csv` | 540 | Meta Ads daily spend across 3 campaigns |
| `email_sends.csv` | 2,000 | Email campaign delivery and engagement |
| `survey_responses.csv` | 500 | NPS survey with open-text feedback |
| `search_console.csv` | 1,000 | Google Search Console keyword data |

## Step 3: Copy Data into Your Workspace

Most skills expect data in a `workspace/raw/` directory:

```bash
mkdir -p workspace/raw
cp examples/data/transactions.csv workspace/raw/
cp examples/data/events.csv workspace/raw/
```

## Step 4: Run Your First Analysis

Try audience segmentation on the transaction data:

```
/marketing-analytics:audience-segmentation transactions.csv
```

The skill will:

1. **Load** `workspace/raw/transactions.csv` and validate the schema
   (`customer_id`, `date`, `amount`).
2. **Compute RFM scores** -- recency, frequency, and monetary quintiles for
   each of the 500 customers.
3. **Run K-Means clustering** with silhouette-based cluster count selection
   (typically finds 4-5 segments in this dataset).
4. **Output segment profiles** with summary statistics, segment labels
   (e.g., "Champions," "At-Risk," "New Customers"), and targeting
   recommendations.

### Expected Output

The skill produces:

- **`workspace/output/segments.csv`** -- one row per customer with RFM scores,
  cluster assignment, and segment label.
- **Segment summary table** printed to the console showing count, average
  monetary value, average recency, and recommended actions per segment.
- **Retention curve** data if cohort analysis is requested.

A typical segment summary looks like:

```
Segment          | Count | Avg Monetary | Avg Recency | Action
-----------------+-------+--------------+-------------+------------------
Champions        |    68 |      $247.30 |      12 days | Loyalty program
Loyal Customers  |   112 |      $158.45 |      34 days | Cross-sell
At-Risk          |    89 |      $132.10 |      98 days | Win-back campaign
New Customers    |   145 |       $42.80 |      18 days | Onboarding nurture
Hibernating      |    86 |       $67.20 |     210 days | Re-engagement
```

## Next Steps

- **CLV modeling**: `/marketing-analytics:clv-modeling transactions.csv` --
  see [CLV Segmentation Workflow](clv_segmentation_workflow.md).
- **Funnel analysis**: `/marketing-analytics:funnel-analysis events.csv` --
  see [Funnel Optimization](funnel_optimization.md).
- **Paid media audit**: `/marketing-analytics:paid-media campaign_spend_google.csv`
- **Email analytics**: `/marketing-analytics:email-analytics email_sends.csv`
