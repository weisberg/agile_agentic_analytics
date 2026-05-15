# Advanced Skill Design Patterns from gstack

This document distills the advanced features, workflow mechanics, and writing style
choices from the `SKILL.md` files under:

`/Users/weisberg/Documents/Development/gh/gstack/`

The gstack skill set is best understood as a prompt-operated engineering system, not
as a loose collection of slash commands. Each skill defines a specialist role, an
execution protocol, evidence requirements, decision gates, memory hooks, artifact
paths, and a distinctive voice. The most advanced skills combine all of these into
an end-to-end operating loop: think, plan, build, review, test, ship, monitor, and
learn.

## Core Thesis

Advanced skills in gstack do four things at once:

1. They route intent into a named specialist role.
2. They gather evidence before deciding.
3. They force explicit user decisions at meaningful one-way or taste boundaries.
4. They leave durable artifacts so later skills and future sessions can compound.

The style is intentionally opinionated: direct, evidence-led, builder-to-builder,
and allergic to vague consultant prose. The workflows reward completeness when AI
makes marginal work cheap, but they still stop for scope, safety, taste, security,
and irreversible operations.

## Source Corpus

The scanned skill files cover these families:

| Family | Skills |
|---|---|
| Planning | `office-hours`, `plan-ceo-review`, `plan-eng-review`, `plan-design-review`, `plan-devex-review`, `autoplan`, `plan-tune` |
| Design | `design-consultation`, `design-shotgun`, `design-html`, `design-review` |
| Review and quality | `review`, `codex`, `cso`, `health`, `investigate` |
| Browser and QA | `browse`, `qa`, `qa-only`, `benchmark`, `canary`, `setup-browser-cookies`, `open-gstack-browser`, `pair-agent` |
| Release | `ship`, `land-and-deploy`, `setup-deploy`, `document-release`, `landing-report`, `gstack-upgrade` |
| Memory and learning | `context-save`, `context-restore`, `learn`, `setup-gbrain`, `sync-gbrain`, `retro` |
| Browser-skill automation | `scrape`, `skillify`, `browser-skills/hackernews-frontpage` |
| Safety | `careful`, `freeze`, `guard`, `unfreeze` |
| Output utilities | `make-pdf`, `benchmark-models` |
| OpenClaw native variants | `gstack-openclaw-office-hours`, `gstack-openclaw-ceo-review`, `gstack-openclaw-investigate`, `gstack-openclaw-retro` |

## Metadata Conventions

Most skills start with YAML frontmatter. The frontmatter is not decorative; it is
part routing contract, part capability declaration, and part safety boundary.

Common fields:

- `name`: canonical skill name.
- `version`: explicit skill version.
- `preamble-tier`: controls how much generated runtime scaffolding is included.
- `interactive: true`: marks skills that rely on decision gates and user choices.
- `description`: long-form routing description with proactive-use guidance.
- `triggers`: semantic trigger phrases for invocation.
- `allowed-tools`: capability allowlist.
- `benefits-from`: soft composition hint, such as planning skills benefiting from
  `office-hours`.
- `hooks`: PreToolUse guards for destructive commands or edit boundaries.
- `gbrain`: declarative context queries for project memory.
- Browser-skill-specific fields: `host`, `trusted`, `source`, `args`.

Advanced frontmatter style choices:

- Descriptions include "Use when..." and "Proactively suggest..." text.
- Some skills include voice-trigger aliases for speech-to-text mistakes.
- Tool lists are deliberately narrow. Read-only skills omit write tools.
- Safety skills register hooks directly in frontmatter instead of relying only on
  prose.
- Browser-skills declare domain trust, host binding, input arguments, and trigger
  phrases so the browser daemon can match intents quickly.

## Generated Preamble as Platform

The larger skills share a generated preamble. It turns every skill run into a
stateful, instrumented workflow.

Advanced preamble features:

