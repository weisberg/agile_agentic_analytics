#!/usr/bin/env python3
"""Routing evaluation harness for the Agile Agentic Analytics marketplace.

This executes the ``routing-eval.jsonl`` corpus that lives next to skills
(``plugins/*/skills/*/routing-eval.jsonl``) and at plugin scope
(``plugins/*/references/routing-eval.jsonl``). Historically those files were
only syntax-checked by ``plugin_audit.py``; this harness actually *runs* them:
for every intent it ranks the full cross-plugin portfolio of skill descriptions
and asserts the expected skill wins.

Design notes
------------
* Stdlib only. No third-party dependencies, no network calls.
* The candidate set is the ENTIRE portfolio of skills, cross-plugin, because
  that is the production condition a real router faces.
* Two tiers are provided:
    - ``deterministic`` (default): a transparent lexical scorer (token overlap
      with idf-style downweighting of common words plus a skill-name boost).
    - ``model``: a documented NO-OP stub. Model-based evaluation is run
      manually via a headless model; this harness never calls a model.

Eval record format (backward compatible with the existing corpus)
-----------------------------------------------------------------
One JSON object per line; blank lines and lines starting with ``#`` or ``//``
are ignored (comment support matches ``plugin_audit.py``)::

    {"intent": "...", "expected_skill": "..."}

Extended, optional fields:

* ``ambiguous_with``: list of skill names that are ALSO acceptable as the #1
  pick. A top-1 hit against any of these counts as correct.
* ``forbidden_skill``: negative assertion. The case FAILS if this skill ranks
  #1. May be combined with ``expected_skill`` (positive + negative in one case)
  or used alone (pure negative case).
* ``plugin``: optional namespace to disambiguate identically named skills across
  plugins.

Namespacing convention
----------------------
``expected_skill`` / ``forbidden_skill`` / entries of ``ambiguous_with`` may be
written either as a bare skill name (``"sample-size"``) or fully qualified as
``"plugin:skill"`` (``"ab-testing:sample-size"``). A bare name resolves against
the portfolio by skill name; if the name is unique it resolves unambiguously.
If two plugins ship a skill with the same name, the bare form is ambiguous and
you MUST qualify it (``plugin:skill``) or set the record-level ``plugin`` field.
The harness reports unresolved/ambiguous references as errors.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"

# Common words carry little routing signal. idf downweights them automatically,
# but an explicit stoplist keeps the scorer from being nudged by filler tokens
# that happen to be rare in this particular corpus.
STOPWORDS = frozenset(
    """
    a an and the this that these those for of to in on with without from into
    is are be being been was were do does did done use used using when where
    what which who whom why how should would could can may might will shall
    our your their its his her my we you they it he she them us
    also or but if then than so such as at by out up down over under again
    want wants wanted need needs needed run running runs get gets got
    make makes made turn turns turned help please just like any some all
    """.split()
)

TOKEN_RE = re.compile(r"[a-z0-9]+")


def _stem(token: str) -> str:
    """Naive plural normalization, applied symmetrically to docs and queries.

    Because the same transform runs on both sides, any collapse it makes still
    preserves matching (e.g. 'funnels'->'funnel' matches 'funnel'). The 'ss'
    guard avoids mangling words like 'process' or 'business'.
    """
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        if token.endswith("ies"):
            return token[:-3] + "y"
        return token[:-1]
    return token


def tokenize(text: str) -> list[str]:
    """Lowercase, stopword-filtered, plural-normalized word tokens."""
    return [_stem(t) for t in TOKEN_RE.findall(text.lower()) if len(t) > 1 and t not in STOPWORDS]


def bigrams(tokens: list[str]) -> list[str]:
    """Adjacent token pairs as single features (e.g. 'sample size').

    Multi-word trigger phrases ('sample size', 'share of voice', 'open rate')
    are far more discriminating than their component unigrams, which collide
    across many skills. Bigrams are rare, so idf makes them strong signals.
    """
    return [f"{a}\x1f{b}" for a, b in zip(tokens, tokens[1:])]


def features(text: str) -> list[str]:
    toks = tokenize(text)
    return toks + bigrams(toks)


# --------------------------------------------------------------------------- #
# Frontmatter parsing (stdlib only; handles YAML block scalars for description)
# --------------------------------------------------------------------------- #
def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
    if not m:
        return {}
    block = m.group(1)
    lines = block.splitlines()
    result: dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not km:
            i += 1
            continue
        key, raw = km.group(1), km.group(2).strip()
        if raw in (">", ">-", ">+", "|", "|-", "|+"):
            # Block scalar: gather subsequent more-indented (or blank) lines.
            buf: list[str] = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt.strip() == "":
                    buf.append("")
                    i += 1
                    continue
                if re.match(r"^\s", nxt):
                    buf.append(nxt.strip())
                    i += 1
                    continue
                break
            folded = " ".join(part for part in buf if part).strip()
            result[key] = folded
            continue
        # Plain scalar; strip surrounding quotes if present.
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
            raw = raw[1:-1]
        result[key] = raw
        i += 1
    return result


# --------------------------------------------------------------------------- #
# Portfolio model
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Skill:
    plugin: str
    name: str
    description: str
    path: Path

    @property
    def qualified(self) -> str:
        return f"{self.plugin}:{self.name}"


def discover_skills(plugins_dir: Path = PLUGINS_DIR) -> list[Skill]:
    """Load every skill's (plugin, name, description) portfolio-wide."""
    skills: list[Skill] = []
    for skill_file in sorted(plugins_dir.glob("*/skills/*/SKILL.md")):
        plugin = skill_file.parents[2].name
        dir_name = skill_file.parent.name
        fm = read_frontmatter(skill_file)
        name = fm.get("name", dir_name).strip() or dir_name
        description = fm.get("description", "").strip()
        skills.append(Skill(plugin=plugin, name=name, description=description, path=skill_file))
    return skills


