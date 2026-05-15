# Claude Code Plugin Development Toolkit — Research Brief & Skill Suite

## TL;DR

- **Build it as a self-contained plugin (`plugin-development-toolkit`)** that lives in your existing `./plugins/` marketplace at `weisberg/agent_tools`, containing seven generic skills (`plugin-creator`, `plugin-component-author`, `plugin-validator`, `plugin-tester`, `plugin-marketplace-manager`, `plugin-publisher`, `plugin-improver`) plus one optional Vanguard layer (`vanguard-plugin-conventions`). This mirrors how Anthropic ships its own `plugin-dev` plugin (which itself bundles 7 expert skills covering hooks, MCP, commands, agents, plugin structure, settings, and skill development) and keeps every component cleanly namespaced.
- **The single most important spec fact** for your suite is that, per the official `Plugins reference`, *the only required field in `.claude-plugin/plugin.json` is `name`*; everything else (manifest schema, marketplace entry fields, hook/MCP merging rules, `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` substitution, version resolution, the read-only plugin cache at `~/.claude/plugins/cache`, and `claude plugin validate`) is what the skills must enforce — write all skills against those rules, not against community blog posts.
- **Cross-skill orchestration**: `plugin-creator` always delegates skill authoring to your existing Anthropic `skill-creator` skill (not a homegrown re-implementation), `plugin-component-author` is a single dispatcher skill with five `references/` files (one per component), and `plugin-improver` reuses `plugin-validator` and `plugin-tester` as subroutines. Open questions worth verifying are flagged at the end (notably: the `claude plugin validate` exact CLI output format, whether `marketplace.json` `version` field is honored anywhere, and whether `claude plugin tag` semver conventions apply to your internal commit-SHA versioning).

---

## 1. Research Summary — Claude Code Plugin Architecture

This summary is derived from `code.claude.com/docs/en/plugins-reference`, `…/plugins`, `…/plugin-marketplaces`, `…/discover-plugins`, `…/hooks`, `…/skills`, `…/sub-agents`, `…/mcp`, the changelog, the `anthropics/claude-code` and `anthropics/claude-plugins-official` repos, and the unofficial `hesreallyhim/claude-code-json-schema` repo (which mirrors current docs).

### 1.1 Plugin manifest (`.claude-plugin/plugin.json`)

The manifest is **optional**. If present, only `name` is required. Claude Code auto-discovers components in default locations and derives the plugin name from the directory if no manifest exists.

**Complete schema:**

```json
{
  "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json",
  "name": "plugin-name",                      // REQUIRED, kebab-case, no spaces
  "version": "1.2.0",                         // optional; pins update detection
  "description": "Brief plugin description",  // optional
  "author": {                                 // optional
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://github.com/author"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/author/plugin",
  "license": "MIT",
  "keywords": ["k1", "k2"],
  "skills": "./custom/skills/",               // ADDS to default skills/
  "commands": ["./custom/commands/special.md"], // REPLACES default commands/
  "agents": ["./custom/agents/reviewer.md"],  // REPLACES default agents/
  "hooks": "./config/hooks.json",             // own merge rules (merged)
  "mcpServers": "./mcp-config.json",          // own merge rules (merged)
  "outputStyles": "./styles/",                // REPLACES default
  "lspServers": "./.lsp.json",
  "experimental": {
    "themes": "./themes/",
    "monitors": "./monitors.json"
  },
  "userConfig": { /* see §1.1.1 */ },
  "channels": [ /* see §1.1.2 */ ],
  "dependencies": [
    "helper-lib",
    { "name": "secrets-vault", "version": "~2.1.0" }
  ]
}
```

**Field reference (consolidated):**

| Field | Type | Req | Notes |
|---|---|---|---|
| `name` | string | ✅ | kebab-case, no spaces. Used to namespace components: `plugin-name:command-name`. Lowercased letters/digits/hyphens recommended. |
| `$schema` | string | ❌ | Editor hint only. Anthropic's published URL `https://anthropic.com/claude-code/marketplace.schema.json` currently 404s — Claude Code ignores it at load time. JSON Schema Store has community-supplied schemas. |
| `version` | string | ❌ | If set, plugin is pinned to that string; users only get updates when you bump it. If unset, falls back to the marketplace entry's version, then to the git commit SHA, then to `unknown`. |
| `description` | string | ❌ | Shown in `/plugin` Discover UI. |
| `author` | object | ❌ | `{ name, email?, url? }`. |
| `homepage`, `repository`, `license`, `keywords` | mixed | ❌ | Standard package metadata. |
| `skills` | string \| string[] | ❌ | Custom skill directories *in addition to* default `skills/`. |
| `commands` | string \| string[] | ❌ | Custom flat-file or directory paths; **replaces** default `commands/`. List `./commands/` explicitly to keep it. |
| `agents` | string \| string[] | ❌ | Replaces default `agents/`. |
| `hooks` | string \| object | ❌ | Path to hook JSON or inline hooks object. Merges with other hook sources. |
| `mcpServers` | string \| object | ❌ | Path or inline; merges. |
| `outputStyles`, `lspServers` | string \| array | ❌ | Replaces defaults. |
| `experimental.themes`, `experimental.monitors` | string \| array | ❌ | Experimental schemas. |
| `userConfig` | object | ❌ | Prompts user for values at enable time. See §1.1.1. |
| `channels` | array | ❌ | Telegram/Slack/Discord-style message-injection channels. |
| `dependencies` | array | ❌ | Other plugins this depends on, with optional semver constraints. See `plugin-dependencies` doc. |

#### 1.1.1 `userConfig`

Prompts user when plugin is enabled. Each option supports:
- `type`: `string` | `number` | `boolean` | `directory` | `file` (required)
- `title`, `description` (required)
- `sensitive` (boolean) — masked input, stored in keychain not settings.json (≈2 KB total keychain limit shared with OAuth)
- `required`, `default`, `multiple`
- `min` / `max` for numeric

Substitution: `${user_config.KEY}` works in MCP/LSP server configs, hook commands, monitor commands, and (for non-sensitive values) skill/agent content. Also exported as `CLAUDE_PLUGIN_OPTION_<KEY>` env vars to subprocesses.

#### 1.1.2 `channels`

```json
{ "channels": [{ "server": "telegram", "userConfig": { ... } }] }
```
The `server` must match a key in the plugin's `mcpServers`.

### 1.2 Marketplace manifest (`.claude-plugin/marketplace.json`)

**Required**: `name`, `owner`, `plugins`. Lives at the **repository root** under `.claude-plugin/marketplace.json`.

```json
{
  "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
  "name": "my-plugins",                       // kebab-case, public-facing
  "owner": { "name": "Your Name", "email": "you@example.com" },
  "description": "Brief marketplace description",
  "version": "1.0.0",                          // optional, currently unused per community report
  "metadata": { "pluginRoot": "./plugins" },  // base dir prepended to relative source paths
  "allowCrossMarketplaceDependenciesOn": ["other-marketplace"],
  "plugins": [
    {
      "name": "quality-review-plugin",         // REQUIRED, kebab-case
      "source": "./plugins/quality-review-plugin",
      "description": "...",
      "version": "1.0.0",
      "author": { "name": "..." },
      "homepage": "...",
      "repository": "...",
      "license": "MIT",
      "keywords": ["..."],
      "category": "development",
      "tags": ["..."],
      "strict": true,
      "commands": ["./commands/foo.md"],
      "agents": [],
      "hooks": {},
      "mcpServers": {},
      "lspServers": {},
      "skills": []
    }
  ]
}
```

**Reserved marketplace names** (cannot be used by third parties): `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`. Names that impersonate official ones (e.g. `official-claude-plugins`) are also blocked.

**Plugin source types:**

| Source | Shape | Notes |
|---|---|---|
| Relative path | `"./plugins/foo"` (string) | Resolved against marketplace root (the dir containing `.claude-plugin/`). Must start with `./`. **Footgun**: only works if the marketplace was added via Git (GitHub/GitLab/git URL). URL-distributed marketplaces silently fail. |
| `github` | `{ "source":"github", "repo":"owner/repo", "ref"?, "sha"? }` | `ref` = branch/tag, `sha` = full 40-char commit. |
| `url` | `{ "source":"url", "url":"https://…", "ref"?, "sha"? }` | Any git URL (HTTPS or `git@`). `.git` suffix optional. |
| `git-subdir` | `{ "source":"git-subdir", "url", "path", "ref"?, "sha"? }` | Sparse clone for monorepos. |
| `npm` | `{ "source":"npm", "package", "version"?, "registry"? }` | Installed via `npm install`. |

**Strict mode:**
- `strict: true` (default) — `plugin.json` is authority; marketplace can supplement. Both merge.
- `strict: false` — marketplace entry is the entire definition. If `plugin.json` also declares components, the plugin fails to load.

