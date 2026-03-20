---
name: reporting
description: >
  Use when the user mentions dashboard, report, executive summary, performance
  summary, weekly report, monthly report, data visualization, chart, graph,
  KPI dashboard, marketing scorecard, insight generation, report automation,
  stakeholder update, board deck, or performance review. Also trigger on
  'summarize our marketing performance' or 'create a deck for leadership.'
  This skill consumes outputs from all other skills in the portfolio. In
  financial services mode, all reports containing performance claims must pass
  through compliance-review before distribution.
---

# Dashboard & Reporting Automation

Automated executive dashboards, cross-skill synthesis, and natural language
insight generation.

| Field | Value |
|---|---|
| Skill ID | `reporting` |
| Priority | P0 — Foundational (integration layer for all skills) |
| Category | Reporting & Visualization |
| Depends On | All other skills (consumes their outputs) |
| Feeds Into | `compliance-review` (in FS mode), stakeholder distribution |

## Objective

Serve as the universal reporting layer for the entire skill portfolio. Aggregate
outputs from every analytical skill into cohesive executive dashboards, weekly
performance summaries, and ad-hoc analysis reports. Generate natural language
insights that translate statistical results into business-language
recommendations. Support HTML interactive dashboards, XLSX data exports, PPTX
presentation decks, and DOCX narrative reports. Automate recurring report
generation with configurable schedules and distribution lists.

## Functional Scope

- Cross-skill output aggregation and synthesis into unified narratives.
- Interactive HTML dashboards with plotly/D3.js visualizations.
- Natural language insight generation: translate stats into business recommendations.
- Multi-format output: HTML, XLSX (via `xlsx` skill), PPTX (via `pptx` skill),
  DOCX (via `docx` skill).
- Anomaly-driven reporting: auto-highlight metrics that deviate from targets or
  historical trends.
- Configurable report templates: weekly snapshot, monthly deep-dive, quarterly
  business review, ad-hoc analysis.

## Data Aggregation

1. Discover and load all `workspace/analysis/*.json` files from completed skill
   runs using `scripts/aggregate_outputs.py`.
2. Merge metrics across skills into a unified KPI framework with consistent date
   alignment.
3. Compute derived metrics: blended ROAS, portfolio-level conversion rate,
   weighted CLV.
4. Validate incoming data against `shared/schemas/data_contracts.md` before
   processing.
5. Handle missing or partial data gracefully — report which skills have not yet
   produced outputs and proceed with available data.

## Visualization

1. Generate interactive plotly charts using `scripts/generate_charts.py`:
   time series, waterfall, funnel, scatter, heatmap.
2. Apply automated chart selection based on metric type:
   - **Time series data** -> line chart or area chart.
   - **Categorical comparisons** -> bar chart or grouped bar chart.
   - **Part-to-whole relationships** -> stacked bar, treemap, or pie chart.
   - **Conversion flows** -> funnel chart.
   - **Correlation analysis** -> scatter plot or heatmap.
   - **Distribution data** -> histogram or box plot.
3. Build responsive HTML layouts with drill-down capability and tooltip
   interactivity.
4. All charts must use colorblind-safe palettes (see `references/visualization_guide.md`).
5. All charts must include alt text for screen reader accessibility.

## Insight Generation

1. Run statistical summarization via `scripts/generate_insights.py` to identify
   top movers, trend reversals, and anomalies across all metrics.
2. Translate effect sizes and p-values into plain-English recommendations using
   the pattern library in `references/insight_patterns.md`.
3. Produce a priority-ranked insight list ordered by business impact magnitude.
4. Every insight must cite the specific metric, magnitude, and time period — no
   vague claims.
5. Flag anomalies that exceed two standard deviations from trailing averages.

## Multi-Format Output

### HTML Dashboard
- Generate self-contained HTML with inlined CSS/JS and base64-encoded images for
  offline viewing using `scripts/build_dashboard.py`.
- Primary outputs:
  - `workspace/reports/executive_dashboard.html` — interactive cross-skill dashboard.
  - `workspace/reports/weekly_summary.html` — weekly performance snapshot with insights.
- HTML must load in under 3 seconds in a modern browser with 50+ charts.

### XLSX Data Export
- Export underlying data tables to `workspace/reports/data_export.xlsx` for
  stakeholder manipulation.
- Delegate to the `xlsx` skill via its SKILL.md conventions.

### PPTX Presentation Deck
- Produce presentation-ready slides at `workspace/reports/leadership_deck.pptx`
  from key insights and charts.
- Delegate to the `pptx` skill via its SKILL.md conventions.
- Slides must render correctly in both PowerPoint and Google Slides.

### DOCX Narrative Report
- Produce long-form narrative reports with embedded charts and data tables.
- Delegate to the `docx` skill via its SKILL.md conventions.

## Input / Output Data Contracts

