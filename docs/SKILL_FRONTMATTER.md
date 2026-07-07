# Skill & Agent Frontmatter Specification

Normative frontmatter spec for skills and agents in this repository. This is the
single source of truth. Where `docs/ADVANCED_SKILLS.md` (the gstack corpus notes)
describes fields like `preamble-tier`, `interactive`, `hooks`, or `gbrain`, treat
those as external-corpus conventions — this document governs what we ship here.

Routing in this repo rides entirely on `description`. No other field is read by
the Claude Code loader for invocation. Everything else is either a documented
repo convention (kept, not read) or deprecated (do not add).

## Three tiers

### Tier 1 — Loader-recognized (Claude Code reads these)

These are the only skill frontmatter fields the loader acts on.

| Field | Rules |
|-------|-------|
| `name` | Lowercase kebab-case. Must match the skill's directory name. |
| `description` | The **only** routing signal. Must state *what* the skill does, *when* to trigger it (concrete phrases), and *when NOT* to (name the nearest-neighbor skill). |
| `allowed-tools` | Capability allowlist. Canonical tool names only (see list below). Omit to inherit all tools. **`tools` is an AGENT field and is invalid on skills** — the loader ignores it, so any restriction written as `tools:` is a silent no-op. |
| `disable-model-invocation` | `false` lets the model auto-invoke on description match (the default intent for these skills). `true` makes the skill explicit-invocation only. Keep it uniform across the repo. |

`allowed-tools` accepts either YAML list form or a comma-separated string; the
loader treats them identically. Prefer the list form for readability.

### Tier 2 — Repo-convention metadata (documented, kept, NOT read by the loader)

Retained for tooling, docs, and audits. The loader ignores them; they must never
be relied on for routing or capability enforcement.

| Field | Semantics | Format |
|-------|-----------|--------|
| `triggers` | Human-facing catalog of representative trigger phrases, mirrored into `PLUGINS_AND_SKILLS.md` / `CLAUDE.md` tables. Documentation only — actual routing is driven by `description`. Do not add generic phrases already claimed by a sibling skill. | YAML list of short lowercase strings. |
| `mutating` | Declares whether the skill writes files or performs side effects. Advisory signal for audits and reviewers; does not gate tools. | Boolean. `true` = writes artifacts/state; `false` = read-only/advisory. |
| `version` | SemVer skill version for changelog/audit tracking. Not the installable plugin version (that lives in the generated `plugin.json`). | Quoted SemVer string, e.g. `"1.1.0"`. |

### Tier 3 — Deprecated (do NOT add to new skills; scheduled for removal)

Present in parts of the corpus but unrecognized and non-normative here. Do not
add them; remove on next substantive edit.

`writes_pages`, `writes_to`, `preamble-tier`, `interactive`, `benefits-from`,
`category`, `priority`, `depends_on`, `feeds_into`, and `tools` (on skills).

Rationale: none are loader-recognized. `preamble-tier`/`interactive` are gstack
runtime concepts we do not implement. `category`/`priority`/`depends_on`/
`feeds_into` duplicate content that belongs in the skill body and the marketplace
tables. `writes_*` is superseded by `mutating`. `tools` on a skill is a bug —
see migration notes.

## Complete valid example

```yaml
---
name: metric-movement-diagnostic
description: >
  Use when a KPI moved and someone needs to know why — separating measurement
  artifacts, mix shift, segment effects, timing, and plausible drivers. Trigger
  on "why did X change", "explain the drop/spike", "root-cause this metric".
  For defining the metric itself use metric-contract; for tracing its lineage
  use metric-lineage.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
mutating: false
version: "1.0.0"
disable-model-invocation: false
---
```

## Canonical tool names (relevant to skills)

Use these exact strings in `allowed-tools`. Full table: `docs/TOOLS_REFERENCE.md`.

`Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `LSP`, `NotebookEdit`,
`WebFetch`, `WebSearch`, `AskUserQuestion`, `Skill`, `Agent`, `TodoWrite`,
`Monitor`.

Common mappings for legacy/invented values:

| Wrong | Canonical |
|-------|-----------|
| `Task` | `Agent` (subagent spawn) |
| `read` / `write` / `exec` | `Read` / `Write`+`Edit` / `Bash` |
| `search` | `Grep` + `Glob` |
| `get_page`, `put_page`, `sync_kb`, `add_link`, … | (not tools — delete) |

Read-only skills should list only read/search tools (`Read`, `Grep`, `Glob`,
`Bash` for inspection) and omit `Write`/`Edit`.

## Agent-file frontmatter (plugin agents)

Agents live in `plugins/<plugin>/agents/*.md` and use a **different** allowlist
than skills. Plugin-shipped agents support only these fields:

`name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`,
`skills`, `memory`, `background`, `isolation`.

Rules:

- `tools` (allowlist) and `disallowedTools` (denylist) both use the **same
  canonical tool names** as `allowed-tools` above. On agents this is the correct
  field — `tools` is valid here and invalid on skills.
- Reviewer, auditor, and read-only planner agents should **omit `Write` and
  `Edit`** (via a `tools` allowlist that excludes them, or `disallowedTools: Write, Edit`).
- `model` accepts `sonnet`, `opus`, `haiku`, a full model ID, or `inherit`.
  `effort` accepts `low`/`medium`/`high`/`xhigh`/`max`.
- `isolation`'s only valid value is `worktree`.
- Plugin agents do **not** support `hooks`, `mcpServers`, or `permissionMode` —
  these are silently ignored when loaded from a plugin.

## Migration notes: `tools` → `allowed-tools`

The most common defect in the repo is `tools:` on a skill. Because the loader
only honors `allowed-tools` on skills, every `tools:` restriction is a silent
no-op — the skill actually runs with all tools available.

To fix a skill:

1. Rename the key `tools:` → `allowed-tools:`.
2. Map every value to a canonical name (`Task`→`Agent`, `read`→`Read`,
   `write`→`Write, Edit`, `exec`→`Bash`, `search`→`Grep, Glob`).
3. Delete invented values that map to no real tool.
4. Confirm the result is a subset of the canonical list above.

Do **not** apply this rename to agent files — on agents, `tools` is already the
correct field. There, the fix is only to canonicalize the values.

Guardrail: `grep -rn "^tools:" plugins/*/skills` must return nothing, and every
`allowed-tools` value must be in the canonical set from `docs/TOOLS_REFERENCE.md`.
