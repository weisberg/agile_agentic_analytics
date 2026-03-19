# Marketing Analytics Plugin

15 interconnected marketing analytics skills for Claude Code. Covers the full marketing analytics lifecycle from data extraction through attribution, experimentation, and compliance review.

## Installation

```
/plugin install marketing-analytics@agile-agentic-analytics
```

## Skills

### P0 — Foundational

| Skill | Command | Description |
|-------|---------|-------------|
| Attribution Analysis | `/marketing-analytics:attribution-analysis` | Bayesian MMM, multi-touch attribution, budget optimization |
| Experimentation | `/marketing-analytics:experimentation` | A/B testing, CUPED, sequential testing, Bayesian analysis |
| Paid Media | `/marketing-analytics:paid-media` | Cross-platform ad performance, anomaly detection, creative fatigue |
| Reporting | `/marketing-analytics:reporting` | Executive dashboards, cross-skill synthesis, insight generation |
| Compliance Review | `/marketing-analytics:compliance-review` | SEC/FINRA/FCA content screening (financial services) |

### P1 — Strategic/Tactical

| Skill | Command | Description |
|-------|---------|-------------|
| CLV Modeling | `/marketing-analytics:clv-modeling` | BG/NBD, Gamma-Gamma, Bayesian CLV with confidence intervals |
| Audience Segmentation | `/marketing-analytics:audience-segmentation` | RFM scoring, K-Means/DBSCAN clustering, cohort retention |
| Funnel Analysis | `/marketing-analytics:funnel-analysis` | Multi-step funnels, bottleneck identification, revenue impact |
| Email Analytics | `/marketing-analytics:email-analytics` | Deliverability, engagement (post-iOS 15), send-time optimization |
| Web Analytics | `/marketing-analytics:web-analytics` | GA4 extraction, behavioral patterns, predictive audiences |
| SEO & Content | `/marketing-analytics:seo-content` | Search Console, keyword tracking, AI search optimization (GEO) |

### P2 — Supporting

| Skill | Command | Description |
|-------|---------|-------------|
| CRM Lead Scoring | `/marketing-analytics:crm-lead-scoring` | Predictive scoring, pipeline velocity, win/loss analysis |
| Social Analytics | `/marketing-analytics:social-analytics` | Cross-platform social, sentiment analysis, share of voice |
| Competitive Intel | `/marketing-analytics:competitive-intel` | Keyword gap, traffic estimation, ad creative monitoring |
| VoC Analytics | `/marketing-analytics:voc-analytics` | NPS/CSAT/CES, theme extraction, satisfaction-behavior correlation |

## Architecture

Skills communicate through three mechanisms:

1. **Shared Data Contracts** — Canonical schemas in `shared/schemas/data_contracts.md`
2. **Filesystem State** — Structured workspace directories (`workspace/raw/`, `workspace/processed/`, `workspace/analysis/`, `workspace/reports/`, `workspace/compliance/`)
3. **Description-Driven Composition** — Each skill's trigger description names prerequisites and downstream consumers

## Financial Services Mode

When the workspace is tagged as financial services, all content-generating skills automatically route through `compliance-review` before distribution. The compliance skill checks against SEC Marketing Rule 206(4)-1, FINRA Rule 2210, and FCA financial promotions requirements.

## License

MIT
