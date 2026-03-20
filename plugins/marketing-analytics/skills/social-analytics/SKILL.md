---
name: social-analytics
description: >
  Use when the user mentions social media analytics, social performance,
  Facebook insights, Instagram analytics, LinkedIn analytics, TikTok analytics,
  YouTube analytics, X analytics, Twitter analytics, social engagement, social
  reach, share of voice, social sentiment, brand mentions, social content
  performance, viral content, social ROI, social listening, or social
  benchmarking. Also trigger on 'how are we doing on social' or 'what's
  performing on LinkedIn.' If social platform data is not yet extracted, suggest
  running data-extraction first. Share-of-voice data feeds into competitive-intel.
  Social engagement data feeds attribution-analysis as a channel input. Results
  feed into reporting.
category: Channel Analytics
priority: P2
depends_on:
  - data-extraction
feeds_into:
  - competitive-intel
  - attribution-analysis
  - reporting
---

# Social Media Analytics

Cross-platform social performance, sentiment analysis, and competitive benchmarking.

| Property       | Value                                                       |
| :------------- | :---------------------------------------------------------- |
| Skill ID       | social-analytics                                            |
| Priority       | P2 — Supporting (brand and awareness channel)               |
| Category       | Channel Analytics                                           |
| Depends On     | data-extraction                                             |
| Feeds Into     | competitive-intel, attribution-analysis, reporting          |

## Objective

Aggregate performance data across social platforms (Meta, LinkedIn, TikTok,
YouTube, X/Twitter), perform sentiment analysis on brand mentions, analyze
content performance patterns, and benchmark against competitors. Support both
organic and paid social analytics with clear delineation between earned and
boosted content.

## Cross-Platform Performance Aggregation

Normalize engagement metrics across platforms to a single comparable schema
so that downstream consumers can evaluate social performance holistically.

### Unified metric taxonomy

| Unified Metric     | Meta (FB/IG)        | LinkedIn             | TikTok              | YouTube             | X (Twitter)         |
|--------------------|---------------------|----------------------|---------------------|---------------------|---------------------|
| impressions        | impressions         | impressions          | video_views         | views               | impressions         |
| reach              | reach               | uniqueImpressionsCount | reach             | uniqueViewers       | reach               |
| engagements        | post_engagements    | totalEngagements     | engagements         | likes + comments    | engagements         |
| likes/reactions    | reactions           | likes                | likes               | likes               | likes               |
| comments           | comments            | comments             | comments            | comments            | replies             |
| shares             | shares              | shares               | shares              | shares              | retweets + quotes   |
| clicks             | link_clicks         | clicks               | clicks              | card_clicks         | url_clicks          |
| video_views        | video_views         | videoViews           | video_views         | views               | video_views         |
| followers          | page_followers      | followerCount        | followerCount       | subscriberCount     | followers_count     |

### Key normalization rules

- Engagement rate is always calculated as `engagements / reach` to enable
  cross-platform comparison. Where reach is unavailable, fall back to
  impressions with a transparent label.
- Video view definitions differ by platform (Meta: 3s, TikTok: display,
  YouTube: 30s or completion). Label all video metrics with platform-native
  view definition.
- Currency normalization for any paid social metrics using daily FX rates.
- Distinguish organic vs paid metrics: separate columns for organic reach,
  paid reach, and total reach.

Use `scripts/normalize_social.py` for deterministic transformation.

See `references/social_api_mapping.md` for the full metric taxonomy.

## Content Performance Analysis

### Content type benchmarking

Compare engagement rates across content formats within and across platforms:

| Content Type | Platforms                        |
|--------------|----------------------------------|
| Video        | All                              |
| Carousel     | Meta, LinkedIn                   |
| Static image | All                              |
| Text-only    | LinkedIn, X                      |
| Stories      | Meta, LinkedIn, YouTube (Shorts) |
| Reels/Shorts | Meta (Reels), YouTube (Shorts), TikTok |
| Polls        | LinkedIn, X                      |

### Topic and theme analysis

Classify posts by topic using keyword extraction and semantic clustering.
Measure per-topic engagement rates to identify high-performing themes.

### Optimal posting cadence

Analyze engagement rate as a function of posting frequency to identify
diminishing-returns thresholds per platform.

### Best time to post

Build historical engagement heatmaps by platform, day of week, and hour.
Account for audience timezone distribution when generating recommendations.

Use `scripts/content_analysis.py` for computation.

## Sentiment Analysis

### Classification approach

Use transformer-based NLP models (e.g., `cardiffnlp/twitter-roberta-base-sentiment`)
to classify brand mentions, comments, and replies into positive, neutral, and
negative categories. Do not use simple keyword matching.

### Trend detection

Identify emerging conversation themes around the brand or category using
topic modeling on mention text. Track topic volume over time to detect
rising narratives.

### Crisis signal detection

Monitor negative sentiment volume using a rolling window. Generate an alert
when negative sentiment exceeds a configurable threshold (default: 3x
standard deviation above the rolling mean). Include:

- Spike magnitude and start time
- Sample mentions driving the spike
- Affected platforms
- Recommended immediate actions

See `references/sentiment_methodology.md` for model selection and scoring details.

