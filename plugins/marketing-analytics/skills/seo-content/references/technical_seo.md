# Technical SEO Reference

Core Web Vitals thresholds, structured data requirements, and crawl
optimization guidance for technical SEO auditing.

## Core Web Vitals

### Metrics and Thresholds

| Metric | Full Name | Good | Needs Improvement | Poor |
| :----- | :-------- | :--- | :----------------- | :--- |
| LCP | Largest Contentful Paint | <= 2.5s | 2.5s - 4.0s | > 4.0s |
| INP | Interaction to Next Paint | <= 200ms | 200ms - 500ms | > 500ms |
| CLS | Cumulative Layout Shift | <= 0.1 | 0.1 - 0.25 | > 0.25 |

### Measurement Sources

- **Field data (CrUX):** Chrome User Experience Report provides real-user
  data aggregated over 28 days at the origin and URL level. Accessed via
  CrUX API or BigQuery.
- **Lab data (Lighthouse):** Synthetic measurement via Lighthouse or
  PageSpeed Insights API. Useful for debugging but does not reflect real-user
  conditions.
- **PageSpeed Insights API:** Combines field (CrUX) and lab (Lighthouse)
  data in a single response. Preferred for automated auditing.

### PageSpeed Insights API

**Endpoint:** `GET https://www.googleapis.com/pagespeedonline/v5/runPagespeedtest`

| Parameter | Description |
| :-------- | :---------- |
| `url` | Page URL to analyze |
| `strategy` | `mobile` or `desktop` |
| `category` | `performance`, `accessibility`, `best-practices`, `seo` |
| `key` | API key (required for production usage) |

**Rate Limit:** 25,000 queries per day with API key; 400 per 100 seconds.

### Optimization Priorities

1. **LCP:** Optimize server response time, preload critical resources,
   compress images (WebP/AVIF), implement CDN.
2. **INP:** Reduce JavaScript execution time, break long tasks, defer
   non-critical scripts, optimize event handlers.
3. **CLS:** Set explicit width/height on images and embeds, avoid inserting
   content above existing content, use CSS containment.

## Structured Data Requirements

### Supported Schema Types

| Schema Type | Use Case | Required Properties |
| :---------- | :------- | :------------------ |
| `Article` | Blog posts, news articles | `headline`, `image`, `datePublished`, `author` |
| `FAQPage` | FAQ sections | `mainEntity` array with `Question` and `acceptedAnswer` |
| `HowTo` | Step-by-step guides | `name`, `step` array with `HowToStep` |
| `Product` | Product pages | `name`, `image`, `offers` (with `price`, `priceCurrency`) |
| `Organization` | About/company pages | `name`, `url`, `logo`, `contactPoint` |
| `BreadcrumbList` | Site navigation | `itemListElement` array with `ListItem` |
| `LocalBusiness` | Location pages | `name`, `address`, `telephone`, `openingHours` |
| `FinancialProduct` | Financial services | `name`, `description`, `provider`, `feesAndCommissionsSpecification` |

### Implementation Format

Use JSON-LD embedded in the `<head>` section. Example:

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "image": "https://example.com/image.jpg",
  "datePublished": "2025-01-15",
  "dateModified": "2025-03-01",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Company Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  }
}
```

### Validation

- Use Google Rich Results Test to validate structured data.
- Check for errors and warnings in GSC Enhancement reports.
- Ensure required properties are present for each schema type.
- Verify that structured data matches visible page content (no hidden or
  misleading markup).

## Crawl Optimization

### Robots.txt Best Practices

- Allow crawling of all important content pages and resources (CSS, JS,
  images).
- Block crawling of duplicate content, internal search results, and admin
  pages.
- Reference XML sitemap location: `Sitemap: https://example.com/sitemap.xml`.
- Do not block resources needed to render the page (CSS, JS) as this
  prevents proper indexing.

### XML Sitemap Requirements

- Include all canonical, indexable URLs.
- Exclude noindex pages, redirected URLs, and error pages.
- Keep individual sitemap files under 50,000 URLs and 50 MB uncompressed.
- Use sitemap index files for sites with multiple sitemaps.
- Update `<lastmod>` timestamps only when content genuinely changes.

### Common Crawl Issues

| Issue | Detection Method | Impact |
| :---- | :--------------- | :----- |
| Redirect chains (3+ hops) | Crawl log analysis | Wasted crawl budget, lost link equity |
| Orphaned pages | Cross-reference sitemap with internal link graph | Pages unreachable by crawlers |
| Soft 404s | Response code + content analysis | Index bloat with low-quality pages |
| Duplicate content | Canonical tag audit | Diluted ranking signals |
| Broken internal links | Crawl error reports | Poor user experience, wasted crawl budget |
| Slow server responses (TTFB > 800ms) | Server timing headers | Reduced crawl rate |

### Redirect Rules

- Use 301 (permanent) redirects for URL changes and content consolidation.
- Use 302 (temporary) redirects only for genuinely temporary situations.
- Limit redirect chains to a single hop where possible.
- Update internal links to point directly to final URLs.

## Mobile Optimization

Google uses mobile-first indexing. Ensure:

- Responsive design or dynamic serving with proper `Vary: User-Agent` header.
- Mobile viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Touch targets at least 48x48 CSS pixels with adequate spacing.
- No horizontal scrolling at any standard mobile viewport width.
- Font sizes at least 16px for body text.

## Indexing Controls

| Directive | Implementation | Purpose |
| :-------- | :------------- | :------ |
| `noindex` | Meta tag or X-Robots-Tag header | Prevent indexing of specific pages |
| `canonical` | `<link rel="canonical">` | Specify preferred URL for duplicate content |
| `nofollow` | Meta tag or link attribute | Prevent passing link equity |
| `hreflang` | `<link rel="alternate" hreflang="x">` | Specify language/region targeting |

## Audit Checklist

The `scripts/seo_audit.py` script checks the following:

1. Core Web Vitals for all template page types (homepage, category, article,
   product).
2. Structured data presence and validity on applicable pages.
3. Robots.txt accessibility and correctness.
4. XML sitemap validity, freshness, and coverage.
5. Canonical tag consistency across the site.
6. Mobile usability issues flagged by GSC.
7. HTTPS implementation and mixed content warnings.
8. Internal link structure and orphaned page detection.
