---
name: web-analytics
description: >
  Use when the user mentions web analytics, GA4, Google Analytics, site traffic,
  page views, sessions, bounce rate, engagement rate, user behavior, session flow,
  site speed, traffic sources, acquisition channels, landing page performance,
  conversion tracking, UTM parameters, event tracking, behavioral analysis,
  Mixpanel, Amplitude, user journey, click path, scroll depth, or heatmap data.
  Also trigger on 'what's happening on our website' or 'where is traffic coming
  from.' For organic-search / keyword performance use seo-content; for step-by-step
  conversion drop-off use funnel-analysis; this skill is the foundational
  behavioral data layer. If GA4 data is not yet in the workspace, run
  data-extraction first.

disable-model-invocation: false
---

# Web Analytics

GA4 extraction, normalized web metrics, seasonal anomaly detection, navigation
path analysis, and predictive audience scoring — the behavioral data layer other
skills build on.

## Contract

**Role:** Advisory analyst and data layer. Extracts, normalizes, detects
anomalies, and scores propensity; does not change the site or run experiments.
All statistics and models run in deterministic Python scripts.

**Mode:**
- `quick` — normalized metrics + anomaly detection.
- `standard` (default) — add navigation path and content-affinity analysis.
- `deep` — add predictive audiences and page-performance correlation.

**When to use:** GA4/traffic analysis, anomaly detection, session/path behavior,
predictive audiences, landing-page performance.

**When NOT to use:** organic-search keyword/ranking work → `seo-content`;
funnel-step drop-off → `funnel-analysis`; clustering customers →
`audience-segmentation`. See `../../references/skill-index.md`.

**Evidence required (inputs):**
- `workspace/raw/ga4_reports.csv` — date, source, medium, page_path, sessions,
  conversions. Required. If absent, STOP and run **data-extraction** first (or use
  the google-analytics-mcp server / `scripts/extract_ga4.py` to land it).
- `workspace/raw/events.csv` — event-level data (optional; enables path analysis).

**Depends on:** data-extraction. **Feeds into:** funnel-analysis, seo-content,
paid-media, audience-segmentation, experimentation, reporting. Builder detail in
`references/authoring-notes.md`.

**Hard STOP (analysis validity):** anomaly detection requires ≥8 weeks of history
for a stable seasonal baseline. If history is shorter, STOP the anomaly step,
report descriptive trends only, and label the seasonal baseline as unavailable —
do not emit anomaly flags from an unstable decomposition.

Parse `$ARGUMENTS` for inline paths, date range, or Z-score threshold overrides.

## Workflow

1. **Validate inputs.** Load `ga4_reports.csv` and/or `events.csv`; verify
   required columns. Normalize UTM parameters (lowercase source/medium, trim,
   URL-decode).

2. **Extract-source gate (AskUserQuestion).** When fresh data is needed and both
   a live source and a stale file exist, ask before pulling:
   - **Question:** "How should I source GA4 data?"
   - **Options:** (a) *Use the workspace CSV as-is* — fastest, may be stale;
     (b) *Pull fresh via google-analytics-mcp* — when the MCP server is connected;
     (c) *Run `scripts/extract_ga4.py`* — Data API fallback with named dimensions.
   Skip when the workspace file is fresh and sufficient.

3. **Normalize metrics.** Aggregate to daily traffic/engagement/conversion; write
   `workspace/processed/web_metrics.json`.

4. **Anomaly detection.** Run `scripts/web_anomaly_detection.py`: STL seasonal
   decomposition (period=7) then Z-score residual flags. Apply the Hard STOP gate
   on history length first.

5. **Root-cause decomposition.** For each anomaly, break the deviation down by
   source/medium, device, geography, and landing page; suppress known events
   (holidays, launches) when a suppression calendar is provided.

6. **Navigation paths.** Run `scripts/path_analysis.py`: second-order (bigram)
   Markov transition matrices; top conversion paths, loops, dead-ends.

7. **Content affinity & exit pages.** Conversion-lift ratio
   P(convert|category)/P(convert), ranked; exit-rate ranking weighted by
   conversion proximity. See `references/behavioral_patterns.md`.

8. **Predictive audiences** (deep mode). Run `scripts/predictive_scoring.py`:
   logistic regression for convert/churn propensity on behavioral features;
   temporal holdout validation (target AUC > 0.70).

9. **Page performance** (deep mode). Correlate load time with bounce rate,
   segmented by device.

10. **Write outputs.**

## Output Format

Artifacts:

| File | Contents |
|------|----------|
| `workspace/processed/web_metrics.json` | Normalized traffic/engagement/conversion metrics |
| `workspace/analysis/web_anomalies.json` | Anomalies with root-cause decomposition |
| `workspace/analysis/navigation_paths.json` | Common paths with conversion correlation |
| `workspace/analysis/predictive_audiences.json` | Convert/churn propensity scores |

Report states: history length used, anomaly threshold, path-analysis order, and
predictive-model holdout AUC (or that scoring was skipped).

**Financial services mode:** track regulatory disclosure page views for compliance
verification; authenticated investor-portal analytics require PII handling (GDPR,
CCPA, SEC); report cookie-consent rate as a data-quality metric; verify required
disclosures rendered before conversion events. Any customer-facing output routes
through **compliance-review**.

**Completion status:**
- `DONE` — metrics, anomalies, and requested behavioral artifacts written.
- `DONE_WITH_CONCERNS` — e.g., short history (anomalies skipped), missing events
  (no path analysis), or low predictive AUC.
- `BLOCKED` — no GA4 data and extraction unavailable; state the fix.
- `NEEDS_CONTEXT` — extraction-source choice unresolved by the user.

## Anti-Patterns

- Emitting anomaly flags from fewer than 8 weeks of history.
- First-order Markov chains where bigram transitions are specified.
- Random (non-temporal) holdouts in predictive scoring — they leak the future.
- Skipping UTM normalization, so `Google` and `google` split traffic.
- Reporting raw exit rate without conversion-proximity weighting.
- Letting the model estimate anomaly thresholds or propensity scores instead of
  the scripts.