### 1.3 Directory structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json            ← ONLY manifest goes here
├── skills/
│   └── <skill-name>/SKILL.md
├── commands/
│   └── <command>.md            ← Flat skill files
├── agents/
│   └── <agent>.md
├── output-styles/
│   └── terse.md
├── themes/
│   └── dracula.json
├── monitors/
│   └── monitors.json
├── hooks/
│   └── hooks.json
├── bin/                        ← Added to Bash tool's PATH while plugin enabled
├── settings.json               ← Default plugin settings (only `agent` and `subagentStatusLine` keys honored)
├── .mcp.json
├── .lsp.json
├── scripts/
├── LICENSE
└── CHANGELOG.md
```

**Critical mistakes** docs explicitly call out:
- ❌ Putting `commands/`, `agents/`, `skills/`, or `hooks/` inside `.claude-plugin/`. Only `plugin.json` belongs there.
- ❌ Loading `CLAUDE.md` from plugin root — it is **not** loaded as project context. Ship instructions through skills.
- ❌ Path traversal (`../shared-utils`) — does not work after install because external files aren't copied to the cache. Use **symlinks** instead; symlinks are preserved in the cache rather than dereferenced.

### 1.4 Commands component (now merged with skills)

The docs note: "**Custom commands have been merged into skills.**" A file at `commands/foo.md` and a skill at `skills/foo/SKILL.md` both create `/plugin-name:foo` and work the same way. Skills are recommended for new plugins because they support `scripts/`, `references/`, and `assets/` subdirectories.

**Frontmatter (commands and skills share these):**

```yaml
---
name: my-skill                   # optional; falls back to dir/file basename. ≤64 chars, [a-z0-9-]
description: …                   # recommended; primary trigger mechanism
when_to_use: …                   # additional context; appended to description
argument-hint: "[issue] [prio]"  # autocomplete hint
arguments: [issue, branch]       # named positional args; expand as $issue / $branch
disable-model-invocation: true   # only user can invoke (no auto-trigger)
user-invocable: false            # only Claude can invoke (hidden from / menu)
allowed-tools: Bash(git:*) Read  # pre-approved tools; space- or list-separated
model: sonnet | opus | haiku | inherit | claude-sonnet-4-6
effort: low | medium | high | xhigh | max
context: fork                    # run in subagent context
agent: Explore                   # subagent type when context: fork
hooks: { … }                     # scoped to this skill's lifecycle
paths: ["**/*.ts"]               # glob restriction for auto-trigger
shell: bash | powershell
---
```

**String substitutions inside skill body:**
- `$ARGUMENTS` — full args
- `$ARGUMENTS[N]` or `$N` — positional
- `$<name>` — named (declared in `arguments:`)
- `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}`
- `` !`<command>` `` — runs shell, replaces with output **before** Claude sees content
- ` ```! ` fenced block — same, multi-line

**Namespacing**: Plugin commands always render as `/plugin-name:command`. To change the prefix, change `name` in `plugin.json`.

**Subdirectory namespacing for commands**: `commands/frontend/component.md` → `/plugin:frontend:component` (per Steve Kinney's documentation; verify behavior in your version).

### 1.5 Agents (subagents) component

**Location**: `agents/<name>.md`. **Frontmatter (per `code.claude.com/docs/en/sub-agents` and `plugins-reference`):**

```yaml
---
name: agent-name
description: When Claude should invoke this agent (third-person, action-oriented)
model: sonnet | opus | haiku | inherit | claude-sonnet-4-6
effort: low | medium | high | xhigh | max
maxTurns: 20
tools: Read, Grep, Glob, Bash(git:*)        # comma- or space-separated
disallowedTools: Write, Edit
skills: [api-conventions, error-handling]    # preload skill content at startup
memory: …                                    # custom memory config
background: false
isolation: worktree                          # ONLY valid value
color: blue                                  # used by /agents UI
---
You are a senior X engineer. When invoked: 1. … 2. … 3. …
```

**Plugin-shipped agents do NOT support**: `hooks`, `mcpServers`, `permissionMode` (security restriction).

**Invocation**: Claude auto-delegates via the Task tool when the description matches; users can manually invoke via `/agents`. Action-oriented descriptions ("Use proactively after writing code") fire more reliably than passive ones.

### 1.6 Skills component (nested in plugins)

**Location**: `skills/<skill-name>/SKILL.md`. The directory name becomes the skill identifier; if `name:` is set in frontmatter, that wins.

**Progressive disclosure (three levels):**
1. **Metadata** (name + description) — always in context, ~100 words.
2. **SKILL.md body** — loads when skill triggers (target <500 lines).
3. **Bundled resources** — loaded only as needed:
   - `scripts/` — executable code, runs without loading into context
   - `references/` — markdown loaded on demand (link from SKILL.md with guidance on when to read)
   - `assets/` — output materials (templates, fonts, images)

**Lifecycle nuance**: Once invoked, SKILL.md content stays in context for the session. Claude does not re-read the file on later turns. Auto-compaction re-attaches the most recent invocation of each skill (first 5,000 tokens; combined 25,000-token cap across re-attached skills).

**User skills vs plugin skills vs built-in**: Plugin skills are namespaced (`/my-plugin:hello`). User skills (`~/.claude/skills/`) and project skills (`.claude/skills/`) are not. Built-in skills (e.g. `/simplify`, `/debug`, `/loop`, `/claude-api`) ship with Claude Code.

**Triggering**: Description quality is the primary mechanism. Anthropic's `skill-creator` recommends writing descriptions in **third person** and being slightly **"pushy"** (e.g. "Make sure to use this skill whenever the user mentions X, even if they don't explicitly ask"). Combined description+`when_to_use` is truncated at **1,536 characters** in the skill listing; the global budget scales at 1% of the context window with an 8,000-char fallback (override with `SLASH_COMMAND_TOOL_CHAR_BUDGET`).

### 1.7 Hooks component

**Schema** (`hooks/hooks.json` or inline in `plugin.json` → `hooks`):

```json
{
  "description": "Optional plugin-level description",
  "hooks": {
    "<EventName>": [
      {
        "matcher": "Bash|Edit|Write" | "*" | "regex",
        "hooks": [
          {
            "type": "command" | "http" | "mcp_tool" | "prompt" | "agent",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/x.sh",
            "if": "Bash(git *)",        // permission-rule syntax filter
            "timeout": 60,               // seconds; defaults: 600 cmd, 30 prompt, 60 agent
            "async": false,
            "asyncRewake": false,
            "shell": "bash" | "powershell",
            "statusMessage": "Running formatter…",
            "once": false               // only honored in skill frontmatter
          }
        ]
      }
    ]
  }
}
```

**All event types:** `SessionStart`, `Setup`, `UserPromptSubmit`, `UserPromptExpansion`, `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Notification`, `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `Stop`, `StopFailure`, `TeammateIdle`, `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`, `Elicitation`, `ElicitationResult`, `SessionEnd`.

**Hook handler types:**
- `command` — shell process. JSON arrives on stdin; results via exit code + stdout.
- `http` — POST event JSON to a URL; response body parsed as JSON-output schema.
- `mcp_tool` — call a tool on a configured MCP server.
- `prompt` — single-turn LLM evaluation (default fast model).
- `agent` — spawn a subagent verifier (experimental).

**Matcher patterns:**
- `"*"`, `""`, omitted → match all
- Letters/digits/`_`/`|` only → exact string or pipe-separated list
- Anything else → JavaScript regex (e.g. `mcp__memory__.*`)

**Exit codes:**
- `0` — success. stdout parsed for JSON. For `UserPromptSubmit`/`UserPromptExpansion`/`SessionStart`, plain stdout is added to context; otherwise stdout goes to debug log only.
- `2` — blocking error. stdout ignored, stderr fed back to Claude. Effect varies per event (see table in §1.7.1).
- Anything else — non-blocking error. Transcript shows `<hook> hook error` with first stderr line. **Note**: `WorktreeCreate` is the lone exception where any non-zero aborts.

**Exit code 2 effect (selected events):**

| Event | Exit 2 effect |
|---|---|
| `PreToolUse` | Blocks the tool call |
| `PermissionRequest` | Denies the permission |
| `UserPromptSubmit` | Blocks and erases the prompt |
| `Stop` / `SubagentStop` | Continues conversation |
| `PreCompact` | Blocks compaction |
| `TaskCreated` / `TaskCompleted` | Rolls back |
| `PostToolUse`/`Failure`/`Notification`/`SessionStart`/`SessionEnd` | Ignored (already happened); stderr shown to user/Claude |

**JSON output (richer than exit codes):**

Universal fields: `continue` (stop entirely), `stopReason` (user-facing), `suppressOutput`, `systemMessage`.

Event-specific decision control:
- `PreToolUse`: `hookSpecificOutput.permissionDecision` ∈ `allow|deny|ask|defer`, plus `permissionDecisionReason`, `updatedInput`, `additionalContext`.
- `PermissionRequest`: `hookSpecificOutput.decision.behavior` ∈ `allow|deny`, plus `updatedInput`, `updatedPermissions[]`, `message`, `interrupt`.
- `PostToolUse`: top-level `decision: "block"` + `reason`; or `updatedToolOutput` to replace tool output.
- `UserPromptSubmit`/`UserPromptExpansion`: top-level `decision: "block"` + `reason`; `additionalContext`; `sessionTitle`.
- `SessionStart`/`Setup`/`SubagentStart`/`PostToolBatch`/`PostToolUseFailure`: `additionalContext` only.
- `WorktreeCreate`: stdout = path; or `hookSpecificOutput.worktreePath`.
- `Elicitation`/`ElicitationResult`: `hookSpecificOutput.action` ∈ `accept|decline|cancel` + `content`.

**Environment variables hooks see:**
- `CLAUDE_PROJECT_DIR` — absolute path to project root (always, in all script types)
- `CLAUDE_PLUGIN_ROOT` — plugin install dir (changes on update; treat as ephemeral)
- `CLAUDE_PLUGIN_DATA` — `~/.claude/plugins/data/{plugin-id}/` — survives updates; for `node_modules`, caches, generated code
- `CLAUDE_ENV_FILE` — only in `SessionStart`, `Setup`, `CwdChanged`, `FileChanged` hooks; write `export FOO=bar` lines to persist env vars to subsequent Bash calls
- `CLAUDE_CODE_REMOTE` — `"true"` in remote web sessions

**Security**: Plugins/hooks execute arbitrary code with user privileges. Anthropic does not vet community plugins. Use `allowManagedHooksOnly` in managed settings to block user/project/plugin hooks (managed-marketplace plugins force-enabled in `enabledPlugins` are exempt).

### 1.8 MCP servers component

**Location**: `.mcp.json` at plugin root, or inline in `plugin.json` → `mcpServers`.

```json
{
  "mcpServers": {
    "plugin-database": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": { "DB_PATH": "${CLAUDE_PLUGIN_ROOT}/data" },
      "cwd": "${CLAUDE_PLUGIN_ROOT}"
    },
    "remote-api": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": { "Authorization": "Bearer ${user_config.api_token}" }
    },
    "legacy-sse": {
      "type": "sse",
      "url": "https://example.com/sse"
    }
  }
}
```

**Transports**: `stdio` (default; spawns subprocess), `http` (recommended for remote), `sse` (deprecated; migrate to http).

**Plugin MCP servers vs user-configured**:
- Plugin servers start automatically when the plugin is enabled; lifecycle managed by Claude Code.
- Run `/reload-plugins` to start/stop after enable/disable mid-session.
- Appear in `/mcp` alongside user-configured servers, but managed independently.
- Variable substitution: `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${user_config.<KEY>}`, and any `${ENV_VAR}` available in the user's shell.

**Reconnection**: HTTP/SSE servers retry initial connection up to 3 times on transient errors (5xx, ECONNREFUSED, timeout). Mid-session disconnects retry up to 5 times with exponential backoff (1s, 2s, 4s…). Stdio servers are not auto-reconnected.

### 1.9 Marketplace mechanics

**User flow:**

```bash
# Add a marketplace
/plugin marketplace add anthropics/claude-code        # GitHub shorthand
/plugin marketplace add owner/repo@v1.2.0             # pin to ref
/plugin marketplace add https://gitlab.com/x/y.git#main
/plugin marketplace add ./local-marketplace           # local dir
/plugin marketplace add https://example.com/marketplace.json  # URL (relative-path plugins won't work)

