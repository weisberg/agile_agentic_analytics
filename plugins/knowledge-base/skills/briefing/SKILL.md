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

## Output Format

- KB BRIEFING
- Context, changes, risks, decisions, preparation, sources.

## Anti-Patterns

- Dumping search results.
- Leaving out what the user should do next.
