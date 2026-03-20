---
name: email-analytics
description: >
  Use when the user mentions email analytics, email performance, open rate,
  click rate, deliverability, bounce rate, unsubscribe rate, email engagement,
  lifecycle email, drip campaign, email automation, send-time optimization,
  subject line testing, email A/B test, email deliverability, SPF, DKIM, DMARC,
  email blocklist, inbox placement, email revenue attribution, or email
  segmentation. Also trigger on 'how are our emails performing' or 'improve
  email engagement.' If segment-level analysis is needed and segments are not
  defined, suggest running audience-segmentation first. All A/B testing is
  delegated to the experimentation skill. Results feed into reporting. In
  financial services mode, content must pass compliance-review before deployment.
---

# Email Marketing Analytics

Deliverability monitoring, engagement analysis, lifecycle flow optimization,
and send-time intelligence.

| Property       | Value                                                        |
| :------------- | :----------------------------------------------------------- |
| Skill ID       | email-analytics                                              |
| Priority       | P1 — Tactical (direct revenue channel in financial services) |
| Category       | Channel Analytics                                            |
| Depends On     | data-extraction, audience-segmentation, experimentation      |
| Feeds Into     | reporting, compliance-review (in FS mode)                    |

## Objective

Provide comprehensive email marketing analytics: deliverability health
monitoring (bounce rates, blocklist checks, authentication compliance),
engagement analysis prioritizing click-based metrics over unreliable open rates,
lifecycle flow performance optimization, send-time intelligence, and subject
line performance analysis. Delegate all statistical testing of email experiments
to the experimentation skill.

## Process Steps

1. **Validate inputs.** Load `email_sends.csv` and verify required columns
   (`campaign_id`, `send_time`, `recipient`, `delivered`, `bounced`, `opened`,
   `clicked`, `converted`). If lifecycle flow analysis is requested, also load
   `email_flows.csv` and confirm (`flow_id`, `step_number`, `trigger`, `delay`).

2. **Run deliverability check.** Execute `scripts/deliverability_check.py` to
   compute bounce rate trends, detect spikes, and validate SPF/DKIM/DMARC
   authentication records. If hard bounce rate exceeds 2% or soft bounce rate
   exceeds 5%, flag for immediate investigation. Check blocklist status for
   sending domains.

3. **Compute engagement metrics.** Execute `scripts/engagement_analysis.py` to
   calculate click-to-delivered rate (CTDR) as the primary engagement metric.
   De-emphasize open rates due to iOS 15 Mail Privacy Protection unreliability.
   Compute revenue attribution per email using the organization's standard
   attribution window.

4. **Analyze engagement decay.** Within engagement analysis, identify
   subscribers whose click activity is declining over recent send windows.
   Flag subscribers trending toward inactivity before they fully churn.

5. **Generate send-time intelligence.** Execute `scripts/send_time_optimizer.py`
   to build historical engagement heatmaps by day-of-week and hour, segmented
   by audience. Account for time zones in multi-region campaigns.

6. **Evaluate lifecycle flows.** Analyze per-flow conversion rates, identify
   flows with highest and lowest conversion efficiency, and evaluate
   time-between-sends and sequence length. Refer to
   `references/lifecycle_patterns.md` for benchmark conversion rates.

7. **Assess list health.** Execute `scripts/list_health.py` to score inactive
   subscribers (default: 90 days without click activity, configurable). Identify
   re-engagement campaign triggers and compute list hygiene scores.

8. **Analyze subject lines.** Evaluate subject line patterns including length,
   personalization tokens, emoji usage, and urgency words correlated with click
   rates. Delegate all statistical testing (chi-squared on click rates) to the
   experimentation skill.

9. **Delegate A/B tests.** For any email experiment analysis (subject line
   tests, send-time tests, content variants), write experiment data to
   `workspace/raw/experiment_data.csv` and invoke the experimentation skill.
   Do not implement statistical tests directly.

10. **Generate report.** Compile all results into
    `workspace/reports/email_performance.html` with deliverability trends,
    engagement metrics, flow performance, send-time heatmaps, and list health
    summaries.

## Key Capabilities

### Deliverability Monitoring

- Track hard/soft bounce rates with automated spike detection and root cause
  suggestions.
- Monitor domain reputation indicators and blocklist status.
- Validate SPF, DKIM, and DMARC authentication records and flag
  misconfigurations. See `references/deliverability_guide.md` for validation
  rules and remediation procedures.
- Support both ESP API integration (Braze, SendGrid, Iterable) and CSV upload
  for deliverability data ingestion.

### Engagement Analysis (Click-Based, Post-iOS 15)

- Calculate click-to-delivered rate (CTDR) as primary engagement metric,
  de-emphasizing open rates which are inflated by Apple Mail Privacy Protection.
- Revenue attribution: track downstream conversion and revenue from email
  click-throughs using the organization's standard attribution window.
- Engagement decay analysis: identify subscribers whose engagement is declining
  before they churn, using rolling window click frequency.
- Unsubscribe trend monitoring with root cause analysis by campaign type.

Refer to `references/email_metrics.md` for metric definitions, post-iOS-15
measurement guidance, and industry benchmarks.

### Lifecycle Flow Optimization

- Per-flow conversion rate analysis: identify highest and lowest performing
  flows by step-level and end-to-end conversion.
- Time-between-sends optimization: evaluate whether send cadence helps or
  hurts flow-through rates.
