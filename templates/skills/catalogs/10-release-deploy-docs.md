# Release, Deployment, and Documentation Components

Release pipelines, test failure ownership, version queues, changelog voice, deployment discovery, rollback gates, and documentation sync.

Components: 81-87.

Source: distilled from the gstack `SKILL.md` corpus. Each component includes a context paragraph, reusable description, and compact sample.

## **81. Release Pipeline Component**

**Reusable purpose:** Turn "ship it" into a verified sequence rather than a vibe.

**Context:** Use this when the user asks to ship, prepare a PR, or move a branch toward release. It turns shipping into a sequence of branch checks, review readiness, tests, plan completion, docs, versioning, commits, push, PR update, and metrics rather than a single optimistic action.

**Reusable phases:**

```text
1. Refuse to ship from base branch.
2. Read review readiness dashboard.
3. Merge or rebase latest base as configured.
4. Run tests/build/typecheck/lint as available.
5. Audit plan completion and scope drift.
6. Run pre-landing review.
7. Update docs, VERSION, CHANGELOG, and TODOs.
8. Create bisectable commits.
9. Push branch.
10. Create or update PR/MR.
11. Dispatch release documentation sync.
12. Record metrics for retro.
```

**Use this for:** PR creation, release branches, deploy prep.

**Sample:**

```text
Release sequence:
1. Confirm branch is not main.
2. Read review readiness dashboard.
3. Merge latest main.
4. Run tests, typecheck, lint, build.
5. Audit plan completion and scope drift.
6. Run pre-landing review.
7. Update docs and changelog.
8. Commit cleanly.
9. Push branch.
10. Open or update PR.
```

------

## **82. Test Failure Ownership Triage Component**

**Reusable purpose:** Decide whether failures belong to the current change before fixing them.

**Context:** Use this when tests fail during QA, CI, or release preparation. It helps the skill classify failures as caused by the current change, pre-existing, environmental, or unknown, so it fixes owned regressions without silently broadening scope to unrelated failures.

**Reusable classification:**

```text
caused_by_this_change:
  fix before ship

pre_existing:
  report and do not silently broaden scope

environmental:
  retry once, then document evidence

unknown:
  investigate enough to classify
```

**Use this for:** Ship, QA, CI repair, release gates.

**Sample:**

```text
Failure: ImportCsvTest#test_old_fixture_format.
Classification: pre_existing.
Evidence: fails on main at commit def5678.
Action: report in ship notes, do not broaden this branch unless user asks.

Failure: ImportDiagnosticsTest#test_unknown_error.
Classification: caused_by_this_change.
Action: fix before ship.
```

------

## **83. Version Queue Component**

**Reusable purpose:** Coordinate version bumps across parallel worktrees.

**Context:** Use this in repositories where multiple worktrees, agents, or branches may claim package versions concurrently. It prevents version collisions by checking current versions, sibling worktrees, changelog entries, and the next safe bump slot before release commits.

**Reusable checks:**

```text
- Claimed versions.
- Collision candidates.
- Sibling worktrees.
- Next safe bump slot.
- Existing changelog entries.
```

**Use this for:** Multi-agent release work, packages with manual versioning.

**Sample:**

```text
Version queue:
- Current package version: 1.8.3.
- Claimed by sibling worktree: 1.8.4.
- Safe next patch: 1.8.5.
- Changelog section exists for 1.8.4; do not reuse.
- Recommendation: claim 1.8.5 before release commit.
```

------

## **84. Changelog Voice Component**

**Reusable purpose:** Keep release notes factual and user-centered.

**Context:** Use this whenever a skill writes release notes or changelog entries. It keeps language factual, user-centered, and non-destructive, preserving existing entries while translating implementation work into value users or stakeholders can understand.

**Reusable rules:**

```text
- Lead with user-visible value.
- Keep internal implementation details out unless users need them.
- Never clobber existing entries.
- Preserve unreleased vs released sections.
- Do not bump VERSION silently.
```

**Use this for:** `document-release`, `ship`, package releases.

**Sample:**

```markdown
## Unreleased

### Added

- Added import failure diagnostics so admins can see why rows failed and what to
  fix next.

### Fixed

- Prevented expired import sources from causing retry crashes.
```

------

## **85. Deployment Discovery Component**

**Reusable purpose:** Infer how a project deploys and persist the result.

**Context:** Use this when a project needs deploy configuration before release automation can be trusted. It detects platforms, deploy scripts, health checks, and production URLs, then persists non-secret guidance so future ship and deploy skills know how the system reaches production.

**Reusable detection targets:**

```text
- Fly.io
- Render
- Vercel
- Netlify
- Heroku
- Railway
- GitHub Actions
- custom deploy scripts
- health check URLs
- production URL candidates
```

**Reusable output:** A deployment guidance block in project instructions, excluding secrets.

**Use this for:** One-time deploy setup, land-and-deploy workflows, canary setup.

**Sample:**

```text
Deployment discovery:
- Found vercel.json: frontend deploys on Vercel.
- Found .github/workflows/deploy.yml: backend deploys after main CI passes.
- Health check: /healthz.
- Production URL candidate: https://app.example.com.

Persist non-secret guidance to CLAUDE.md.
```

------

## **86. Deploy Polling and Rollback Gate Component**

**Reusable purpose:** Monitor merge, CI, deploy, and production health with explicit rollback choices.

**Context:** Use this for merge-and-deploy workflows where CI, deploy status, staging, production checks, or rollback decisions need active monitoring. It polls progress, verifies changed surfaces, selects canary depth from risk, and stops for explicit rollback or investigation choices on failure.

**Reusable flow:**

```text
1. Dry-run readiness.
2. Merge via queue or direct strategy.
3. Poll CI with progress updates.
4. Detect auto-deploy or trigger deploy.
5. Verify staging if available.
6. Run canary depth selected from diff risk.
7. On failure, offer investigate, retry, rollback, or stop.
8. Write deploy report with timings and verdict.
```

**Use this for:** Production release skills.

**Sample:**

```text
Deploy monitor:
1. Merge queued PR.
2. Poll CI every 30 seconds.
3. Detect deploy workflow run ID.
4. Verify /healthz and changed routes.
5. Run canary for 10 minutes.
6. On failure, ask:
   A) rollback (recommended for user-facing outage)
   B) investigate in place
   C) continue monitoring
```

------

## **87. Documentation Diff Sync Component**

**Reusable purpose:** Keep docs aligned with code changes without overwriting authored narrative.

**Context:** Use this after code changes affect docs, README content, API descriptions, changelogs, or PR bodies. It lets the skill auto-update factual drift, stop for narrative rewrites, preserve authored changelog entries, and keep documentation consistent with what actually shipped.

**Reusable behavior:**

```text
- Audit diff against docs.
- Auto-update factual drift.
- Stop for narrative, positioning, or risky docs.
- Check cross-doc consistency.
- Update PR/MR body idempotently.
- Clean completed TODOs with evidence.
```

**Use this for:** Release docs, README/API docs, changelog, generated docs.

**Sample:**

```text
Docs sync:
- Diff adds import failure categories.
- README has old "imports either succeed or fail" wording.
- Auto-update factual API docs.
- Ask before rewriting onboarding narrative.
- Preserve existing CHANGELOG entries.
- Update PR body with docs summary.
```