# Browse and install
/plugin                                                # interactive (Discover, Installed, Marketplaces, Errors tabs)
/plugin install <plugin>@<marketplace>                 # CLI
/plugin install foo@bar --scope project                # to .claude/settings.json (team-shared)

# Reload after install/enable/disable mid-session
/reload-plugins

# Manage
/plugin disable <p>@<m>
/plugin enable <p>@<m>
/plugin uninstall <p>@<m>
/plugin marketplace update [<name>]
/plugin marketplace remove <name>
/plugin marketplace list
```

**Equivalent non-interactive CLI** (for scripting):

```bash
claude plugin install <p>@<m> [--scope user|project|local]
claude plugin uninstall <p>@<m> [--keep-data] [--prune]
claude plugin enable | disable | update <p>@<m>
claude plugin list [--json] [--available]
claude plugin tag [--push] [--dry-run] [--force]   # creates release git tag from inside plugin dir
claude plugin prune [--dry-run] [--yes]            # removes orphaned auto-installed deps (v2.1.121+)
claude plugin marketplace add | list | remove | update
claude plugin validate [path]                      # validates plugin.json, marketplace.json, frontmatter, hooks
```

**Update behavior**: Claude Code uses the plugin's *resolved* version as the cache key. Resolution order:
1. `plugin.json` `version`
2. marketplace entry `version`
3. git commit SHA (for `github`, `url`, `git-subdir`, relative-path-in-git sources)
4. `unknown` (npm sources or non-git local dirs)

**If you set `version` and don't bump it, users won't get updates.** For internal/actively-developed plugins, leave `version` unset to use commit SHA.

**Caching**: Marketplace plugins are copied to `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. Each version is a separate dir. Old versions are marked orphaned and removed automatically after **7 days**. Glob/Grep skip orphaned dirs.

**Team marketplaces** via `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "company-tools": { "source": { "source": "github", "repo": "your-org/claude-plugins" } }
  },
  "enabledPlugins": {
    "code-formatter@company-tools": true
  }
}
```

**Managed restrictions** (`managed-settings.json`):

```json
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "acme-corp/approved" },
    { "source": "hostPattern", "hostPattern": "^github\\.acme\\.com$" },
    { "source": "pathPattern", "pathPattern": "^/opt/approved/" }
  ]
}
```

Empty array `[]` = full lockdown. Undefined = no restrictions.

**Container seed dirs**: `CLAUDE_CODE_PLUGIN_SEED_DIR` (read-only seed of `~/.claude/plugins`) for prebuilt CI/dev images.

### 1.10 Validation, testing, settings, and edge cases

**Validation:**
- `claude plugin validate <path>` (or `/plugin validate <path>` interactively) checks plugin.json, marketplace.json, skill/agent/command frontmatter, and `hooks/hooks.json`.
- Common errors observed in docs: `name: Required`, JSON parse errors, `Path contains ".."`, `Duplicate plugin name`, `YAML frontmatter failed to parse`, `No commands found in plugin … directory`.
- Warnings (non-blocking): `Marketplace has no plugins defined`, `Plugin name "X" is not kebab-case`, missing description.
- Per the changelog, recent versions of `claude plugin validate` also accept `$schema`, `version`, and `description` at top level of marketplace.json.

**Local testing:**
- `claude --plugin-dir ./my-plugin` — load directly without install. Repeat the flag for multiple plugins.
- `claude --plugin-url https://…/plugin.zip` — fetch a zip for the session (CI artifact testing).
- `/reload-plugins` — pick up changes without restart.
- A `--plugin-dir` plugin overrides an installed plugin of the same name (except managed-force-enabled ones).
- `claude --debug` — see "loading plugin" messages, registration details, MCP init errors.

**Plugin installation scopes:**

| Scope | File | Use |
|---|---|---|
| `user` | `~/.claude/settings.json` | Personal across projects (default) |
| `project` | `.claude/settings.json` | Team-shared via VC |
| `local` | `.claude/settings.local.json` | Project-personal, gitignored |
| `managed` | Managed-settings.json | Read-only org-wide |

**Settings.json plugin-relevant keys:**
- `enabledPlugins` — `{ "<plugin>@<marketplace>": true|false }`
- `extraKnownMarketplaces`, `strictKnownMarketplaces`
- `permissions` (`allow`, `deny`, `ask`, `additionalDirectories`, `defaultMode`, `disableBypassPermissionsMode`)
- `hooks`, `disableAllHooks`
- `disableSkillShellExecution`
- `skillOverrides`: `"on" | "name-only" | "user-invocable-only" | "off"`
- Plugin-bundled `settings.json` at plugin root supports only `agent` and `subagentStatusLine` keys; unknown keys silently ignored.

**Cross-platform / Windows gotchas:**
- Stdio MCP servers using `npx` need `cmd /c` wrapper on native Windows: `claude mcp add --transport stdio my -- cmd /c npx -y @some/pkg`.
- Hook `shell: "powershell"` runs PowerShell on Windows; doesn't require `CLAUDE_CODE_USE_POWERSHELL_TOOL`.
- Path resolution uses `:` separator on Unix, `;` on Windows for `CLAUDE_CODE_PLUGIN_SEED_DIR`.

**Performance:**
- LSP plugins (rust-analyzer, pyright) consume significant memory on large projects.
- Skill descriptions + names are truncated under a global char budget — too many skills strips keywords from descriptions. Tune with `SLASH_COMMAND_TOOL_CHAR_BUDGET` or set low-priority skills to `"name-only"` in `skillOverrides`.

**Plugin-to-plugin interaction:**
- Components are namespaced by plugin name; `/plugin-a:foo` and `/plugin-b:foo` coexist.
- Hooks merge across user/project/plugin sources — there is no "owner" of a hook event.
- `dependencies` in `plugin.json` use semver ranges; `claude plugin tag` creates a `<plugin-name>--v<version>` git tag for dependency resolution.

