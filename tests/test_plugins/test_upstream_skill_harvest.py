import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "plugins/plugin-manager/skills/upstream-skill-harvest/scripts/harvest_check.py"


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def run_checker(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--repo-root", str(tmp_path), *args, "--json"],
        check=False,
        capture_output=True,
        text=True,
    )


def parse_json(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


def test_clean_kb_harvest_record_passes(tmp_path: Path) -> None:
    source = write(
        tmp_path / "upstream/skills/example/SKILL.md",
        """---
name: example
version: 1.0.0
description: Example upstream skill.
triggers:
  - "example"
tools:
  - read
---

# Example

Use the upstream source.
""",
    )
    target = write(
        tmp_path / "plugins/knowledge-base/skills/example/SKILL.md",
        """---
name: example
version: 1.0.0
description: Example KB skill.
triggers:
  - "example"
tools:
  - read
---

# Example

Use the knowledge base source.
""",
    )
    ledger = write(
        tmp_path / "plugins/knowledge-base/references/upstream-sources.md",
        """# Knowledge Base Upstream Source Ledger

## plugins/knowledge-base/skills/example/SKILL.md

- Source: `$GBRAIN_ROOT/skills/example/SKILL.md`
- Source commit: `abc1234`
- Imported or reviewed: `2026-05-20`
- Mode: `new-import`
- Frontmatter policy: `preserve-keys`
- Frontmatter notes: `description adapted for KB routing`
- Adaptation notes: `Converted user-facing wording to knowledge base terminology.`
- Privacy/path check: `pass`
- Files included: `SKILL.md`
- Files skipped: `none`
- Validation: `harvest_check.py --kb-terminology passed`
- Drift status: `current`
- Next review: `monthly`
""",
    )

    result = run_checker(
        tmp_path,
        "--source",
        str(source),
        "--target",
        str(target),
        "--ledger",
        str(ledger),
        "--require-source-frontmatter-keys",
        "--kb-terminology",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert parse_json(result)["ok"] is True


def test_exact_frontmatter_preservation_fails_on_change(tmp_path: Path) -> None:
    source = write(
        tmp_path / "upstream/skills/example/SKILL.md",
        """---
name: example
description: Original description.
triggers:
  - "example"
---

# Example
""",
    )
    target = write(
        tmp_path / "plugins/knowledge-base/skills/example/SKILL.md",
        """---
name: example
description: Adapted description.
triggers:
  - "example"
---

# Example
""",
    )

    result = run_checker(
        tmp_path,
        "--source",
        str(source),
        "--target",
        str(target),
        "--preserve-frontmatter",
    )

    assert result.returncode == 1
    codes = {failure["code"] for failure in parse_json(result)["failures"]}
    assert "frontmatter_exact_mismatch" in codes


def test_private_paths_and_raw_brain_terms_are_flagged(tmp_path: Path) -> None:
    target = write(
        tmp_path / "plugins/knowledge-base/skills/example/SKILL.md",
        """---
name: example
description: Example.
---

Save this to the brain with gbrain from /Users/example/private.
""",
    )

    result = run_checker(
        tmp_path,
        "--target",
        str(target),
        "--kb-terminology",
    )

    assert result.returncode == 1
    codes = {failure["code"] for failure in parse_json(result)["failures"]}
    assert "absolute_user_path" in codes
    assert "gbrain_runtime_term" in codes
    assert "brain_runtime_term" in codes
