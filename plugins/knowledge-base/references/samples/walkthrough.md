# Sample Vault Walkthrough

The synthetic mini vault under `references/samples/mini-vault` demonstrates:

- people, company, concept, meeting, source, article, and strategic-reading pages
- a non-markdown SQL asset with a sidecar
- frontmatter fields used by `vaultli`
- citations, back-links, and relationship hints

Expected agent flow:

```bash
CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(pwd)/plugins/knowledge-base}"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search "renewal risk" --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json context --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault" --id companies/acme-example
```

All names are synthetic.
