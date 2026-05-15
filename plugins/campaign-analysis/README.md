# Campaign Analysis

Campaign performance analysis toolkit for measurement, diagnostics, optimization, and stakeholder reporting.

## Status

Skeleton. Skills, agents, references, and scripts can be added under the standard plugin directories:

| Directory | Purpose |
| --- | --- |
| `skills/<name>/SKILL.md` | User-facing campaign analysis workflows |
| `agents/*.md` | Specialized campaign analysis subagents |
| `references/` | Methodology notes, metric definitions, templates, and data contracts |
| `scripts/` | Reusable campaign analysis utilities |

## Installation

```text
/plugin install campaign-analysis@agile-agentic-analytics
```

## Local Testing

```bash
claude --plugin-dir ./plugins/campaign-analysis
```

Reload after edits with `/reload-plugins`. Validate with `claude plugin validate`.
