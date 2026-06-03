---
name: briefing
version: 0.1.0
description: >-
  Create daily, meeting, project, or entity briefings from KB context with risks, decisions, open loops, and source links.
triggers:
  - "kb briefing"
  - "daily briefing"
  - "meeting prep"
  - "brief me on"
tools:
  - search
  - get_page
  - vaultli
mutating: false
writes_pages: false

disable-model-invocation: false
---

# Briefing

## Contract

- Briefings are concise, sourced, and action-oriented.
- Upcoming meetings and open loops are connected to relevant people, companies, and projects.
- Unknowns and stale context are flagged.

## Workflow

- Identify briefing scope and time horizon.
- Retrieve related pages, timelines, tasks, and recent sources.
- Summarize what matters, what changed, decisions needed, and risks.
- Include follow-up questions and stale-context warnings.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py query`
- `python3 plugins/knowledge-base/scripts/kb_ops.py dashboard`


## Output Format

- KB BRIEFING
- Context, changes, risks, decisions, preparation, sources.

## Anti-Patterns

- Dumping search results.
- Leaving out what the user should do next.
