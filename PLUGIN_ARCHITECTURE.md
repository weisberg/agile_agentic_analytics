# Agile Agentic Analytics Plugin Marketplace Architecture

## 1. Purpose

This document explains how the `agile_agentic_analytics` repository is structured as a Claude Code plugin marketplace, how that maps to the official Claude Code plugin system, and how contributors should add new plugins safely and consistently.

It is intentionally both:

- a **repository architecture guide** for this codebase
- a **practical implementation reference** for Claude Code marketplaces and plugins

Where relevant, this document distinguishes between:

- **official Claude Code behavior** documented by Anthropic
- **repository conventions** used in this marketplace

## 2. Architectural Summary

At a high level, the system has three layers:

1. **Marketplace repository**
   - This repository is the marketplace.
   - It exposes `.claude-plugin/marketplace.json`, which is the catalog Claude Code reads to discover available plugins.

2. **Plugin packages**
   - Each plugin lives in its own directory under `plugins/`.
   - A plugin is a self-contained bundle of Claude Code extension components such as skills, agents, hooks, MCP servers, and LSP servers.

3. **Claude Code runtime**
   - Claude Code installs plugins from a marketplace, copies them into its local plugin cache, loads their components, and exposes those capabilities in the CLI and agent runtime.

This means the repository is not just documentation plus examples: it is a distributable marketplace that Claude Code can consume directly.

## 3. Official Claude Code Model vs. This Repository

Claude Code's extension layer is broader than plugins alone. Official docs describe these major mechanisms:

- `CLAUDE.md` for always-loaded instructions
- **skills** for reusable knowledge and workflows
- **subagents** for isolated specialist workers
- **hooks** for deterministic automation
- **MCP servers** for external tools and APIs
- **plugins** as the packaging layer
- **marketplaces** as the discovery and distribution layer

This repository focuses on the last two:

- packaging reusable functionality into plugins
- distributing those plugins through a marketplace catalog

The result is a shareable, versioned, installable set of domain-specific capabilities for agile analytics work.

## 4. Current Repository Layout

The current repository layout is:

```text
agile_agentic_analytics/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── ab-testing/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── agents/
│       │   ├── experiment-auditor.md
│       │   └── statistician.md
│       ├── skills/
│       │   ├── analyze-results/
│       │   │   └── SKILL.md
│       │   ├── design-experiment/
│       │   │   └── SKILL.md
│       │   ├── experiment-report/
│       │   │   └── SKILL.md
│       │   ├── review-experiment/
│       │   │   └── SKILL.md
│       │   └── sample-size/
│       │       └── SKILL.md
│       ├── README.md
│       └── settings.json
├── PLUGIN_ARCHITECTURE.md
└── README.md
```

### What matters operationally

- `.claude-plugin/marketplace.json` is the marketplace entry point.
- `plugins/ab-testing/` is the only currently published plugin.
- The `ab-testing` plugin currently provides:
  - multiple skills
  - two custom agents
  - plugin metadata in `.claude-plugin/plugin.json`
- There are currently no plugin hooks, MCP servers, or LSP servers in this repository, but the architecture supports them.

## 5. Marketplace Architecture

## 5.1 Marketplace manifest

Claude Code expects a marketplace catalog in:

```text
.claude-plugin/marketplace.json
```

In this repository, that file currently looks like:

```json
{
  "name": "agile-agentic-analytics",
  "owner": {
    "name": "Brian Weisberg"
  },
  "metadata": {
    "description": "A marketplace of Claude Code plugins for agile agentic analytics",
    "version": "0.1.0",
    "pluginRoot": "./plugins"
  },
  "plugins": [
    {
      "name": "ab-testing",
      "source": "./plugins/ab-testing",
      "description": "Design, analyze, and review A/B tests with statistical rigor",
      "version": "1.0.0",
      "keywords": ["ab-testing", "experimentation", "statistics", "analytics"],
      "license": "MIT"
    }
  ]
}
```

