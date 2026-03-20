---
name: voc-analytics
description: >
  Use when the user mentions NPS, Net Promoter Score, CSAT, customer satisfaction,
  CES, Customer Effort Score, survey analytics, survey results, customer feedback,
  open-text analysis, verbatim analysis, sentiment analysis on feedback, voice of
  customer, VoC, customer comments, feedback themes, review analysis, or
  satisfaction tracking. Also trigger on 'what are customers saying' or 'analyze
  our survey results.' If segment-level cross-tabulation is needed and segments
  are not defined, suggest running audience-segmentation first. Theme insights
  inform seo-content strategy and email-analytics messaging. Satisfaction trends
  feed into reporting.
---

# Survey & Voice-of-Customer Analytics

NPS/CSAT/CES tracking, open-text theme extraction, and satisfaction-behavior
correlation.

| Property       | Value                                                       |
| :------------- | :---------------------------------------------------------- |
| Skill ID       | voc-analytics                                               |
| Priority       | P2 — Supporting (qualitative insight layer)                 |
| Category       | Customer Experience Analytics                               |
| Depends On     | data-extraction, audience-segmentation                      |
| Feeds Into     | reporting, seo-content (content strategy), email-analytics (messaging) |

## Objective

Automate voice-of-customer analytics: track NPS, CSAT, and CES metrics over
time, extract themes from open-text responses using LLM-powered categorization,
perform sentiment scoring at scale, and cross-correlate satisfaction metrics
with behavioral data. Enable the organization to systematically translate
customer feedback into marketing strategy adjustments.

## Process Steps

1. **Validate inputs.** Load `survey_responses.csv` and verify required columns
   (`respondent_id`, `question_id`, `response`, `score`, `timestamp`). Confirm
   score ranges match the expected metric type (0-10 for NPS, 1-5 for CSAT,
   1-7 for CES).

2. **Compute satisfaction metrics.** Execute `scripts/compute_metrics.py` to
   calculate NPS, CSAT, and CES with bootstrap confidence intervals. If fewer
   than 30 responses exist for a segment, flag the result as low-confidence.

3. **Extract themes from open-text responses.** Run
   `scripts/text_categorization.py` to categorize free-text responses into
   predefined and emergent themes using LLM-based structured output. Apply
   sentiment scoring (positive/neutral/negative with intensity) to each
   response.

4. **Run key driver analysis.** Execute `scripts/key_driver_analysis.py` to
   identify which themes and touchpoints most strongly predict Promoter vs.
   Detractor classification. Use permutation importance from random forest, not
   simple correlations.

5. **Analyze satisfaction trends.** Run `scripts/satisfaction_trends.py` to
   detect statistically significant shifts in NPS, CSAT, or CES over time.
   Flag any NPS movement greater than 5 points for review.

6. **Cross-tabulate by segment.** If `segments.json` is available, break down
   all metrics by audience segment, product line, channel, and touchpoint.
   Identify high-value Detractors and low-effort Promoters.

7. **Correlate satisfaction with behavior.** If `clv_predictions.json` is
   available, link satisfaction scores to behavioral outcomes (retention, CLV,
   referral activity). Include causal reasoning disclaimers in all outputs.

8. **Generate report.** Compile results into
   `workspace/reports/voc_dashboard.html` with NPS trend charts, theme
   frequency heat maps, key driver rankings, and segment-level breakdowns.

## Key Capabilities

### NPS / CSAT / CES Metric Tracking

- Compute NPS as `% Promoters - % Detractors` (scores 9-10 are Promoters,
  0-6 are Detractors, 7-8 are Passives).
- Compute CSAT as percentage of respondents selecting top-box satisfaction
  scores (e.g., 4 or 5 on a 5-point scale).
- Compute CES as the arithmetic mean of effort scores.
- Bootstrap confidence intervals on all metrics (not normal approximation)
  because NPS is bounded and non-Gaussian.
- Trend significance testing: determine whether the current period's score
  is statistically different from a prior period.

Refer to `references/survey_methodology.md` for NPS/CSAT/CES formulas,
confidence interval methods, and significance testing procedures.

### Open-Text Theme Extraction

- LLM-based categorization of free-text responses into predefined and
  emergent themes using Claude API with structured output.
- Support both a predefined theme taxonomy and emergent theme discovery; let
  the LLM suggest new themes beyond the predefined list.
- Sentiment scoring: positive/neutral/negative classification with intensity
  scaling (e.g., strongly positive, mildly negative).
- Theme frequency and sentiment tracking over time periods.
- Handle multilingual responses when operating internationally.

Refer to `references/text_analytics.md` for theme extraction prompting
patterns and sentiment scoring approach.

### Key Driver Analysis

- Identify which themes most strongly correlate with Promoter vs. Detractor
  classification.
- Use relative importance metrics (permutation importance from random forest)
  rather than simple bivariate correlations.
- Touchpoint analysis: which interaction points drive highest and lowest
  satisfaction.
- Generate actionable insight summaries translating theme + sentiment +
  correlation into specific recommendations.

### Cross-Tabulation

- Break down satisfaction metrics by segment, product, channel, and
  touchpoint.