def discover_eval_files(plugins_dir: Path = PLUGINS_DIR) -> list[Path]:
    """All skill-level and plugin-level routing-eval.jsonl files."""
    files = set(plugins_dir.glob("*/skills/*/routing-eval.jsonl"))
    files |= set(plugins_dir.glob("*/references/routing-eval.jsonl"))
    return sorted(files)


# --------------------------------------------------------------------------- #
# Deterministic lexical scorer
# --------------------------------------------------------------------------- #
# BM25 parameters. k1 controls term-frequency saturation; b controls how much
# document length is normalized away. NAME_BOOST injects extra term frequency for
# tokens that appear in the skill *name* (a high-signal field), implemented as a
# field boost rather than a flat multiplier so length normalization still applies.
BM25_K1 = 1.5
BM25_B = 0.75
NAME_BOOST = 2  # extra tf added per name-token occurrence


class LexicalScorer:
    """Rank skills for an intent with BM25 over (description + name-boosted) text.

    BM25 gives three properties the naive overlap scorer lacked and that matter
    for a cross-plugin candidate set:

    * idf downweights words common across many skills ("analysis", "data").
    * term-frequency saturation stops a keyword-stuffed description from winning
      purely by repetition.
    * length normalization removes the bias toward verbose descriptions (the
      marketing-analytics keyword lists and ab-testing multi-sentence blurbs
      otherwise out-score short, precise lead-analyst descriptions).

    Skill-name tokens are boosted by adding extra term frequency, so a name hit
    counts for more without escaping length normalization.
    """

    def __init__(self, skills: Iterable[Skill]):
        self.skills = list(skills)
        self._tf: dict[str, dict[str, int]] = {}
        self._len: dict[str, int] = {}
        df: dict[str, int] = defaultdict(int)
        total_len = 0
        for sk in self.skills:
            name_feats = features(sk.name.replace("-", " "))
            desc_feats = features(sk.description)
            tf: dict[str, int] = defaultdict(int)
            for tok in desc_feats:
                tf[tok] += 1
            for tok in name_feats:
                tf[tok] += 1 + NAME_BOOST  # count name feature + boost
            self._tf[sk.qualified] = dict(tf)
            doc_len = sum(tf.values())
            self._len[sk.qualified] = doc_len
            total_len += doc_len
            for tok in tf:
                df[tok] += 1
        self._n = max(len(self.skills), 1)
        self._avgdl = (total_len / self._n) if self._n else 0.0
        # BM25 idf with the standard +0.5 smoothing (floored at a small positive
        # value so a token present in every doc still contributes a little).
        self._idf: dict[str, float] = {}
        for tok, freq in df.items():
            idf = math.log((self._n - freq + 0.5) / (freq + 0.5) + 1.0)
            self._idf[tok] = max(idf, 1e-6)

    def score(self, intent_tokens: list[str], skill: Skill) -> float:
        q = skill.qualified
        tf = self._tf[q]
        if not tf:
            return 0.0
        dl = self._len[q]
        denom_norm = BM25_K1 * (1 - BM25_B + BM25_B * (dl / self._avgdl if self._avgdl else 0.0))
        total = 0.0
        for tok in set(intent_tokens):
            f = tf.get(tok, 0)
            if f == 0:
                continue
            idf = self._idf.get(tok, 0.0)
            total += idf * (f * (BM25_K1 + 1)) / (f + denom_norm)
        return total

    def rank(self, intent: str) -> list[tuple[Skill, float]]:
        toks = features(intent)
        scored = [(sk, self.score(toks, sk)) for sk in self.skills]
        # Deterministic tie-break: score desc, then qualified name asc.
        scored.sort(key=lambda item: (-item[1], item[0].qualified))
        return scored