## 5.2 Meaning of the key fields

### Required marketplace fields

- `name`
  - Public marketplace identifier.
  - Users reference it during installation, for example:
    - `/plugin install ab-testing@agile-agentic-analytics`

- `owner`
  - Marketplace maintainer metadata.

- `plugins`
  - Array of installable plugin entries.

### Useful optional marketplace metadata

- `metadata.description`
  - Human-readable description of the marketplace.

- `metadata.version`
  - Marketplace version identifier.

- `metadata.pluginRoot`
  - A convenience base path for relative plugin sources.
  - This repository sets it to `./plugins`, which aligns with the top-level `plugins/` directory.

## 5.3 Plugin entries inside the marketplace

Each object in `plugins` identifies one installable plugin and where Claude Code should fetch it from.

In this repository, plugin entries are expected to include:

- `name`
- `source`
- `description`
- `version`
- optional discovery metadata such as `keywords`, `license`, `author`, `category`, and `tags`

## 5.4 Plugin source types

Official Claude Code marketplace support is broader than just local relative paths. A plugin entry can point at:

- a relative path inside the marketplace repository
- a GitHub repository
- a generic git URL
- a git subdirectory in a monorepo
- an npm package
- a pip package

This repository currently uses the simplest and most maintainable option:

- **relative in-repo sources**

That keeps each plugin versioned alongside the marketplace itself.

## 5.5 Strict mode

Official marketplace entries support a `strict` field:

- `true` (default): `plugin.json` remains the main authority for component definitions
- `false`: the marketplace entry becomes the full definition, and component declarations in `plugin.json` may conflict

This repository should generally prefer the default behavior:

- let each plugin own its own manifest and component layout
- keep marketplace entries focused on discovery and distribution metadata

That keeps plugin ownership clear and reduces the chance of marketplace/plugin drift.

## 6. Plugin Package Architecture

Each plugin is a self-contained package rooted at its own directory.

The current `ab-testing` plugin illustrates the intended pattern:

```text
plugins/ab-testing/
├── .claude-plugin/
│   └── plugin.json
├── agents/
├── skills/
├── README.md
└── settings.json
```

## 6.1 Plugin manifest

The plugin manifest lives at:

```text
plugins/<plugin-name>/.claude-plugin/plugin.json
```

The current `ab-testing` manifest is:

```json
{
  "name": "ab-testing",
  "description": "Design, analyze, and review A/B tests with statistical rigor",
  "version": "1.0.0",
  "author": {
    "name": "Brian Weisberg"
  },
  "license": "MIT",
  "keywords": ["ab-testing", "experimentation", "statistics", "analytics"]
}
```

### Manifest role

Per official Claude Code behavior:

- `name` is the only required field if a manifest exists
- the manifest is optional when default discovery paths are used
- the manifest is still strongly recommended because it provides identity, metadata, and future extensibility

### Recommended manifest fields for this repository

Every plugin in this marketplace should include:

- `name`
- `description`
- `version`
- `author`
- `license`
- `keywords`

Also consider:

- `homepage`
- `repository`

## 6.2 Default component discovery

Claude Code automatically discovers plugin components from standard locations.

Important default locations include:

- `commands/`
- `agents/`
- `skills/`
- `hooks/hooks.json`
- `.mcp.json`
- `.lsp.json`
- `settings.json`

This repository currently relies on default discovery for:

- `agents/`
- `skills/`

## 6.3 Namespacing behavior

Plugin-provided capabilities are namespaced by plugin name to avoid collisions.

For example:

- the `ab-testing` plugin exposes commands such as `/ab-testing:design-experiment`
- agents are surfaced under plugin-qualified names in Claude Code interfaces

This is a major reason plugins are preferable to copying raw `.claude/` content between repositories: namespacing makes independent distribution safer.

## 7. Supported Component Types

## 7.1 Skills