### Inputs

| Source | Description |
|---|---|
| `workspace/analysis/*.json` | All analytical outputs from other skills |
| `workspace/reports/*.html` | Existing skill-level reports to aggregate |
| `references/report_templates.md` | Configurable templates for report types |
| `shared/schemas/data_contracts.md` | Unified metric schema consumed from all skills |

### Outputs

| Path | Description |
|---|---|
| `workspace/reports/executive_dashboard.html` | Interactive cross-skill dashboard |
| `workspace/reports/weekly_summary.html` | Weekly performance snapshot with insights |
| `workspace/reports/data_export.xlsx` | Underlying data tables for all metrics |
| `workspace/reports/leadership_deck.pptx` | Presentation-ready slide deck |

## Cross-Skill Integration

The reporting skill is the terminal node in most workflow chains. It consumes:

- **attribution-analysis**: MMM contribution decompositions.
- **experimentation**: Experiment results (lift, significance, confidence intervals).
- **paid-media**: Media performance metrics (ROAS, CPA, spend efficiency).
- **audience-segmentation**: Segment profiles and migration matrices.
- **clv-modeling**: CLV distributions and cohort retention curves.
- **funnel-analysis**: Funnel conversion rates and drop-off points.
- **compliance-review**: Compliance flags and required disclaimers.
- **email-analytics**: Campaign performance, deliverability, engagement.
- **web-analytics**: Session data, page performance, user journeys.
- **seo-analytics**: Keyword rankings, organic traffic trends.
- **crm-analytics**: Pipeline metrics, win rates, account health.
- **social-media**: Engagement metrics, sentiment scores, share of voice.
- **competitive-intel**: Market share estimates, competitor benchmarks.
- **voice-of-customer**: NPS, CSAT, theme clusters.

When producing DOCX, PPTX, or XLSX outputs, delegate to the corresponding skill
using that skill's SKILL.md conventions rather than generating those formats
directly.

## Financial Services Considerations

When operating in financial services mode:

1. All reports containing performance claims must pass through
   `compliance-review` before distribution.
2. Investment performance reporting must follow GIPS standards where applicable.
3. Disclaimers and disclosures must appear on every page or slide containing
   return or performance data.
4. Reports distributed to external audiences must be archived per SEC Rule 17a-4.
5. Include regulatory footer on all HTML pages and PDF exports.
6. Never present back-tested results without clear labeling.

## Reference Files

| File | Purpose |
|---|---|
| `references/report_templates.md` | Template configs for weekly/monthly/quarterly reports |
| `references/visualization_guide.md` | Chart type selection rules, palettes, accessibility |
| `references/insight_patterns.md` | Pattern library: stats to business language |
| `shared/schemas/data_contracts.md` | Unified metric schema from all skills |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/aggregate_outputs.py` | Discover and merge workspace/analysis files |
| `scripts/generate_charts.py` | Plotly chart generation with automated type selection |
| `scripts/generate_insights.py` | Statistical pattern detection and NL templating |
| `scripts/build_dashboard.py` | Assemble HTML dashboard from charts, tables, narratives |

## Development Guidelines

1. Generate self-contained HTML with inlined CSS/JS and base64-encoded images
   for offline viewing.
2. All charts must be accessible: include alt text, use colorblind-safe palettes,
   support screen readers.
3. Natural language insights must cite the specific metric, magnitude, and time
   period — never vague claims.
4. Template system must be extensible: users should be able to add new report
   types without modifying core scripts.
5. Implement progressive report generation: produce a summary within 30 seconds,
   enrich with deep analysis over the next 2 minutes.
6. Use the `docx`, `pptx`, and `xlsx` skills via their existing SKILL.md
   conventions when generating those file types.
7. All date handling must use ISO 8601 format and be timezone-aware.
8. Log every aggregation step so users can trace which skill outputs were
   included and which were missing.

## Acceptance Criteria

- Dashboard aggregates outputs from at least 5 different skill analysis files
  into a unified view.
- Interactive HTML dashboard loads in under 3 seconds in a modern browser with
  50+ charts.
- Natural language insights correctly identify the top 3 movers by magnitude
  across all metrics.
- PPTX output produces presentation-ready slides that render correctly in
  PowerPoint and Google Slides.
- Report generation completes within 120 seconds for a full portfolio of skill
  outputs.

## Workflow

```
1. User requests a report or dashboard
2. Run scripts/aggregate_outputs.py to discover and merge analysis files
3. Run scripts/generate_insights.py to detect patterns and generate narratives
4. Run scripts/generate_charts.py to produce visualizations
5. Run scripts/build_dashboard.py to assemble final HTML output
6. (Optional) Delegate to xlsx/pptx/docx skills for additional formats
7. (If FS mode) Route through compliance-review before distribution
8. Write outputs to workspace/reports/
```
