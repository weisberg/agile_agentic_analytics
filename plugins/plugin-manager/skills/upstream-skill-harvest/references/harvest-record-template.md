# Upstream Harvest Record Template

Use one record per imported or refreshed skill. Keep source paths stable by
using `$GBRAIN_ROOT`, `$GSTACK_ROOT`, or repo-relative paths instead of absolute
local paths.

```markdown
## plugins/<plugin>/skills/<slug>/SKILL.md

- Source: `$GBRAIN_ROOT/skills/<slug>/SKILL.md`
- Source commit: `<short-sha or unknown>`
- Imported or reviewed: `YYYY-MM-DD`
- Mode: `new-import | refresh | diff-only | ledger-only`
- Frontmatter policy: `preserve-exact | preserve-keys | adapt-with-notes`
- Frontmatter notes: `<what changed, or "unchanged">`
- Adaptation notes: `<terminology, tool, path, or plugin-fit changes>`
- Privacy/path check: `<pass/fail and command>`
- Files included: `<SKILL.md, routing-eval.jsonl, references/...>`
- Files skipped: `<none, or reason>`
- Validation: `<commands and outcomes>`
- Drift status: `current | intentional-fork | needs-refresh | blocked`
- Next review: `<date or cadence>`
```