# --------------------------------------------------------------------------- #
# Skill-name resolution
# --------------------------------------------------------------------------- #
class Resolver:
    def __init__(self, skills: Iterable[Skill]):
        self._by_qualified: dict[str, Skill] = {}
        self._by_name: dict[str, list[Skill]] = defaultdict(list)
        for sk in skills:
            self._by_qualified[sk.qualified] = sk
            self._by_name[sk.name].append(sk)

    def resolve(self, ref: str, record_plugin: str | None = None) -> tuple[Skill | None, str | None]:
        """Return (skill, error). Exactly one of the two is None."""
        ref = ref.strip()
        if ":" in ref:
            sk = self._by_qualified.get(ref)
            if sk is None:
                return None, f"unknown qualified skill {ref!r}"
            return sk, None
        matches = self._by_name.get(ref, [])
        if record_plugin:
            matches = [m for m in matches if m.plugin == record_plugin] or matches
        if not matches:
            return None, f"unknown skill {ref!r}"
        if len(matches) > 1:
            plugins = ", ".join(sorted(m.plugin for m in matches))
            return None, f"ambiguous skill {ref!r} (in {plugins}); qualify as plugin:skill"
        return matches[0], None


# --------------------------------------------------------------------------- #
# Evaluation
# --------------------------------------------------------------------------- #
@dataclass
class CaseResult:
    eval_file: Path
    owning_plugin: str
    intent: str
    expected: list[str]  # accepted qualified names (expected + ambiguous_with)
    forbidden: str | None
    predicted_top: str | None
    predicted_top3: list[str]
    top1_ok: bool
    top3_ok: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class EvalStats:
    total: int = 0
    top1_hits: int = 0
    top3_hits: int = 0

    def add(self, top1: bool, top3: bool) -> None:
        self.total += 1
        self.top1_hits += 1 if top1 else 0
        self.top3_hits += 1 if top3 else 0

    @property
    def top1_acc(self) -> float:
        return self.top1_hits / self.total if self.total else 0.0

    @property
    def top3_acc(self) -> float:
        return self.top3_hits / self.total if self.total else 0.0


def parse_eval_lines(path: Path) -> list[dict]:
    records: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("//"):
            continue
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        obj["_line"] = line_no
        records.append(obj)
    return records


