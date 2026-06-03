# Agile Agentic Analytics Agents Guide

Reference `CLAUDE.md` for the full repo operating index. This repository is a
dual-platform plugin marketplace for Claude Code and Codex, so agent work must
preserve both harness surfaces.

## Dual-Platform Marketplace Rules

- Treat `marketplace.yaml` as the only human-edited source of marketplace
  metadata.
- Do not hand-edit generated marketplace or manifest JSON except while debugging
  a renderer failure. Generated files are:
  - `.claude-plugin/marketplace.json`
  - `.agents/plugins/marketplace.json`
  - `plugins/<plugin>/.claude-plugin/plugin.json`
  - `plugins/<plugin>/.codex-plugin/plugin.json`
- After marketplace metadata, plugin versions, component flags, or shared skill
  frontmatter changes, run `npm run render`.
- Before handoff, run at minimum:

```bash
npm run render:check
npm run validate
./scripts/smoke-claude.sh
./scripts/smoke-codex.sh
```

- Shared skills under `plugins/<plugin>/skills/<skill>/SKILL.md` must keep
  frontmatter compatible with both harnesses:

```yaml
---
name: skill-name
description: Short routing description.
disable-model-invocation: false
---
```

- Keep Codex-only metadata in `.codex-plugin/plugin.json` through the renderer,
  and Claude-only metadata in `.claude-plugin/plugin.json` through the renderer.
- If a plugin uses MCP or app files, enable those component flags in
  `marketplace.yaml` only when the corresponding `.mcp.json` or `.app.json`
  exists.
- Claude strict validation is required when the Claude CLI is available. Codex
  validation is structural through `npm run validate` unless a stable local
  Codex plugin validator exists.
- For local Codex marketplace testing, `codex plugin marketplace add ./` is the
  relevant smoke path. `codex plugin marketplace upgrade <name>` applies to
  Git-backed marketplaces, not plain local checkouts.
