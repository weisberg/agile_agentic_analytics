# Agile Agentic Analytics

A Claude Code plugin marketplace for agile agentic analytics.

## Installation

Add this marketplace to Claude Code:

```
/plugin marketplace add weisberg/agile_agentic_analytics
```

Then browse and install plugins:

```
/plugin
```

Or install a specific plugin directly:

```
/plugin install <plugin-name>@agile-agentic-analytics
```

## Available Plugins

_No plugins yet. See [Creating a Plugin](#creating-a-plugin) to add one._

## Creating a Plugin

Each plugin lives in its own directory under `plugins/`. The minimum structure is:

```
plugins/my-plugin/
├── .claude-plugin/
│   └── plugin.json        # Plugin manifest (required)
├── skills/                 # Custom slash commands
│   └── my-skill/
│       └── SKILL.md
├── agents/                 # Custom subagents
│   └── my-agent.md
├── hooks/                  # Event handlers
│   └── hooks.json
├── .mcp.json               # MCP server configs
├── .lsp.json               # LSP server configs
├── settings.json           # Default settings
└── README.md
```

### plugin.json

```json
{
  "name": "my-plugin",
  "description": "What the plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  },
  "license": "MIT"
}
```

After creating your plugin directory, register it in `.claude-plugin/marketplace.json`:

```json
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin",
  "description": "What the plugin does"
}
```

## License

MIT
