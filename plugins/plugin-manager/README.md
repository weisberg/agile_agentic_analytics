# Plugin Manager

Marketplace maintenance workflows for creating, validating, harvesting, syncing,
and publishing Claude Code plugins.

## Skills

| Skill | Description |
|-------|-------------|
| **manage-plugins** | Route plugin maintenance work: create or update plugins, inspect manifests, validate packaging, update marketplace entries, and prepare release/publish steps. |
| **plugin-devex-review** | Review a plugin's fresh-clone setup, README flow, local testing path, prerequisites, bundled CLIs, and contributor experience. |
| **plugin-health** | Run plugin health, conformance, packaging, manifest, marketplace, skill frontmatter, routing, and generated-artifact audits. |
| **plugin-quality-gate** | Run or record a cross-model/second-opinion quality gate for high-impact plugin skills before release. |
| **plugin-release** | Validate, version, document, and gate plugin releases before commit, push, PR, tag, or publish. |
| **plugin-work-checkpoint** | Save or restore resumable context for long plugin maintenance work. |
| **upstream-skill-harvest** | Import, adapt, diff, and periodically review skills harvested from GBrain or GStack into marketplace plugins. |

## Use Cases

- Create or revise a plugin under `plugins/<plugin-name>/`.
- Keep plugin manifests, README files, marketplace entries, and skill locations aligned.
- Harvest upstream skills from GBrain or GStack into a target plugin with source/adaptation notes.
- Validate skill frontmatter, KB terminology, privacy/path safety, and upstream ledgers.
- Run a JSON-producing health audit that can be used by agents or CI.
- Review fresh-clone onboarding and improve quickstarts.
- Save/restore long-running plugin work without leaking secrets.
- Run quality gates for high-impact plugin skills before tests and releases
  cement behavior.
- Prepare plugin release or publishing work after local validation.

## Local Testing

```bash
claude --plugin-dir ./plugins/plugin-manager
```

Reload after edits with `/reload-plugins`. Validate with `claude plugin validate`
when the Claude Code CLI is available.

Run the health audit:

```bash
python3 plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py --plugin plugin-manager --json
```
