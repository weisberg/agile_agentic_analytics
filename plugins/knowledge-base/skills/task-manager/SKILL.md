---
name: task-manager
version: 0.2.0
description: >-
  Manage tasks, commitments, waiting states, and follow-ups backed by KB pages and meeting/action-item sources. Trigger on 'KB tasks', 'extract action items', 'what do I owe / what am I waiting on', 'track this commitment'. For proactively prepping a briefing document use briefing; for extracting a whole meeting into pages use meeting-ingestion.
triggers:
  - "kb tasks"
  - "extract action items"
  - "what do i owe"
  - "what am i waiting on"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
disable-model-invocation: false
mutating: true
---

# Task Manager

## Contract

- Tasks have a source, owner, status, due/review date, and a back-link to their origin.
- Completed and waiting tasks stay auditable instead of disappearing.
- Mutating skill: task writes are allowed only when source, owner/status, and originating page or message are recorded.

## Intake And Modes

- Treat `$ARGUMENTS` as the task source, owner/status filter, date window, or desired task view.
- Quick mode: extract or answer a narrow "what do I owe / wait on" question.
- Standard mode: update task pages/sections from one meeting, message, or project.
- Deep mode: reconcile tasks across meetings/projects, waiting states, and stale follow-ups.
- Use `ask-user` when owner, due date, or commitment wording is ambiguous enough to change accountability.

## Evidence Requirements

- Inspect source meeting/message/project pages and existing task records before creating duplicates.
- Preserve the source link/back-link and keep completed/waiting status auditable.

## Workflow

- Extract tasks from meetings, messages, voice notes, and project pages.
- Normalize status: open, waiting, scheduled, done, dropped.
- Write task pages or task sections with citations and back-links.
- Generate next-action views for briefings.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" query`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" graph-audit`


## Output Format

- TASK UPDATE
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Created, updated, completed, waiting, blocked, and source links.
- Artifact path: updated task pages/sections and source page back-links.

## Anti-Patterns

- Creating tasks without source context.
- Silently dropping ambiguous commitments.