**Things explicitly called out as "important", "warning", or "note" in docs:**
- `bypassPermissions` mode is never persisted as `defaultMode` regardless of destination.
- Plugins/marketplaces "are highly trusted components that can execute arbitrary code on your machine" — only install from sources you trust.
- Plugin updates mid-session: hooks/MCP/LSP keep using the previous version's path until `/reload-plugins`; monitors require a session restart.
- A `CLAUDE.md` at plugin root **is not loaded** as project context. Use a skill instead.
- Once a skill loads, its content stays in context for the session. Claude does not re-read SKILL.md on later turns.
- Anthropic's published `https://anthropic.com/claude-code/marketplace.schema.json` URL currently 404s — open issue #9686 in `anthropics/claude-code`.

---

## 2. Skill Suite Design

### Architecture

**Recommended deliverable**: a single plugin called `plugin-development-toolkit` that lives at `./plugins/plugin-development-toolkit/` in the user's existing marketplace repo. This mirrors Anthropic's own `plugin-dev` plugin and gets you:
- Single-namespace install (`/plugin-development-toolkit:create-plugin`, etc.)
- One version cadence
- Clean way to ship a `vanguard-plugin-conventions` skill as an additive layer

### Skill graph

```
plugin-creator ──┬──► skill-creator (Anthropic's, already installed)
                 ├──► plugin-component-author (delegates per-component work)
                 └──► plugin-validator (validates after generation)

plugin-component-author ──┬──► skill-creator (for skill subcomponents)
                          └──► references/{commands,agents,hooks,mcp,skills}.md

plugin-improver ──┬──► plugin-validator
                  └──► plugin-component-author (to add what's missing)

plugin-publisher ──┬──► plugin-validator (must pass before publish)
                   ├──► plugin-tester (smoke test after install)
                   └──► plugin-marketplace-manager (update marketplace.json)

plugin-tester ──► uses claude --plugin-dir + /reload-plugins; calls plugin-validator first

vanguard-plugin-conventions  (additive layer; called by plugin-creator/improver
                              when the user signals AAA/Vanguard intent)
```

### Skill catalog

| Skill | Fires when | Primary outputs | Cross-references |
|---|---|---|---|
| **plugin-creator** | "create a new claude code plugin", "scaffold a plugin", "new plugin from scratch" | `.claude-plugin/plugin.json`, directory tree, README, stub files | `skill-creator`, `plugin-component-author`, `plugin-validator`, optionally `vanguard-plugin-conventions` |
| **plugin-component-author** | "add a command/agent/hook/mcp/skill to an existing plugin" | One new component file with valid frontmatter and references | `skill-creator` (for skill subcomponents); `references/{commands,agents,hooks,mcp,skills}.md` |
| **plugin-validator** | "validate this plugin", "check my plugin.json", "lint plugin" | Severity-ranked report (error/warning/info) + autofix suggestions | wraps `claude plugin validate`; static checks for path traversal, frontmatter, namespacing |
| **plugin-tester** | "test my plugin locally", "smoke-test before I publish" | A test plan + transcript with `--plugin-dir`, `/reload-plugins`, exercise each component | `plugin-validator` (precondition) |
| **plugin-marketplace-manager** | "add this plugin to my marketplace", "update marketplace.json", "validate marketplace" | Edited `marketplace.json`, with a new/updated plugin entry | `plugin-validator`; understands strict mode, source types, reserved names |
| **plugin-publisher** | "publish this plugin", "release v1.2.0", "tag and push" | semver bump, CHANGELOG.md entry, `claude plugin tag --push`, marketplace.json update, git push | `plugin-validator`, `plugin-tester`, `plugin-marketplace-manager` |
| **plugin-improver** | "review and improve this plugin", "what's missing in this plugin" | Improvement plan + applied edits | `plugin-validator`, `plugin-component-author`, optionally `vanguard-plugin-conventions` |
| **vanguard-plugin-conventions** *(optional layer)* | The user mentions Vanguard, Orion, AAA, astack, scrum-master, athena-analyst, experiment-analyst, agentli, or asks to "apply Vanguard conventions" | Adds Vanguard naming, AAA framework references, scrum-master/astack patterns, Orion-team conventions to plugin output | called by plugin-creator and plugin-improver |

### Why one `plugin-component-author` instead of five

