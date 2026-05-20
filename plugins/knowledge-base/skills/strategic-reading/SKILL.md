---
name: strategic-reading
version: 0.1.0
description: Read a book, article, transcript, or case study through the lens of a specific strategic problem you're facing. Produces an applied playbook that maps the source onto the problem and gives short/medium/long-term recommendations. NOT for general book summaries.
triggers:
  - "strategic reading"
  - "read this through the lens of"
  - "apply this to my problem"
  - "what can I learn from this about"
  - "extract a playbook from"
mutating: true
writes_pages: true
writes_to:
  - concepts/
  - projects/
---

# strategic-reading - Applied Analysis from Source Texts

> **Convention:** see `../ingest/references/quality.md` for citation rules and
> back-link expectations.
>
> **Convention:** see `../ingest/references/kb-filing-rules.md` for filing by
> primary subject: `concepts/` for general strategy, `projects/` for
> problem-tied playbooks.

## What this is

Take a large text PLUS a specific strategic problem, then produce analysis that
maps the text's insights onto the problem. This is not book summarization. This
is reading with a mission.

Where a general book-summary workflow explains a source on its own terms,
`strategic-reading` personalizes it to ONE current problem. Same rough shape
(extract -> analyze -> mirror), different lens.

**Canonical example:** a power-dynamics history book read against a specific
gatekeeper-vs-incumbent fight, producing a tactical analysis that maps the
book's playbook onto the situation with counter-tactics and a
short/medium/long-term playbook.

## Inputs

1. **Source text** - book (EPUB/PDF), article, transcript, historical case
   study, or any large document.
2. **Strategic problem** - the specific situation to analyze through the lens of
   the text. The user describes this explicitly, or it is obvious from context.

If either input is missing, ask for the missing piece before producing the
playbook. Do not silently turn this into a generic summary.

## Output

The knowledge base page is the artifact. PDF or other rendering is optional and
never primary.

### Knowledge base page structure

```markdown
# [Source Title] - Applied to [Problem]

> One-paragraph executive summary: how the source maps to the situation,
> the key insight, the bottom line.

## The Core Parallel
How the source's central dynamic maps onto the user's situation.

## Chapter / Section Triage
For each major section of the source:
- 2-3 sentence summary of what it says
- Relevance to the problem: HIGH / MEDIUM / LOW
- One directly applicable quote, if any

## The Source's Playbook
The author's framework, tactics, or strategies, organized as:
- What the protagonist DID (tactics)
- What WORKED and why
- What FAILED and why
- What OPPONENTS did that was effective

## Counter-Tactics
Specific moves from the source that map to the user's situation:
- What to DO, with source evidence
- What to AVOID, with source evidence
- What to WATCH FOR, with warning signs from the source

## Applied Playbook
The synthesis - actionable recommendations:
- **Short-term** (this week / this month)
- **Medium-term** (this quarter)
- **Long-term** (this year+)

## Key Quotes
Direct quotes from the source that are devastatingly relevant.
Maximum 5-10. Quality over quantity.

## See Also
Links to relevant KB pages (related concepts, related projects).
```

## Process

```text
Phase 1: Ingest the source
  - EPUB: extract chapters with a reliable EPUB/text pipeline.
  - PDF: use pdftotext -layout or OCR when needed.
  - Article: fetch the content and preserve URL/publication/date.
  - Transcript: preserve speaker labels when available.
  - Identify table of contents and total size.

Phase 2: Triage chapters/sections
  - Read the first 2000 chars of each chapter or major section.
  - Classify relevance to the problem: HIGH / MEDIUM / LOW.
  - HIGH sections get full reads. MEDIUM sections get partial reads. LOW sections are skipped.

Phase 3: Deep read HIGH sections
  - Tactics and strategies used.
  - Power dynamics and how they shifted.
  - Specific quotes that map to the problem.
  - Moments where the protagonist's approach succeeded or failed.

Phase 4: Synthesize
  - Map source insights onto the specific problem.
  - Build the playbook: do / avoid / watch for.
  - Generate short/medium/long-term recommendations.
  - Select the most relevant quotes.

Phase 5: Write and deliver
  - Write the KB page at the right location:
      * If problem-specific: projects/<slug>/playbook.md
      * If general strategy: concepts/<slug>.md
  - Use the standard KB write flow.
  - For file-based KB vaults, run vaultli index and vaultli validate.
  - Optional: render to PDF or another shareable format after the KB page is complete.
```

## Quality bar

- **Every recommendation must cite the source.** Do not say "go direct to the
  mayor"; say "go direct to the mayor, because when the protagonist refused to
  be intimidated by a resignation threat (Ch 48), the bluff that worked on five
  mayors finally failed."
- **Direct quotes are mandatory.** The source's own words carry more weight
  than paraphrase.
- **The analysis must be actionable.** Not "this is interesting", but "do this,
  avoid that, watch for this."
- **Short/medium/long-term breakdown is mandatory.** The user needs to know what
  to do tomorrow and what to do this year.
- **The problem lens must stay visible.** Every section should make clear how
  the source maps, or does not map, to the actual strategic problem.

## What this skill is NOT

- Not a book summary tool. Use a different skill for general summaries.
- Not a research tool. Use a research workflow for finding new information about
  a topic.
- Not academic literary analysis. Literary merit is secondary to strategic
  application.
- Not a quote dump. Quotes support the playbook; they are not the playbook.

## Related skills

- `skills/ingest/SKILL.md` - route and preserve the source in the KB.
- `skills/vaultli/SKILL.md` - index and validate file-based KB artifacts.
- `skills/ask-user/SKILL.md` - gate if the strategic problem is ambiguous.
- `skills/skillify/SKILL.md` - make this or adjacent workflows more complete.

## Contract

This skill guarantees:

- Routing matches the canonical triggers in the frontmatter.
- Output is written under the directories listed in `writes_to:` when applicable.
- KB citation, filing, and back-link conventions are followed.
- The output is an applied strategic playbook, not a generic source summary.
- Privacy contract is preserved: no unnecessary real names, no fork-specific
  filesystem path literals, and no upstream-fork references in deliverables.

The full behavior contract is documented in the body sections above; this
section exists for conformance tests.

## Output Format

The skill's output shape is documented inline above in "Knowledge base page
structure". The literal section header here exists for conformance tests.

## Anti-Patterns

- Producing a generic book or article summary.
- Treating every chapter as equally relevant instead of triaging against the
  problem lens.
- Making recommendations without source citations.
- Paraphrasing when a short direct quote would carry the argument.
- Writing a clever analysis that does not produce concrete do/avoid/watch-for
  moves.
- Skipping the short/medium/long-term breakdown.
