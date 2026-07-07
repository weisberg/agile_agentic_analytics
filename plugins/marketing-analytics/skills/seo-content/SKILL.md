---
name: seo-content
description: >
  Use when the user mentions SEO, search engine optimization, keyword ranking,
  search console, organic search, organic traffic, content performance, keyword
  research, keyword gap, content audit, technical SEO, backlinks, domain authority,
  AI Overviews, AI search, GEO, generative engine optimization, AIO, search
  visibility, SERP, featured snippets, content optimization, or page speed. Also
  trigger on 'how is our content performing' or 'which keywords should we target.'
  For overall site traffic and session behavior use web-analytics; for competitor
  keyword/traffic benchmarking use competitive-intel; this skill owns organic
  search and content performance. If Search Console data is not yet in the
  workspace, run data-extraction first.

disable-model-invocation: false
---

# SEO & Content Analytics

Search Console integration, keyword-position tracking, content performance and
decay, technical SEO auditing, and AI-search (GEO) visibility.

## Contract

**Role:** Advisory analyst. Measures organic performance and recommends content
and technical fixes; does not publish pages or change markup. Deterministic
computation (rolling averages, trend tests) runs in Python scripts.

**Mode:**
- `quick` — keyword-position tracking + top content performance.
- `standard` (default) — add content decay, technical SEO audit.
- `deep` — add GEO/AI-search visibility and competitive keyword-gap analysis.

**When to use:** organic keyword rankings, content performance/decay, technical
SEO health, AI-Overview visibility, organic/paid keyword overlap.

**When NOT to use:** total site traffic and sessions → `web-analytics`; competitor
traffic/ad benchmarking → `competitive-intel`; paid keyword bidding → paid-media.
See `../../references/skill-index.md`.

**Evidence required (inputs):**
- `workspace/raw/search_console.csv` — query, page, clicks, impressions, ctr,
  position, date. Required. If absent, STOP and run **data-extraction** first.
- `workspace/raw/content_inventory.csv` — url, title, category, publish_date
  (recommended; enables content-cluster mapping).
- `workspace/processed/web_metrics.json` — from web-analytics (optional).

**Depends on:** data-extraction, web-analytics. **Feeds into:** competitive-intel,
reporting, paid-media. Builder detail in `references/authoring-notes.md`.

**Hard STOP (data integrity):** if `search_console.csv` is missing required
columns or covers too short a span to compute a 7-day rolling average, STOP the
mover-detection step and report raw positions only — smoothed movers off a partial
series are false signals.

Parse `$ARGUMENTS` for inline paths, decay threshold, or competitor domains.

## Workflow

1. **Validate inputs.** Load `search_console.csv`; verify columns. If a content
   inventory is present, confirm URL matching. Apply the Hard STOP gate.

2. **Extract GSC.** Run `scripts/extract_gsc.py` to pull Search Console data with
   date-range handling and pagination past the 25,000-row limit.

3. **Track keyword positions.** Run `scripts/keyword_tracking.py`: 7-day rolling
   average positions, movers (change > 5), new rankings, lost rankings.

4. **Content performance.** Run `scripts/content_analysis.py`: map pages to topic
   clusters, detect decay (default 20% traffic decline over 90 days, statistical
   trend test), surface underperformers (high impressions, low CTR).

5. **Technical SEO audit.** Run `scripts/seo_audit.py`: Core Web Vitals via
   PageSpeed Insights, structured-data validation, crawl errors. See
   `references/technical_seo.md`.

6. **GEO / AI-search** (deep mode). Monitor brand mentions and citation frequency
   in AI answers; recommend structure for AI extractability; measure AI share of
   voice. See `references/geo_methodology.md`.

7. **Competitive keyword gap** (deep mode). When a competitor comparison is
   requested, first run the data-availability gate:
   - **AskUserQuestion:** "Competitive gap analysis needs third-party keyword data
     (Semrush/Ahrefs). How should I proceed?"
   - **Options:** (a) *I have an export* — point me to
     `workspace/raw/competitor_data.csv`; (b) *No third-party data* — run
     gap analysis on GSC-visible overlap only and label coverage as partial;
     (c) *Skip gap analysis* — focus on owned-property SEO.
   Then identify keywords where competitors rank top-20 and you do not; score by
   `search_volume * (1 - keyword_difficulty) * business_relevance`.

8. **Organic/paid overlap.** Cross-reference rankings with paid keyword lists to
   flag keywords where strong organic rank makes paid bids unnecessary.

9. **Report.** Write outputs and the HTML dashboard.

## Output Format

Artifacts:

| File | Contents |
|------|----------|
| `workspace/analysis/keyword_performance.json` | Ranking trends, movers, new/lost rankings |
| `workspace/analysis/content_performance.json` | Page/topic-cluster traffic and conversion |
| `workspace/analysis/seo_audit.json` | Technical issues, Core Web Vitals, structured-data gaps |
| `workspace/analysis/keyword_gap.json` | Competitive gap opportunities with scores |
| `workspace/reports/seo_dashboard.html` | Interactive SEO performance dashboard |

Report states: data span used, rolling-average window, decay threshold, and
whether gap analysis had full third-party coverage.

**Financial services mode:** never remove or obscure regulatory disclosures for
ranking; monitor AI-search citations of fund performance for SEC Marketing Rule
accuracy; content targeting investment keywords must clear advertising rules
before publication; flag regulated terms in gap analysis. Content drafted from
these recommendations routes through **compliance-review** before publishing.

**Completion status:**
- `DONE` — positions, content, and technical audit written.
- `DONE_WITH_CONCERNS` — e.g., partial gap coverage, short data span, missing
  content inventory.
- `BLOCKED` — Hard STOP tripped (bad/missing GSC data); state the fix.
- `NEEDS_CONTEXT` — competitive-data availability unresolved by the user.

## Anti-Patterns

- Reporting smoothed movers off a series too short for a 7-day rolling average.
- Calling every traffic dip "decay" without a statistical trend test.
- Presenting a partial-coverage keyword gap as complete when third-party data is
  missing.
- Recommending removal of compliance language to improve ranking.
- Bidding paid budget on keywords already ranking #1 organically.
- Letting the model estimate rolling averages, decay, or CWV instead of the
  scripts.
