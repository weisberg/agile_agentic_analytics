---
name: audience-segmentation
description: >
  Use when the user mentions segmentation, customer segments, cohort analysis,
  RFM analysis, behavioral clustering, K-Means, DBSCAN, customer personas,
  segment profiles, retention curves, cohort retention, segment migration,
  customer tiers, high-value customers, at-risk segment, churn cohort,
  acquisition cohort, engagement tiers, or audience definition. Also trigger
  on 'group our customers' or 'which customers should we target.' If CLV
  scores are available from clv-modeling, they enrich segment profiles. Segments
  feed into experimentation (stratification), email-analytics (targeting),
  paid-media (lookalike audiences), and reporting skills.
---

# Customer Segmentation & Cohort Analysis

Automated RFM scoring, behavioral clustering, and cohort retention analysis.

| Field | Value |
|---|---|
| **Skill ID** | audience-segmentation |
| **Priority** | P1 — Strategic (used by most downstream skills) |
| **Category** | Customer Analytics |
| **Depends On** | data-extraction, clv-modeling (value enrichment) |
| **Feeds Into** | experimentation (stratification), email-analytics (targeting), paid-media (lookalike), reporting |

## Objective

Automate customer segmentation through RFM scoring, behavioral K-Means/DBSCAN
clustering with silhouette-based cluster count optimization, and cohort-based
retention analysis. Assign interpretable segment labels, track segment migration
over time, generate cohort retention curves, and produce segment profiles
suitable for targeting in email campaigns and paid media lookalike audiences.

## Functional Scope

- **RFM scoring** — quintile-based recency, frequency, monetary scoring with composite RFM score.
- **Behavioral clustering** — K-Means and DBSCAN with automated feature scaling and cluster count selection.
- **Cohort retention** — acquisition cohort definition, retention curve generation, churn rate calculation.
- **Segment profiling** — demographic, behavioral, and value-based segment descriptions.
- **Migration tracking** — segment transition matrices showing customer movement between segments over time.
- **Actionable targeting** — segment-to-campaign mapping recommendations for email and paid media.

---

## RFM Analysis

### Metrics

- **Recency** — days since last transaction relative to the analysis date.
- **Frequency** — total transaction count within the analysis window.
- **Monetary** — total (or average) spend within the analysis window.

### Scoring

1. Compute raw values for every customer.
2. Assign quintile scores 1-5 per dimension (5 = best). Use `scripts/rfm_scoring.py`.
3. Derive composite RFM score (e.g., concatenated string "555" or weighted sum).
4. Map composite scores to named segments using the label mapping in
   `references/rfm_methodology.md`.

### Named Segments

| Segment | RFM Pattern | Description |
|---|---|---|
| Champions | High R, High F, High M | Best customers — recent, frequent, high spend |
| Loyal | Mid-High R, High F, Mid-High M | Consistent repeat buyers |
| Potential Loyalists | High R, Low-Mid F, Low-Mid M | Recent customers showing growth potential |
| At-Risk | Low R, High F, High M | Previously valuable, lapsing |
| Hibernating | Low R, Low F, Low-Mid M | Inactive but previously engaged |
| Lost | Very Low R, Low F, Low M | Long-inactive, minimal spend |

Quintile boundaries should be recomputed monthly to account for distribution
drift. See `references/rfm_methodology.md` for detailed boundary guidance.

---

## Behavioral Clustering

### Feature Engineering

Derive features from raw behavioral event data:

- Session frequency (sessions per week/month)
- Page depth (avg pages per session)
- Content affinity (category-level engagement ratios)
- Channel preference (traffic source distribution)
- Engagement recency and intensity

### Algorithms

**K-Means**

1. Normalize features with `StandardScaler`.
2. Optionally reduce dimensionality with PCA (retain >= 95% variance).
3. Sweep cluster count k in [2, 10].
4. Select optimal k via elbow method confirmed by silhouette score (target > 0.3).
5. Fit final model with deterministic `random_state=42`.

**DBSCAN**

1. Normalize features with `StandardScaler`.
2. Estimate epsilon via k-distance plot (k = 2 * n_features).
3. Set `min_samples` relative to dataset size (heuristic: 1% of rows, minimum 5).
4. Evaluate cluster quality via silhouette score on non-noise points.

See `references/clustering_guide.md` for detailed optimization guidance.
Use `scripts/behavioral_clustering.py` for execution.

---

## Cohort Retention Analysis

### Cohort Definition

Cohorts can be defined by:

- **Acquisition month** — the calendar month of a customer's first transaction.
- **First product** — the product category of the initial purchase.
- **First channel** — the marketing channel that drove the first conversion.

### Retention Matrix

1. Assign each customer to a cohort based on the chosen dimension.
2. For each cohort, compute the percentage of customers active in each
   subsequent period (month or week).
3. Output as a matrix: rows = cohorts, columns = periods since acquisition.

### Metrics

