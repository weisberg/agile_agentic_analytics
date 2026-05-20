---
name: academic-verify
version: 0.1.0
description: >-
  Verify academic claims against original papers, replication status, methods, data, and limitations before they enter the KB.
triggers:
  - "academic verify"
  - "verify this study"
  - "check this paper"
  - "has this been replicated"
tools:
  - search
  - read
  - write
  - vaultli
mutating: true
writes_pages: true
---

# Academic Verify

## Contract

- Academic claims are traced to primary sources where available.
- Replication, sample, method, measurement, and limitation notes are explicit.
- Unverified or overstated claims are labeled before reuse.

## Workflow

- Extract the exact claim and citation chain.
- Find primary paper, DOI, authors, date, and publication venue.
- Check methods, sample, effect size, limitations, and replication signals.
- Write verification status and citation into relevant KB page.
- Route unresolved current facts to `current-research`.

## Output Format

- ACADEMIC VERIFICATION
- Claim, source, status, limitations, KB update.

## Anti-Patterns

- Relying on a secondary article for a technical claim.
- Ignoring failed replication or narrow samples.
