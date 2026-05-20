# Sample Vault Walkthrough

The synthetic mini vault under `references/samples/mini-vault` demonstrates:

- people, company, concept, meeting, source, article, and strategic-reading pages
- a non-markdown SQL asset with a sidecar
- frontmatter fields used by `vaultli`
- citations, back-links, and relationship hints

Expected agent flow:

```bash
vaultli --json root plugins/knowledge-base/references/samples/mini-vault
vaultli --json index --root plugins/knowledge-base/references/samples/mini-vault
vaultli --json validate --root plugins/knowledge-base/references/samples/mini-vault
vaultli --json search "renewal risk" --root plugins/knowledge-base/references/samples/mini-vault
vaultli --json context --root plugins/knowledge-base/references/samples/mini-vault --id companies/acme-example
```

All names are synthetic.

