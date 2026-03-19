---
name: competitive-intel
description: >
  Use when the user mentions competitive analysis, competitor research,
  competitive intelligence, competitor keywords, competitor ads, share of voice,
  market share, competitive benchmarking, competitor traffic, competitor strategy,
  competitive landscape, SWOT, competitor monitoring, ad spy, competitor ad
  creative, pricing intelligence, or market positioning. Also trigger on 'what
  are competitors doing' or 'how do we compare to [competitor].'
category: Market Intelligence
priority: P2
depends_on:
  - seo-content
  - social-analytics
  - paid-media
feeds_into:
  - attribution-analysis
  - reporting
---

# Competitive Intelligence

Competitor keyword tracking, traffic estimation, ad creative monitoring, and market positioning.

## Objective

Provide systematic competitive intelligence: competitor keyword ranking overlap,
estimated traffic share, ad creative and messaging monitoring, share-of-voice
aggregation across channels, and pricing intelligence. Synthesize competitive
signals into actionable strategic recommendations grounded in specific data
points.

## Competitor Keyword Overlap & Gap Analysis

Identify keyword opportunities by comparing your rankings against each defined
competitor.

### Gap types

| Gap Type       | Definition                                         | Action                            |
|----------------|----------------------------------------------------|-----------------------------------|
| Missing        | Competitor ranks, you do not                       | Evaluate for content creation     |
| Weak           | Both rank, competitor significantly higher          | Optimize existing content         |
| Strong         | Both rank, you significantly higher                | Defend position                   |
| Shared         | Both rank in similar positions                     | Monitor for movement              |
| Unique         | You rank, competitor does not                      | Leverage as competitive advantage |

### Opportunity scoring

Score each gap opportunity using:

```
opportunity_score = search_volume * (1 - keyword_difficulty) * business_relevance
```

Where:
- `search_volume` — monthly average from SEO tool data
- `keyword_difficulty` — normalized 0-1 scale from SEO tool
- `business_relevance` — 0-1 score based on keyword-to-product/service alignment

Track competitor keyword position changes and new keyword targeting over time to
detect strategy shifts.

Use `scripts/keyword_gap.py` for computation.

## Traffic Estimation

Estimate competitor traffic share using available data sources.

### Methods

1. **Third-party estimates** — SimilarWeb, Semrush Traffic Analytics, or
   DataForSEO rank tracker data provide directional traffic estimates.
2. **CTR-curve proxy** — Multiply keyword search volume by position-based CTR
   curves to estimate organic traffic per keyword, then aggregate.
3. **Relative indexing** — When absolute numbers are unreliable, index all
   competitors relative to your own verified traffic to produce a ratio-based
   comparison.

Always label traffic estimates with methodology and confidence level. Never
present third-party estimates as precise figures.

## Ad Creative Monitoring

Track competitor advertising activity across search and social channels.

### Tracking scope

- **Ad copy** — Headlines, descriptions, display URLs, and extensions
- **Offers** — Promotional pricing, discounts, free trials, lead magnets
- **Landing pages** — URL destinations, page structure, key messaging
- **Messaging themes** — Value propositions, CTAs, emotional appeals

### Analysis outputs

- Identify seasonal patterns in competitor advertising intensity.
- Detect ad copy rotations and new offer launches.
- Compare competitor messaging positioning against your own.
- Flag competitors making potentially non-compliant performance claims
  (especially relevant for financial services).

Data sources include Meta Ad Library, Google Ads Transparency Center, SpyFu,
and manual monitoring exports placed in `workspace/raw/competitor_data.csv`.

## Share of Voice Aggregation

Combine signals from organic search, paid search, social media, and earned
media into a unified share-of-voice metric.

### Channel components

| Channel        | Signal Source                        | Weight Method                      |
|----------------|-------------------------------------|------------------------------------|
| Organic search | Keyword rankings weighted by volume | CTR-curve weighted visibility      |
| Paid search    | Impression share, ad position data  | Spend-weighted or impression share |
| Social media   | Engagement, follower growth, post volume | Engagement-weighted share      |
| Earned media   | Mentions, backlinks, PR coverage    | Volume-weighted share              |

### Aggregation

Aggregate channel-level SOV into a composite score using configurable channel
weights that reflect business priorities. Default equal weighting unless
configured otherwise.

See `references/competitive_methodology.md` for full calculation details.

Use `scripts/share_of_voice.py` for computation.

## Pricing Intelligence

Monitor competitor pricing, offers, and promotional patterns.

### Scope

- Track competitor product/service pricing from public sources.
- Detect promotional patterns: frequency, depth, timing, and triggers.
- Compare pricing positioning: premium, parity, or discount relative to market.
- Monitor offer structure changes (packaging, bundling, feature gating).

### Constraints

- Use only publicly available pricing information.
- Do not scrape competitor sites in violation of terms of service.
- Flag pricing data freshness — stale data must be labeled with last-verified date.

## Strategic Synthesis

Translate raw competitive data into strategic recommendations.

### Competitive scorecard

Aggregate all signals into a per-competitor scorecard:

| Dimension          | Metrics                                              |
|--------------------|------------------------------------------------------|
| Search presence    | Organic SOV, keyword overlap, content velocity       |
| Paid media         | Ad impression share, creative freshness, offer depth |
| Social presence    | Engagement SOV, audience growth rate                 |
| Pricing position   | Price index, promotional frequency                   |
| Overall trajectory | Accelerating / stable / decelerating investment      |

