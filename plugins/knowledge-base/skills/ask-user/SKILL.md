---
name: ask-user
description: >
  Use when a workflow needs to present the user with 2-4 explicit choices and
  wait for their response before proceeding. Trigger on requests or internal
  decision points such as "present options", "ask before proceeding",
  "choice gate", "user decision", destructive operation confirmation,
  ambiguous filing/routing choices, priority triage, or phase gates. This is a
  reusable pattern for other skills that need a human decision before execution.
---

# Ask User - Choice Gate Pattern

## Contract

- Present 2-4 options. Do not exceed four.
- Include an escape hatch such as `Skip`, `Cancel`, or `None of these`.
- Ask one question per message.
- Use self-explanatory option labels: action verb plus brief qualifier.
- Stop the turn immediately after presenting choices.
- Make no follow-up tool calls and take no preemptive action until the user responds.
- On the next turn, acknowledge the user's choice briefly, then branch.

## What This Is

This is the canonical pattern for gating execution on user input. In an agent
workflow, a gate means:

1. Present the choices as buttons if the current platform supports them, or as
   numbered options if it does not.
2. Stop the current turn.
3. Let the user's response trigger the next turn.
4. Read the response and branch accordingly.

This is not a traditional async operation. The stop is part of the protocol.

## When To Use

- Ambiguous requests with multiple valid interpretations.
- Destructive or risky operations such as deletes, overwrites, bulk moves, or irreversible sends.
- Filing and routing decisions such as where a note, artifact, or source should go.
- Priority triage when the user should choose what happens first.
- Workflow phase gates before starting the next import, scan, or enrichment step.
- Any fork where the wrong default would waste significant work or erode trust.

## When Not To Use

- Clear, unambiguous instructions: just do the work.
- Low-stakes decisions: pick the best option and mention the assumption.
- Time-critical operations where waiting costs more than a wrong choice.
- Cases where the user has already expressed a preference.

## How To Present Choices

Use a short question, 1-3 lines of decision context, and numbered options:

```markdown
[Routing] **How should I handle this?**

One to three lines explaining the decision in plain language.

1. **Merge into existing page** - combine this with the matching knowledge page
2. **Create new page** - keep this as a separate knowledge artifact
3. **Skip** - do not file this now
```

If the active environment has a native clarification or choice UI, use it only
when it preserves the same constraints: 2-4 options, one question, escape hatch,
and no execution after the gate is emitted.

## Decision Prefixes

Use a compact text prefix to signal the decision type:

| Prefix | Use for |
| --- | --- |
| `[Routing]` | Filing, merge, destination, or ownership choices |
| `[Risk]` | Destructive, irreversible, security-sensitive, or costly choices |
| `[Priority]` | Triage and sequencing choices |
| `[Strategy]` | Creative, analytical, or strategic forks |
| `[Workflow]` | Process, phase, or import choices |
| `[Security]` | Credential, permission, privacy, or access choices |

## Option Labels

Format labels as `Action verb + short qualifier`.

Good labels:

- `Merge into existing page`
- `Create new meeting page`
- `Archive first`
- `Show list`

Avoid:

- `Option 1`
- `Click here`
- Long labels that force the user to reread the context.

## How To Gate

After presenting choices, stop the turn. Do not:

- Continue with "while you decide..."
- Pick a default and proceed.
- Send follow-up messages before the user responds.
- Run tools or make assumptions about which option they will pick.

End with a brief waiting sentence if helpful, then stop. The gate only works if
the user controls what happens next.

## Handling The Response

When the user responds:

1. Read the selected button, number, or text.
2. Map common text responses gracefully:
   - `the first one`, `A`, or `1` maps to the first option.
   - A word from an option label maps to that option when the match is clear.
   - `none`, `skip`, or `cancel` maps to the escape hatch.
3. Acknowledge briefly: `Got it, going with <choice>.`
4. Execute the chosen branch.
5. If the response is unclear, ask a new single choice-gate question.

If the user sends an unrelated message, treat it as a new request and drop the
pending gate unless the user explicitly returns to it.

## Examples

### Phase Gate

```markdown
[Workflow] **Ready for the next import source?**

The people directory is seeded. I can now import contact data, which may create
about 200 additional pages.

1. **Import contacts** - create pages for matched real contacts
2. **Import from export** - use an offline file instead
3. **Skip** - move to the next phase
```

### Filing Decision

```markdown
[Routing] **Where should this go?**

Meeting notes mention Jane Smith and the Acme deal. Both already have knowledge
pages, so either location could be valid.

1. **Merge into Jane's page** - add this to her timeline
2. **Add to Acme deal page** - treat it as deal context
3. **Create meeting page** - keep the notes standalone
4. **Skip** - do not file this now
```

### Destructive Operation

```markdown
[Risk] **How should I handle stale cache files?**

There are 847 stale cache files using 2.3 GB. They can be recreated, but that
would take several hours.

1. **Delete files** - free up space now
2. **Archive first** - preserve them before deleting
3. **Keep files** - make no changes
4. **Show list** - review before deciding
```

## Integration With Other Skills

Use this pattern from any knowledge-base skill that needs a decision before it
can safely continue, especially:

- Cold-start import phase gates.
- Ingestion routing decisions.
- Entity enrichment merge-vs-create decisions.
- Knowledge filing location choices.
- Meeting-note filing choices.
- Archive scan-vs-ingest gates.

Reference this pattern instead of inventing a new choice format.

## Anti-Patterns

- Continuing the turn after presenting choices.
- Picking a default after asking.
- Presenting more than four options.
- Omitting `Skip`, `Cancel`, or another escape hatch.
- Asking multiple questions in the same gate.
- Using cryptic labels.
- Asking about low-stakes decisions.

## Output Format

The skill's output is the choice-gate message itself:

```markdown
[{decision-type}] **{question}**

{1-3 lines of context}

1. **{Option A label}** - {short qualifier}
2. **{Option B label}** - {short qualifier}
3. **{Skip or Cancel}** - {what skipping means}
```

After emitting this, stop the turn. The user's response triggers the next turn,
where the calling skill branches on the chosen option.
