# Knowledge Base Upstream Source Ledger

This ledger records source paths, adaptation choices, and review cadence for
skills imported or adapted into the `knowledge-base` plugin.

Use stable aliases rather than absolute local paths:

- `$GBRAIN_ROOT` defaults to the local GBrain checkout.
- `$GSTACK_ROOT` defaults to the local GStack checkout.
- Repo-relative paths refer to this marketplace repository.

Review cadence: monthly for active upstream skills, and before each
knowledge-base plugin release.

## plugins/knowledge-base/skills/ask-user/SKILL.md

- Source: `$GBRAIN_ROOT/skills/ask-user/SKILL.md`
- Source commit: `39e14cd5`
- Imported or reviewed: `2026-05-20`
- Mode: `ledger-only`
- Frontmatter policy: `adapt-with-notes`
- Frontmatter notes: `User-provided frontmatter was kept intact during import.`
- Adaptation notes: `No KB terminology rewrite was needed; this is a generic choice-gate pattern.`
- Privacy/path check: `pass; no absolute local paths or private fork names in target skill`
- Files included: `SKILL.md`
- Files skipped: `none`
- Validation: `manual ledger creation for existing imported skill`
- Drift status: `needs-refresh`
- Next review: `monthly`

## plugins/knowledge-base/skills/ingest/SKILL.md

- Source: `$GBRAIN_ROOT/skills/ingest/SKILL.md`
- Source commit: `39e14cd5`
- Imported or reviewed: `2026-05-20`
- Mode: `ledger-only`
- Frontmatter policy: `adapt-with-notes`
- Frontmatter notes: `Routing fields were preserved and adapted for KB commands and vaultli availability.`
- Adaptation notes: `Converted user-facing brain/GBrain wording to knowledge base, KB, kb, and vaultli terminology. Added file-vault validation guidance.`
- Privacy/path check: `pass; no absolute local paths or private fork names in target skill`
- Files included: `SKILL.md`, `references/kb-filing-rules.md`, `references/quality.md`
- Files skipped: `none`
- Validation: `manual ledger creation for existing imported skill`
- Drift status: `intentional-fork`
- Next review: `monthly`

## plugins/knowledge-base/skills/skillify/SKILL.md

- Source: `$GBRAIN_ROOT/skills/skillify/SKILL.md`
- Source commit: `39e14cd5`
- Imported or reviewed: `2026-05-20`
- Mode: `ledger-only`
- Frontmatter policy: `adapt-with-notes`
- Frontmatter notes: `YAML frontmatter was preserved from the provided source with KB-safe wording in the body.`
- Adaptation notes: `Converted brain filing language to KB filing. Kept explicit GBrain eval command references where the upstream eval gateway is the named tool.`
- Privacy/path check: `pass; no absolute local paths or private fork names in target skill`
- Files included: `SKILL.md`
- Files skipped: `none`
- Validation: `manual ledger creation for existing imported skill`
- Drift status: `intentional-fork`
- Next review: `monthly`

## plugins/knowledge-base/skills/strategic-reading/SKILL.md

- Source: `$GBRAIN_ROOT/skills/strategic-reading/SKILL.md`
- Source commit: `39e14cd5`
- Imported or reviewed: `2026-05-20`
- Mode: `ledger-only`
- Frontmatter policy: `adapt-with-notes`
- Frontmatter notes: `YAML frontmatter was kept and adapted for KB write targets.`
- Adaptation notes: `Converted brain page wording to knowledge base page wording, added KB filing and vaultli validation references, and kept strategic-reading output structure intact.`
- Privacy/path check: `pass; no absolute local paths or private fork names in target skill`
- Files included: `SKILL.md`, `routing-eval.jsonl`
- Files skipped: `none`
- Validation: `manual ledger creation for existing imported skill`
- Drift status: `intentional-fork`
- Next review: `monthly`

## plugins/knowledge-base/skills/vaultli/SKILL.md

- Source: `plugins/knowledge-base/vaultli/SKILL.md`
- Source commit: `631031c`
- Imported or reviewed: `2026-05-20`
- Mode: `ledger-only`
- Frontmatter policy: `adapt-with-notes`
- Frontmatter notes: `Wrapper skill frontmatter was written for plugin routing, not copied exactly from the bundled tool guide.`
- Adaptation notes: `Exposes the bundled vaultli CLI as a KB plugin workflow and points to the full tool guide in the bundled implementation directory.`
- Privacy/path check: `pass; source path is repo-relative and no private fork names are in the wrapper skill`
- Files included: `skills/vaultli/SKILL.md`, `bin/vaultli`, `vaultli/`
- Files skipped: `vaultli/rs/target/` and Python cache files should remain ignored/generated, not curated source`
- Validation: `manual ledger creation for existing imported tool wrapper`
- Drift status: `intentional-fork`
- Next review: `before each knowledge-base plugin release`
