# seo-content — Authoring Notes

Builder-facing guidance evicted from `SKILL.md`. Consult when editing scripts,
references, or data contracts; do not paste back into `SKILL.md`.

## Development guidelines

1. Search Console API has a 25,000-row-per-request limit — paginate for
   high-volume sites (`scripts/extract_gsc.py`).
2. Keyword position changes use a 7-day rolling average to smooth daily
   fluctuation and reduce false-positive movers.
3. GEO/AI-search tracking is emerging; design the module to be extensible as
   provider APIs appear.
4. Content-decay threshold configurable; default 20% traffic decline over 90 days.
   Use a statistical trend test (e.g., Mann-Kendall) to separate decline from
   noise.
5. Competitive gap analysis needs third-party API access (Semrush, Ahrefs); handle
   missing data gracefully with clear messaging.
6. Technical SEO checks use Lighthouse or PageSpeed Insights for Core Web Vitals;
   cache results to avoid redundant API calls.
7. All deterministic computation (rolling averages, trend tests, decay detection)
   runs in Python scripts, not LLM estimation.

## Acceptance criteria

- GSC extraction paginates and retrieves the complete dataset for 50K+ query
  sites.
- Keyword-mover detection identifies 95%+ of keywords with position change > 5.
- Content-decay detection flags statistically significant declines (not noise).
- Competitive keyword gap matches a manual Semrush/Ahrefs audit.

## Cross-skill integration detail

- **paid-media** — shares keyword intelligence for organic/paid overlap; stop
  bidding where you rank #1 organically.
- **competitive-intel** — keyword-gap data feeds competitive positioning.
- **web-analytics** — provides traffic/behavioral data validating SEO
  improvements.
- **reporting** — organic trends, keyword movement, and technical health feed
  dashboards.
