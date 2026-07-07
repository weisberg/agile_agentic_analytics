# KB Quality Conventions

## Iron Law Back-Linking

Every mention of a person or company that has a knowledge base page must create
a back-link from that entity's page to the page mentioning them.

An unlinked mention is an incomplete KB update because future retrieval will miss
the relationship.

## Citation Discipline

Every factual claim written to a KB page needs an inline source citation with
date and provenance. Prefer exact source references over broad summaries.

## Source Preservation

Raw sources should be preserved before or during transformation so summaries can
be audited later. For large files or media, use the KB raw-file workflow and keep
the redirect pointer with the page.

## vaultli Validation

For file-based KB vaults, use the bundled vaultli wrapper as the integrity
layer:

- create or refresh metadata with `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json add`, `scaffold`, or `ingest`
- rebuild `INDEX.jsonl` with `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index`
- run `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate` before treating ingestion as complete
- use `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search`, `resolve`, `cat`, or `context` for retrieval instead of opening guessed paths