- Sequence length analysis: determine optimal number of touches per lifecycle
  flow.

Refer to `references/lifecycle_patterns.md` for flow best practices and
benchmark conversion rates.

### Send-Time Intelligence

- Generate send-time heatmaps from historical click data by audience segment
  and day-of-week / hour-of-day.
- Account for recipient time zones in multi-region campaigns.
- Produce optimal send-time recommendations per segment with confidence
  intervals.

### Subject Line Analysis

- Analyze subject line patterns: length, personalization tokens, emoji usage,
  urgency words, question marks, and number usage correlated with click rates.
- Structure-level analysis: preheader text impact, subject-to-preheader
  coherence.
- All significance testing is delegated to the experimentation skill.

### List Health

- Inactive subscriber scoring based on configurable lookback period (default
  90 days without click activity).
- Re-engagement campaign trigger identification: segment inactive subscribers
  by recency and historical value for targeted re-engagement.
- List hygiene scoring: overall list quality metric based on bounce rates,
  engagement rates, and complaint rates.

## Input / Output Data Contracts

### Inputs

| File | Description | Required |
| :--- | :---------- | :------- |
| `workspace/raw/email_sends.csv` | Send-level data: campaign_id, send_time, recipient, delivered, bounced, opened, clicked, converted | Yes |
| `workspace/processed/segments.json` | Segment definitions from audience-segmentation for segment-level analysis | No |
| `workspace/raw/email_flows.csv` | Lifecycle flow definitions: flow_id, step_number, trigger, delay | No (for flow analysis) |

### Outputs

| File | Description |
| :--- | :---------- |
| `workspace/analysis/email_deliverability.json` | Deliverability health scores and issue flags |
| `workspace/analysis/email_engagement.json` | Campaign and flow-level engagement metrics |
| `workspace/analysis/send_time_heatmap.json` | Optimal send-time recommendations by segment |
| `workspace/analysis/list_health.json` | Inactive subscriber identification and re-engagement targets |
| `workspace/reports/email_performance.html` | Email analytics dashboard with deliverability, engagement, and flow charts |

## Cross-Skill Integration

The email analytics skill integrates with the broader analytics portfolio:

- **experimentation:** All A/B testing (subject lines, send times, content
  variants) is delegated to the experimentation skill rather than implementing
  statistical tests directly. Write experiment data to workspace files and
  invoke experimentation for proper statistical rigor.
- **audience-segmentation:** Provides targeting segments for segment-level
  performance comparison. If segments are not yet defined, suggest running
  audience-segmentation first.
- **clv (customer lifetime value):** Probability-alive scores trigger
  re-engagement flows for at-risk high-value customers.
- **reporting:** Email trend summaries feed into cross-channel dashboards and
  periodic performance reports.
- **compliance-review (financial services mode):** All email content and
  experiment variants must pass compliance-review before deployment.

## Financial Services Considerations

When operating in financial services mode:

- All email content for investment products must include required regulatory
  disclosures and disclaimers.
- CAN-SPAM compliance is mandatory; additionally SEC archival rules apply to
  all investor communications.
- Email experiment variants must preserve all compliance-required elements
  across all variants — regulatory disclosures cannot be the variable under
  test.
- Transactional emails (statements, confirmations) have different regulatory
  requirements than marketing emails and must be tracked separately.

## Development Guidelines

1. Prioritize click-to-delivered rate over open rate as the primary engagement
   metric due to iOS 15 / Mail Privacy Protection unreliability.

2. Send-time optimization must account for time zones in multi-region
   campaigns.

3. Deliverability monitoring should support both ESP API integration (Braze,
   SendGrid, Iterable) and CSV upload.

4. Inactive subscriber threshold should be configurable; default to 90 days
   without click activity.

5. Subject line analysis must use statistical tests (chi-squared on click
   rates), not just observational patterns — delegate to experimentation skill.

6. Revenue attribution must use consistent attribution windows matching the
   organization's standard model.

7. All statistical computations must be deterministic Python scripts. Never
   let the LLM estimate metrics or p-values directly.

## Scripts

| Script | Purpose |
| :----- | :------ |
| `scripts/deliverability_check.py` | Bounce rate trend analysis, authentication record validation |
| `scripts/engagement_analysis.py` | CTDR calculation, revenue attribution, engagement decay detection |
| `scripts/send_time_optimizer.py` | Historical engagement heatmap generation by segment and day/hour |
| `scripts/list_health.py` | Inactive subscriber scoring, re-engagement trigger identification |

## Reference Files

| Reference | Content |
| :-------- | :------ |
| `references/email_metrics.md` | Metric definitions, post-iOS-15 measurement guidance, industry benchmarks |
| `references/deliverability_guide.md` | SPF/DKIM/DMARC validation rules, blocklist remediation procedures |
| `references/lifecycle_patterns.md` | Email lifecycle flow best practices and benchmark conversion rates |

## Acceptance Criteria

- Deliverability check correctly identifies misconfigured SPF/DKIM/DMARC
  records against DNS lookup.
- Engagement analysis produces CTDR calculations that match ESP-reported
  metrics within 1% tolerance.
- Send-time heatmap correctly identifies the top 3 send-time windows verified
  against held-out test sends.
- Inactive subscriber identification correctly flags 95%+ of subscribers with
  zero clicks in the configured lookback period.
- Email analytics delegates experiment analysis to experimentation skill via
  proper workspace file handoff.