### Recommendation requirements

- Every recommendation must link to at least one specific data point.
- Recommendations must be framed as actionable next steps, not generic advice.
- Include estimated impact where data supports it.
- Prioritize recommendations by expected impact and implementation effort.

Use `scripts/competitive_synthesis.py` for scorecard aggregation.

### Change detection and alerting

Monitor competitor metrics for significant changes using percentage-based
thresholds (not absolute) to handle competitors of different sizes.

Alert categories:
- New keyword targeting detected
- Ad copy or offer change
- Traffic share shift beyond threshold
- Pricing change
- Social activity spike

Use `scripts/competitive_alerting.py` for change detection.

## Input / Output Data Contracts

### Inputs

| File pattern                                  | Description                                     |
|-----------------------------------------------|-------------------------------------------------|
| `workspace/analysis/keyword_performance.json` | Your keyword data from seo-content skill        |
| `workspace/analysis/social_benchmarks.json`   | Social share of voice from social-analytics     |
| `workspace/raw/competitor_data.csv`           | Third-party competitive data (Semrush, SimilarWeb, SpyFu exports) |

### Outputs

| File                                              | Description                                                |
|---------------------------------------------------|------------------------------------------------------------|
| `workspace/analysis/competitive_landscape.json`   | Aggregated competitive intelligence across all channels    |
| `workspace/analysis/keyword_gap.json`             | Competitive keyword opportunities with volume and difficulty |
| `workspace/analysis/competitive_alerts.json`      | New competitor activities and strategy shifts detected      |
| `workspace/reports/competitive_briefing.html`     | Executive competitive intelligence briefing                |

### Competitive landscape schema

| Field              | Type    | Description                                    |
|--------------------|---------|------------------------------------------------|
| competitor_name    | string  | Competitor identifier                          |
| competitor_domain  | string  | Primary domain                                 |
| organic_sov        | decimal | Organic search share of voice (0-1)            |
| paid_sov           | decimal | Paid search share of voice (0-1)               |
| social_sov         | decimal | Social media share of voice (0-1)              |
| composite_sov      | decimal | Weighted composite share of voice (0-1)        |
| keyword_overlap    | integer | Count of shared ranking keywords               |
| keyword_gap_count  | integer | Keywords where competitor ranks and you do not |
| trajectory         | string  | accelerating / stable / decelerating           |
| last_updated       | date    | Analysis date (YYYY-MM-DD)                     |

### Keyword gap schema

| Field              | Type    | Description                                    |
|--------------------|---------|------------------------------------------------|
| keyword            | string  | Search term                                    |
| search_volume      | integer | Monthly search volume                          |
| keyword_difficulty | decimal | Difficulty score (0-1)                         |
| your_position      | integer | Your ranking position (null if not ranking)    |
| competitor         | string  | Competitor name                                |
| competitor_position| integer | Competitor ranking position                    |
| gap_type           | string  | missing / weak / strong / shared / unique      |
| opportunity_score  | decimal | Composite opportunity score                    |
| business_relevance | decimal | Relevance to business (0-1)                    |

## Cross-Skill Integration

| Skill                | Relationship                                                                 |
|----------------------|------------------------------------------------------------------------------|
| seo-content          | Upstream: provides keyword performance data for gap analysis                 |
| social-analytics     | Upstream: provides social engagement benchmarks for social SOV               |
| paid-media           | Upstream: provides ad performance baselines for paid SOV comparison          |
| attribution-analysis | Downstream: competitor activity levels serve as control variables in MMM models — when a competitor increases spend, your conversion rate may change independently |
| reporting            | Downstream: competitive trends feed executive dashboards                     |

## Financial Services Considerations

When performing competitive intelligence for financial services clients:

- Use only publicly available information. Do not use non-public or proprietary
  competitor data.
- Competitor performance claims (returns, AUM growth) sourced from public filings
  (SEC EDGAR, FINRA BrokerCheck) are acceptable; internal estimates are not.
- Ad creative monitoring should flag competitors making potentially non-compliant
  performance claims (e.g., guaranteed returns, missing risk disclosures) for
  internal compliance awareness.
- Do not make investment performance comparisons without proper disclaimers and
  time-period matching.

## Development Guidelines

1. Design for graceful degradation: some data sources require paid subscriptions
   (Semrush, Ahrefs, SimilarWeb). The skill must function with whatever data is
   available and clearly state what is missing.
2. Keyword gap opportunity scoring must use:
   `search_volume * (1 - keyword_difficulty) * business_relevance`.
3. Share of voice calculations must include methodology notes and data source
   limitations in every output.
4. Change detection for competitive alerting must use percentage change, not
   absolute values, to handle competitors of different sizes.
5. Strategic recommendations must be grounded in specific data points — never
   produce generic "best practices" advice.
6. Support manual competitor list definition. Do not auto-discover competitors
   to avoid scope creep.
7. All monetary calculations must use `decimal.Decimal` (Python) to avoid
   floating-point rounding errors.
8. Reference files in `references/` contain methodology details. Keep this file
   focused on instructions and contracts.
9. Scripts in `scripts/` handle deterministic computation. The LLM handles
   interpretation, insight generation, and recommendation framing.