- **Retention rate** — percentage of cohort still active in period N.
- **Churn rate** — 1 - retention rate.
- **Revenue per user** — average revenue per cohort member in period N.
- **LTV trajectory** — cumulative revenue per user over periods.

Use `scripts/cohort_retention.py` for computation.

---

## Segment Profiling

Each segment (RFM-based or cluster-based) must include:

- **Size** — customer count and percentage of total.
- **Behavioral indicators** — top distinguishing features (e.g., avg session frequency, preferred channel).
- **Value metrics** — average CLV, average order value, total revenue contribution.
- **Demographic summary** — if demographic data is available.
- **Recommended actions** — campaign type, messaging strategy, channel recommendation.

Profiles are written to `workspace/analysis/segment_profiles.json`.

---

## Segment Migration Tracking

Track how customers move between segments across consecutive analysis periods.

1. Run segmentation for period T and period T+1 using consistent definitions.
2. Build a transition matrix: rows = segment in T, columns = segment in T+1.
3. Each row sums to 100% (all customers accounted for).
4. Flag notable migrations: Champions to At-Risk, Hibernating to Loyal, etc.

Use `scripts/segment_migration.py` for computation.
Output to `workspace/analysis/segment_migration.json`.

---

## Input / Output Data Contracts

### Inputs

| File | Description | Required |
|---|---|---|
| `workspace/raw/transactions.csv` | Transaction data: customer_id, date, amount, product | Yes |
| `workspace/raw/behavioral_events.csv` | Web/app events: user_id, event, timestamp, properties | Optional |
| `workspace/analysis/clv_predictions.json` | CLV scores from clv-modeling for value enrichment | Optional |

### Outputs

| File | Description |
|---|---|
| `workspace/processed/segments.json` | Customer-level segment assignments with profiles |
| `workspace/analysis/segment_profiles.json` | Aggregate statistics per segment |
| `workspace/analysis/cohort_retention.json` | Retention matrices by cohort definition |
| `workspace/analysis/segment_migration.json` | Transition matrices showing segment movement |
| `workspace/reports/segmentation_report.html` | Interactive segment explorer with charts |

### Segment Assignment Schema

```json
{
  "customer_id": "string",
  "rfm_segment": "string",
  "rfm_scores": {"recency": 1-5, "frequency": 1-5, "monetary": 1-5},
  "cluster_id": "int | null",
  "cluster_label": "string | null",
  "cohort": "string",
  "clv_score": "float | null"
}
```

---

## Cross-Skill Integration

Segmentation is a foundational enabler for most downstream skills:

- **experimentation** — uses segments for stratified randomization and subgroup analysis.
- **email-analytics** — targets segments with personalized lifecycle flows.
- **paid-media** — builds lookalike audiences from high-value segments.
- **clv-modeling** — enriches segments with a value dimension.
- **reporting** — includes segment trends in executive dashboards.
- **compliance-review** — validates that segment-based targeting in financial services avoids prohibited discrimination.

When integrating, read segment assignments from `workspace/processed/segments.json`
and segment profiles from `workspace/analysis/segment_profiles.json`.

---

## Financial Services Considerations

- Segmentation criteria **must not** use prohibited characteristics (race, religion, national origin) even indirectly through proxies.
- Investor accreditation status may be a segmentation dimension but requires special handling under Reg D.
- AUM-based tiering must align with the firm's stated service model and fiduciary obligations.
- Segment-based marketing targeting must be documented for fair lending examination readiness.
- Maintain an audit trail of segmentation logic and any manual overrides.

---

## Development Guidelines

1. Use `scikit-learn` for all clustering; provide deterministic random seeds (`random_state=42`) for reproducibility.
2. RFM quintile boundaries should be recomputed monthly to account for distribution drift.
3. Behavioral clustering features must be normalized (`StandardScaler`) before distance-based algorithms.
4. Always produce both statistical clusters and business-interpretable RFM segments; let the user choose.
5. Segment profiles must include size (count and percentage), top behavioral indicators, and average CLV.
6. Migration tracking requires consistent segment definitions across periods; document any re-clustering decisions.
7. Validate that cohort retention matrices never exceed 100% retention.
8. Validate that segment migration matrix rows sum to 100%.
9. Write all intermediate DataFrames to workspace paths so downstream skills can consume them.
10. Include logging at INFO level for key pipeline milestones (scoring complete, clustering fit, etc.).

---

## Reference Files

- `references/rfm_methodology.md` — RFM scoring rules, segment label mapping, quintile boundary guidance.
- `references/clustering_guide.md` — K-Means, DBSCAN, silhouette optimization, feature scaling best practices.

## Scripts

- `scripts/rfm_scoring.py` — RFM computation, quintile assignment, segment labeling.
- `scripts/behavioral_clustering.py` — Feature engineering, scaling, clustering, silhouette optimization.
- `scripts/cohort_retention.py` — Cohort definition, retention matrix generation, churn rate calculation.
- `scripts/segment_migration.py` — Period-over-period segment transition matrix computation.