Skills are reusable knowledge or workflow packages. In plugin form, they typically live under:

```text
skills/<skill-name>/SKILL.md
```

The `ab-testing` plugin uses this pattern extensively:

- `design-experiment`
- `sample-size`
- `analyze-results`
- `experiment-report`
- `review-experiment`

### What skills are good for

Use skills for:

- structured task workflows
- domain guidance
- reference material
- repeatable prompts with arguments

In this repository, skills are the primary way to package experimentation workflows.

## 7.2 Agents

Agents are plugin-provided subagents with isolated context and specialized prompts. They live in:

```text
agents/*.md
```

The current plugin provides:

- `statistician`
- `experiment-auditor`

These are good examples of high-value specialist roles:

- one focuses on rigorous statistical reasoning
- one focuses on experiment design and implementation audit

Use agents when:

- context isolation matters
- a specialist role benefits from a narrow mandate
- a task needs a reusable review persona or operating procedure

## 7.3 Hooks

Hooks are deterministic lifecycle handlers. Officially, plugin hooks can live in:

- `hooks/hooks.json`
- or inline in `plugin.json`

Hooks can respond to many Claude Code events, including:

- `SessionStart`
- `PreToolUse`
- `PostToolUse`
- `SubagentStart`
- `SubagentStop`
- `TaskCompleted`
- `SessionEnd`

Hook handlers can be:

- shell commands
- HTTP calls
- prompt-based checks
- agent-based verification flows

This repository does not currently ship hooks, but hooks are the right place for future deterministic automation such as:

- validating plugin file structure
- checking experiment artifacts after edits
- enforcing contributor conventions

## 7.4 MCP servers

Plugins can bundle MCP server definitions in:

- `.mcp.json`
- or inline in `plugin.json`

MCP is the official mechanism for connecting Claude Code to external tools and services such as:

- issue trackers
- databases
- analytics systems
- communication tools
- internal APIs

For this marketplace, MCP is likely the most important future expansion point because analytics work often depends on external systems such as:

- experimentation platforms
- event warehouses
- BI tools
- Jira or Linear
- incident and observability systems

## 7.5 LSP servers

Plugins can bundle LSP server definitions in:

- `.lsp.json`
- or inline in `plugin.json`

LSP plugins give Claude Code code intelligence such as:

- diagnostics after edits
- go-to-definition
- references
- symbol lookup

This repository does not currently ship LSP plugins. If it later includes language-specific analytics tooling, LSP support would be useful for:

- SQL-heavy codebases
- Python analytics repositories
- TypeScript experimentation frontends

## 7.6 Settings

Plugins can include `settings.json`, but there is an important nuance:

- official Claude Code docs currently document plugin-applied support primarily for the `agent` setting
- unknown keys may be ignored by Claude Code itself

This matters in this repository because `plugins/ab-testing/settings.json` currently stores domain defaults such as:

- significance level
- statistical power
- test sidedness
- default language
- report audience

Those values are useful repository data, but they should be treated as **plugin-owned configuration content**, not as automatically enforced Claude Code platform settings unless supporting runtime logic explicitly reads them.

In other words:

- `settings.json` can be included
- but contributors should not assume arbitrary keys are interpreted by Claude Code automatically

## 8. Installation, Scope, and Lifecycle

## 8.1 Marketplace registration

Users register this marketplace with Claude Code by pointing at the repository:

```text
/plugin marketplace add weisberg/agile_agentic_analytics
```

Claude Code also supports adding marketplaces from:

- GitHub shorthand
- full git URLs
- local filesystem paths
- remote `marketplace.json` URLs

## 8.2 Plugin installation

Once the marketplace is known, users install a plugin from it:

```text
/plugin install ab-testing@agile-agentic-analytics
```

Install scopes officially include:

- `user`
- `project`
- `local`
- `managed` for administrator-controlled installs

These scopes determine where enablement is stored and whether the plugin is shared with collaborators.

