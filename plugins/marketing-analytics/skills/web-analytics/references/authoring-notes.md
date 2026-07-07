# web-analytics — Authoring Notes

Builder-facing guidance evicted from `SKILL.md`. Consult when editing scripts,
references, or data contracts; do not paste back into `SKILL.md`.

## Development guidelines

1. Prefer the google-analytics-mcp server for GA4 data when available; fall back
   to the Data API Python client (`scripts/extract_ga4.py`).
2. Anomaly detection needs at least 8 weeks of history for stable seasonal
   baselines.
3. Path-analysis Markov chains use second-order (bigram) transitions.
4. Predictive audience scoring validates on a temporal holdout to avoid leakage;
   target AUC > 0.70.
5. Support incremental data loading — append new date ranges without full
   re-extraction.
6. UTM normalization must handle case, trailing spaces, and URL-encoded
   characters.
7. All statistical/ML computation runs in deterministic Python scripts.

## Acceptance criteria

- GA4 extraction retrieves reports for all standard dimensions and metrics.
- Anomaly detection false-positive rate < 5% on a 90-day validation period.
- Navigation path analysis identifies the top 5 conversion paths, verified against
  manual GA4 exploration.
- Predictive audience scores reach AUC > 0.70 on temporal holdout for conversion
  propensity.

## Cross-skill integration detail

- **funnel-analysis** — builds funnels from the web event sequences produced here.
- **seo-content** — uses traffic data to measure organic performance.
- **paid-media** — analyzes landing-page conversion from ad clicks.
- **audience-segmentation** — consumes behavioral features (session frequency,
  content affinity).
- **experimentation** — CUPED variance reduction uses pre-experiment behavioral
  data from here.
- **reporting** — anomalies and predictive scores surface in dashboards.
