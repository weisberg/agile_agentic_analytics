# GBrain/GStack Learnings For Plugin Manager

Use this reference when extending `plugin-manager` skills. It records the
source patterns behind the plugin-manager workflows without copying upstream
implementation-specific preambles.

## GBrain Patterns

### skillpack-check

- Health checks should return structured JSON that an agent or CI job can act on.
- Reports need a human summary, machine-readable findings, and remediation
  commands.
- Exit codes matter: `0` healthy, `1` action needed, `2` unable to determine.
- A health wrapper should compose lower-level checks rather than hiding them.

### skillpack-harvest

- Upstream import is editorial work, not just file copy.
- Always record source path, upstream commit, adaptation notes, privacy/path
  scrub, included/skipped files, and next review cadence.
- Preserve YAML frontmatter when requested; otherwise document every intentional
  frontmatter change.
- Dry-run and privacy lint should precede real writes.

### skillify and testing

- A durable skill has frontmatter, a contract, a stepwise process, output
  expectations, tests, routing examples, and clear validation.
- Cross-model or second-opinion review is useful before tests freeze behavior,
  but receipt absence should be visible rather than silently ignored.

## GStack Patterns

### health

- Health should produce a composite view, not a pile of logs.
- Include weighted checks, remediation hints, and trend-ready JSON.
- Wrap existing repo tools where possible instead of inventing parallel checks.

### ship and document-release

- Release work should detect base branch, inspect diff, run validation, update
  docs, bump versions intentionally, and only then commit/push.
- Documentation sync is part of the release, not cleanup for later.
- One-way operations such as push, merge, tag, and publish require explicit user
  approval.

### context-save and context-restore

- Long operations need resumable context: branch, modified files, decisions,
  commands run, validation state, blockers, and remaining work.
- Checkpoints must avoid secrets and raw private content.
- Prefer append-only, timestamped state over mutable notes.

### devex-review and QA

- Developer experience should be tested from a fresh-user perspective.
- Measure concrete steps: install, load plugin, run CLI helper, execute one
  validation command, and read the expected first success message.
- Confusing paths and missing prerequisites are product bugs.

