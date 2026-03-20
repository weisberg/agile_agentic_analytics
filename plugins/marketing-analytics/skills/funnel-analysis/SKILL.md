---
name: funnel-analysis
description: >
  Use when the user mentions funnel, conversion funnel, drop-off, drop off,
  conversion rate, conversion optimization, CRO, bottleneck, funnel analysis,
  checkout flow, signup flow, onboarding funnel, activation funnel, abandonment,
  cart abandonment, form abandonment, user flow, step completion, or funnel
  comparison. Also trigger on 'where are we losing people' or 'why is conversion
  low.' If segment-level funnel comparison is needed and segments are not
  defined, suggest running audience-segmentation first. Behavioral event data
  typically comes from web-analytics. CRO hypotheses feed into experimentation
  for A/B testing. Results feed into reporting and paid-media (landing page
  optimization) skills.
---

# Funnel Analysis & Conversion Optimization

Multi-step funnel tracking, bottleneck identification, and revenue impact
estimation.

| Property       | Value                                                          |
| :------------- | :------------------------------------------------------------- |
| Skill ID       | funnel-analysis                                                |
| Priority       | P1 — Tactical (direct conversion impact)                       |
| Category       | Conversion Analytics                                           |
| Depends On     | data-extraction, web-analytics                                 |
| Feeds Into     | experimentation (CRO hypotheses), reporting, paid-media (landing page optimization) |

## Objective

Automate multi-step conversion funnel analysis with statistical significance
testing on drop-off rates, cohort-based funnel comparison, and automated
bottleneck identification. Estimate revenue impact per funnel improvement to
enable prioritization. Support both linear (e.g., landing page to signup to
activation) and branching funnels (e.g., multiple entry points converging to
purchase).

## Process Steps

1. **Validate inputs.** Load `workspace/raw/events.csv` and verify required
   columns (`user_id`, `event_name`, `timestamp`). If a funnel definition file
   is provided, parse the step sequence and time-window constraints. Otherwise,
   infer the funnel from the most common event sequences.

2. **Construct the funnel.** Execute `scripts/build_funnel.py` to assign users
   to funnel stages based on event sequences. Apply time-window filtering so
   that users who do not complete the next step within the configured window are
   counted as dropped. Support both strict (ordered) and relaxed (any-order)
   step matching.

3. **Compute stage-by-stage metrics.** Execute `scripts/funnel_stats.py` to
   calculate conversion rates at each stage with Wilson score confidence
   intervals. Compute overall funnel conversion rate and per-stage drop-off
   rates.

4. **Compare cohorts (if segments available).** If
   `workspace/processed/segments.json` is present, compute funnel metrics per
   segment and run chi-squared tests to identify statistically significant
   differences between segments at each stage.

5. **Identify bottlenecks.** Rank stages by composite bottleneck score:
   `drop_off_rate * sqrt(volume) * revenue_proximity`. Output the ranked list
   to `workspace/analysis/bottleneck_ranking.json`.

6. **Estimate revenue impact.** Execute `scripts/revenue_impact.py` using
   historical revenue-per-converter data. For each bottleneck stage, project the
   revenue gain from a 1, 5, and 10 percentage-point improvement in conversion
   rate. Use conservative estimates (50th percentile of improvement range).

7. **Analyze time-to-convert.** Compute median and distribution of time between
   consecutive funnel stages. Identify stages where longer dwell times correlate
   with higher abandonment. Flag stages with bimodal time distributions that may
   indicate distinct user intent patterns.

8. **Generate CRO hypotheses.** For each identified bottleneck, produce a
   structured CRO hypothesis with: observation, hypothesis, suggested test type,
   expected impact estimate, and priority score. Output to
   `workspace/analysis/cro_hypotheses.json`.

9. **Generate report.** Compile all results into
   `workspace/reports/funnel_report.html` with an interactive funnel
   visualization, stage-level drill-downs, cohort comparisons, bottleneck
   rankings, revenue impact projections, and CRO hypothesis backlog.

## Key Capabilities

### Funnel Construction

- Define funnels from event sequences with configurable time windows between
  steps.
- Support both strict (ordered) and relaxed (any order) step sequences.
- Handle session-based and user-based funnel aggregation.
- Accept funnel definitions as JSON or YAML step sequences, allowing
  configuration without code changes.
- Support both GA4 event export format and generic event CSV for maximum data
  source flexibility.

Refer to `references/funnel_methodology.md` for funnel construction rules,
time-window handling, and event matching logic.

### Stage-by-Stage Analysis

- Compute stage-wise conversion rates with Wilson score confidence intervals
  (more accurate than normal approximation at low rates).
- Calculate absolute and relative drop-off rates at each stage.
- Compare funnel performance across segments, cohorts, or time periods with
  chi-squared tests.
- Support period-over-period funnel comparison to detect trend changes.

### Bottleneck Identification

- Rank bottlenecks by composite score:
  `drop_off_rate * sqrt(volume) * revenue_proximity`.
- The scoring formula is documented and adjustable via configuration.
- Surface the top bottlenecks with contextual data: traffic volume, drop-off
  rate, confidence interval, and estimated revenue at stake.

Refer to `references/funnel_methodology.md` for the bottleneck scoring formula,
weighting rationale, and calibration guidance.

### Revenue Impact Estimation

- Estimate revenue impact per stage improvement using historical
  revenue-per-converter.
- Project gains at 1, 5, and 10 percentage-point improvement scenarios.
- Use conservative estimates: 50th percentile of improvement range, not
  optimistic projections.
