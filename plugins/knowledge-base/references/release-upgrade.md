# Knowledge Base Release And Upgrade Notes

Use this reference and `/plugin-manager:plugin-release` when shipping KB plugin
changes.

## Version Rules

- Patch: docs, examples, validation fixes.
- Minor: new skills, new vaultli commands, new workflow behavior.
- Major: breaking path, schema, command, or plugin install behavior.

## Validation Bundle

```bash
npm run render:check
npm run validate
python3 -m json.tool .claude-plugin/marketplace.json
python3 -m json.tool .agents/plugins/marketplace.json
python3 -m json.tool plugins/knowledge-base/.claude-plugin/plugin.json
python3 -m json.tool plugins/knowledge-base/.codex-plugin/plugin.json
claude plugin validate plugins/knowledge-base
CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(pwd)/plugins/knowledge-base}"
python3 "${CLAUDE_PLUGIN_ROOT}/../plugin-manager/skills/plugin-health/scripts/plugin_audit.py" --plugin knowledge-base --json
python3 -m pytest tests/test_knowledge_base tests/test_plugins
```

Add vaultli-specific Rust/Python parity tests when code changes touch `vaultli/`.

## Upgrade Note Template

```markdown
## Knowledge Base Plugin Upgrade

- Version: old -> new
- User-visible changes:
- Existing vault action required:
- New validation command:
- Rollback:
```
