---
name: briefing
version: 0.2.0
description: >-
  Assemble a proactive briefing from KB context — a daily digest, meeting prep, or a project/entity brief — surfacing risks, decisions needed, open loops, changed state, and source links. Trigger on 'brief me on X', 'daily briefing', 'meeting prep', 'prep me for tomorrow's meeting', 'what should I know before'. This pushes a prepared briefing document; to pull the answer to one specific question use query; for a saved, timestamped analytical report with a source manifest use reports.
triggers:
  - "brief me on"
  - "daily briefing"
  - "meeting prep"
  - "prep for tomorrows meeting"
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
disable-model-invocation: false
mutating: false
---

# Briefing

## Contract

- Briefings are concise, sourced, and action-oriented — never a dump of search results.
- Upcoming meetings and open loops are connected to the relevant people, companies, and projects.
- Unknowns and stale context are flagged with what the user should do next.
- Read-only by default: do not write a briefing artifact unless the user asks to save it or the workflow routes to `reports`.

## Intake And Modes

- Treat `$ARGUMENTS` as the subject plus optional audience, date window, meeting/event, and source scope.
- Quick mode: answer "what should I know" from a narrow entity/project slice.
- Standard mode: produce a meeting or daily prep brief with risks, decisions, open loops, and sources.
- Deep mode: compare multiple projects/entities over a wider date window and call out stale or missing context.
- Use `ask-user` when the requested briefing mixes personal/team/org scopes without a clear audience.

## Evidence Requirements

- Query the KB first, then hydrate pages that drive claims; metadata alone is not enough.
- Check tasks, recent timeline entries, related people/company pages, and freshness dates before stating priorities.

## Workflow

- Identify the briefing scope and time horizon (day, meeting, project, entity).
- Retrieve related pages, timelines, tasks, and recent sources with `query`.
- Summarize what matters, what changed, decisions needed, and risks.
- Include follow-up questions and stale-context warnings.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" query`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" dashboard`


## Output Format

- KB BRIEFING
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Context, changes, risks, decisions, preparation, sources.
- Artifact path: inline unless saved through `reports` as `reports/<YYYYMMDD>-<slug>.md`.

## Anti-Patterns

- Dumping search results instead of a briefing.
- Leaving out what the user should do next.
