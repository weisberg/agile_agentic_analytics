"""Golden-value tests for lead-analyst / profile_table.py.

Builds CSVs with known grain, null, and duplicate counts and verifies the
profiler reports them exactly.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


_SCRIPT = Path(__file__).resolve().parents[2] / "plugins" / "lead-analyst" / "scripts" / "profile_table.py"


def _load():
    spec = importlib.util.spec_from_file_location("profile_table", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pt = _load()


def _write(tmp_path, text):
    p = tmp_path / "data.csv"
    p.write_text(text, encoding="utf-8")
    return p


class TestProfile:
    def test_row_and_column_counts(self, tmp_path):
        csv = _write(tmp_path, "a,b,c\n1,2,3\n4,5,6\n7,8,9\n")
        r = pt.profile(csv, max_examples=3)
        assert r["row_count"] == 3
        assert r["column_count"] == 3
        assert r["columns"] == ["a", "b", "c"]

    def test_missing_counts(self, tmp_path):
        # column b has 2 empty cells; column c has 1
        csv = _write(tmp_path, "a,b,c\n1,,x\n2,,y\n3,z,\n")
        r = pt.profile(csv, max_examples=3)
        assert r["missing"]["a"] == 0
        assert r["missing"]["b"] == 2
        assert r["missing"]["c"] == 1

    def test_whitespace_counts_as_missing(self, tmp_path):
        csv = _write(tmp_path, "a,b\n1,   \n2,ok\n")
        r = pt.profile(csv, max_examples=3)
        assert r["missing"]["b"] == 1

    def test_duplicate_full_rows(self, tmp_path):
        # 3 identical rows -> 2 duplicates (first is the canonical)
        csv = _write(tmp_path, "a,b\n1,2\n1,2\n1,2\n9,9\n")
        r = pt.profile(csv, max_examples=3)
        assert r["duplicate_full_rows"] == 2

    def test_distinct_counts(self, tmp_path):
        csv = _write(tmp_path, "id,grp\n1,A\n2,A\n3,B\n4,B\n5,B\n")
        r = pt.profile(csv, max_examples=5)
        assert r["distinct_count_capped_1001"]["id"] == 5
        assert r["distinct_count_capped_1001"]["grp"] == 2

    def test_examples_capped(self, tmp_path):
        csv = _write(tmp_path, "x\n1\n2\n3\n4\n5\n")
        r = pt.profile(csv, max_examples=2)
        assert len(r["examples"]["x"]) == 2

    def test_tab_delimited_sniffed(self, tmp_path):
        p = tmp_path / "data.tsv"
        p.write_text("a\tb\n1\t2\n3\t4\n", encoding="utf-8")
        r = pt.profile(p, max_examples=3)
        assert r["column_count"] == 2
        assert r["row_count"] == 2

    def test_cli_emits_json(self, tmp_path):
        csv = _write(tmp_path, "a,b\n1,2\n3,\n")
        res = subprocess.run([sys.executable, str(_SCRIPT), str(csv)], capture_output=True, text=True)
        assert res.returncode == 0
        payload = json.loads(res.stdout)
        assert payload["row_count"] == 2
        assert payload["missing"]["b"] == 1
