---
name: cron-scheduler
version: 0.1.0
description: >-
  Design recurring KB jobs with quiet hours, staggered schedules, idempotent prompts, health checks, and explicit user-visible outputs.
triggers:
  - "schedule kb job"
  - "cron kb"
  - "recurring kb task"
  - "run this periodically"
tools:
  - read
  - write
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Cron Scheduler

## Contract

- Scheduled jobs are idempotent, scoped, and quiet unless there is meaningful output.
- Jobs include failure behavior, health checks, and privacy boundaries.

## Workflow

- Define job purpose, cadence, timezone, quiet hours, and max runtime.
- Choose heartbeat vs detached cron based on whether thread context is needed.
- Write a self-contained prompt with expected output.
- Add health and checkpoint behavior for long jobs.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py validate-schedule`


## Output Format

- KB SCHEDULE
- Job name, cadence, prompt, quiet hours, failure behavior.

## Anti-Patterns

- Scheduling vague jobs that spam the user.
- Letting jobs write without source or privacy rules.
