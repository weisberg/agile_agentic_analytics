# Plugin Manager

Marketplace maintenance workflows for creating, validating, harvesting, syncing,
and publishing shared Claude Code and Codex plugins.

## Skills

| Skill | Description |
|-------|-------------|
| **manage-plugins** | Route plugin maintenance work: create or update plugins, inspect manifests, validate packaging, update marketplace entries, and prepare release/publish steps. |
| **plugin-devex-review** | Review a plugin's fresh-clone setup, README flow, local testing path, prerequisites, bundled CLIs, and contributor experience. |
| **plugin-health** | Run plugin health, conformance, packaging, manifest, marketplace, skill frontmatter, routing, and generated-artifact audits. |
| **plugin-quality-gate** | Run or record a cross-model/second-opinion quality gate for high-impact plugin skills before release. |
| **plugin-release** | Validate, version, document, and gate plugin releases before commit, push, PR, tag, or publish. |
| **plugin-work-checkpoint** | Save or restore resumable context for long plugin maintenance work. |
| **skill-improve** | Improve an existing skill in one bounded evidence-backed pass without running a full SkillOpt training loop. |
| **skillopt-training-run** | Orchestrate an offline SkillOpt-style optimization run for a plugin skill. |
| **skillopt-rollout-evidence** | Capture scored rollout evidence, task splits, verifier output, and failure modes for skill optimization. |
| **skillopt-reflection-edits** | Convert rollout successes and failures into bounded structured skill edits. |
| **skillopt-validation-gate** | Apply candidate edits to a copy and accept only held-out validation improvements. |
| **skillopt-slow-meta-update** | Run epoch-boundary slow-update guidance and optimizer-side meta memory. |
| **skillopt-transfer-release** | Export, transfer-check, document, and promote a validated best skill. |
| **upstream-skill-harvest** | Import, adapt, diff, and periodically review skills harvested from GBrain or GStack into marketplace plugins. |

## Use Cases

- Create or revise a plugin under `plugins/<plugin-name>/`.
- Keep `marketplace.yaml`, generated manifests, README files, marketplace entries,
  and skill locations aligned.
- Harvest upstream skills from GBrain or GStack into a target plugin with source/adaptation notes.
- Validate skill frontmatter, KB terminology, privacy/path safety, and upstream ledgers.
- Run a JSON-producing health audit that can be used by agents or CI.
- Review fresh-clone onboarding and improve quickstarts.
- Save/restore long-running plugin work without leaking secrets.
- Run quality gates for high-impact plugin skills before tests and releases
  cement behavior.
- Improve a single skill with SkillOpt-inspired evidence, bounded edits, and
  validation without creating a full optimization run.
- Run SkillOpt-style skill optimization loops with scored rollouts, bounded
  edits, held-out gates, rejected-edit buffers, slow/meta updates, and best-skill
  release checks.
- Prepare plugin release or publishing work after local validation.

## Local Testing

```bash
claude --plugin-dir ./plugins/plugin-manager
```

Reload after edits with `/reload-plugins`. Validate with `claude plugin validate`
when the Claude Code CLI is available.

Run the health audit and dual-marketplace validation:

```bash
npm run render:check
npm run validate
python3 plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py --plugin plugin-manager --json
```