- Identify critical intersections: high-value Detractors requiring immediate
  attention, low-effort Promoters suitable for referral campaigns.
- Statistical significance testing for segment-level differences.

### Satisfaction-Behavior Correlation

- Link survey respondents to behavioral data: do Promoters have higher CLV?
- Quantify the revenue impact of satisfaction improvements.
- All correlation outputs include explicit disclaimers that correlation does
  not imply causation.

### Longitudinal Tracking

- Detect statistically significant shifts in satisfaction metrics over time.
- Control for seasonality and response-mix changes when evaluating trends.
- Alert when NPS shifts exceed 5 points with supporting statistical test
  results.

## Input / Output Data Contracts

### Inputs

| File | Description | Required |
| :--- | :---------- | :------- |
| `workspace/raw/survey_responses.csv` | Survey data with `respondent_id`, `question_id`, `response`, `score`, `timestamp` | Yes |
| `workspace/processed/segments.json` | Segment definitions from audience-segmentation for cross-tabulation | No |
| `workspace/analysis/clv_predictions.json` | CLV predictions for satisfaction-value correlation | No |

### Outputs

| File | Description |
| :--- | :---------- |
| `workspace/analysis/satisfaction_metrics.json` | NPS, CSAT, CES with confidence intervals and trend significance |
| `workspace/analysis/text_themes.json` | Theme extraction results with frequency and sentiment |
| `workspace/analysis/satisfaction_drivers.json` | Key driver analysis linking themes to satisfaction scores |
| `workspace/reports/voc_dashboard.html` | Voice-of-customer analytics dashboard |

## Cross-Skill Integration

VoC analytics enriches audience-segmentation with a satisfaction dimension,
enabling segments like "High-value Detractors" that are critical for retention
marketing. Theme extraction insights inform seo-content's content strategy by
revealing which topics resonate with customers. Email-analytics uses
satisfaction scores to personalize messaging (Promoter referral asks vs.
Detractor recovery outreach). The reporting skill includes satisfaction trends
in executive dashboards alongside operational metrics.

- **audience-segmentation:** Satisfaction scores add a qualitative dimension
  to behavioral segments, enabling satisfaction-aware targeting.
- **seo-content:** Extracted themes reveal the language and concerns of
  customers, informing content strategy and keyword selection.
- **email-analytics:** NPS classification drives email personalization:
  Promoters receive referral incentives, Detractors receive recovery
  sequences.
- **reporting:** Satisfaction trend summaries and key driver rankings feed
  into executive dashboards and periodic performance reports.

## Financial Services Considerations

When operating in financial services mode:

- Survey data may contain PII and is subject to data protection regulations.
  Apply appropriate access controls and anonymization before analysis.
- NPS or satisfaction data used in marketing claims must comply with SEC
  Marketing Rule testimonial provisions. Do not present satisfaction scores
  as endorsements without proper disclaimers.
- Open-text responses may contain account-specific information requiring
  redaction before theme extraction. Run PII detection prior to sending
  text to external LLM APIs.
- Satisfaction survey distribution and collection must comply with applicable
  consumer protection regulations.

## Development Guidelines

1. Theme extraction should use an LLM (Claude API) with structured output for
   consistent categorization rather than traditional NLP topic models.

2. NPS confidence intervals must use bootstrapping (not normal approximation)
   because NPS is bounded and non-Gaussian.

3. Key driver analysis should use relative importance metrics (e.g.,
   permutation importance from random forest) not simple correlations.

4. Support both predefined theme taxonomies and emergent theme discovery; let
   the LLM suggest new themes beyond the predefined list.

5. Text categorization must handle multilingual responses if the organization
   operates internationally.

6. Satisfaction-behavior linking must use appropriate causal reasoning
   disclaimers (correlation, not causation).

7. All deterministic metric computations must be in Python scripts using
   `numpy` and `scipy.stats`. Never let the LLM compute NPS or confidence
   intervals directly.

8. Bootstrap resampling must use at least 10,000 iterations for stable CI
   estimates.

## Scripts

| Script | Purpose |
| :----- | :------ |
| `scripts/compute_metrics.py` | NPS, CSAT, CES computation with bootstrap confidence intervals |
| `scripts/text_categorization.py` | Theme extraction using LLM API calls with structured output |
| `scripts/key_driver_analysis.py` | Correlation/regression of themes against satisfaction scores |
| `scripts/satisfaction_trends.py` | Time series trend analysis with statistical change detection |

## Reference Files

| Reference | Content |
| :-------- | :------ |
| `references/survey_methodology.md` | NPS/CSAT/CES formulas, confidence interval methods, significance testing |
| `references/text_analytics.md` | Theme extraction prompting patterns, sentiment scoring approach |

## Acceptance Criteria

- NPS computation matches manual calculation within 0.1 point; bootstrap CIs
  have nominal coverage at 95%.
- Theme extraction achieves 85%+ agreement with human-labeled categories on a
  validation set of 200 responses.
- Key driver analysis correctly identifies the top 3 drivers verified against
  expert knowledge of known service issues.
- Trend detection correctly flags NPS shifts greater than 5 points as
  statistically significant with the appropriate test.
