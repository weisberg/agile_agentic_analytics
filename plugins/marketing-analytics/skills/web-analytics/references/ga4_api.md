# GA4 Data API Reference

Dimensions, metrics, and filter syntax for the Google Analytics 4 Data API v1.

## Common Dimensions

| API Name | UI Name | Description |
| :------- | :------ | :---------- |
| `date` | Date | Event date in YYYYMMDD format |
| `sessionSource` | Session source | Traffic source (e.g., google, facebook) |
| `sessionMedium` | Session medium | Traffic medium (e.g., organic, cpc, email) |
| `sessionCampaignName` | Session campaign | Campaign name from UTM parameter |
| `sessionDefaultChannelGroup` | Default channel group | Auto-classified channel (Organic Search, Paid Search, etc.) |
| `pagePath` | Page path | URL path of the page |
| `pageTitle` | Page title | HTML title of the page |
| `landingPage` | Landing page | First page in the session |
| `deviceCategory` | Device category | desktop, mobile, or tablet |
| `country` | Country | User country based on IP geolocation |
| `region` | Region | User region/state |
| `city` | City | User city |
| `browser` | Browser | Browser name (Chrome, Safari, etc.) |
| `operatingSystem` | Operating system | OS name (Windows, iOS, Android, etc.) |
| `eventName` | Event name | GA4 event name (page_view, purchase, etc.) |
| `contentGroup` | Content group | Custom content grouping |
| `firstUserSource` | First user source | Source that first acquired the user |
| `firstUserMedium` | First user medium | Medium that first acquired the user |
| `unifiedScreenName` | Screen name | App screen or web page title |

## Common Metrics

| API Name | UI Name | Description |
| :------- | :------ | :---------- |
| `sessions` | Sessions | Count of sessions |
| `totalUsers` | Total users | Count of distinct users |
| `newUsers` | New users | Count of first-time users |
| `activeUsers` | Active users | Count of users with engaged sessions |
| `screenPageViews` | Views | Total page/screen views |
| `screenPageViewsPerSession` | Views per session | Average pages viewed per session |
| `averageSessionDuration` | Avg. session duration | Mean session length in seconds |
| `bounceRate` | Bounce rate | Fraction of sessions with no engagement |
| `engagementRate` | Engagement rate | Fraction of engaged sessions (1 - bounceRate) |
| `engagedSessions` | Engaged sessions | Sessions lasting > 10s, or with conversion/2+ views |
| `conversions` | Conversions | Count of conversion events |
| `eventCount` | Event count | Total events fired |
| `ecommercePurchases` | Purchases | Count of purchase events |
| `purchaseRevenue` | Purchase revenue | Total revenue from purchases |
| `userEngagementDuration` | User engagement | Total foreground engagement time in seconds |
| `sessionsPerUser` | Sessions per user | Average sessions per user |
| `crashFreeUsersRate` | Crash-free users rate | Fraction of users without crashes |

## Filter Syntax

GA4 Data API filters use a nested JSON structure. Filters are applied inside
the `dimensionFilter` or `metricFilter` field of the request body.

### String Filter

```json
{
  "filter": {
    "fieldName": "sessionSource",
    "stringFilter": {
      "matchType": "EXACT",
      "value": "google",
      "caseSensitive": false
    }
  }
}
```

**Match types:** `EXACT`, `BEGINS_WITH`, `ENDS_WITH`, `CONTAINS`,
`FULL_REGEXP`, `PARTIAL_REGEXP`.

### In-List Filter

```json
{
  "filter": {
    "fieldName": "deviceCategory",
    "inListFilter": {
      "values": ["mobile", "tablet"],
      "caseSensitive": false
    }
  }
}
```

### Numeric Filter

```json
{
  "filter": {
    "fieldName": "sessions",
    "numericFilter": {
      "operation": "GREATER_THAN",
      "value": { "int64Value": "100" }
    }
  }
}
```

**Operations:** `EQUAL`, `LESS_THAN`, `LESS_THAN_OR_EQUAL`, `GREATER_THAN`,
`GREATER_THAN_OR_EQUAL`.

### Between Filter

```json
{
  "filter": {
    "fieldName": "sessions",
    "betweenFilter": {
      "fromValue": { "int64Value": "10" },
      "toValue": { "int64Value": "100" }
    }
  }
}
```

### Combining Filters

Use `andGroup` or `orGroup` to compose filters:

```json
{
  "andGroup": {
    "expressions": [
      {
        "filter": {
          "fieldName": "sessionSource",
          "stringFilter": { "matchType": "EXACT", "value": "google" }
        }
      },
      {
        "filter": {
          "fieldName": "deviceCategory",
          "stringFilter": { "matchType": "EXACT", "value": "mobile" }
        }
      }
    ]
  }
}
```

Use `notExpression` to negate:

```json
{
  "notExpression": {
    "filter": {
      "fieldName": "country",
      "stringFilter": { "matchType": "EXACT", "value": "(not set)" }
    }
  }
}
```

## Date Ranges

Specify one or more date ranges in the request body:

```json
{
  "dateRanges": [
    { "startDate": "2025-01-01", "endDate": "2025-01-31" },
    { "startDate": "2024-01-01", "endDate": "2024-01-31", "name": "yoy_comparison" }
  ]
}
```

Special date values: `today`, `yesterday`, `NdaysAgo` (e.g., `30daysAgo`).

## Order-By Clauses

```json
{
  "orderBys": [
    {
      "metric": { "metricName": "sessions" },
      "desc": true
    }
  ]
}
```

Dimension ordering uses `"dimension": { "dimensionName": "date", "orderType": "ALPHANUMERIC" }`.

## Pagination

- `limit`: Maximum rows to return (default 10000, max 250000).
- `offset`: Row offset for pagination.

## Rate Limits

- Core reporting: 10 requests per second per property.
- Batch requests: Group up to 5 report requests in a single batch call.
- Quota tokens: Each request consumes tokens based on complexity; monitor via
  `propertyQuota` in the response.

## UTM Parameter Mapping

| UTM Parameter | GA4 Dimension |
| :------------ | :------------ |
| `utm_source` | `sessionSource` |
| `utm_medium` | `sessionMedium` |
| `utm_campaign` | `sessionCampaignName` |
| `utm_term` | `sessionManualAdContent` |
| `utm_content` | `sessionManualAdContent` |