- Express impact in both absolute revenue and percentage of total funnel
  revenue.

### CRO Hypothesis Generation

- Generate a structured CRO hypothesis backlog from bottleneck analysis.
- Each hypothesis includes: observation, root cause hypothesis, suggested test
  type (A/B, multivariate, redirect), expected impact, and priority score.
- Map common bottleneck patterns to proven CRO interventions.

Refer to `references/cro_patterns.md` for common CRO patterns and hypothesis
templates organized by funnel stage.

### Time-to-Convert Analysis

- Compute median and percentile distributions of time between funnel stages.
- Handle censored data: users still in funnel at analysis time are right-censored.
- Identify stages where delays correlate with abandonment using survival
  analysis techniques.
- Detect bimodal time distributions that may signal distinct user cohorts or
  intent patterns.

## Input / Output Data Contracts

### Inputs

| File | Description | Required |
| :--- | :---------- | :------- |
| `workspace/raw/events.csv` | Event-level data with `user_id`, `event_name`, `timestamp`, and optional properties | Yes |
| `workspace/processed/segments.json` | Segment definitions from audience-segmentation for cohort comparison | No |
| `workspace/raw/revenue.csv` | Revenue per converter for impact estimation | No (recommended) |
| `workspace/config/funnel_definition.json` | Step sequence, time windows, and matching mode | No (auto-inferred if absent) |

### Outputs

| File | Description |
| :--- | :---------- |
| `workspace/analysis/funnel_results.json` | Stage-by-stage conversion rates, drop-offs, confidence intervals |
| `workspace/analysis/bottleneck_ranking.json` | Priority-ranked bottleneck list with impact estimates |
| `workspace/analysis/cro_hypotheses.json` | Generated test ideas linked to bottleneck findings |
| `workspace/analysis/time_to_convert.json` | Per-stage time distributions, medians, and censoring stats |
| `workspace/reports/funnel_report.html` | Interactive funnel visualization with drill-down |

## Cross-Skill Integration

Funnel analysis sits at the intersection of behavioral analytics and
experimentation:

- **experimentation:** CRO hypotheses generated by this skill feed directly
  into the experimentation skill as test candidates for A/B testing.
- **web-analytics:** Web analytics provides the behavioral event stream from
  which funnels are constructed. Page-level and session-level data are the
  primary funnel inputs.
- **audience-segmentation:** Segment definitions enable cohort-level funnel
  comparison, revealing which user groups experience the worst drop-off.
- **paid-media:** Landing page performance is a key funnel entry point.
  Funnel entry-stage analysis feeds back into paid media landing page
  optimization.
- **reporting:** Funnel conversion trends, bottleneck rankings, and CRO
  progress are included in executive dashboards and periodic reports.

## Financial Services Considerations

When operating in financial services mode:

- Account opening funnels in financial services see 50-70% abandonment;
  KYC/AML verification steps are mandatory and cannot be optimized away.
- Funnel optimization must preserve all required regulatory disclosure steps
  and consent flows. Never recommend removing or shortening compliance steps.
- Investment product purchase funnels must maintain suitability questionnaire
  integrity. CRO hypotheses must not suggest reducing the number of suitability
  questions.
- Optimization recommendations for regulated steps should focus on UX clarity,
  progress indicators, and save-and-resume functionality rather than step
  elimination.

## Development Guidelines

1. Use Wilson score intervals for conversion rate CIs (more accurate than
   normal approximation at low rates). See `references/funnel_methodology.md`.

2. Funnel definitions must be configurable without code changes. Store as
   JSON or YAML step sequences in `workspace/config/funnel_definition.json`.

3. Time-to-convert analysis must handle censored data (users still in funnel
   at analysis time). Use Kaplan-Meier estimation where appropriate.

4. Revenue impact should use conservative estimates: 50th percentile of
   improvement range, not optimistic projections.

5. Support both GA4 event export format and generic event CSV to maximize
   data source flexibility.

6. Bottleneck scoring formula must be documented and adjustable. Default to
   `drop_off_rate * sqrt(volume) * revenue_proximity`.

7. All statistical computations must be deterministic Python scripts using
   `scipy.stats` and `numpy`. Never let the LLM estimate conversion rates or
   p-values directly.

8. Chi-squared tests for segment comparison must apply Bonferroni correction
   when testing across more than two segments simultaneously.

## Scripts

| Script | Purpose |
| :----- | :------ |
| `scripts/build_funnel.py` | Funnel construction from event sequences with time window filtering |
| `scripts/funnel_stats.py` | Conversion rates, CIs, chi-squared comparison, bottleneck scoring |
| `scripts/revenue_impact.py` | Revenue projection per stage improvement |

## Reference Files

| Reference | Content |
| :-------- | :------ |
| `references/funnel_methodology.md` | Funnel construction rules, confidence interval formulas, bottleneck scoring |
| `references/cro_patterns.md` | Common CRO patterns and hypothesis templates by funnel stage |

## Acceptance Criteria

- Funnel construction correctly handles time-window constraints (users who do
  not complete within the window are counted as dropped).
- Wilson score CIs are statistically accurate: coverage verified via simulation
  at 95% nominal level.
- Bottleneck ranking agrees with manual expert assessment on 80%+ of top-3
  bottleneck identifications.
- Revenue impact estimates are within 25% of actual observed revenue change
  when a bottleneck is subsequently fixed.
- Funnel comparison correctly identifies statistically significant differences
  between segments at p < 0.05.
- End-to-end pipeline from raw events to funnel report executes in under 60
  seconds for 1M-row event datasets.
