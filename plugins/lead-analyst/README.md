# Lead Analyst Plugin

Senior analyst workflows for turning messy business and data questions into
well-planned, decision-ready analysis. The plugin is deliberately skeptical: it
frames the decision first, audits the evidence, separates descriptive patterns
from causal claims, and makes the recommendation useful to a real team.

## Installation

```bash
/plugin install lead-analyst@agile-agentic-analytics
```

## Components

| Component | Description |
|-----------|-------------|
| `/lead-analyst:analysis-planning` | Plan analytical work before execution: decision, metrics, evidence, data-quality gates, candidate methods, and handoff artifact. |
| `/lead-analyst:analysis-brief` | Lead an analysis from question framing through evidence, data-quality checks, interpretation, and recommendation. |
| `/lead-analyst:analysis-review` | Review an existing analysis, dashboard, notebook, report, or KPI claim for validity and decision risk. |
| `lead-analyst` agent | Reusable senior analyst subagent for independent analytical judgment, data-quality audit, and decision-ready synthesis. |
| `analysis-planner` agent | Planning-focused analyst subagent for analysis design, validity threats, metric precision, and plan review. |

## Operating Stance

- Decision first: every analysis starts with the decision or action it should inform.
- Evidence over polish: attractive charts do not outrank source data, metric definitions, and reproducible calculations.
- Causal humility: the plugin labels descriptive, correlational, experimental, and causal claims separately.
- Executive usefulness: outputs say what changed, why it matters, how confident we are, and what to do next.

## Local Testing

```bash
claude --plugin-dir ./plugins/lead-analyst
```

Reload after edits with `/reload-plugins`. Validate with `claude plugin validate`
or the repository plugin-health audit.