def evaluate(
    scorer: LexicalScorer,
    resolver: Resolver,
    eval_files: list[Path],
) -> list[CaseResult]:
    results: list[CaseResult] = []
    for path in eval_files:
        # Owning plugin: the plugin directory that contains this eval file.
        try:
            owning_plugin = path.relative_to(PLUGINS_DIR).parts[0]
        except ValueError:
            owning_plugin = path.parent.name
        for rec in parse_eval_lines(path):
            intent = rec.get("intent", "")
            record_plugin = rec.get("plugin")
            errors: list[str] = []

            accepted: list[str] = []
            expected_ref = rec.get("expected_skill")
            if expected_ref:
                sk, err = resolver.resolve(expected_ref, record_plugin)
                if err:
                    errors.append(err)
                else:
                    accepted.append(sk.qualified)
            for alt in rec.get("ambiguous_with", []) or []:
                sk, err = resolver.resolve(alt, record_plugin)
                if err:
                    errors.append(err)
                else:
                    accepted.append(sk.qualified)

            forbidden_q: str | None = None
            forbidden_ref = rec.get("forbidden_skill")
            if forbidden_ref:
                sk, err = resolver.resolve(forbidden_ref, record_plugin)
                if err:
                    errors.append(err)
                else:
                    forbidden_q = sk.qualified

            ranking = scorer.rank(intent)
            top = ranking[0][0].qualified if ranking else None
            top3 = [item[0].qualified for item in ranking[:3]]

            # Positive component: if any accepted skills are declared, #1 (top1)
            # / top-3 must include an accepted skill.
            if accepted:
                top1_pos = top in accepted
                top3_pos = any(a in top3 for a in accepted)
            else:
                # Pure negative case: positive component is vacuously satisfied.
                top1_pos = True
                top3_pos = True

            # Negative component: forbidden skill must not be #1.
            neg_ok = True
            if forbidden_q is not None:
                neg_ok = top != forbidden_q

            top1_ok = bool(top1_pos and neg_ok and not errors)
            top3_ok = bool(top3_pos and neg_ok and not errors)

            results.append(
                CaseResult(
                    eval_file=path,
                    owning_plugin=owning_plugin,
                    intent=intent,
                    expected=accepted,
                    forbidden=forbidden_q,
                    predicted_top=top,
                    predicted_top3=top3,
                    top1_ok=top1_ok,
                    top3_ok=top3_ok,
                    errors=errors,
                )
            )
    return results


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def aggregate(results: list[CaseResult]) -> tuple[EvalStats, dict[str, EvalStats]]:
    portfolio = EvalStats()
    per_plugin: dict[str, EvalStats] = defaultdict(EvalStats)
    for r in results:
        portfolio.add(r.top1_ok, r.top3_ok)
        per_plugin[r.owning_plugin].add(r.top1_ok, r.top3_ok)
    return portfolio, per_plugin


def render_text(
    results: list[CaseResult],
    portfolio: EvalStats,
    per_plugin: dict[str, EvalStats],
    threshold: float,
    show_failures: bool,
) -> str:
    out: list[str] = []
    out.append("Routing evaluation (deterministic lexical tier)")
    out.append("=" * 60)
    out.append("")
    out.append(f"{'Plugin':<24}{'Cases':>7}{'Top-1':>9}{'Top-3':>9}")
    out.append("-" * 49)
    for plugin in sorted(per_plugin):
        s = per_plugin[plugin]
        out.append(f"{plugin:<24}{s.total:>7}{s.top1_acc:>8.1%}{s.top3_acc:>8.1%}")
    out.append("-" * 49)
    out.append(f"{'PORTFOLIO':<24}{portfolio.total:>7}{portfolio.top1_acc:>8.1%}{portfolio.top3_acc:>8.1%}")
    out.append("")
    out.append(f"Threshold (top-1 with ambiguity allowance): {threshold:.0%}")
    status = "PASS" if portfolio.top1_acc >= threshold else "FAIL"
    out.append(f"Result: {status}")

    errored = [r for r in results if r.errors]
    if errored:
        out.append("")
        out.append(f"Resolution errors: {len(errored)}")
        for r in errored:
            out.append(f"  {r.eval_file.relative_to(REPO_ROOT)}: {r.intent!r}")
            for e in r.errors:
                out.append(f"    - {e}")

    if show_failures:
        fails = [r for r in results if not r.top1_ok]
        if fails:
            out.append("")
            out.append(f"Top-1 failures: {len(fails)}")
            for r in fails:
                exp = ", ".join(r.expected) if r.expected else "(negative-only)"
                forb = f" forbidden={r.forbidden}" if r.forbidden else ""
                out.append(f"  [{r.owning_plugin}] {r.intent!r}")
                out.append(f"    expected={exp}{forb} got={r.predicted_top} top3={r.predicted_top3}")
    return "\n".join(out)