- Update check: detects available gstack upgrades and routes to `gstack-upgrade`.
- Session tracking: creates active session markers under `~/.gstack/sessions`.
- Repo mode: detects solo vs collaborative ownership and changes proactive behavior.
- Proactive mode: lets the user opt into or out of automatic skill suggestions.
- Skill prefix mode: supports alternate `/gstack-*` names without changing disk paths.
- Writing style mode: supports default explanatory prose or terse mode.
- Question tuning: records user preferences for recurring decision questions.
- Telemetry gates: one-time opt-in, anonymous mode, or fully off.
- Context recovery: loads recent artifacts, timelines, review logs, and checkpoints.
- Artifacts sync: optionally syncs gstack artifacts through a private git-backed brain.
- GBrain hinting: tells the agent when to prefer semantic `gbrain` search over grep.
- Continuous checkpoint mode: optional WIP commits with `[gstack-context]` blocks.
- Completion protocol: forces `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or
  `NEEDS_CONTEXT`.
- Plan status footer: appends a `GSTACK REVIEW REPORT` to plan files in plan mode.

The preamble is a skill runtime. It handles upgrades, memory, sync, style,
telemetry, and plan-mode exceptions before the domain-specific workflow begins.

## AskUserQuestion Pattern

The most important interaction pattern is the structured decision brief.

Required elements:

- `D<N>` numbered decision title.
- Project, branch, or task grounding.
- ELI10 explanation in plain language.
- Stakes if the choice is wrong.
- Recommendation with a concrete reason.
- Completeness score when options differ in coverage.
- Explicit note when options differ in kind rather than coverage.
- Pros and cons for each option.
- Human-time and AI-agent-time effort estimates where relevant.
- Net tradeoff line.
- `(recommended)` label on the default option.

Style rules:

- Questions are tool calls, not prose.
- One issue usually equals one question.
- STOP points are real. The skill must not proceed until the user answers.
- Never silently auto-decide unless a recorded question-tuning preference allows it.
- If no AskUserQuestion tool exists, plan-mode workflows write decisions into the
  plan file and exit plan mode; outside plan mode they stop with a prose brief.
- Questions are framed around user outcomes, not implementation trivia.

This pattern makes interactive skills auditable. The user can see what is at stake,
why the agent recommends an option, and what completeness tradeoff they are accepting.

## Voice and Prose Style

The gstack voice is direct, concrete, and pragmatic.

Preferred style:

- Lead with the point.
- Name files, functions, commands, outputs, screenshots, scores, and real numbers.
- Tie technical choices to what users see, lose, wait for, or can now do.
- Say when something is broken.
- Prefer short sentences and active voice.
- Sound like a builder talking to a builder.
- Close decisions with user impact.

Avoid:

- Corporate, academic, PR, or generic optimistic prose.
- Throat-clearing and filler.
- Overused AI vocabulary such as "delve", "robust", "comprehensive",
  "nuanced", "multifaceted", "furthermore", "pivotal", and similar stock terms.
- Default design language such as "clean modern UI" without concrete decisions.
- Completion claims without evidence.

Writing style is also configurable. The default mode glosses jargon on first use
and explains stakes; terse mode removes that layer for power users.

## Completeness Principle

The recurring principle is "Boil the Lake": AI makes many complete versions cheap,
so the agent should prefer fully handled tests, edge cases, error paths, and docs
when the incremental cost is small.

The distinction:

- A lake is complete scope that is now cheap enough to do well.
- An ocean is a rewrite, migration, or multi-quarter expansion that should still be
  challenged.

Decision briefs use completeness scores:

- `10/10`: complete, edge cases covered.
- `7/10`: happy path or materially incomplete.
- `3/10`: shortcut or risky deferment.

This principle appears in planning reviews, shipping, test bootstrap, QA, design,
and release workflows.

## Search Before Building

Many skills include a "search before building" stance.

The framework:

- Layer 1: tried and true. Use established tools and built-ins when appropriate.
- Layer 2: current popular approaches. Scrutinize for hype and footguns.
- Layer 3: first-principles reasoning. Prize it when it contradicts convention for
  a specific reason.

When first-principles reasoning contradicts conventional wisdom, skills name the
insight as a "eureka" and log it for future sessions.

## Evidence-First Workflows

Advanced gstack skills are built around evidence collection.

Common evidence types:

- Git diff, commit log, file lists, status, and base branch detection.
- Browser screenshots, annotated snapshots, responsive captures, console errors,
  network failures, and performance timings.
- Test output, build output, eval output, and coverage deltas.
- Review logs and JSONL state.
- Before/after screenshots and before/after scores.
- Baseline manifests for benchmark, canary, QA, and design.
- Cross-model review output from Codex or subagents.
- Active verification of security findings through code tracing.

Hard rule repeated across skills:

Do not claim completion without fresh verification evidence.

## Planning Skill Stack

### `office-hours`

Acts as the top-of-funnel design doc generator. It asks what the user's goal is
and switches posture:

- Startup or intrapreneurship: YC-style product diagnostic.
- Hackathon, open source, research, learning, or fun: builder-mode collaborator.

Advanced choices:

- Separates demand evidence from interest.
- Pushes for specific humans, status quo workflows, narrow wedges, and actual user
  observation.
- Searches related prior design docs.
- Uses a privacy gate before external landscape search.
- Challenges premises before proposing solutions.
- Produces design docs, not code.

### `plan-ceo-review`

Founder-mode plan review. It has four explicit scope modes:

- Scope expansion: dream bigger and ask for opt-in expansions.
- Selective expansion: hold current scope while surfacing optional upgrades.
- Hold scope: make the existing plan rigorous.
- Scope reduction: cut to the minimum viable version.

Advanced choices:

- Requires a pre-review system audit.
- Reads office-hours design docs and handoff notes.
- Challenges premises, ambition, user value, and strategic coherence.
- Uses cognitive patterns from CEOs and product leaders as hidden review instincts.
- Logs review metadata and recommends next reviews.
- Can promote compelling plans into `docs/designs/`.

### `plan-eng-review`

Engineering-manager plan review. It locks architecture, data flow, tests,
failure modes, diagrams, and parallelization.

Advanced choices:

- Complexity gate at Step 0 if file or service count suggests overbuilding.
- Searches for built-ins and best practices before approving custom architecture.
- Requires architecture, code quality, test, and performance sections.
- Forces one AskUserQuestion per non-trivial issue.
- Requires test diagrams and failure mode mapping.
- Produces "NOT in scope", "What already exists", TODO updates, and parallel lanes.
- Uses confidence calibration for findings.

### `plan-design-review`

Design-plan review before implementation. It treats mockups as the plan for UI work.

Advanced choices:

- Generates visual mockups by default when the design binary is available.
- Saves design artifacts under `~/.gstack/projects/$SLUG/designs/`.
- Rates design completeness before and after each pass.
- Checks information architecture, states, journey, AI slop, design system,
  responsive behavior, and unresolved choices.
- Uses comparison boards for visual preference instead of inline text choices.
- Writes approved mockup paths into the plan.

### `plan-devex-review`

Developer-experience plan review. It focuses on Time to Hello World, developer
persona, friction, errors, docs, upgrades, and magical moments.

Advanced choices:

- Auto-detects developer product type: API, CLI, SDK, platform, docs, or skill.
- Starts with persona interrogation and a first-person empathy narrative.
- Benchmarks competitors and sets a TTHW target.
- Designs the "magical moment" before scoring.
- Scores eight DX dimensions and produces a checklist.
- Recommends live `devex-review` after implementation to compare plan vs reality.

### `autoplan`

Runs CEO, design, eng, and DX reviews as a sequential pipeline with auto-decisions.

Advanced choices:

- Reads full skill files from disk instead of duplicating their logic.
- Uses six decision principles to auto-decide routine choices.
- Separates auto-decisions from taste decisions and user challenges.
- Uses cross-model voices for plan critique.
- Writes a decision audit trail.
- Ends with a final approval gate containing plan summary, decisions, scores,
  cross-phase themes, and deferred TODOs.

### `plan-tune`

Lets the user tune how often recurring questions are asked.

Advanced choices:

- Records per-question preferences.
- Separates declared preferences from observed behavior.
- Supports `never-ask`, `always-ask`, and ask-only-for-one-way choices.
- Includes profile-poisoning defenses by only honoring user-originated `tune:`
  messages.

## Design System and Visual Taste

### Design Philosophy

The design skills share a strong visual stance:

- Empty states are features.
- Hierarchy is service to the user.
- Specificity beats vibes.
- Edge cases are user experiences.
- Responsive design is not simply stacking desktop content on mobile.
- Accessibility is not optional.
- Subtract before adding.
- Trust is earned at the pixel level.

### AI Slop Detection

The design-review skills explicitly blacklist patterns that look generated:

- Purple or blue-purple gradients as default.
- Three-column feature grids with icon circles.
- Centered-everything layouts.
- Uniform bubbly border radius.
- Decorative blobs, waves, and empty ornament.
- Generic hero copy.
- Cookie-cutter hero, features, testimonials, pricing, CTA rhythm.
- Default system fonts as the primary design choice.

### Landing Page vs App UI

Design-review classifies the target as:

- Marketing or landing page.
- App UI.
- Hybrid.

Landing pages need a first-screen composition, clear brand signal, visual anchor,
intentional motion, strong hierarchy, and no hero cards unless the card is the
interaction.

App UIs need calm density, utility language, predictable navigation, minimal chrome,
few colors, and cards only when the card is a genuine interaction unit.

### `design-consultation`

Creates a full `DESIGN.md` from product context, research, and taste decisions.

Advanced choices:

- Proposes, rather than presenting generic menus.
- Evaluates coherence across typography, color, layout, spacing, motion, and mood.
- Generates visual previews or AI mockups when the design binary is available.
- Extracts approved tokens into `DESIGN.md`.
- Updates `CLAUDE.md` so future visual work reads the design system.

### `design-shotgun`

Generates multiple visual design variants and uses a comparison board for feedback.

Advanced choices:

- Reads prior approved designs and persistent taste profiles.
- Applies taste decay so recent approvals matter more.
- Forces variants to differ in font, palette, and layout.
- Uses parallel subagents for image generation.
- Generates to `/tmp` first, then copies into `~/.gstack` to avoid sandbox issues.
- Uses board feedback files (`feedback.json`, `feedback-pending.json`) for structured
  choice, remix, and regeneration loops.
- Updates the user's taste profile after approvals and rejections.

### `design-html`

Turns plans or approved mockups into Pretext-native HTML or framework components.

Advanced choices:

- Routes design types to different Pretext APIs.
- Embeds or imports Pretext for dynamic text layout.
- Includes contenteditable text and MutationObserver relayout.
- Uses ResizeObserver, responsive breakpoints, semantic HTML, ARIA, reduced motion,
  dark mode, real content, and design tokens.
- Runs a live preview server.
- Verifies mobile, tablet, and desktop screenshots.
- Uses surgical edits during refinement to preserve user changes.

### `design-review`

Live-site design audit plus fix loop.

Advanced choices:

- Requires clean working tree.
- Uses rendered screenshots as evidence, not source-code speculation.
- Runs outside design voices with Codex and a Claude subagent.
- Uses litmus checks and hard rejection criteria.
- Fixes one issue per atomic commit.
- Prefers CSS-first changes.
- Generates target mockups for non-trivial visual fixes.
- Reverts any fix that regresses.
- Stops if design-fix risk gets too high or after a hard cap.

## Browser and QA System

### `browse`

The browser skill is a full headless or headed Chromium control surface.

Advanced features:

- Persistent daemon with cookies, tabs, and login state.
- `snapshot` command with interactive refs, compact mode, depth limits, diffs,
  annotations, cursor-interactive detection, and heatmaps.
- CSS inspector and live style mutation with undo.
- Local HTML rendering by file URL or setContent.
- Retina screenshots via deviceScaleFactor.
- Dialog, upload, storage, cookies, headers, and user agent controls.
- CDP allowlist for raw Chrome DevTools Protocol calls.
- Headed mode, proxy support, SOCKS5 auth bridge, anti-bot stealth, and Xvfb in
  Linux containers.
- User handoff for CAPTCHA, MFA, OAuth, and complex auth.
- Prompt-injection wrapping for untrusted page output.
- Domain-skill memory for per-site notes.
- Browser-skill runner with project, global, and bundled lookup tiers.

### `qa`

Full test, fix, verify workflow for web apps.

Advanced choices:

- Automatically enters diff-aware mode on feature branches without a URL.
- Maps changed files to affected routes and pages.
- Falls back to homepage plus top navigation when route inference is unclear.
- Requires clean working tree.
- Bootstraps a test framework if none exists.
- Tests in browser as a user, then fixes bugs and re-verifies.
- Writes regression tests for behavioral fixes.
- Uses one commit per fix.
- Reverts on regression.
- Computes a weighted health score.

### `qa-only`

Report-only variant of QA.

Advanced choices:

- Same exploration discipline as `qa`.
- Never reads source code or fixes bugs.
- Produces reports, screenshots, baselines, and health scores.
- Recommends `qa` when test infrastructure is absent and regression tests would help.

### `benchmark`

Web performance regression detector.

Advanced choices:

- Captures baselines for page timings, resource sizes, request counts, JS, and CSS.
- Compares current metrics against baseline.
- Uses thresholds for regressions and warnings.
- Reports slowest resources and budget status.
- Supports trend analysis across historical reports.

### `canary`

Post-deploy production monitor.

Advanced choices:

- Captures pre-deploy or baseline screenshots and metrics.
- Monitors pages every 60 seconds during a deploy window.
- Alerts on changes relative to baseline, not absolute noise.
- Requires consecutive failures before crying wolf.
- Offers investigate, continue, rollback, or dismiss options.

### `setup-browser-cookies`

Bridges real browser sessions into headless browse.

Advanced choices:

- Skips import when CDP mode already exposes real browser sessions.
- Opens an interactive cookie-domain picker.
- Supports direct domain import.
- Handles platform caveats such as macOS Keychain and Linux secret storage.

### `open-gstack-browser`

Launches the visible GStack Browser with extension side panel.

Advanced choices:

- Kills stale daemons and Chromium locks first.
- Uses headed Chromium with custom branding, side panel, and stealth patches.
- Guides the user through extension pinning and side-panel connection.
- Demonstrates live command feed with a Hacker News navigation.

### `pair-agent`

Gives another AI agent scoped access to the user's browser.

Advanced choices:

- Distinguishes local agent config writes from remote setup-key exchange.
- Uses one-time setup keys and 24-hour session tokens.
- Supports OpenClaw, Codex, Cursor, Claude, and generic HTTP clients.
- Uses ngrok for remote agents.
- Separates read/write access from admin access.

## Review and Security Workflows

### `review`

Pre-landing PR review.

Advanced choices:

- Detects platform and base branch.
- Checks scope drift before code review.
- Discovers and audits plan completion.
- Verifies cross-repo and external-state plan items honestly.
- Reads a checklist and full diff.
- Runs specialist subreviews and red-team review.
- Uses fix-first classification: auto-fix mechanical issues, ask on judgment calls.
- Deduplicates findings skipped in prior reviews.
- Handles Greptile comments with evidence-based reply templates.
- Runs always-on adversarial review through Claude subagent and Codex when available.
- Logs structured review results for `/ship`.

### `codex`

OpenAI Codex CLI wrapper for outside opinion.

Advanced choices:

- Supports review, challenge, and consult modes.
- Probes binary, auth, and known-bad CLI versions before expensive prompts.
- Uses portable state roots for plans and temp files.
- Adds a filesystem boundary instruction so Codex ignores Claude skill files.
- Wraps Codex calls with timeout and hang detection.
- Surfaces auth errors instead of dropping stderr.
- Estimates cost and reasoning effort.
- Supports session continuity in consult mode.

### `cso`

Chief Security Officer audit.

Advanced choices:

- Scans infrastructure, secrets, dependencies, CI/CD, LLM security, skill supply
  chain, OWASP Top 10, STRIDE, and data classification.
- Has daily mode with an 8/10 confidence gate and comprehensive mode with a lower
  inclusion threshold.
- Uses hard false-positive exclusions.
- Requires exploit scenarios.
- Actively verifies findings through safe code tracing.
- Uses independent verification tasks where possible.
- Tracks trend across security reports.
- Includes incident response playbooks for leaked secrets.
- Is read-only and always includes an audit disclaimer.

### `investigate`

Root-cause debugging.

Advanced choices:

- Iron law: no fixes without root cause investigation.
- Collects symptoms, traces code paths, checks recent changes, reproduces, and only
  then hypothesizes.
- Locks edit scope with freeze when possible.
- Tests hypotheses before writing fixes.
- Uses a three-strike rule: after three failed hypotheses, stop and reassess.
- Requires regression tests and fresh verification.
- Logs investigation learnings.

### `health`

Code quality dashboard.

Advanced choices:

- Detects or reads a configured health stack.
- Runs typecheck, lint, tests, dead-code tools, shellcheck, and optionally gbrain.
- Scores each category with weighted composite scoring.
- Redistributes weights for skipped tools.
- Persists JSONL trend history.
- Reports regressions and prioritized recommendations.
- Read-only by hard gate.

## Release and Deployment Workflows

### `ship`

End-to-end shipping workflow.

Advanced choices:

- Aborts on base branch.
- Shows review readiness dashboard.
- Checks distribution pipeline for new artifacts.
- Merges base before tests.
- Bootstraps a test framework when needed.
- Runs test failure ownership triage.
- Adds first real tests when bootstrapping.
- Runs coverage audit and plan completion audit.
- Verifies plan execution against diff and external deliverables.
- Runs scope drift detection and pre-landing review.
- Dispatches specialist review army and adversarial review.
- Handles Greptile review comments.
- Updates VERSION, CHANGELOG, and TODOS.
- Squashes continuous-checkpoint WIP commits safely.
- Creates bisectable commits.
- Requires fresh verification before push.
- Pushes, dispatches `document-release` in a fresh subagent, and creates or updates
  PR/MR body and title.
- Logs ship metrics for retros.

### `document-release`

Post-ship documentation sync.

Advanced choices:

- Audits docs against branch diff.
- Auto-updates factual docs.
- Stops for narrative or risky doc changes.
- Never clobbers CHANGELOG entries.
- Polishes CHANGELOG voice around user-visible value.
- Checks cross-doc consistency and discoverability.
- Cleans completed TODOs.
- Never bumps VERSION silently.
- Can update PR/MR body and title idempotently.

### `land-and-deploy`

Merge, deploy, verify, and optionally revert.

Advanced choices:

- Performs dry-run readiness checks.
- Explains stale reviews in plain English.
- Supports merge queues and direct merges.
- Detects CI auto-deploy and platform-specific deploy strategy.
- Offers staging-first verification when available.
- Polls CI and deploy workflows with progress updates.
- Uses diff scope to choose canary depth.
- Offers rollback at failure points.
- Writes a detailed deploy report with timings and verdict.

### `setup-deploy`

One-time deployment configuration.

Advanced choices:

- Detects Fly.io, Render, Vercel, Netlify, Heroku, Railway, GitHub Actions, and
  custom hooks.
- Infers production URLs and health checks.
- Persists deploy configuration to `CLAUDE.md`.
- Lets users reconfigure or edit fields later.

### `landing-report`

Read-only version queue dashboard.

Advanced choices:

- Queries the same version queue utility used by `ship`.
- Shows claimed versions, collisions, sibling worktrees, and next bump slots.
- Helps parallel Conductor workspaces avoid version collisions.

### `gstack-upgrade`

Upgrade workflow.

Advanced choices:

- Detects global vs vendored installs.
- Handles team-mode migration away from vendored copies.
- Shows what's new.
- Continues the originally invoked skill after inline upgrade.

## Memory, Learning, and Brain

### `context-save` and `context-restore`

Session handoff system.

Advanced choices:

- Saves git state, modified files, decisions, remaining work, notes, and duration.
- Writes append-only checkpoint files with sanitized filenames.
- Uses filename timestamp ordering instead of mtime.
- Restore searches across all branches by default for workspace handoffs.
- Does not modify code.

### `learn`

Learning management.

Advanced choices:

- Shows, searches, prunes, exports, stats, and manually adds learnings.
- Checks staleness by referenced file existence.
- Detects conflicting learnings.
- Exports markdown for `CLAUDE.md` or project docs.
- Uses confidence, type, source, and file references.

### `setup-gbrain`

Installs and configures persistent semantic memory.

Advanced choices:

- Supports local PGLite, Supabase existing URL, Supabase auto-provision, manual
  Supabase setup, remote HTTP MCP, engine switching, resume, and cleanup.
- Treats secrets carefully: env-var only, never argv or logs where possible.
- Registers Claude Code MCP at user scope.
- Sets per-repo trust policy: read-write, read-only, deny, or skip.
- Offers artifact sync through a private repo.
- Handles transcript ingest with explicit privacy and history caveats.
- Writes machine-aware configuration and capability-gated search guidance to
  `CLAUDE.md`.
- Ends with a green/yellow/red doctor block.

### `sync-gbrain`

Keeps code and artifacts current.

Advanced choices:

- Uses native gbrain code surfaces, not markdown import for code.
- Runs code, memory, and brain-sync stages.
- Uses lock files and atomic state writes.
- Performs code-index health check and offers full reindex when empty.
- Updates or removes `GBrain Search Guidance` based on actual capability.
- Explains cross-machine behavior and worktree-specific `.gbrain-source` pins.

### `retro`

Engineering retrospective.

Advanced choices:

- Analyzes commits, sessions, hotspots, PRs, test coverage, authors, and gstack
  skill usage.
- Uses local time windows with midnight alignment for day and week windows.
- Distinguishes "you" from teammates based on git config.
- Supports compare and global modes.
- Incorporates non-git context from `~/.gstack/retro-context.md`.

## Browser-Skill Automation

### `scrape`

Read-only web data extraction entrypoint.

Advanced choices:

- Fast match path: routes to existing browser-skills in about 200ms.
- Prototype path: drives `$B` primitives and returns JSON.
- Refuses mutating intents.
- Returns one JSON document without surrounding prose by default.
- Nudges exactly once to use `skillify` after successful prototype.

### `skillify`

Turns a successful prototype scrape into a permanent deterministic browser-skill.

Advanced choices:

- Provenance guard: only skillifies recent successful prototype `/scrape` output.
- Confirms name, trigger phrases, host, and tier.
- Writes a pure parser function plus daemon-driving `main`.
- Captures an HTML fixture.
- Writes fixture-replay tests with meaningful assertions.
- Copies canonical browse-client SDK into the skill.
- Stages in a temp directory, tests there, and only commits after test pass plus
  user approval.
- Uses atomic commit or discard semantics.
- Verifies post-commit output matches the prototype.

### `hackernews-frontpage`

Reference bundled browser-skill.

Advanced choices:

- Minimal stable example with host binding, trusted source, zero args, and triggers.
- Emits typed JSON.
- Uses stable HTML selectors and fixture tests.
- Demonstrates the expected SKILL.md, `script.ts`, `script.test.ts`, fixture, and
  SDK shape for future browser-skills.

## Safety Skills

### `careful`

Registers Bash preflight checks for destructive commands.

Protected patterns include recursive deletes, SQL destructive operations, force
push, hard reset, mass restore, `kubectl delete`, and destructive Docker cleanup.
It allows safe cache/build directory removal.

### `freeze`

Restricts Edit and Write tools to a user-selected directory.

Advanced choices:

- Resolves absolute path.
- Stores trailing slash to avoid prefix false positives such as `/src` matching
  `/src-old`.
- Blocks file edits outside boundary.
- Does not claim to be a full security boundary because Bash can still mutate files.

### `guard`

Composes `careful` and `freeze` into full safety mode.

### `unfreeze`

Clears the stored freeze boundary while leaving hooks installed but permissive.

## Output and Utility Skills

### `benchmark-models`

Cross-model benchmark for gstack prompts.

Advanced choices:

- Dry-runs provider auth before any paid run.
- Supports Claude, GPT via Codex, and Gemini.
- Optional LLM judge with explicit cost prompt.
- Compares latency, tokens, cost, and optional quality.
- Offers JSON baseline persistence for trend comparison.

### `make-pdf`

Converts markdown or HTML into publication-quality PDF through the browse PDF path.

Advanced choices:

- Uses browser rendering rather than naive markdown conversion.
- Leans on page layout options, print backgrounds, page numbers, tags, outline, and
  optional table of contents support from the browse PDF command.

## Artifact and State Conventions

gstack distinguishes project files from user artifacts.

Project-local outputs:

- `.gstack/qa-reports/`
- `.gstack/benchmark-reports/`
- `.gstack/canary-reports/`
- `.gstack/deploy-reports/`
- `.gstack/security-reports/`

User-scoped durable outputs:

- `~/.gstack/projects/$SLUG/checkpoints/`
- `~/.gstack/projects/$SLUG/designs/`
- `~/.gstack/projects/$SLUG/ceo-plans/`
- `~/.gstack/projects/$SLUG/retros/`
- `~/.gstack/projects/$SLUG/learnings.jsonl`
- `~/.gstack/projects/$SLUG/timeline.jsonl`
- `~/.gstack/projects/$SLUG/health-history.jsonl`

Rule of thumb:

- User taste, design explorations, checkpoints, and cross-session memory go under
  `~/.gstack/projects/$SLUG`.
- Reports that belong to the current repo workflow may go under `.gstack/`.
- `CLAUDE.md` stores durable project guidance, not transient machine state or secrets.
- Secrets never go into `CLAUDE.md`.

## Advanced Composition Patterns

### Review Chaining

Planning reviews recommend the next review based on findings and stale review logs:

- CEO changes can trigger fresh eng and design reviews.
- Eng review can recommend design review for UI scope.
- Design review can recommend eng review when interaction specs changed.
- DX review recommends eng review for API, CLI, error, or docs architecture effects.
- Ship reads all review logs and distinguishes current vs stale.

### Outside Voices

Several skills use independent models or subagents:

- `review`: Claude adversarial subagent plus Codex adversarial challenge.
- `plan-ceo-review` and `plan-eng-review`: optional outside voice for plan critique.
- `design-review`: Codex source audit plus Claude design consistency subagent.
- `autoplan`: dual voices and decision audit trail.
- `benchmark-models`: model performance comparison as a first-class workflow.

The style is to treat cross-model agreement as strong evidence, not as a replacement
for user judgment.

### Fix-First Loops

`review`, `qa`, and `design-review` all prefer action when safe:

- Auto-fix mechanical findings.
- Ask on ambiguous or risky findings.
- Commit atomic fixes.
- Re-verify.
- Revert if a fix regresses.

Read-only variants (`qa-only`, `cso`, `health`, `landing-report`) state their hard
gate clearly and do not mutate code.

### Baseline and Trend Systems

Many skills persist history:

- `benchmark`: performance baselines and trends.
- `canary`: visual and console baselines.
- `qa`: health score baseline and regression mode.
- `health`: composite score history.
- `cso`: security posture trend.
- `retro`: retrospective history and skill usage.
- `ship`: coverage and plan completion metrics.

This turns single runs into longitudinal signals.

## Skill-by-Skill Advanced Feature Map

| Skill | Advanced feature to copy |
|---|---|
| `autoplan` | Sequential multi-skill orchestration with auto-decision audit trail and final taste gate |
| `benchmark` | Baseline-vs-current metrics with thresholds, budgets, and trend reports |
| `benchmark-models` | Provider dry-run before spend, optional quality judge, saved JSON baselines |
| `browse` | Persistent browser daemon, rich snapshot refs, untrusted content boundaries, headed/proxy/handoff modes |
| `canary` | Post-deploy monitoring that alerts on changes from baseline and avoids one-off noise |
| `careful` | PreToolUse hook that asks before destructive Bash commands |
| `codex` | Cross-AI second opinion with auth probes, timeouts, and filesystem boundary prompts |
| `context-save` | Append-only checkpoint files with decisions and remaining work |
| `context-restore` | Cross-branch resume by canonical filename timestamp order |
| `cso` | Security audit with confidence gates, exploit scenarios, false-positive filtering, and trend tracking |
| `design-consultation` | Opinionated design-system creation with visual previews and coherence validation |
| `design-html` | Pretext-native HTML generation with live preview and responsive screenshot verification |
| `design-review` | Live visual audit plus CSS-first fix loop, atomic commits, and before/after screenshots |
| `design-shotgun` | Parallel mockup generation, comparison boards, persistent taste memory |
| `document-release` | Diff-aware doc audit, CHANGELOG clobber protection, PR body update |
| `freeze` | Directory-scoped edit boundary via hook state |
| `gstack-upgrade` | Inline upgrade flow that resumes the invoking skill |
| `guard` | Composition of destructive-command warnings and edit boundary |
| `health` | Weighted composite quality dashboard with historical trend |
| `investigate` | Root-cause-first debugging with scope lock and three-strike reassessment |
| `land-and-deploy` | Merge queue, CI, deploy, canary, staging, rollback, and deploy report in one workflow |
| `landing-report` | Read-only VERSION queue awareness for parallel worktrees |
| `learn` | Durable learning CRUD with staleness and contradiction checks |
| `make-pdf` | Browser-rendered PDF production path |
| `office-hours` | Goal-sensitive product interrogation that writes design docs instead of code |
| `open-gstack-browser` | Visible browser plus side panel and real-time command feed |
| `pair-agent` | Scoped browser sharing with setup keys, session tokens, local config, or ngrok |
| `plan-ceo-review` | Scope mode selection and CEO-level premise challenge |
| `plan-design-review` | Mockups by default, scorecards, approved mockup paths in plan |
| `plan-devex-review` | Persona, empathy narrative, TTHW benchmarking, magical moment design |
| `plan-eng-review` | Architecture, tests, failure modes, TODOs, and parallel lanes before implementation |
| `plan-tune` | Per-question preference tuning and auto-decision guardrails |
| `qa` | Browser QA with fix loop, regression tests, health score, and atomic commits |
| `qa-only` | Browser QA report-only mode with no code reading or fixes |
| `retro` | Commit, author, hotspot, test, and gstack-usage retrospective |
| `review` | Scope drift, plan completion, specialist review, fix-first, adversarial passes |
| `scrape` | Match-path browser-skill routing plus prototype-path JSON extraction |
| `setup-browser-cookies` | Real browser cookie import with CDP-mode shortcut |
| `setup-deploy` | Platform detection and persisted deploy config |
| `setup-gbrain` | Multi-path semantic memory setup with trust policy, artifact sync, MCP registration |
| `ship` | Full release pipeline from tests through PR creation with docs subagent |
| `skillify` | Atomic browser-skill synthesis from proven scrape with fixture tests |
| `sync-gbrain` | Capability-gated semantic search guidance and worktree-scoped code indexing |
| `unfreeze` | Clears edit boundary state without unregistering hooks |

## Authoring Guidance for New Advanced Skills

Use this checklist when creating new skills inspired by gstack.

### 1. Define the Role

Write the opening as a specialist identity:

- "You are a staff engineer who..."
- "You are a senior product designer who..."
- "You are a QA engineer and bug-fix engineer..."
- "You are a security officer..."

Then state the hard gate:

- Read-only.
- Plan-only.
- Fix allowed but only after verification.
- No implementation.
- No destructive actions.

### 2. Declare Routing Metadata

Include:

- Clear `description`.
- `triggers`.
- `allowed-tools`.
- `preamble-tier` if using the generated runtime.
- `interactive: true` if decisions are core.
- `hooks` if safety belongs in enforcement, not just prose.
- `gbrain` context queries when prior artifacts matter.

### 3. Add Preflight State

Before core work:

- Detect branch and base branch.
- Read project instructions.
- Gather git diff and logs.
- Detect relevant binaries.
- Check clean working tree when atomic commits matter.
- Check prior artifacts and learnings.
- Establish output directories.

### 4. Classify Mode

Parse user intent into explicit modes:

- Quick, standard, exhaustive.
- Read-only vs fix loop.
- Plan-driven vs mockup-driven vs freeform.
- Daily vs comprehensive.
- Local vs remote.
- Startup vs builder.

Do not let mode drift silently.

### 5. Gather Evidence

Never rely on assumptions when tools can inspect:

- Browser screenshots for UI.
- Console and network for web behavior.
- Diff and plan audit for scope.
- Test output for correctness.
- Performance entries for speed.
- Dependency and CI files for security and release.

### 6. Ask at Real Decision Points

Ask when:

- Scope changes.
- Taste choices.
- Risky fixes.
- One-way operations.
- Cost-bearing options.
- Secrets or privacy.
- Version bumps.
- Deleting, reverting, force-like actions.

Do not ask for trivial confirmations.

### 7. Write Artifacts

Good skills leave behind durable state:

- Markdown reports.
- JSON baselines.
- JSONL logs.
- Screenshot directories.
- Plan sections.
- `CLAUDE.md` guidance blocks.
- TODO entries with context.

Artifacts should be discoverable by later skills.

### 8. Verify Freshly

Before final output:

- Re-run relevant tests if code changed.
- Re-open pages after fixes.
- Compare before/after screenshots.
- Confirm PR titles or bodies after editing.
- Re-read files after writing important plan or guidance sections.
- Check that generated skills run after committing.

### 9. Log Learnings Sparingly

Log only durable insights that will save future time:

- Project quirks.
- Reusable patterns.
- Pitfalls.
- User-stated preferences.
- Architectural decisions.
- Tool behavior.

Include confidence and source.

### 10. End With Status

Use a clear completion status:

- `DONE`: completed with evidence.
- `DONE_WITH_CONCERNS`: completed but with stated risk.
- `BLOCKED`: cannot continue, with what was tried.
- `NEEDS_CONTEXT`: missing exact information.

The final answer should be terse, evidence-backed, and tell the user what changed.

## The Big Style Lesson

The most advanced gstack skills are not longer because they are verbose. They are
longer because they encode operational judgment:

- when to ask,
- when to act,
- when to stop,
- what to measure,
- how to verify,
- where to write memory,
- how to avoid repeating mistakes,
- and how to keep the user in control without making them babysit routine work.

That is the pattern worth copying.
