# KB Automation And Checkpoints

Reference for scheduling and long-running KB work. Recurring-job design (cron
cadence, quiet hours, idempotent prompts) and resumable checkpointing were
formerly the `cron-scheduler` and `context-checkpoint` skills; both now live
here. The runtime home for orchestrating and checkpointing long jobs is the
`background-jobs` skill. Connector polling contracts are in
`connector-ingestion.md`.

## Job Envelope

```yaml
name: weekly-kb-health
cadence: weekly
timezone: America/New_York
quiet_hours: "21:00-08:00"
max_runtime_minutes: 30
idempotency_key: weekly-kb-health:{iso-week}
prompt: "Run KB health and summarize only failures or new warnings."
writes: false
checkpoint: .kb/checkpoints/weekly-kb-health.md
```

## Long Job Rules

- Sample before bulk.
- Batch writes and validate between batches.
- Checkpoint decisions, completed ids, remaining ids, validation, and blockers.
- Do not store secrets, raw transcripts, or long diffs in checkpoints.
- Stop on repeated failures and ask before changing strategy.