- All five components share the same enclosing concerns (where files live, how they're namespaced, `${CLAUDE_PLUGIN_ROOT}` substitution, manifest registration).
- Splitting fragments the trigger surface; Claude has to choose the right one. One dispatcher with five `references/` files keeps the skill body lean (~250 lines) while letting Claude load only the relevant reference.
- Cleanly mirrors how Anthropic's `plugin-dev` plugin organizes its expert skills (one entry skill + reference files per topic).

---

## 3. SKILL.md files

All SKILL.md files below go under `plugins/plugin-development-toolkit/skills/<skill-name>/SKILL.md`.

---

### `skills/plugin-creator/SKILL.md`

```markdown
---
name: plugin-creator
description: Creates a new Claude Code plugin from scratch with a valid .claude-plugin/plugin.json manifest, the correct directory structure, and stub files for each component the user wants. This skill should be used whenever the user asks to "create a plugin", "scaffold a new plugin", "start a new claude code plugin", "new plugin", "make me a plugin", "bootstrap a plugin", or describes wanting to package commands, agents, skills, hooks, or MCP servers as a shareable plugin. Always delegates skill authoring to the skill-creator skill, and validates the final structure with plugin-validator before declaring success.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: "[plugin-name]"
---

# Plugin Creator

Scaffolds a new Claude Code plugin and orchestrates the rest of this toolkit (skill-creator, plugin-component-author, plugin-validator) to fill it in.

## When to use this skill

- The user wants a brand-new plugin in their marketplace's `./plugins/` dir.
- The user has loose `.claude/commands/` or hook config they want to migrate to a plugin.
- The user asks to start a plugin "for X" — capture intent first, then scaffold.

If a plugin already exists and the user wants to add components, hand off to `plugin-component-author` instead. If the user wants to improve an existing plugin, hand off to `plugin-improver`.

## Inputs to capture

Before writing files, gather:

1. **Plugin name** (kebab-case, no spaces; `[a-z0-9-]`). Validate with: `[[ "$NAME" =~ ^[a-z][a-z0-9-]*$ ]]`.
2. **One-sentence purpose** (becomes `description`).
3. **Author** (`{ name, email?, url? }`). Default to git config `user.name` / `user.email`.
4. **Components** (any subset): commands, agents, skills, hooks, MCP servers, LSP servers, monitors, output styles, themes, executables.
5. **Versioning strategy**: explicit semver (set `version`) or commit-SHA (omit `version`). Recommend commit-SHA for internal/active plugins.
6. **Distribution target**: which marketplace repo and where it lives on disk (default: this repo's `./plugins/<name>/`).
7. **Vanguard/AAA conventions?** If yes (user mentions Vanguard, Orion, AAA, astack, scrum-master, etc.), invoke `vanguard-plugin-conventions` after scaffold.

Capture defaults from conversation context first; only ask the user for what isn't already obvious.

## Scaffolding procedure

1. Run `scripts/scaffold_plugin.py <name> --dir <marketplace>/plugins`. The script:
   - Creates the directory tree (`.claude-plugin/`, plus dirs for each chosen component).
   - Writes `.claude-plugin/plugin.json` with `name`, optional `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`.
   - Writes a stub `README.md` and an empty `CHANGELOG.md`.
   - Writes one stub component per chosen type (e.g. `commands/example.md`, `hooks/hooks.json` with `{"hooks":{}}`).
   - Skips `CLAUDE.md` at plugin root — it is **not** loaded by Claude Code.
2. **Review the manifest** with the user before writing additional content.
3. **Add components**: for each chosen type, delegate to `plugin-component-author` with the component name and any specifics. **For skill components inside the plugin (`skills/<name>/SKILL.md`), invoke the `skill-creator` skill** rather than authoring inline — `skill-creator` runs the test-iterate loop that produces high-quality skills.
4. **Validate**: invoke `plugin-validator` against the new plugin path. Fix any errors before declaring done.
5. **Test locally**: tell the user how to test:
   ```bash
   claude --plugin-dir ./plugins/<name>
   /reload-plugins
   /<name>:<command>
   ```
6. **Marketplace registration** (optional, but recommended): if the user wants to publish, hand off to `plugin-marketplace-manager` to add the entry to `.claude-plugin/marketplace.json` at the repo root.

## Critical rules to enforce

- `commands/`, `agents/`, `skills/`, `hooks/`, `monitors/`, `output-styles/`, `themes/`, `bin/`, `.mcp.json`, `.lsp.json`, `settings.json` MUST live at the plugin root, **never** inside `.claude-plugin/`.
- All paths in the manifest must be relative and start with `./`. Paths like `../shared` are silently broken after install (cache copy).
- `name` is the only required field in `plugin.json`.
- If user wants `commands/` plus extra dirs, list `./commands/` explicitly: `"commands": ["./commands/", "./extras/"]`. Otherwise the default is replaced.
- Never put a `CLAUDE.md` at plugin root expecting it to load. Convert it to a skill.
- Skills inside plugins are **always** namespaced as `/<plugin>:<skill>`.

## References

- `references/manifest-schema.md` — the full plugin.json schema with examples.
- `references/directory-layout.md` — canonical directory tree.
- `references/version-strategy.md` — when to set `version` vs use commit SHA.

## Scripts

- `scripts/scaffold_plugin.py` — interactive scaffolder.
- `scripts/manifest_template.json` — minimal plugin.json template.
```

---

### `skills/plugin-component-author/SKILL.md`

```markdown
---
name: plugin-component-author
description: Adds a single component (command, agent, skill, hook, or MCP server) to an existing Claude Code plugin with the correct file location, frontmatter, and manifest registration. This skill should be used whenever the user asks to "add a command", "add a hook", "add an agent", "add an mcp server", "add a skill to my plugin", "scaffold a hook", or wants to extend an existing plugin with a new piece. For skill components, this skill delegates to the skill-creator skill rather than authoring SKILL.md inline.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: "<component-type> <component-name>"
---

# Plugin Component Author

Adds one component to an existing plugin. Component type ∈ {`command`, `agent`, `skill`, `hook`, `mcp`}.

## When to use this skill

- The plugin already has `.claude-plugin/plugin.json`. (If not, hand off to `plugin-creator`.)
- The user wants exactly one new component, not a refactor. (If broader, hand off to `plugin-improver`.)

## Dispatch

Identify component type from the user's request, then read the matching reference file:

- `command` → `references/commands.md`
- `agent` → `references/agents.md`
- `skill` → `references/skills.md` **and invoke the skill-creator skill** for the actual SKILL.md authoring
- `hook` → `references/hooks.md`
- `mcp` → `references/mcp.md`

Each reference has the canonical frontmatter schema, file location, naming rules, and an annotated example.

## Authoring procedure (per component)

1. **Read the plugin manifest** to know the plugin name, current components, and any custom paths.
2. **Read the matching reference** (above).
3. **Author the file** at the correct location:
   - command → `commands/<name>.md` (or wherever `plugin.json.commands` points)
   - agent → `agents/<name>.md`
   - skill → `skills/<name>/SKILL.md` (delegate body to skill-creator)
   - hook → merge into `hooks/hooks.json` (do not overwrite)
   - MCP server → merge into `.mcp.json` (do not overwrite)
4. **Update `plugin.json`** if the user is using non-default paths or if the new component changes the manifest's component arrays.
5. **Use `${CLAUDE_PLUGIN_ROOT}`** for any script paths in hooks/MCP/monitor commands. Use `${CLAUDE_PLUGIN_DATA}` for state that must survive plugin updates.
6. **Validate**: run `plugin-validator` against the plugin.

## Critical rules

- Plugin agents do **not** support `hooks`, `mcpServers`, or `permissionMode` frontmatter — these are stripped at load time for security.
- The only valid `isolation` value for plugin agents is `"worktree"`.
- Hook matchers: `"*"` / `""` / omitted = all; letters+digits+`_`+`|` only = exact or pipe list; anything else = JS regex.
- Hook exit codes: `0` = success; `2` = blocking error (effect varies per event); other = non-blocking error. **`WorktreeCreate` is the exception** — any non-zero aborts.
- Commands and skills both create slash commands; new plugins should prefer `skills/<name>/SKILL.md` over flat `commands/<name>.md` because skills support `scripts/`, `references/`, and `assets/`.
- Skill descriptions in **third person**, slightly "pushy" wording (per Anthropic's skill-creator best practices). Combined description+`when_to_use` is truncated at 1,536 chars in the skill listing.

## References

- `references/commands.md`
- `references/agents.md`
- `references/skills.md`
- `references/hooks.md`
- `references/mcp.md`
- `references/env-substitution.md` — `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${user_config.*}`, `${ENV_VAR}`.
```

---

### `skills/plugin-validator/SKILL.md`

```markdown
---
name: plugin-validator
description: Validates a Claude Code plugin's structure, manifests, frontmatter, and cross-references. Reports issues with severity (error / warning / info) and concrete autofix suggestions. This skill should be used whenever the user asks to "validate my plugin", "check the plugin.json", "lint this plugin", "is my marketplace.json valid", "why won't my plugin load", or before publishing or testing. Wraps `claude plugin validate` and adds static checks the CLI does not perform (path traversal, kebab-case, namespacing, dead `${CLAUDE_PLUGIN_ROOT}` references).
allowed-tools: Read, Bash, Glob, Grep
argument-hint: "[path-to-plugin-or-marketplace]"
---

# Plugin Validator

Two layers of validation:

1. **CLI layer**: `claude plugin validate <path>` (covers JSON syntax, schema, frontmatter parse, hooks.json parse).
2. **Static layer** (this skill): catches things the CLI doesn't.

## When to use this skill

- Pre-publish gate.
- After scaffolding or any non-trivial edit.
- When the user reports "plugin not loading", "skills not appearing", "MCP server fails", "hooks not firing".
- Before `plugin-tester` or `plugin-publisher` runs.

## Procedure

1. **Run the CLI**: `claude plugin validate <path>` and capture stdout+stderr.
2. **Run the static checks** (`scripts/validate_static.py <path>`):
   - `.claude-plugin/plugin.json` exists and parses (or auto-discovery rules apply).
   - `name` is kebab-case `[a-z][a-z0-9-]*`.
   - No component dirs (`commands/`, `agents/`, `skills/`, `hooks/`, `monitors/`, `output-styles/`, `themes/`) exist **inside** `.claude-plugin/`.
   - All paths in `plugin.json` are relative and start with `./`.
   - No path contains `..`.
   - All scripts referenced in `hooks/hooks.json` and `.mcp.json` use `${CLAUDE_PLUGIN_ROOT}` (warn on absolute paths).
   - All `${CLAUDE_PLUGIN_ROOT}/...` references actually resolve to a file in the plugin.
   - SKILL.md and agent/command frontmatter parses as YAML.
   - Skill `description` is in third person and ≤1,536 chars combined with `when_to_use`.
   - Skill `name` is ≤64 chars and `[a-z0-9-]`.
   - Plugin agent files do **not** have `hooks`, `mcpServers`, or `permissionMode` frontmatter (security restriction).
   - Plugin agent `isolation`, if set, equals `"worktree"`.
   - No `CLAUDE.md` at plugin root (warn — it is not loaded).
   - For marketplace.json: `name` is not in the reserved list (`claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`, or anything starting with `official-` or `anthropic-`).
   - Each marketplace plugin entry has a `name` and `source`.
   - No duplicate plugin names in `marketplace.json`.
   - Relative `source:` paths only used if marketplace is git-distributed (warn otherwise).
   - `version` is not set in **both** `plugin.json` and the marketplace entry (the plugin.json wins silently — flag as info).
3. **Aggregate** errors / warnings / infos into a single report with severity, file:line, message, and suggested fix.
4. **Print the report** in this format:
   ```
   plugin-development-toolkit  v1.0.0
   ─────────────────────────────────
   [ERROR]   plugin.json:5  name "Plugin Dev" is not kebab-case
             Fix: rename to "plugin-dev"
   [WARN]    hooks/hooks.json:12  command uses absolute path
             Fix: prefix with ${CLAUDE_PLUGIN_ROOT}
   [INFO]    skills/foo/SKILL.md:1  description in second person
             Fix: rewrite in third person ("This skill processes…")
   ─────────────────────────────────
   2 errors, 1 warning, 1 info
   ```
5. **If errors**: instruct the user to fix or invoke `plugin-component-author` / `plugin-creator` to regenerate.

## Common errors and their fixes (from Anthropic docs)

| Error | Cause | Fix |
|---|---|---|
| `name: Required` | Missing `name` in plugin.json | Add `"name": "<plugin>"` |
| `Invalid JSON syntax: Unexpected token } in JSON at position N` | Trailing comma, missing comma, unquoted string | Fix JSON |
| `No commands found in plugin … directory: ./cmds` | Custom `commands` path empty | Add at least one `.md` file or remove the override |
| `Plugin directory not found at path: ./plugins/foo` | marketplace.json source path wrong | Correct the path; ensure it starts with `./` |
| `conflicting manifests: both plugin.json and marketplace entry specify components` | strict mode mismatch | Set `"strict": false` in marketplace entry, or remove duplicate |
| `Path contains ".."` | Path traversal | Use a symlink instead |
| `Skills not appearing` | Components inside `.claude-plugin/` | Move to plugin root |
| `Hooks not firing` | Script not executable | `chmod +x scripts/*.sh` |
| `MCP server fails` (Executable not found) | Missing `${CLAUDE_PLUGIN_ROOT}` | Use the variable |

## References

- `references/error-catalog.md`
- `references/static-checks.md`

## Scripts

- `scripts/validate_static.py`
```

---

### `skills/plugin-tester/SKILL.md`

```markdown
---
name: plugin-tester
description: Provides a structured procedure for testing a Claude Code plugin locally before publishing. This skill should be used whenever the user asks to "test my plugin", "smoke test", "try it before publishing", "verify the plugin works", or just before plugin-publisher fires. Uses claude --plugin-dir, /reload-plugins, and a per-component exercise script. Always invokes plugin-validator first; aborts if validation has errors.
allowed-tools: Read, Bash, Glob, Grep
argument-hint: "[path-to-plugin]"
---

# Plugin Tester

## When to use this skill

- Pre-publish smoke test.
- After scaffolding to confirm the new plugin loads.
- When debugging "plugin loads but components don't appear".

## Procedure

1. **Validate first** (precondition): invoke `plugin-validator`. Abort if any errors.
2. **Inventory**: list every component the plugin ships (commands, agents, skills, hooks, MCP servers, monitors, LSP servers).
3. **Build the test plan** (`scripts/generate_test_plan.py <plugin-path>`): one exercise per component.
4. **Start a side-by-side test session**:
   ```bash
   claude --plugin-dir ./plugins/<name> --debug 2>&1 | tee /tmp/plugin-test.log
   ```
   In that session, watch for "loading plugin" messages, MCP server init logs, and component registration.
5. **Exercise each component**:
   - **Commands/skills**: run `/<plugin>:<name>` with realistic args. Confirm Claude responds with the expected behavior.
   - **Agents**: type a prompt that should trigger the agent description; confirm `/agents` lists it; manually invoke via Task tool if Claude doesn't auto-delegate.
   - **Hooks**: trigger the matched event (e.g. for `PostToolUse` on `Write|Edit`, ask Claude to write a file); inspect `--debug` output for the hook firing.
   - **MCP servers**: run `/mcp` to confirm connection; ask Claude to use a tool from the server.
   - **Monitors**: confirm they appear in the task panel and emit notifications.
6. **Mid-session edits**: change a file, run `/reload-plugins`, exercise again. Confirm the change is picked up. (Monitors require session restart.)
7. **Test as installed**: install the plugin via your marketplace path and re-run the exercises:
   ```bash
   /plugin marketplace add <path-to-marketplace>
   /plugin install <plugin>@<marketplace>
   /reload-plugins
   ```
8. **Test cross-platform** (if relevant): on Windows, confirm stdio MCP servers using `npx` use `cmd /c` wrapper; confirm `shell: powershell` hooks work.
9. **Regression**: maintain a `tests/regression.md` in the plugin with the exercise commands and expected outputs. Re-run on every version bump.

## Common diagnostics

- **Skills don't appear**: check `~/.claude/plugins/cache` was populated; check skill descriptions aren't truncated by char budget; check `disable-model-invocation`.
- **Hook not firing**: matcher is case-sensitive (`PostToolUse`, not `postToolUse`); script needs `chmod +x`; `${CLAUDE_PLUGIN_ROOT}` typo'd.
- **MCP server fails**: missing binary in PATH; `${CLAUDE_PLUGIN_ROOT}` not used; SSE deprecated → switch to HTTP.
- **Plugin updates not picked up**: explicit `version` in plugin.json hasn't been bumped; clear cache with `rm -rf ~/.claude/plugins/cache` and reinstall.

## References

- `references/test-recipes.md` — one exercise template per component type.
- `references/debug-flags.md` — `claude --debug`, `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE`, `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS`.

## Scripts

- `scripts/generate_test_plan.py`
```

---

### `skills/plugin-marketplace-manager/SKILL.md`

```markdown
---
name: plugin-marketplace-manager
description: Manages the marketplace catalog file at .claude-plugin/marketplace.json — adds new plugins to the marketplace, updates plugin versions and metadata, validates the marketplace manifest, and enforces source-type and reserved-name rules. This skill should be used whenever the user asks to "add my plugin to the marketplace", "update marketplace.json", "register this plugin", "publish the marketplace catalog entry", or "validate the marketplace". Always invokes plugin-validator on the marketplace and on each referenced plugin before declaring success.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: "<add|update|remove|validate> [plugin-name]"
---

# Plugin Marketplace Manager

## When to use this skill

- After `plugin-creator` finishes a new plugin and the user wants it discoverable.
- When bumping a plugin's version in the marketplace catalog.
- When auditing the marketplace before pushing.
- When restructuring (renaming, moving, splitting plugins).

## Procedure

### 1. Locate `marketplace.json`

It lives at `<repo-root>/.claude-plugin/marketplace.json`. If missing, scaffold it (`scripts/init_marketplace.py`).

### 2. Validate the existing file

Invoke `plugin-validator` on the marketplace. Fix any errors before editing.

### 3. Choose a source type

| Choose | When |
|---|---|
| Relative path (`"./plugins/foo"`) | Plugin lives in the same repo. **Only safe for git-distributed marketplaces.** |
| `github` | Plugin lives in another GitHub repo. |
| `url` | Plugin lives in any git repo (GitLab, Bitbucket, self-hosted). |
| `git-subdir` | Plugin lives in a subdirectory of a monorepo (sparse clone). |
| `npm` | Plugin distributed via npm. |

For Brian's marketplace at `weisberg/agent_tools` with `./plugins/`, use **relative paths**.

### 4. Add a plugin entry

Minimum:
```json
{
  "name": "plugin-development-toolkit",
  "source": "./plugins/plugin-development-toolkit",
  "description": "…",
  "version": "1.0.0",
  "category": "development"
}
```

Optional fields the marketplace entry can also carry: `author`, `homepage`, `repository`, `license`, `keywords`, `tags`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `skills`, `strict`. **Avoid setting `version` in both plugin.json and the marketplace entry** — plugin.json wins silently.

### 5. Enforce constraints

- `name` must be kebab-case.
- `name` must NOT be in the reserved list (see plugin-validator).
- `name` must be unique across all entries in this marketplace.
- All relative `source` paths must start with `./`.

### 6. Validate again

Run `plugin-validator` on the marketplace. Confirm:
- JSON parses
- All `source` paths exist
- No duplicate plugin names
- Each referenced plugin's `plugin.json` is itself valid

### 7. (Optional) Local install dry-run

```bash
/plugin marketplace add <path>
/plugin install <new-plugin>@<marketplace>
/reload-plugins
```
Then exercise via `plugin-tester`.

### 8. Hand off to plugin-publisher

If the user wants to push, hand off to `plugin-publisher`.

## References

- `references/marketplace-schema.md` — full marketplace.json schema.
- `references/source-types.md` — when to use each source type.
- `references/reserved-names.md`

## Scripts

- `scripts/init_marketplace.py`
- `scripts/edit_marketplace.py` — safe JSON editor that preserves formatting.
```

---

### `skills/plugin-publisher/SKILL.md`

```markdown
---
name: plugin-publisher
description: Walks a Claude Code plugin through the publish flow — version bump, CHANGELOG entry, git tag via `claude plugin tag`, push to GitHub, and marketplace.json update. This skill should be used whenever the user asks to "publish my plugin", "release a new version", "ship v1.x", "tag and push", "cut a release", or otherwise wants to make a plugin update available to users. Hard-gates on plugin-validator success and recommends plugin-tester before pushing.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: "<patch|minor|major|x.y.z>"
---

# Plugin Publisher

## When to use this skill

- The plugin is in a finished state on a feature branch.
- The user wants to release a new version (or the first version).

## Versioning decision tree

Before bumping:

1. **Is `version` set in `plugin.json`?**
   - **No** (commit-SHA versioning): every push is automatically a new version. Skip the bump steps; just run validate/test/push.
   - **Yes** (explicit semver): proceed.
2. **What kind of change?**
   - Breaking → MAJOR
   - New feature, additive → MINOR
   - Bug fix, doc, internal → PATCH
3. **Avoid version drift**: if `version` is also set in `marketplace.json`, plugin.json wins silently. Pick one source of truth (plugin.json recommended).

## Procedure

1. **Validate**: invoke `plugin-validator`. Hard-gate: errors must be 0.
2. **Test**: invoke `plugin-tester`. Recommended; ask user before skipping.
3. **Bump version**:
   - Edit `plugin.json` `"version"` to new semver.
   - If `marketplace.json` has a `version` for this plugin entry, sync it (or remove it to avoid drift).
4. **Update CHANGELOG.md**: prepend a section with the new version, date, and bullet list of changes (added/changed/fixed/removed).
5. **Commit**: `git commit -am "Release <plugin-name> v<version>"`.
6. **Tag** (from inside the plugin's directory):
   ```bash
   cd plugins/<plugin-name>
   claude plugin tag --push
   ```
   This creates a `<plugin-name>--v<version>` git tag and pushes it. Use `--dry-run` first to preview.
7. **Update the marketplace entry**: hand off to `plugin-marketplace-manager` to sync metadata if needed.
8. **Push the marketplace**: `git push origin main`.
9. **Notify users**: if private, share `/plugin marketplace update <name>` instructions.
10. **Verify**: in a clean session, `/plugin marketplace update <name>`, then `/plugin update <plugin>@<marketplace>` and confirm the new version installs.

## Common pitfalls

- **Bumping version but forgetting to push** → users on `/plugin update` see "already at the latest version".
- **Setting `version` in both manifests** → plugin.json wins, marketplace.json bump is silently ignored.
- **Forgetting to bump `version` when set explicitly** → no users get the update.
- **Tagging from outside the plugin dir** → `claude plugin tag` fails.

## References

- `references/release-checklist.md`
- `references/changelog-format.md`
- `references/version-resolution.md` — Claude Code's exact version-resolution order.

## Scripts

- `scripts/bump_version.py` — semver bump in plugin.json + marketplace.json.
- `scripts/update_changelog.py`
```

---

### `skills/plugin-improver/SKILL.md`

```markdown
---
name: plugin-improver
description: Reviews an existing Claude Code plugin and proposes a ranked list of improvements — clearer descriptions, missing components, validation issues, frontmatter cleanup, dead `${CLAUDE_PLUGIN_ROOT}` references, undocumented user-config, missing CHANGELOG, weak skill descriptions, and more. This skill should be used whenever the user asks to "review my plugin", "what's missing", "improve this plugin", "audit", "make this plugin better", or hands over a plugin they did not author. Internally invokes plugin-validator and plugin-component-author.
allowed-tools: Read, Edit, Bash, Glob, Grep
argument-hint: "[path-to-plugin]"
---

# Plugin Improver

Analogous to Anthropic's `skill-improver`. Reads a plugin, scores it across dimensions, proposes specific edits, applies them with consent.

## When to use this skill

- Inheriting an existing plugin.
- Pre-publish quality pass.
- Periodic audits.

## Dimensions

1. **Manifest hygiene** — required fields, kebab-case, version strategy, license, repository, homepage, keywords, author. Flag missing or weak.
2. **Directory layout** — anything inside `.claude-plugin/` that shouldn't be; CLAUDE.md at root; orphaned files.
3. **Validation** — invoke `plugin-validator`; surface errors and warnings.
4. **Description quality** — every command/skill/agent description checked: third person, action-oriented, includes trigger phrasings, "pushy" enough, ≤1,536 chars combined with `when_to_use`.
5. **Component coverage** — does the plugin describe behavior the user mentions but doesn't actually implement? Are there obvious missing hooks (e.g. plugin claims to "auto-format on save" but ships no `PostToolUse` hook)?
6. **Tool restrictions** — agents and skills with no `allowed-tools` or with overly broad tool grants (e.g. `Bash` instead of `Bash(git:*)`).
7. **Path hygiene** — absolute paths, `..` traversal, missing `${CLAUDE_PLUGIN_ROOT}`, dead references.
8. **Documentation** — README.md present and useful; CHANGELOG.md present; user-config documented.
9. **Cross-platform** — Windows/PowerShell handling for hook scripts; `cmd /c` wrapper for stdio MCP `npx`.
10. **Vanguard/AAA layer** — if the user signals Vanguard/Orion/AAA, hand off to `vanguard-plugin-conventions` for additional checks.

## Procedure

1. Read all files in the plugin (`Glob` + `Read`).
2. Run validator and capture report.
3. Run static dimension checks (`scripts/improve_plugin.py`).
4. Produce a prioritized improvement report:
   ```
   Plugin: foo  v1.2.0
   Score: 72/100
   ─────────────────────────────────
   HIGH PRIORITY
   1. [ERROR] hooks/hooks.json:12 — missing ${CLAUDE_PLUGIN_ROOT}
   2. [WARN]  agents/reviewer.md — no allowed-tools (full toolbox grant)
   MEDIUM
   3. README.md missing
   4. Skill description in second person ("Use this skill to…")
   LOW
   5. Add `keywords` to plugin.json for discovery
   ```
5. For each accepted improvement, either edit directly or hand off to `plugin-component-author` (for new components) / `plugin-marketplace-manager` (for catalog updates).
6. Re-run `plugin-validator`. Confirm green before declaring done.
7. (Optional) Hand off to `plugin-tester` for regression.

## References

- `references/improvement-rubric.md`
- `references/description-patterns.md`

## Scripts

- `scripts/improve_plugin.py`
```

---

### `skills/vanguard-plugin-conventions/SKILL.md` *(optional Vanguard layer)*

```markdown
---
name: vanguard-plugin-conventions
description: Applies Vanguard Marketing Analytics & Experimentation Lead conventions to Claude Code plugins — Vanguard/Orion naming, AAA (Agile Agentic Analytics) framework references, scrum-master/astack orchestration patterns, athena-analyst and experiment-analyst sub-agent integration, and agentli memory-hierarchy hooks. This skill should be used whenever the user mentions Vanguard, Orion, AAA, astack, gstack, scrum-master, athena-analyst, experiment-analyst, agentli, or asks to "apply Vanguard conventions" / "make this Orion-team-ready" / "use AAA patterns". Layers on top of plugin-creator and plugin-improver outputs without replacing them.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Vanguard Plugin Conventions

Adds Brian's Vanguard Orion-team conventions to a generic plugin. Always layered on top of `plugin-creator` or `plugin-improver`, never run alone.

## When to use this skill

- The user explicitly mentions Vanguard, Orion, AAA, astack, scrum-master, athena-analyst, experiment-analyst, agentli, or vanguard-plugin-template.
- The user asks "make this Orion-ready" or similar.

## Conventions to apply

### Naming
- Plugin name prefix: `vanguard-` or `orion-`.
- Slash-command verbs map to AAA framework verbs (e.g. `/vanguard-x:plan`, `/vanguard-x:experiment`, `/vanguard-x:analyze`, `/vanguard-x:retro`).

### AAA framework references
- Add to `plugin.json` `keywords`: `["vanguard", "orion", "aaa", "agentic-analytics"]`.
- README references the AAA framework's four phases (planning, design, execution, retrospective).

### Astack pattern
- If the plugin orchestrates anything analytical, define a `scrum-master` subagent in `agents/scrum-master.md` that delegates to:
  - `agents/athena-analyst.md` — exploratory analysis
  - `agents/experiment-analyst.md` — experiment readouts
- The scrum-master's frontmatter `description` mentions the astack analytics adaptation of Garry Tan's gstack so Claude routes correctly.

### agentli memory hooks
- Add `SessionStart` and `InstructionsLoaded` hooks that call `agentli` to keep CLAUDE.md hierarchies fresh:
  ```json
  {
    "hooks": {
      "SessionStart": [{
        "hooks": [{
          "type": "command",
          "command": "${CLAUDE_PLUGIN_ROOT}/scripts/agentli-sync.sh"
        }]
      }]
    }
  }
  ```

### vanguard-plugin-template alignment
- Diff the plugin against `weisberg/agent_tools/plugins/vanguard-plugin-template`. Surface drift and offer to sync.

### SKILL.md conventions
- Skills follow the AAA SKILL.md pattern: a "When to use this skill" section, a "Procedure" section, a "References" section, third-person descriptions, "pushy" trigger language.

## Procedure

1. Detect signals (user keywords, existing files in the plugin).
2. Read `vanguard-plugin-template/` if present in the marketplace.
3. Diff target plugin against template; surface a checklist.
4. Apply each convention with user consent (don't bulk-edit).
5. Re-run `plugin-validator`.

## References

- `references/aaa-framework.md`
- `references/astack-pattern.md`
- `references/agentli-integration.md`
- `references/vanguard-naming.md`
```

---

## 4. Supporting `references/` and `scripts/`

These are stubs/specifications for the bundled files each skill references. Brian or `skill-creator` can flesh them out during install.

### `references/` files (consolidated)

| Skill | File | Contents |
|---|---|---|
| plugin-creator | `references/manifest-schema.md` | Full plugin.json schema (table from §1.1). |
| plugin-creator | `references/directory-layout.md` | Tree from §1.3 + the "must NOT be inside `.claude-plugin/`" warning. |
| plugin-creator | `references/version-strategy.md` | Decision tree for explicit-semver vs commit-SHA. |
| plugin-component-author | `references/commands.md` | Frontmatter table + canonical command file example, namespacing rules. |
| plugin-component-author | `references/agents.md` | Frontmatter table including the "no hooks/mcpServers/permissionMode" plugin restriction and `isolation: worktree`. |
| plugin-component-author | `references/skills.md` | Skill structure, frontmatter, progressive disclosure, third-person rule, **explicit instruction to delegate body authoring to skill-creator**. |
| plugin-component-author | `references/hooks.md` | Hooks.json schema, full event list, exit-code-2 effect table, JSON output decision-control patterns, env vars. |
| plugin-component-author | `references/mcp.md` | .mcp.json schema, stdio/http/sse, `${CLAUDE_PLUGIN_ROOT}`, plugin vs user MCP differences, Windows `cmd /c` note. |
| plugin-component-author | `references/env-substitution.md` | The four substitution scopes (`${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${user_config.*}`, `${ENV_VAR}`) with examples. |
| plugin-validator | `references/error-catalog.md` | All known errors and warnings from the docs, with fixes. |
| plugin-validator | `references/static-checks.md` | Each static check spec, with the regex / rule. |
| plugin-tester | `references/test-recipes.md` | One per component type: test command, expected behavior, debug output. |
| plugin-tester | `references/debug-flags.md` | `--debug`, `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1`, `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS=300000`, cache reset. |
| plugin-marketplace-manager | `references/marketplace-schema.md` | Schema from §1.2. |
| plugin-marketplace-manager | `references/source-types.md` | Source-type comparison table; relative-path footgun. |
| plugin-marketplace-manager | `references/reserved-names.md` | The reserved-name list. |
| plugin-publisher | `references/release-checklist.md` | The full publish-flow checklist. |
| plugin-publisher | `references/changelog-format.md` | Keep-a-Changelog template. |
| plugin-publisher | `references/version-resolution.md` | The 4-step version resolution order. |
| plugin-improver | `references/improvement-rubric.md` | The 10 dimensions with scoring. |
| plugin-improver | `references/description-patterns.md` | Pulled from Anthropic's skill-creator: third-person, "pushy", trigger phrasings, examples. |
| vanguard-plugin-conventions | `references/aaa-framework.md`, `astack-pattern.md`, `agentli-integration.md`, `vanguard-naming.md` | Brian-specific docs (he authors). |

### `scripts/` files (specifications)

```
plugin-creator/scripts/
  scaffold_plugin.py              # CLI: scaffold_plugin.py <name> --dir ./plugins
                                  # Creates dirs, writes plugin.json, README, CHANGELOG, stubs.
  manifest_template.json

plugin-component-author/scripts/  # (none required; logic lives in references)

plugin-validator/scripts/
  validate_static.py              # All static checks; returns JSON report.

plugin-tester/scripts/
  generate_test_plan.py           # Reads plugin.json + dirs; emits markdown test plan.

plugin-marketplace-manager/scripts/
  init_marketplace.py             # Creates .claude-plugin/marketplace.json.
  edit_marketplace.py             # JSON-Patch-style add/update/remove that preserves formatting.

plugin-publisher/scripts/
  bump_version.py                 # CLI: bump_version.py <patch|minor|major|x.y.z>
                                  # Reads/writes plugin.json + marketplace entry.
  update_changelog.py

plugin-improver/scripts/
  improve_plugin.py               # 10-dimension scorer; emits ranked improvement report.

vanguard-plugin-conventions/scripts/
  agentli-sync.sh                 # Stub; calls into Brian's agentli tool.
  diff_against_template.py
```

All Python scripts should be **stdlib-only** (per Anthropic's skill conventions) so they run in any environment without `pip install`.

---

## 5. Installation guidance

### Where this lives

The deliverable is a single plugin `plugin-development-toolkit` placed at:

```
weisberg/agent_tools/                              # marketplace repo root
├── .claude-plugin/
│   └── marketplace.json                           # ← edit this
└── plugins/
    └── plugin-development-toolkit/                # ← drop the whole tree here
        ├── .claude-plugin/
        │   └── plugin.json
        ├── README.md
        ├── CHANGELOG.md
        └── skills/
            ├── plugin-creator/
            │   ├── SKILL.md
            │   ├── references/
            │   └── scripts/
            ├── plugin-component-author/
            ├── plugin-validator/
            ├── plugin-tester/
            ├── plugin-marketplace-manager/
            ├── plugin-publisher/
            ├── plugin-improver/
            └── vanguard-plugin-conventions/        # optional
```

### `plugins/plugin-development-toolkit/.claude-plugin/plugin.json`

```json
{
  "name": "plugin-development-toolkit",
  "description": "Full-lifecycle Claude Code plugin development: create, modify, validate, test, publish, improve. Includes seven generic skills plus an optional Vanguard/AAA conventions layer.",
  "author": {
    "name": "Brian Weisberg",
    "url": "https://github.com/weisberg"
  },
  "homepage": "https://github.com/weisberg/agent_tools/tree/main/plugins/plugin-development-toolkit",
  "repository": "https://github.com/weisberg/agent_tools",
  "license": "MIT",
  "keywords": ["claude-code", "plugin", "scaffold", "validator", "marketplace", "publish", "vanguard", "orion", "aaa"]
}
```

Note: `version` is intentionally **omitted** — this gives you commit-SHA versioning, so every push to the marketplace counts as a new version (per §1.2 / version-resolution).

### `marketplace.json` entry to add

Add this object to the `plugins` array of your existing `weisberg/agent_tools/.claude-plugin/marketplace.json`:

```json
{
  "name": "plugin-development-toolkit",
  "source": "./plugins/plugin-development-toolkit",
  "description": "Full-lifecycle Claude Code plugin development: create, modify, validate, test, publish, improve. Includes seven generic skills plus an optional Vanguard/AAA conventions layer.",
  "category": "development",
  "tags": ["plugin-dev", "scaffold", "validator", "marketplace", "publisher"]
}
```

Do **not** set `version` here either, for the same reason. If you ever decide you want pinned semver releases, add `"version": "1.0.0"` to `plugin.json` (only) and bump on every release.

### Installation steps for end users (and for Brian to test)

```bash
# In any Claude Code session:
/plugin marketplace update weisberg-agent-tools     # if already added
# or, first time:
/plugin marketplace add weisberg/agent_tools

/plugin install plugin-development-toolkit@<your-marketplace-name>
/reload-plugins
```

Then trigger any of the skills:

```bash
/plugin-development-toolkit:plugin-creator       # explicit invocation
# — or just describe the task naturally —
"Create a new plugin called orion-experiments with a hook that lints SQL files."
```

### Testing the toolkit before publishing

```bash
# From the repo root:
claude --plugin-dir ./plugins/plugin-development-toolkit
/reload-plugins
# Try each skill in the new session:
/plugin-development-toolkit:plugin-creator new-test-plugin
```

Use the toolkit's own `plugin-validator` and `plugin-tester` to validate itself before pushing — a good dogfooding gate.

---

## 6. Open questions / things to verify

These are places where the docs were ambiguous, behavior is in flux, or I made a design judgment that's worth confirming:

1. **`marketplace.json` `version` field** — the docs document it as optional, but a community blogger (just-be.dev) reports Anthropic never bumps it in their own marketplace and "so far as I can tell it's not used anywhere." Likely safe to set or omit; I recommend **omitting** to avoid drift with `plugin.json`.

2. **`$schema` URLs** — Anthropic's published `https://anthropic.com/claude-code/marketplace.schema.json` 404s (issue #9686). The community-supplied `https://json.schemastore.org/claude-code-marketplace.json` and `https://json.schemastore.org/claude-code-plugin-manifest.json` from `hesreallyhim/claude-code-json-schema` are unofficial but more reliable for editor autocomplete. Use those in `$schema` if you want IDE help.

3. **`claude plugin validate` exact output format** — I have docs on what it *checks* (plugin.json, marketplace.json, frontmatter, hooks.json) and a few example errors, but not the exact stdout/stderr format. The plugin-validator skill should `Read` the actual output during operation rather than assume a format.

4. **`claude plugin tag` semver expectations** — docs reference a `<plugin-name>--v<version>` git tag convention used for dependency resolution (per `plugin-dependencies` doc). I haven't fully read that page; if Brian uses commit-SHA versioning, `claude plugin tag` may be unnecessary. Confirm before relying on it in `plugin-publisher`.

5. **Subdirectory namespacing for commands** — Steve Kinney's blog says `commands/frontend/component.md` → `/plugin:frontend:component`. This is **not** in the official Plugins reference for plugin commands specifically (it's documented for user commands). Verify before relying on it inside plugin scaffolds; safer default is flat command files.

6. **Plugin agent `color` frontmatter** — issue #8501 in `anthropics/claude-code` documents that `color` is widely used in community examples and built-in commands but is not officially documented. The plugin-component-author skill includes it as optional with a note. Treat as supported-but-undocumented.

7. **`claude plugin tag` working dir** — I'm relying on docs that say "run from inside the plugin's folder", but if Brian's plugins are a sibling to a marketplace.json at the repo root, this works fine. For monorepo setups you may need `cd plugins/<name>` first.

8. **`vanguard-plugin-template` exact structure** — I have not seen Brian's actual template; the `vanguard-plugin-conventions` skill should `Glob` and `Read` it during operation, not assume a layout. Consider adding a `references/template-snapshot.md` once Brian shares it.

9. **`agentli` integration surface** — I described an `agentli-sync.sh` placeholder. Brian should provide the actual command-line interface so the SessionStart hook calls work.

10. **Whether to bundle this as a plugin or as user-scope skills** — I chose plugin-bundling because that's what Brian asked for and what fits his marketplace. If he ever wants these skills to have **un-namespaced** invocations (e.g. `/plugin-creator` not `/plugin-development-toolkit:plugin-creator`), he'd need to install them at user scope under `~/.claude/skills/` instead. The trade-off is loss of versioning and team-distribution.

11. **Char budget for skill listings** — combined description+`when_to_use` is capped at 1,536 chars, and the global skill listing budget defaults to 8,000 chars or 1% of context window (whichever is greater). With 8 skills in this toolkit averaging ~600 chars each, you're at ~4,800 chars — comfortable. But if Brian installs many more plugins, descriptions may get truncated; raise `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var or set lower-priority skills to `"name-only"` in `skillOverrides`.

12. **Plugin-shipped `settings.json`** — only `agent` and `subagentStatusLine` keys are honored. Don't try to ship `permissions` or `hooks` via the plugin's `settings.json` — use `hooks/hooks.json` for hooks and rely on user-side permission settings.