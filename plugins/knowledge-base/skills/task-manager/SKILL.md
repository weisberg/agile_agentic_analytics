---
name: task-manager
version: 0.1.0
description: >-
  Manage tasks, commitments, waiting states, and follow-ups backed by KB pages and meeting/action-item sources.
triggers:
  - "kb tasks"
  - "task manager"
  - "extract action items"
  - "what do i owe"
tools:
  - search
  - get_page
  - put_page
  - vaultli
mutating: true
writes_pages: true
---

# Task Manager

## Contract

- Tasks have source, owner, status, due date or review date, and backlink to origin.
- Completed and waiting tasks stay auditable instead of disappearing.

## Workflow

- Extract tasks from meetings, messages, voice notes, and project pages.
- Normalize status: open, waiting, scheduled, done, dropped.
- Write task pages or task sections with citations.
- Generate next-action views for briefings.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py query`
- `python3 plugins/knowledge-base/scripts/kb_ops.py graph-audit`


## Output Format

- TASK UPDATE
- Created, updated, completed, waiting, blocked, and source links.

## Anti-Patterns

- Creating tasks without source context.
- Silently dropping ambiguous commitments.
