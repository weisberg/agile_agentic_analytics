# SkillOpt Protocol For Plugin Manager

Use this reference when a plugin-manager skill is running an offline skill
optimization loop inspired by SkillOpt. Keep this file as protocol reference;
task-specific results belong under `.plugin-manager/skillopt/`.

## Source Basis

- Project page: https://microsoft.github.io/SkillOpt/
- Paper: https://arxiv.org/html/2605.23904v2

SkillOpt treats a natural-language skill document as the trainable state of a
fixed agent. The target model, tools, harness, and evaluator stay fixed while an
offline optimizer improves the skill through scored rollouts, minibatch
reflection, bounded text edits, held-out validation, rejected-edit feedback, and
epoch-wise slow/meta updates.

## Run Directory

Use one run directory per target skill:

```text
.plugin-manager/skillopt/YYYY-MM-DD-HHMM-<target-skill>/
├── run.md
├── tasks/
│   ├── train.jsonl
│   ├── selection.jsonl
│   └── test.jsonl
├── rollouts/
│   └── step-000/
│       ├── trajectories.jsonl
│       └── rollout-summary.md
├── reflection/
│   └── step-000/
│       ├── failure-analysis.json
│       ├── success-analysis.json
│       ├── merged-edits.json
│       └── selected-edits.json
├── candidates/
│   └── step-000/
│       ├── SKILL.md
│       └── edit-apply-report.json
├── gates/
│   └── step-000/
│       ├── selection-report.md
│       └── rejected-buffer.jsonl
├── epochs/
│   └── epoch-001/
│       ├── longitudinal-comparison.md
│       ├── slow-update.json
│       └── meta-skill.md
└── best/
    ├── SKILL.md
    ├── best-summary.md
    └── transfer-report.md
```

## Task And Score Records

`tasks/*.jsonl` records should be stable enough to rerun:

```json
{"id":"task-001","prompt":"...","expected":"...","score_type":"exact|rubric|test|manual","verifier":"command or rubric","notes":"optional"}
```

`trajectories.jsonl` should summarize enough evidence for reflection without
leaking secrets or bloating context:

```json
{"task_id":"task-001","skill_version":"step-000","score":1.0,"status":"success|failure","messages_ref":"path or summary","tool_calls":["..."],"verifier_output":"short result","failure_mode":"if any"}
```

When no deterministic verifier exists, use the same explicit rubric for every
candidate and label the score as `manual` or `rubric`. Do not mix rubrics across
candidate versions.

## Patch Schema

Reflection emits structured edits. Prefer patch mode over full rewrites.

```json
{
  "reasoning": "short evidence-grounded explanation",
  "edits": [
    {
      "op": "append|insert_after|replace|delete",
      "target": "exact heading or text when needed",
      "content": "markdown for append/insert/replace",
      "support_count": 3,
      "source_type": "failure|success"
    }
  ]
}
```

Ranking criteria:

1. Systematic impact on recurring failures.
2. Complementarity with existing skill content.
3. Generality beyond a single task or entity.
4. Concrete actionability.

## Protected Slow Update

Step-level reflection must not edit content between these markers:

```markdown
<!-- SLOW_UPDATE_START -->
...
<!-- SLOW_UPDATE_END -->
```

Only the epoch slow/meta update may rewrite that block. The rewritten candidate
still has to pass the held-out selection gate before it becomes current.

## Default Local Settings

Use these as starting points, then scale to the risk and available verifier:

- rollout batch: 8 to 40 tasks
- reflection minibatch: 4 to 8 trajectories
- edit budget: 2 to 4 selected edits per step
- slow-update comparison: 10 to 20 repeated tasks per epoch
- gate rule: accept only if selection score is strictly greater than current

For small internal plugin work, fewer tasks are acceptable if each task has a
real verifier and the final output clearly labels the evidence as thin.

## Acceptance Rules

- Keep target model, harness, tools, evaluator, and selection split fixed inside
  a run.
- Evaluate every candidate before acceptance.
- Reject ties; they are not improvements.
- Keep rejected edits and their score deltas as negative feedback.
- Preserve success patterns only when they are not already covered by the skill.
- Promote the final `best/SKILL.md` to the real plugin only after an explicit
  deploy/release step or user request.
