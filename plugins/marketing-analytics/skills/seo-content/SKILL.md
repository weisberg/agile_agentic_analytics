---
name: seo-content
description: >
  Use when the user mentions SEO, search engine optimization, keyword ranking,
  search console, organic search, organic traffic, content performance, keyword
  research, keyword gap, content audit, technical SEO, backlinks, domain
  authority, AI Overviews, AI search, GEO, generative engine optimization, AIO,
  search visibility, SERP, featured snippets, content optimization, or page
  speed. Also trigger on 'how is our content performing' or 'which keywords
  should we target.' If web traffic context is needed, suggest running
  web-analytics first. Keyword data feeds into competitive-intel and paid-media
  (organic/paid keyword overlap). Results feed into reporting.
---

# SEO & Content Analytics

Search Console integration, keyword tracking, content performance, and AI
search optimization (GEO).

| Property       | Value                                                       |
| :------------- | :---------------------------------------------------------- |
| Skill ID       | seo-content                                                 |
| Priority       | P1 — Tactical (organic channel growth)                      |
| Category       | Channel Analytics                                           |
| Depends On     | data-extraction, web-analytics                              |
| Feeds Into     | competitive-intel, reporting, paid-media (keyword overlap)  |

## Objective

Automate SEO and content performance analysis: Google Search Console
integration for keyword ranking and click-through data, content performance
measurement by topic and category, technical SEO auditing, competitive keyword
gap analysis, and the emerging AI search optimization (GEO/AIO) dimension.
Track visibility across traditional search results and AI-generated answers
(Google AI Overviews, ChatGPT, Perplexity).

## Process Steps

1. **Validate inputs.** Load `search_console.csv` and verify required columns
   (`query`, `page`, `clicks`, `impressions`, `ctr`, `position`, `date`). If a
   content inventory is provided, confirm URL matching between datasets.

2. **Extract Search Console data.** Run `scripts/extract_gsc.py` to pull data
   from the Google Search Console API with automated date range handling and
   pagination for sites with more than 25,000 rows per request.

3. **Track keyword positions.** Run `scripts/keyword_tracking.py` to compute
   7-day rolling average positions, detect movers (position change > 5),
   identify new rankings, and flag lost rankings.

4. **Analyze content performance.** Run `scripts/content_analysis.py` to map
   pages to topic clusters, detect content decay (configurable threshold,
   default 20% traffic decline over 90 days), and identify underperformers
   (high impressions, low CTR).

5. **Audit technical SEO.** Run `scripts/seo_audit.py` to check Core Web
   Vitals via PageSpeed Insights API, validate structured data, and surface
   crawl errors.

6. **Assess AI search visibility (GEO).** Monitor brand mentions and citation
   frequency in AI-generated search results. Recommend content structure
   optimizations for AI extractability.

7. **Perform competitive keyword gap analysis.** Identify high-value keywords
   where competitors rank but you do not. Score opportunities by search volume,
   difficulty, and business relevance.

8. **Identify organic/paid keyword overlap.** Cross-reference organic ranking
   data with paid-media keyword lists to find cost-saving opportunities where
   strong organic rankings make paid bids unnecessary.

9. **Generate report.** Compile all results into
   `workspace/reports/seo_dashboard.html` with keyword trend charts, content
   performance tables, technical audit summaries, and GEO visibility tracking.

## Key Capabilities

### Search Intelligence

- Extract Search Console data via API with automated date range management.
  Handle the 25,000-row-per-request limit through pagination.
- Track keyword position changes: improvements, declines, new rankings, lost
  rankings. Use 7-day rolling averages to smooth daily fluctuations.
- Identify organic/paid keyword overlap: keywords where you rank organically
  AND run ads (cost savings opportunity).
- Discover trending queries with rising impression counts before they achieve
  significant click volume.

Refer to `references/search_console_api.md` for GSC API query dimensions,
filter syntax, and pagination strategies.

### Content Performance

- Map content to topic clusters and measure cluster-level organic performance
  including traffic, engagement, and conversions.
- Identify underperforming content: high impressions but low CTR indicates
  title/description optimization is needed.
- Track content decay: pages with declining traffic over a 3+ month trend.
  Apply statistical trend tests to distinguish real decline from noise.
- Score content freshness and recommend update priorities based on traffic
  impact potential.

### AI Search Optimization (GEO)

- Monitor brand mentions in AI-generated search results (Google AI Overviews,
  conversational AI engines).
- Track citation frequency and accuracy in LLM-powered search engines
  (ChatGPT, Perplexity, Gemini).
- Recommend content structure optimizations for AI extractability: structured
  data, clear headers, factual authority signals, concise answer blocks.
- Measure share of voice in AI-generated answers relative to competitors.

Refer to `references/geo_methodology.md` for AI search optimization strategies
and citation tracking approaches.

### Technical SEO