## 8.3 Reloading plugin state

When a plugin is installed, enabled, or disabled during an active Claude Code session, users should run:

```text
/reload-plugins
```

That reloads plugin commands, skills, agents, hooks, MCP servers, and LSP servers without restarting the session.

## 8.4 Updates

Marketplace listings can be refreshed with:

```text
/plugin marketplace update agile-agentic-analytics
```

Plugins themselves can also be updated through Claude Code plugin management commands or the interactive `/plugin` UI.

## 8.5 Local development mode

Official Claude Code supports plugin development with:

```text
claude --plugin-dir ./path-to-plugin
```

That is the preferred way to test a plugin in isolation before publishing it in the marketplace.

For this repository, contributor workflow should generally be:

1. create or modify a plugin under `plugins/<name>/`
2. test with `claude --plugin-dir ./plugins/<name>`
3. register the plugin in `.claude-plugin/marketplace.json`
4. verify installation through marketplace flows

## 9. Caching, Path Resolution, and Runtime Environment

## 9.1 Installed plugins are cached

Officially, marketplace-installed plugins are copied into Claude Code's local plugin cache rather than executed from the repository working tree.

This has several consequences:

- installation is decoupled from the source repo checkout
- the runtime sees a cached copy, not the original working directory
- plugin implementations must be self-contained

## 9.2 Path traversal restrictions

Installed plugins cannot safely rely on paths outside their own root. For example:

```text
../shared-utils
```

is not a safe architectural dependency for an installed plugin.

Therefore, every plugin in this repository should be treated as a sealed package:

- bundle what you need inside the plugin directory
- avoid hidden dependencies on sibling directories
- do not rely on repository-relative references outside the plugin root

## 9.3 Runtime environment variables

Claude Code provides two important plugin path variables:

- `${CLAUDE_PLUGIN_ROOT}`
  - absolute path to the installed plugin version
  - use for bundled scripts, assets, and config files

- `${CLAUDE_PLUGIN_DATA}`
  - persistent directory for data that should survive plugin updates
  - use for dependency installs, caches, generated state, or retained artifacts

If this marketplace later adds hooks, MCP servers, or LSP servers, contributors should prefer these variables over hardcoded paths.

## 10. Security Model

Plugins are a high-trust mechanism. Official Claude Code guidance is explicit:

- plugins and marketplaces can execute arbitrary code with the user's privileges
- only trusted marketplaces and plugins should be installed

That makes security a design concern, not just a packaging concern.

## 10.1 Security implications for this repository

Contributors should assume:

- a hook can run shell commands
- an MCP server can reach external systems
- plugin updates can change runtime behavior materially
- installation from private repos may depend on local git credentials or environment tokens

## 10.2 Practical guardrails

This marketplace should follow these rules:

1. **Keep plugins self-contained**
   - Do not depend on undeclared external files outside the plugin root.

2. **Minimize execution surfaces**
   - Only add hooks, MCP servers, or scripts when they provide clear value.

3. **Be explicit about side effects**
   - Plugin READMEs should describe external calls, credentials, and automation behavior.

4. **Use stable relative paths**
   - Paths in manifests should start with `./` where required and remain relative to plugin root.

5. **Do not assume secrets exist**
   - If a future plugin needs credentials, document required environment variables explicitly.

## 11. Contributor Guidelines for This Marketplace

## 11.1 Adding a new plugin

To add a new plugin, follow this structure:

```text
plugins/my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
├── agents/
├── hooks/
│   └── hooks.json
├── .mcp.json
├── .lsp.json
├── settings.json
└── README.md
```

Not every directory is required. Only add what the plugin actually uses.

## 11.2 Minimum recommended plugin contents

For this repository, a production-ready plugin should usually include:

- `.claude-plugin/plugin.json`
- at least one actual component directory or config
- `README.md`
- marketplace registration in `.claude-plugin/marketplace.json`

