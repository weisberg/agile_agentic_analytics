# Google Search Console API Reference

API integration patterns for extracting search performance data from Google
Search Console.

## Authentication

Use OAuth 2.0 service account credentials with the
`https://www.googleapis.com/auth/webmasters.readonly` scope. Store credentials
in the workspace secrets vault, never in code or configuration files.

## Search Analytics Query API

**Endpoint:** `POST https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query`

### Request Parameters

| Parameter | Type | Description |
| :-------- | :--- | :---------- |
| `startDate` | string | Start date in `YYYY-MM-DD` format (inclusive) |
| `endDate` | string | End date in `YYYY-MM-DD` format (inclusive) |
| `dimensions` | array | Grouping dimensions: `query`, `page`, `country`, `device`, `date`, `searchAppearance` |
| `type` | string | Search type: `web`, `image`, `video`, `news`, `discover`, `googleNews` |
| `rowLimit` | integer | Max rows per response (default 1000, max 25000) |
| `startRow` | integer | Zero-based offset for pagination |
| `dataState` | string | `final` (default) or `all` (includes fresh/partial data) |
| `dimensionFilterGroups` | array | Filters applied to dimensions |
| `aggregationType` | string | `auto` (default), `byPage`, or `byProperty` |

### Dimension Combinations

Common dimension groupings for analysis:

- **Keyword tracking:** `["query", "date"]` — daily position and CTR per query.
- **Page performance:** `["page", "date"]` — daily traffic per URL.
- **Full detail:** `["query", "page", "date"]` — query-page pairs by date.
  Warning: this combination produces the largest result sets and is most likely
  to require pagination.
- **Device split:** `["query", "device", "date"]` — mobile vs. desktop ranking
  differences.
- **Country split:** `["query", "country"]` — geographic ranking variation.

### Metrics Returned

Each row includes:

| Metric | Type | Description |
| :----- | :--- | :---------- |
| `clicks` | float | Number of clicks from search results |
| `impressions` | float | Number of times a result appeared in search |
| `ctr` | float | Click-through rate (clicks / impressions) |
| `position` | float | Average ranking position (1-based) |

## Filter Syntax

### Dimension Filter Groups

```json
{
  "dimensionFilterGroups": [
    {
      "groupType": "and",
      "filters": [
        {
          "dimension": "query",
          "operator": "contains",
          "expression": "investment fund"
        },
        {
          "dimension": "country",
          "operator": "equals",
          "expression": "usa"
        }
      ]
    }
  ]
}
```

### Filter Operators

| Operator | Description |
| :------- | :---------- |
| `equals` | Exact match |
| `contains` | Substring match |
| `notContains` | Exclude substring |
| `includingRegex` | Regex match (RE2 syntax) |
| `excludingRegex` | Regex exclusion |

### Dimension Values

- **country:** ISO 3166-1 alpha-3 codes (e.g., `usa`, `gbr`, `deu`).
- **device:** `DESKTOP`, `MOBILE`, `TABLET`.
- **searchAppearance:** `RICH_RESULT`, `AMP_BLUE_LINK`, `VIDEO`, etc.

## Pagination Strategy

The API returns a maximum of 25,000 rows per request. For high-volume sites:

1. Set `rowLimit` to 25000.
2. Set `startRow` to 0 for the first request.
3. If the response contains exactly 25,000 rows, increment `startRow` by
   25,000 and repeat.
4. Continue until the response contains fewer than 25,000 rows.
5. Concatenate all response rows into the final dataset.

### Date Range Chunking

For very large sites, even pagination may be slow. An alternative approach:

1. Split the date range into weekly chunks.
2. Run paginated queries for each week.
3. Merge results across weeks.
4. This approach reduces per-request result sizes and improves reliability.

## Rate Limits

- Default quota: 1,200 queries per minute per project.
- Implement exponential backoff on HTTP 429 responses.
- Cache results locally to avoid redundant API calls for the same date range.

## Data Freshness

- GSC data has a 2-3 day delay. The most recent complete data is typically
  from 3 days ago.
- Use `dataState: "all"` to include preliminary data from the last 1-2 days,
  but note that these numbers may change.
- For trend analysis, always use `dataState: "final"` to ensure consistency.

## URL Inspection API

For individual URL status checks:

**Endpoint:** `POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect`

Returns indexing status, crawl information, mobile usability, and rich result
status for a single URL. Rate-limited to 2,000 requests per day per property.
