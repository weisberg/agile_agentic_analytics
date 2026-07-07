# KB Retrieval Reference

Detail behind the `query` skill. `query` owns retrieval end to end: mode
selection, source-scope routing, and graph expansion are sections of one skill,
not separate skills. This reference is the depth `query` points to.

## 1. Retrieval Mode Selection

Classify the question first, then pick the mode. Do not default to semantic
overlap.

| Question type | Mode | First tool |
| --- | --- | --- |
| known slug, id, title, exact phrase | exact | `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search`, `rg` |
| tags, category, status, domain, scope | metadata | `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search --category --tag` |
| "read the actual page" | body hydrate | `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json resolve --body`, `cat` |
| people, companies, relationships | graph | back-link traversal (below) |
| dates, meetings, events, sequence | timeline | `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search` + page timelines |
| concept / fuzzy topic | semantic-overlap | `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search --semantic` |
| across multiple vaults or scopes | federated | `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json federated-search` |
| current / external developments | freshness | hand off to `current-research` |

Rules:

- Use metadata filters before semantic overlap; overlap is token matching over
  indexed metadata, not a vector database.
- Search results are **pointers**. Never answer from `search` metadata alone
  when the body or source content matters — hydrate with `resolve`, `cat`, or
  `context`.
- Record misses as benchmark rows (see `retrieval-and-benchmarks.md`) and fix by
  improving titles, descriptions, tags, or relationships — not by masking the
  miss in prose.

## 2. Source-Scope Routing

Every vault or connector has a scope, trust level, privacy boundary, and
retrieval priority. Route before you read.

| Scope | Trust | Default retrieval priority |
| --- | --- | --- |
| personal | high for the owner | first for personal questions |
| team | shared internal | first for team questions |
| org | broad internal | second |
| public / sample | low | last, and only when explicitly relevant |
| external connector | untrusted until verified | fetch, then verify |

Rules:

- Answers cite **which source scope** produced each fact.
- Never merge personal and team facts without labelling their origin.
- Do not search every vault when the scope is obvious; use
  `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json federated-search` only when the
  question genuinely crosses scopes.
- Apply the privacy model in `privacy-and-security.md` before writing or
  publishing anything retrieved from a lower-trust scope.

## 3. Graph Expansion

Relationship questions ("who introduced X to Y", "what connects these") are
answered by traversing typed back-links, not by keyword search.

- Extract the entities in the question and resolve their pages.
- Follow typed edges (`knows`, `works_at`, `founded`, `invested_in`, `met_at`,
  `discussed`) and back-links to build the path.
- Answer with the path, the edge type at each hop, the **source evidence** for
  each edge, and a confidence level.
- If an edge has no source, treat it as unverified and say so.

Graph *maintenance* — creating missing back-links, fixing orphaned or dead
links, repairing untyped co-mention edges — is a repair operation. Route it to
`health` (which audits graph, citations, frontmatter, and stale state) or to
`enrich` when you are already rewriting a page.

## Answer Contract

Every `query` answer separates cited KB facts, inference, and unknowns, and ends
with a freshness delta. When the freshness gap is material, route to
`current-research` rather than guessing.