## 11.3 Naming guidance

- Use kebab-case for plugin names.
- Keep names concise and domain meaningful.
- Ensure skill and agent names are descriptive when namespaced.

Good examples:

- `ab-testing`
- `metric-debugging`
- `experiment-governance`

## 11.4 Versioning guidance

Use semantic versioning for plugin releases:

- bump patch for small improvements and fixes
- bump minor for backward-compatible new capabilities
- bump major for breaking changes in workflows or expected behavior

## 11.5 README expectations

Each plugin README should document:

- installation command
- provided skills, agents, hooks, MCP servers, or LSP servers
- usage examples
- configuration expectations
- external dependencies, if any

## 11.6 Avoid unsupported assumptions

Contributors should avoid undocumented assumptions such as:

- arbitrary `settings.json` keys being automatically applied by Claude Code
- external sibling directories being available after install
- marketplace metadata overriding plugin runtime structure unless `strict` behavior is intentionally used

## 12. Guidance Specific to Analytics Plugins

Because this marketplace is focused on agile analytics, plugins should be biased toward:

- rigorous, auditable workflows
- explicit assumptions
- decision support rather than hidden automation
- reusable domain knowledge

Strong plugin candidates for this repository include:

- experiment design and audit workflows
- metrics definition assistants
- SRM and instrumentation review tools
- analytics warehouse query helpers via MCP
- stakeholder reporting workflows
- post-incident analytics review support

For this domain, skills and agents are usually the best first step. Hooks and MCP servers should be added only when deterministic automation or external connectivity is truly necessary.

## 13. Recommended Evolution of This Repository

The current repository is already a valid marketplace, but its next natural evolution points are:

1. **Add more plugins**
   - Keep each plugin focused on a narrow analytics capability.

2. **Add richer plugin metadata**
   - Consider `homepage`, `repository`, `category`, and `tags` for discoverability.

3. **Introduce MCP-backed plugins carefully**
   - Especially for analytics warehouses, issue trackers, and experiment systems.

4. **Add validation to contributor workflow**
   - Use Claude Code plugin validation and local test installs before publishing changes.

5. **Clarify plugin-owned config semantics**
   - If domain defaults in `settings.json` are meant to be machine-readable, add explicit readers or supporting runtime components rather than relying on implicit behavior.

## 14. Current State Snapshot

As of the current repository state:

- marketplace name: `agile-agentic-analytics`
- maintainer: `Brian Weisberg`
- published plugin count: `1`
- published plugin:
  - `ab-testing`

The `ab-testing` plugin currently represents the reference implementation for future plugins in this marketplace.

## 15. Official Sources Used for This Architecture

This document is grounded primarily in official Claude Code documentation and the official Anthropic marketplace example:

- Claude Code features overview:
  - `https://code.claude.com/docs/en/features-overview`
- Claude Code plugins guide:
  - `https://code.claude.com/docs/en/plugins`
- Claude Code plugins reference:
  - `https://code.claude.com/docs/en/plugins-reference`
- Claude Code plugin marketplaces guide:
  - `https://code.claude.com/docs/en/plugin-marketplaces`
- Claude Code plugin discovery and installation guide:
  - `https://code.claude.com/docs/en/discover-plugins`
- Claude Code hooks reference:
  - `https://code.claude.com/docs/en/hooks`
- Claude Code MCP guide:
  - `https://code.claude.com/docs/en/mcp`
- Official Anthropic marketplace example:
  - `https://github.com/anthropics/claude-code/blob/main/.claude-plugin/marketplace.json`

## 16. Bottom Line

This repository should be understood as:

- a **real Claude Code marketplace**
- currently centered on a single `ab-testing` plugin
- architected to grow into a broader suite of analytics-focused plugins

The core design principle is simple:

> each plugin should be a self-contained, versioned, installable Claude Code extension package, and the repository-level marketplace should make those packages easy to discover, trust, and evolve.