Use `scripts/sentiment_analysis.py` for computation.

## Share of Voice

Calculate brand mention volume relative to competitors across platforms.

### Methodology

- Define consistent search queries per brand (brand name, handles, hashtags,
  common misspellings).
- Use consistent time windows across all competitors.
- Compute share of voice as `brand_mentions / total_category_mentions`.
- Break down share of voice by platform, sentiment, and content type.
- Track share of voice trends over time to measure campaign impact.

### Competitive benchmarking

Compare engagement rates, posting frequency, follower growth, and content
mix against competitor accounts. Identify content strategies that drive
outsized engagement for competitors.

Use `scripts/share_of_voice.py` for computation.

## Organic vs Paid Delineation

Maintain separate metric streams for organic and paid social:

| View          | Description                                             |
|---------------|---------------------------------------------------------|
| Organic only  | Earned impressions, engagement from non-boosted posts   |
| Paid only     | Boosted/promoted post metrics and paid social campaigns |
| Blended       | Combined organic + paid for total channel view          |

Default dashboards show blended view with organic/paid breakdown available
on drill-down. Attribution-analysis consumes only the paid component for
media mix modeling.

## Influencer and Creator Performance

Track content partnerships and earned media value:

- Partner-attributed impressions, engagements, and conversions
- Earned media value estimation based on equivalent paid CPM
- Creator audience overlap with brand audience

## Input / Output Data Contracts

### Inputs

| File pattern                                    | Description                                    |
|-------------------------------------------------|------------------------------------------------|
| `workspace/raw/social_performance_{platform}.csv` | Platform-specific post performance data       |
| `workspace/raw/social_mentions.csv`             | Brand mentions from social listening tools     |
| `workspace/raw/competitor_social.csv`           | Competitor social metrics for benchmarking     |

### Outputs

| File                                              | Description                                         |
|---------------------------------------------------|-----------------------------------------------------|
| `workspace/analysis/social_performance.json`      | Cross-platform engagement metrics with content analysis |
| `workspace/analysis/social_sentiment.json`        | Sentiment scores, topic themes, crisis signals      |
| `workspace/analysis/social_benchmarks.json`       | Competitive share of voice and benchmarking data    |
| `workspace/reports/social_dashboard.html`         | Cross-platform social analytics dashboard           |

### Normalized social post schema

| Column           | Type    | Description                                  |
|------------------|---------|----------------------------------------------|
| date             | date    | Post date (YYYY-MM-DD)                       |
| platform         | string  | meta / linkedin / tiktok / youtube / x       |
| post_id          | string  | Platform-native post identifier              |
| post_type        | string  | video / carousel / image / text / story / reel |
| topic            | string  | Classified topic or theme                    |
| is_paid          | boolean | Whether post was boosted or promoted         |
| impressions      | integer | Impression count                             |
| reach            | integer | Unique accounts reached                      |
| engagements      | integer | Total engagements                            |
| likes            | integer | Likes or reactions                           |
| comments         | integer | Comments                                     |
| shares           | integer | Shares, retweets, reposts                    |
| clicks           | integer | Link clicks                                  |
| video_views      | integer | Video view count (platform-native definition)|
| engagement_rate  | decimal | Derived: engagements / reach                 |

## Cross-Skill Integration

| Skill                | Relationship                                                              |
|----------------------|---------------------------------------------------------------------------|
| data-extraction      | Upstream: provides raw platform CSV files consumed by this skill          |
| competitive-intel    | Downstream: receives share-of-voice data for comprehensive competitive monitoring |
| attribution-analysis | Downstream: social engagement included as a channel in marketing mix models |
| reporting            | Downstream: social metrics aggregated alongside other channels in executive dashboards |
| seo-content          | Downstream: content performance patterns inform content strategy recommendations |

## Financial Services Considerations

When analyzing social media for financial services clients:

- Social media posts must comply with FINRA Rule 2210 communications
  standards. Flag posts missing required disclosures.
- Testimonials and endorsements must follow SEC Marketing Rule disclosure
  requirements. Monitor for non-compliant user-generated content.
- Employee social media posts about fund performance require pre-approval
  and archival. Track compliance status.
- Crisis detection should include regulatory inquiry and litigation risk
  signals alongside standard brand sentiment monitoring.

## Development Guidelines

1. Use platform APIs where available; fall back to CSV export for platforms
   with restricted API access.
2. Sentiment analysis must use a pre-trained transformer model (e.g.,
   `cardiffnlp/twitter-roberta-base-sentiment`), not simple keyword matching.
3. Engagement rate normalization must account for platform-specific reach
   calculation differences.
4. Share of voice calculations must use consistent time windows and query
   definitions across competitors.
5. Support both organic-only and blended (organic + paid) views of social
   performance.
6. Crisis detection threshold should be configurable; default to 3x standard
   deviation in negative sentiment volume.
7. All monetary calculations must use `decimal.Decimal` (Python) to avoid
   floating-point rounding errors.
8. Reference files in `references/` for methodology details; keep SKILL.md
   focused on instructions and contracts.
9. Scripts in `scripts/` handle deterministic computation; the LLM handles
   interpretation, insight generation, and recommendation framing.
