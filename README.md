# Agile Agentic Analytics

A Claude Code plugin marketplace for agile agentic analytics.

## Installation

Add this marketplace to Claude Code:

```
/plugin marketplace add weisberg/agile_agentic_analytics
```

Then browse and install plugins:

```
/plugin
```

Or install a specific plugin directly:

```
/plugin install <plugin-name>@agile-agentic-analytics
```

## Available Plugins

### A/B Testing

**Install:** `/plugin install ab-testing@agile-agentic-analytics`

Design, analyze, and review A/B tests with statistical rigor.

| Component | Description |
|-----------|-------------|
| `/ab-testing:design-experiment` | Create structured experiment designs with hypothesis, metrics, and guardrails |
| `/ab-testing:sample-size` | Calculate required sample size and experiment duration |
| `/ab-testing:analyze-results` | Statistical analysis with SRM checks, effect sizes, and reproducible code |
| `/ab-testing:experiment-report` | Generate stakeholder-ready reports (technical or executive) |
| `/ab-testing:review-experiment` | Code review for assignment bugs, logging gaps, and bucketing leaks |
| `statistician` agent | Rigorous statistical analysis specialist |
| `experiment-auditor` agent | Systematic experiment lifecycle auditor |

### Marketing Analytics

**Install:** `/plugin install marketing-analytics@agile-agentic-analytics`

15 interconnected marketing analytics skills covering the full lifecycle from data extraction through compliance review.

**P0 — Foundational**

| Skill | Description |
|-------|-------------|
| `/marketing-analytics:attribution-analysis` | Bayesian MMM, multi-touch attribution, budget optimization |
| `/marketing-analytics:experimentation` | A/B testing, CUPED variance reduction, sequential testing |
| `/marketing-analytics:paid-media` | Cross-platform ad performance, anomaly detection, creative fatigue |
| `/marketing-analytics:reporting` | Executive dashboards, cross-skill synthesis, insight generation |
| `/marketing-analytics:compliance-review` | SEC/FINRA/FCA content screening for financial services |

**P1 — Strategic/Tactical**

| Skill | Description |
|-------|-------------|
| `/marketing-analytics:clv-modeling` | BG/NBD, Gamma-Gamma, Bayesian CLV with confidence intervals |
| `/marketing-analytics:audience-segmentation` | RFM scoring, K-Means/DBSCAN clustering, cohort retention |
| `/marketing-analytics:funnel-analysis` | Multi-step funnels, bottleneck identification, revenue impact |
| `/marketing-analytics:email-analytics` | Deliverability, engagement (post-iOS 15), send-time optimization |
| `/marketing-analytics:web-analytics` | GA4 extraction, behavioral patterns, predictive audiences |
| `/marketing-analytics:seo-content` | Search Console, keyword tracking, AI search optimization (GEO) |

**P2 — Supporting**

| Skill | Description |
|-------|-------------|
| `/marketing-analytics:crm-lead-scoring` | Predictive scoring, pipeline velocity, win/loss analysis |
| `/marketing-analytics:social-analytics` | Cross-platform social, sentiment analysis, share of voice |
| `/marketing-analytics:competitive-intel` | Keyword gap, ad creative monitoring, strategic synthesis |
| `/marketing-analytics:voc-analytics` | NPS/CSAT/CES, theme extraction, satisfaction-behavior correlation |

## Creating a Plugin

Each plugin lives in its own directory under `plugins/`. The minimum structure is:

```
plugins/my-plugin/
├── .claude-plugin/
│   └── plugin.json        # Plugin manifest (required)
├── skills/                 # Custom slash commands
│   └── my-skill/
│       └── SKILL.md
├── agents/                 # Custom subagents
│   └── my-agent.md
├── hooks/                  # Event handlers
│   └── hooks.json
├── .mcp.json               # MCP server configs
├── .lsp.json               # LSP server configs
├── settings.json           # Supported Claude Code settings only
└── README.md
```

### plugin.json

```json
{
  "name": "my-plugin",
  "description": "What the plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  },
  "license": "MIT"
}
```

After creating your plugin directory, register it in `.claude-plugin/marketplace.json`:

```json
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin",
  "description": "What the plugin does"
}
```

## License

MIT