def render_json(
    results: list[CaseResult],
    portfolio: EvalStats,
    per_plugin: dict[str, EvalStats],
    threshold: float,
) -> str:
    payload = {
        "tier": "deterministic",
        "threshold": threshold,
        "portfolio": {
            "cases": portfolio.total,
            "top1_accuracy": round(portfolio.top1_acc, 4),
            "top3_accuracy": round(portfolio.top3_acc, 4),
            "pass": portfolio.top1_acc >= threshold,
        },
        "per_plugin": {
            plugin: {
                "cases": s.total,
                "top1_accuracy": round(s.top1_acc, 4),
                "top3_accuracy": round(s.top3_acc, 4),
            }
            for plugin, s in sorted(per_plugin.items())
        },
        "failures": [
            {
                "eval_file": str(r.eval_file.relative_to(REPO_ROOT)),
                "plugin": r.owning_plugin,
                "intent": r.intent,
                "expected": r.expected,
                "forbidden": r.forbidden,
                "predicted_top": r.predicted_top,
                "predicted_top3": r.predicted_top3,
                "errors": r.errors,
            }
            for r in results
            if not r.top1_ok
        ],
    }
    return json.dumps(payload, indent=2)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
MODEL_TIER_NOTICE = """\
The --tier model option is a documented NO-OP in this harness.

Model-based routing evaluation is run MANUALLY, out of band, because it is
non-deterministic and requires a headless model invocation (e.g. `claude -p`
presented with the full portfolio of skill descriptions). This CI-cheap harness
never calls a model. To run the model tier, use the deterministic tier here for
gating and perform the model-based pass manually, recording results as rollout
evidence. Re-run with `--tier deterministic` (the default) for an executable
score.
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="routing_eval.py",
        description="Execute the routing-eval.jsonl corpus against the full skill portfolio.",
    )
    p.add_argument(
        "--tier",
        choices=["deterministic", "model"],
        default="deterministic",
        help="Scoring tier. 'deterministic' (default) runs the lexical scorer; "
        "'model' is a documented no-op stub (model eval is run manually).",
    )
    p.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Minimum portfolio top-1 (with ambiguity allowance) accuracy to pass. Default 0.85.",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    p.add_argument(
        "--plugin",
        action="append",
        default=None,
        help="Restrict evaluation to eval files owned by this plugin (repeatable). "
        "Candidate set stays the full portfolio.",
    )
    p.add_argument(
        "--show-failures",
        action="store_true",
        help="In text format, list each top-1 failure with predicted ranking.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.tier == "model":
        sys.stdout.write(MODEL_TIER_NOTICE)
        return 0

    skills = discover_skills()
    if not skills:
        sys.stderr.write("No skills discovered under plugins/*/skills/*/SKILL.md\n")
        return 2

    scorer = LexicalScorer(skills)
    resolver = Resolver(skills)

    eval_files = discover_eval_files()
    if args.plugin:
        wanted = set(args.plugin)
        eval_files = [f for f in eval_files if f.relative_to(PLUGINS_DIR).parts[0] in wanted]

    results = evaluate(scorer, resolver, eval_files)
    portfolio, per_plugin = aggregate(results)

    if args.format == "json":
        sys.stdout.write(render_json(results, portfolio, per_plugin, args.threshold) + "\n")
    else:
        sys.stdout.write(render_text(results, portfolio, per_plugin, args.threshold, args.show_failures) + "\n")

    has_errors = any(r.errors for r in results)
    passed = portfolio.top1_acc >= args.threshold and not has_errors
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
