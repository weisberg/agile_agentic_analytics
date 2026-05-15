# Memory, Semantic Search, and Retrospective Components

Context checkpoints, learning registries, semantic-memory trust, semantic-search guidance, and retrospective analytics.

Components: 88-92.

Source: distilled from the gstack `SKILL.md` corpus. Each component includes a context paragraph, reusable description, and compact sample.

## **88. Context Checkpoint Component**

**Reusable purpose:** Save enough session state for another agent or future session to resume.

**Context:** Use this when a session needs to be paused, handed off, or recovered later. A checkpoint captures branch, commit, modified files, decisions, commands, tests, blockers, and remaining work so another agent or future session can resume without guessing.

**Reusable contents:**

```text
- branch and commit
- git status
- modified files
- decisions made
- commands run
- tests passed/failed
- remaining work
- blockers
- notes for next agent
```

**Rules:**

```text
- Use append-only checkpoint files.
- Sanitize filenames.
- Prefer timestamp ordering over mtime.
- Do not modify product code.
```

**Patterns copied from:** `context-save`, `context-restore`, continuous checkpoint mode.

**Sample:**

```markdown
# Checkpoint: import diagnostics

Branch: feature/import-diagnostics
Commit: abc1234
Modified files: 6

## Decisions

- Feature flag rollout accepted.
- CSV export deferred.

## Remaining

- Add expired source file regression.
- Run mobile browser QA.

## Blockers

- Need product answer on retention copy.
```

------

## **89. Learning Registry Component**

**Reusable purpose:** Store durable project lessons with confidence and source.

**Context:** Use this for durable lessons that should influence future work in the same repo or plugin. It records project quirks, pitfalls, preferences, architecture decisions, and tooling behavior with confidence and source, then supports pruning and contradiction checks as the code evolves.

**Reusable record:**

```json
{
  "type": "pattern|pitfall|preference|decision|tooling",
  "key": "<short-key>",
  "insight": "<durable lesson>",
  "confidence": 1,
  "source": "<where learned>",
  "files": []
}
```

**Reusable maintenance:**

```text
- Search learnings before repeating work.
- Prune stale learnings when referenced files disappear.
- Detect contradictory learnings.
- Export selected learnings into project docs.
```

**Use this for:** Long-lived repos, teams, agent memory systems.

**Sample:**

```json
{
  "type": "pitfall",
  "key": "imports-source-file-expiry",
  "insight": "Import retry must handle expired source_file attachments; otherwise retry crashes after retention.",
  "confidence": 5,
  "source": "investigate import retry 500",
  "files": ["app/jobs/import_retry_job.rb", "app/models/import_run.rb"]
}
```

------

## **90. Semantic Memory Trust Policy Component**

**Reusable purpose:** Configure semantic search without accidentally indexing or writing sensitive material.

**Context:** Use this when enabling semantic memory or code indexing in a repo with privacy, trust, or client-boundary concerns. It makes indexing and memory writes explicit per repository, keeps secrets out of logs and argv, and prevents one worktree's memory from being mistaken for another's.

**Reusable trust modes:**

```text
read_write:
  Index and allow memory writes.

read_only:
  Search/index, but do not write project learnings.

deny:
  Do not index this repo.

skip_once:
  Do not configure now; ask later if appropriate.
```

**Rules:**

```text
- Secrets go through env vars, not argv or logs.
- Per-repo trust beats global optimism.
- Worktree pins avoid confusing one repo's memory with another.
- Capability checks update guidance dynamically.
```

**Patterns copied from:** `setup-gbrain`, `sync-gbrain`.

**Sample:**

```yaml
semantic_memory:
  repo: example/app
  trust: read_only
  index_code: true
  write_learnings: false
  reason: "Client repo permits code search but not persistent agent-authored memory."
```

------

## **91. Semantic Search Guidance Component**

**Reusable purpose:** Teach the agent when to use semantic code memory instead of grep.

**Context:** Use this when a repo has semantic search available and the skill needs to decide between concept search and exact string search. It tells agents to use semantic tools for behavioral questions and grep for known identifiers, keeping code navigation both fast and appropriate.

**Reusable guidance:**

```text
Use semantic search for:
- "where is this behavior implemented?"
- "what calls this?"
- "what code owns this concept?"
- "have we solved something like this before?"

Use grep for:
- exact strings
- identifiers already known
- generated files
- quick local confirmation
```

**Use this for:** Codebase navigation, investigation, review, onboarding.

**Sample:**

```text
Use semantic search:
- "where is import retry implemented?"
- "what calls FailureReasonMapper?"
- "where do we document import retention?"

Use grep:
- exact constant `IMPORT_DIAGNOSTICS`
- route path `/admin/imports`
- string "source expired"
```

------

## **92. Retrospective Analytics Component**

**Reusable purpose:** Turn recent work into a useful engineering retro.

**Context:** Use this for periodic summaries of engineering or agent work across commits, sessions, PRs, tests, hotspots, and skill usage. It helps teams or solo builders learn from recent work, spot recurring blockers, and decide what process or code improvements should come next.

**Reusable signals:**

```text
- commits and authors
- hotspots
- test coverage changes
- PRs/MRs
- sessions and skills used
- shipped vs abandoned work
- blockers
- local context notes
```

**Modes:**

```text
daily
weekly
compare
global
```

**Use this for:** Team operating reviews, agent productivity tracking, sprint retros.

**Sample:**

```text
Weekly retro signals:
- 14 commits by you, 6 by teammates.
- Hotspot: import pipeline touched in 9 commits.
- Tests added: 12.
- Escaped issue: retry crash found during QA.
- Skill usage: office-hours, plan-eng-review, qa, ship.
- Recommendation: schedule import pipeline cleanup after release.
```
