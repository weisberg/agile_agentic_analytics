"""Unit tests for the routing evaluation harness (scripts/routing_eval.py).

Covered:
* the deterministic lexical scorer ranks the intended skill first on synthetic
  skills + intents;
* ``ambiguous_with`` accepts alternates and ``forbidden_skill`` enforces the
  negative assertion;
* JSONL parsing skips ``#`` and ``//`` comments and blank lines;
* frontmatter block-scalar parsing;
* skill-name resolution incl. ``plugin:skill`` qualification and ambiguity.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS_PATH = REPO_ROOT / "scripts" / "routing_eval.py"


def _load_harness():
    spec = importlib.util.spec_from_file_location("routing_eval_harness", HARNESS_PATH)
    module = importlib.util.module_from_spec(spec)
    # Register before exec so dataclasses can resolve the module namespace.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


re_mod = _load_harness()


def make_skills():
    S = re_mod.Skill
    return [
        S(
            "plug",
            "sample-size",
            "Calculate required sample size, duration, and MDE for an A/B test. How many users do I need, power calculation.",
            Path("a"),
        ),
        S(
            "plug",
            "analyze-results",
            "Analyze A/B test results: significance, confidence intervals, effect sizes, lift, readout.",
            Path("b"),
        ),
        S(
            "plug",
            "funnel-analysis",
            "Conversion funnel drop-off, bottleneck, checkout flow, signup flow abandonment.",
            Path("c"),
        ),
        S(
            "plug",
            "seo-content",
            "SEO keyword ranking, Search Console, organic traffic, backlinks, featured snippets.",
            Path("d"),
        ),
    ]


# --------------------------------------------------------------------------- #
# Tokenization / stemming
# --------------------------------------------------------------------------- #
def test_tokenize_drops_stopwords_and_short_tokens():
    toks = re_mod.tokenize("How many users do I need for a test")
    assert "how" not in toks  # stopword
    assert "a" not in toks  # 1-char
    assert "user" in toks  # plural-stemmed from "users"
    assert "test" in toks


def test_plural_stemming_is_symmetric():
    assert re_mod._stem("funnels") == "funnel"
    assert re_mod._stem("channels") == "channel"
    assert re_mod._stem("categories") == "category"
    # 'ss' guard: do not mangle these
    assert re_mod._stem("process") == "process"
    assert re_mod._stem("business") == "business"


def test_bigrams():
    assert re_mod.bigrams(["sample", "size", "test"]) == ["sample\x1fsize", "size\x1ftest"]


# --------------------------------------------------------------------------- #
# Scorer ranking
# --------------------------------------------------------------------------- #
def test_scorer_ranks_intended_skill_first():
    scorer = re_mod.LexicalScorer(make_skills())
    ranking = scorer.rank("how many users do I need to reach power for this test?")
    assert ranking[0][0].name == "sample-size"


def test_scorer_distinguishes_topics():
    scorer = re_mod.LexicalScorer(make_skills())
    assert scorer.rank("where are users dropping off in the checkout flow?")[0][0].name == "funnel-analysis"
    assert scorer.rank("which keywords rank in organic search console?")[0][0].name == "seo-content"


def test_scorer_deterministic_tiebreak():
    # Two skills with identical text -> tie broken by qualified name ascending.
    S = re_mod.Skill
    skills = [
        S("z", "beta", "identical text here", Path("x")),
        S("a", "alpha", "identical text here", Path("y")),
    ]
    scorer = re_mod.LexicalScorer(skills)
    ranking = scorer.rank("identical text here")
    assert [s.qualified for s, _ in ranking] == ["a:alpha", "z:beta"]


# --------------------------------------------------------------------------- #
# Resolver
# --------------------------------------------------------------------------- #
def test_resolver_bare_and_qualified():
    resolver = re_mod.Resolver(make_skills())
    sk, err = resolver.resolve("sample-size")
    assert err is None and sk.name == "sample-size"
    sk, err = resolver.resolve("plug:funnel-analysis")
    assert err is None and sk.plugin == "plug"


def test_resolver_unknown_and_ambiguous():
    S = re_mod.Skill
    skills = [
        S("p1", "dup", "one", Path("a")),
        S("p2", "dup", "two", Path("b")),
    ]
    resolver = re_mod.Resolver(skills)
    sk, err = resolver.resolve("missing")
    assert sk is None and "unknown" in err
    sk, err = resolver.resolve("dup")
    assert sk is None and "ambiguous" in err
    # Qualification resolves the ambiguity.
    sk, err = resolver.resolve("p2:dup")
    assert err is None and sk.plugin == "p2"
    # Record-level plugin also disambiguates.
    sk, err = resolver.resolve("dup", record_plugin="p1")
    assert err is None and sk.plugin == "p1"


# --------------------------------------------------------------------------- #
# JSONL parsing with comments
# --------------------------------------------------------------------------- #
def test_parse_eval_lines_skips_comments(tmp_path):
    f = tmp_path / "routing-eval.jsonl"
    f.write_text(
        "\n".join(
            [
                "// a slash comment",
                "# a hash comment",
                "",
                '{"intent": "one", "expected_skill": "sample-size"}',
                '{"intent": "two", "expected_skill": "analyze-results"}',
            ]
        ),
        encoding="utf-8",
    )
    records = re_mod.parse_eval_lines(f)
    assert len(records) == 2
    assert records[0]["intent"] == "one"
    assert records[0]["_line"] == 4  # line number preserved past comments


def test_parse_eval_lines_reports_bad_json(tmp_path):
    f = tmp_path / "routing-eval.jsonl"
    f.write_text('{"intent": "x",}\n', encoding="utf-8")
    with pytest.raises(ValueError):
        re_mod.parse_eval_lines(f)


# --------------------------------------------------------------------------- #
# ambiguous_with / forbidden_skill logic (end-to-end via evaluate)
# --------------------------------------------------------------------------- #
def _eval_one(tmp_path, skills, record):
    import json as _json

    f = tmp_path / "plugins" / "plug" / "skills" / "s" / "routing-eval.jsonl"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(_json.dumps(record) + "\n", encoding="utf-8")
    scorer = re_mod.LexicalScorer(skills)
    resolver = re_mod.Resolver(skills)
    # Point the module's PLUGINS_DIR at our temp tree so owning-plugin resolves.
    orig = re_mod.PLUGINS_DIR
    re_mod.PLUGINS_DIR = tmp_path / "plugins"
    try:
        results = re_mod.evaluate(scorer, resolver, [f])
    finally:
        re_mod.PLUGINS_DIR = orig
    return results[0]


def test_ambiguous_with_accepts_alternate(tmp_path):
    skills = make_skills()
    # Intent clearly hits sample-size; declare the wrong expected but allow it.
    rec = {
        "intent": "how many users do I need to reach power for this test?",
        "expected_skill": "analyze-results",
        "ambiguous_with": ["sample-size"],
    }
    res = _eval_one(tmp_path, skills, rec)
    assert res.predicted_top == "plug:sample-size"
    assert res.top1_ok  # accepted via ambiguous_with


def test_expected_without_ambiguity_fails_when_not_top1(tmp_path):
    skills = make_skills()
    rec = {
        "intent": "how many users do I need to reach power for this test?",
        "expected_skill": "analyze-results",
    }
    res = _eval_one(tmp_path, skills, rec)
    assert not res.top1_ok


def test_forbidden_skill_fails_when_it_ranks_first(tmp_path):
    skills = make_skills()
    rec = {
        "intent": "how many users do I need to reach power for this test?",
        "expected_skill": "sample-size",
        "forbidden_skill": "sample-size",  # contrived: forbid the actual winner
    }
    res = _eval_one(tmp_path, skills, rec)
    assert res.predicted_top == "plug:sample-size"
    assert not res.top1_ok  # forbidden won -> fail even though expected matched


def test_pure_negative_case_passes_when_forbidden_not_first(tmp_path):
    skills = make_skills()
    rec = {
        "intent": "how many users do I need to reach power for this test?",
        "forbidden_skill": "seo-content",  # unrelated -> won't be #1
    }
    res = _eval_one(tmp_path, skills, rec)
    assert res.expected == []  # negative-only
    assert res.top1_ok


def test_unresolved_reference_is_error(tmp_path):
    skills = make_skills()
    rec = {"intent": "anything", "expected_skill": "does-not-exist"}
    res = _eval_one(tmp_path, skills, rec)
    assert res.errors
    assert not res.top1_ok


# --------------------------------------------------------------------------- #
# Frontmatter parsing
# --------------------------------------------------------------------------- #
def test_read_frontmatter_block_scalar(tmp_path):
    f = tmp_path / "SKILL.md"
    f.write_text(
        "---\n"
        "name: my-skill\n"
        "description: >-\n"
        "  First line of the description\n"
        "  continues on the second line.\n"
        "disable-model-invocation: false\n"
        "---\n"
        "# Body\n",
        encoding="utf-8",
    )
    fm = re_mod.read_frontmatter(f)
    assert fm["name"] == "my-skill"
    assert fm["description"] == "First line of the description continues on the second line."
    assert fm["disable-model-invocation"] == "false"


def test_read_frontmatter_quoted_plain(tmp_path):
    f = tmp_path / "SKILL.md"
    f.write_text('---\nname: "quoted-name"\n---\nbody\n', encoding="utf-8")
    assert re_mod.read_frontmatter(f)["name"] == "quoted-name"


# --------------------------------------------------------------------------- #
# Portfolio smoke: the real corpus loads and scores above a sane floor.
# --------------------------------------------------------------------------- #
def test_real_portfolio_discovers_skills_and_evals():
    skills = re_mod.discover_skills()
    assert len(skills) >= 90  # consolidated portfolio remains broad
    eval_files = re_mod.discover_eval_files()
    assert any("references" in str(f) for f in eval_files)  # plugin-level file included
    assert any("marketing-analytics" in str(f) for f in eval_files)  # our new files


def test_model_tier_is_noop(capsys):
    rc = re_mod.main(["--tier", "model"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "NO-OP" in out
