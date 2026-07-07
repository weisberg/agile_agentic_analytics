# KB Privacy And Security Model

## Scope

- `personal`: only the owner should see this.
- `team`: internal team context.
- `org`: broad internal context.
- `public`: safe to publish.

## Sensitive Signals

- API keys, tokens, passwords, secrets.
- Personal addresses, phone numbers, medical/therapy content.
- Private repository paths and local absolute paths.
- Internal channels, client names, unreleased deal names.
- Authenticated browser captures.

## Required Checks

1. Classify scope before writing or publishing.
2. Redact secrets before raw source preservation.
3. Use aliases for sensitive people/entities when publication is possible.
4. Keep raw private content out of checkpoints and review artifacts.
5. Require approval before changing scope from personal/team to public.

Use `health` for vault/privacy audits and `publish` for final sharing gates.
