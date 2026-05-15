# Safety, Utility, Setup, and Artifact Components

Destructive-command preflights, edit boundaries, guard mode, pair-agent access, model benchmarks, PDFs, inline upgrades, setup wizards, and artifact paths.

Components: 93-101.

Source: distilled from the gstack `SKILL.md` corpus. Each component includes a context paragraph, reusable description, and compact sample.

## **93. Destructive Command Preflight Component**

**Reusable purpose:** Catch dangerous shell commands before they run.

**Context:** Use this in any environment where the agent can run shell commands and might encounter destructive operations. It blocks or questions high-risk deletes, resets, force pushes, SQL destruction, Kubernetes deletes, and Docker cleanup while allowing safe targeted cleanup.

**Protected patterns:**

```text
- rm -rf broad paths
- git reset --hard
- git checkout/restore mass changes
- force push
- destructive SQL
- kubectl delete
- docker prune / volume deletion
- cloud resource deletion
```

**Allowed examples:**

```text
- removing known build/cache directories
- deleting temp files under explicit temp paths
- non-destructive git status/log/diff
```

**Use this for:** Safety skills, shared hook libraries, repo-level agent guardrails.

**Sample:**

```text
Blocked command:
rm -rf .

Reason: recursive delete at repository root.

Options:
A) Cancel (recommended)
B) Delete only explicit build/cache path
C) Proceed only after user confirms exact path and consequence
```

------

## **94. Edit Boundary Freeze Component**

**Reusable purpose:** Restrict file edits to a specific path while investigating or delegating.

**Context:** Use this when the user wants investigation or edits constrained to a specific part of the repo. It narrows Edit and Write operations to an absolute path boundary, reducing accidental blast radius while still making clear that shell commands need separate protection.

**Reusable behavior:**

```text
1. Resolve absolute boundary path.
2. Store normalized trailing slash.
3. Block Edit/Write outside boundary.
4. Explain that Bash can still mutate files unless separately guarded.
5. Allow explicit unfreeze.
```

**Use this for:** Bug investigations, pair-agent work, high-risk repos, generated-code scopes.

**Sample:**

```text
Freeze boundary:
/Users/alex/project/app/services/imports/

Rules:
- Edit and Write are allowed only under that directory.
- Paths are normalized with trailing slash.
- `/app/services/imports-old` is not inside the boundary.
- Bash mutations still require separate destructive-command protection.
```

------

## **95. Guard Mode Composition Component**

**Reusable purpose:** Bundle multiple safety mechanisms into one user-invocable mode.

**Context:** Use this when users need a quick safety posture rather than separate guardrail commands. It combines destructive-command preflight and edit-boundary freeze into a named mode, making it easy to turn on broad caution before risky debugging or delegated work.

**Reusable composition:**

```text
guard = careful destructive-command preflight + freeze edit boundary
unfreeze = clear boundary state while leaving hooks installed
```

**Use this for:** Safety profiles that users can toggle quickly.

**Sample:**

```text
Guard mode enabled:
- careful: destructive Bash commands require confirmation.
- freeze: edits are limited to app/services/imports/.

To relax edit boundary, run unfreeze.
To keep destructive-command protection, leave careful installed.
```

------

## **96. Scoped Pair-Agent Access Component**

**Reusable purpose:** Let another AI agent use browser state without handing over broad machine access.

**Context:** Use this when another agent needs temporary browser access for authenticated QA, research, or debugging. It scopes access by token, expiry, domain, and permission level so collaboration does not require sharing broad machine or account credentials.

**Reusable controls:**

```text
- one-time setup key
- expiring session token
- read/write/admin access split
- local config write for same-machine agents
- ngrok or equivalent tunnel for remote agents
- revocation instructions
```

**Use this for:** Multi-agent browser testing, authenticated research, remote debugging.

**Sample:**

```json
{
  "agent": "codex",
  "browser_access": "read_write",
  "setup_key": "one-time-redacted",
  "expires_at": "2026-05-10T18:00:00Z",
  "scope": ["http://localhost:3000", "https://staging.example.com"],
  "admin": false
}
```

------

## **97. Cross-Model Benchmark Component**

**Reusable purpose:** Compare models or agents on the same prompt with cost and latency awareness.

**Context:** Use this when evaluating prompts, skills, or model choices across providers. It standardizes auth checks, cost confirmation, comparable runs, latency/tokens/cost capture, optional judge scoring, and saved baselines so model selection is evidence-based.

**Reusable flow:**

```text
1. Dry-run provider auth.
2. Estimate cost.
3. Ask before paid or large runs.
4. Run each model with the same prompt and constraints.
5. Record latency, tokens, cost, and output.
6. Optionally run a judge with explicit cost approval.
7. Save JSON baseline for future comparison.
```

**Use this for:** Prompt optimization, model routing, skill quality evaluation.

**Sample:**

```yaml
benchmark:
  prompt: prompts/plan-review.md
  models:
    - claude
    - gpt-codex
    - gemini
  dry_run_auth: true
  require_cost_confirmation: true
  metrics:
    - latency_ms
    - input_tokens
    - output_tokens
    - estimated_cost_usd
    - judge_score
  save_baseline: .gstack/model-benchmarks/plan-review.json
```