- Assess Core Web Vitals (LCP, INP, CLS) via Lighthouse or PageSpeed Insights
  API. Flag pages exceeding "needs improvement" thresholds.
- Validate structured data (JSON-LD) for completeness and schema.org
  compliance.
- Identify crawl errors, redirect chains, and orphaned pages.
- Monitor robots.txt and sitemap health.

Refer to `references/technical_seo.md` for Core Web Vitals thresholds,
structured data requirements, and crawl optimization guidance.

### Competitive Keyword Gap

- Identify keywords where competitors rank in the top 20 but you do not.
- Score opportunities by estimated search volume, keyword difficulty, and
  business relevance.
- Group gap keywords by topic cluster to inform content strategy.
- Handle missing third-party API data gracefully (Semrush, Ahrefs).

## Input / Output Data Contracts

### Inputs

| File | Description | Required |
| :--- | :---------- | :------- |
| `workspace/raw/search_console.csv` | GSC data: query, page, clicks, impressions, ctr, position, date | Yes |
| `workspace/raw/content_inventory.csv` | Content pages with metadata: URL, title, category, publish_date | No (recommended) |
| `workspace/processed/web_metrics.json` | Traffic and engagement from web-analytics skill | No (for content performance) |

### Outputs

| File | Description |
| :--- | :---------- |
| `workspace/analysis/keyword_performance.json` | Keyword ranking trends, movers, new/lost rankings |
| `workspace/analysis/content_performance.json` | Page and topic cluster level traffic and conversion metrics |
| `workspace/analysis/seo_audit.json` | Technical SEO issues, Core Web Vitals, structured data gaps |
| `workspace/analysis/keyword_gap.json` | Competitive keyword gap analysis with opportunity scores |
| `workspace/reports/seo_dashboard.html` | Interactive SEO performance dashboard |

## Cross-Skill Integration

The seo-content skill connects organic search intelligence across the
analytics portfolio:

- **paid-media:** Shares keyword intelligence for organic/paid overlap
  optimization. Stop bidding on keywords where you rank #1 organically.
- **competitive-intel:** Keyword gap data feeds competitive positioning
  analysis and market share estimation.
- **web-analytics:** Provides the traffic and behavioral data that measures
  content performance and validates SEO improvements.
- **reporting:** Organic search trends, keyword movements, and technical SEO
  health feed into cross-channel dashboards and periodic reports.

## Financial Services Considerations

When operating in financial services mode:

- All landing pages must maintain required regulatory disclosures even after
  SEO optimization. Never remove or obscure compliance language for ranking
  improvement.
- AI search citations of fund performance must be monitored for accuracy and
  compliance with the SEC Marketing Rule.
- Content targeting investment-related keywords must comply with advertising
  regulations (SEC, FINRA) before publication.
- Keyword gap analysis for financial products must flag regulated terms that
  require compliance review before content creation.

## Development Guidelines

1. Search Console API has a 25,000 row limit per request. Implement pagination
   for high-volume sites to ensure complete data extraction.

2. Keyword position changes should use a 7-day rolling average to smooth daily
   fluctuations and reduce false-positive mover detection.

3. AI search (GEO) tracking is an emerging practice. Design the module to be
   extensible as new monitoring APIs emerge from search providers.

4. Content decay detection threshold should be configurable. Default to 20%
   traffic decline over 90 days. Use statistical trend tests (e.g.,
   Mann-Kendall) to distinguish real decline from noise.

5. Competitive gap analysis requires third-party API access (Semrush, Ahrefs).
   Handle missing data gracefully with clear user messaging.

6. Technical SEO checks should use Lighthouse or PageSpeed Insights API for
   Core Web Vitals. Cache results to avoid redundant API calls.

7. All deterministic computations (rolling averages, trend tests, decay
   detection) must be implemented in Python scripts, not estimated by the LLM.

## Scripts

| Script | Purpose |
| :----- | :------ |
| `scripts/extract_gsc.py` | Search Console data extraction with automated date range handling |
| `scripts/keyword_tracking.py` | Position change detection, mover identification, trend analysis |
| `scripts/content_analysis.py` | Topic cluster mapping, content decay detection, underperformer identification |
| `scripts/seo_audit.py` | Technical SEO checks: CWV, structured data, crawl errors |

## Reference Files

| Reference | Content |
| :-------- | :------ |
| `references/search_console_api.md` | GSC API reference, query dimensions, filter syntax |
| `references/geo_methodology.md` | AI search optimization strategies, citation tracking approaches |
| `references/technical_seo.md` | Core Web Vitals thresholds, structured data requirements |

## Acceptance Criteria

- Search Console extraction handles pagination and retrieves complete dataset
  for sites with 50K+ queries.
- Keyword mover detection correctly identifies 95%+ of keywords with position
  change > 5 positions.
- Content decay detection flags pages with statistically significant traffic
  decline (not just noise) using trend test.
- Competitive keyword gap correctly identifies opportunities verified against
  manual Semrush/Ahrefs audit.