------

## **98. Browser-Rendered PDF Component**

**Reusable purpose:** Produce PDFs through the same rendering engine users will see in a browser.

**Context:** Use this when a skill needs to produce a polished PDF from markdown or HTML, such as reports, release packets, or printable dashboards. Browser rendering preserves CSS, layout, print backgrounds, margins, page numbers, and table-of-contents behavior better than naive text conversion.

**Reusable options:**

```text
- print backgrounds
- page size and margins
- page numbers
- table of contents
- tagged PDF when supported
- outline/bookmarks when supported
- HTML or markdown source path
```

**Use this for:** Reports, design docs, release packets, printable dashboards.

**Sample:**

```yaml
pdf:
  source: docs/release-report.md
  output: dist/release-report.pdf
  render_engine: browser
  options:
    print_background: true
    page_size: Letter
    margin: "0.5in"
    page_numbers: true
    table_of_contents: true
```

------

## **99. Inline Upgrade and Resume Component**

**Reusable purpose:** Keep long-lived skill ecosystems current without losing the user's original task.

**Context:** Use this in plugin or skill ecosystems that evolve over time and may be invoked while an update is available. It lets the skill offer upgrade, snooze, skip, or disable choices, then resume the original task after updating instead of abandoning the user's workflow.

**Reusable flow:**

```text
1. Check installed version.
2. Detect global vs vendored install.
3. Show what changed.
4. Auto-upgrade only if configured.
5. Otherwise ask: upgrade now, snooze, skip once, disable checks.
6. Resume originally invoked skill after upgrade.
```

**Use this for:** Skill bundles, CLI-backed workflows, generated preambles.

**Sample:**

```text
Upgrade check:
- Installed: 1.27.0
- Available: 1.28.0
- Install type: global

Options:
A) Upgrade now, then resume `/ship` (recommended)
B) Skip once and continue
C) Snooze for 7 days
D) Disable upgrade checks
```

------

## **100. Setup Wizard With Secret Safety Component**

**Reusable purpose:** Configure external services without leaking credentials.

**Context:** Use this for setup flows that configure external services, credentials, deploy targets, browser auth, or semantic memory. It detects existing config, offers modes, handles secrets through safe channels, writes only non-secret guidance, and ends with a doctor-style readiness result.

**Reusable rules:**

```text
- Detect existing configuration first.
- Offer local, hosted, manual, and remote modes when meaningful.
- Put secrets in env vars or secret stores, not command argv or committed files.
- Redact tokens in logs and final output.
- Write durable non-secret guidance to project instructions.
- End with doctor output: green/yellow/red.
```

**Patterns copied from:** `setup-gbrain`, `setup-deploy`, `setup-browser-cookies`, `pair-agent`.

**Sample:**

```text
Setup wizard:
1. Detect existing config.
2. Offer local, hosted, manual, and remote modes.
3. Ask for secrets through env vars or secret store only.
4. Redact tokens in command output.
5. Write non-secret setup notes to CLAUDE.md.
6. End with doctor result:
   GREEN: configured and verified
   YELLOW: configured but optional feature missing
   RED: not usable yet
```

------

## **101. Artifact Path Taxonomy Component**

**Reusable purpose:** Decide where outputs should live.

**Context:** Use this whenever a skill writes reports, screenshots, checkpoints, designs, learnings, logs, or other generated output. It decides what belongs in repo-local workflow evidence versus user-scoped durable memory, keeping shared artifacts visible and personal state out of project files.

**Reusable taxonomy:**

```text
repo-local workflow reports:
  .gstack/qa-reports/
  .gstack/benchmark-reports/
  .gstack/canary-reports/
  .gstack/deploy-reports/
  .gstack/security-reports/

user-scoped durable project memory:
  ~/.gstack/projects/<slug>/checkpoints/
  ~/.gstack/projects/<slug>/designs/
  ~/.gstack/projects/<slug>/ceo-plans/
  ~/.gstack/projects/<slug>/retros/
  ~/.gstack/projects/<slug>/learnings.jsonl
  ~/.gstack/projects/<slug>/timeline.jsonl
  ~/.gstack/projects/<slug>/health-history.jsonl
```

**Rules:**

```text
- Reports tied to repo workflow can live in the repo.
- Taste, memory, checkpoints, and cross-session artifacts belong in user scope.
- Project instructions store guidance, not machine state.
- Secrets never go into docs.
```

**Sample:**

```text
Repo-local report:
.gstack/qa-reports/import-diagnostics/2026-05-09-report.md

User-scoped memory:
~/.gstack/projects/example-app/checkpoints/2026-05-09-import-diagnostics.md
~/.gstack/projects/example-app/designs/import-diagnostics-board.md
~/.gstack/projects/example-app/learnings.jsonl

Rule: put workflow evidence in the repo when teammates should see it. Put taste,
memory, checkpoints, and personal cross-session context under user scope.
```
