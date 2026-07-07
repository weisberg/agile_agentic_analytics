"""Golden-value tests for data-extraction / validate_extract.py.

Verifies contract pass/fail exit codes, null-rate reporting, and duplicate-key
detection with known counts.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "marketing-analytics"
    / "skills"
    / "data-extraction"
    / "scripts"
    / "validate_extract.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("validate_extract", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ve = _load()


def _csv(tmp_path, text, name="extract.csv"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# profile() + evaluate() -- direct function checks
# ---------------------------------------------------------------------------
class TestProfileEvaluate:
    def test_null_rates(self, tmp_path):
        # col b: 1 of 4 null -> 0.25
        f = _csv(tmp_path, "a,b\n1,x\n2,\n3,y\n4,z\n")
        report = ve.profile(f, required=["a"], date_col=None, key_cols=[])
        assert report["row_count"] == 4
        assert report["null_rates"]["b"] == pytest.approx(0.25)
        assert report["null_rates"]["a"] == pytest.approx(0.0)

    def test_missing_required_is_violation(self, tmp_path):
        f = _csv(tmp_path, "a,b\n1,2\n")
        report = ve.profile(f, required=["a", "missing_col"], date_col=None, key_cols=[])
        assert report["missing_required"] == ["missing_col"]
        violations = ve.evaluate(report)
        assert any("missing required columns" in v for v in violations)

    def test_duplicate_keys_counted(self, tmp_path):
        # key = id; id=1 appears 3x -> 2 duplicate rows
        f = _csv(tmp_path, "id,v\n1,a\n1,b\n1,c\n2,d\n")
        report = ve.profile(f, required=["id"], date_col=None, key_cols=["id"])
        assert report["duplicate_keys"] == 2
        violations = ve.evaluate(report)
        assert any("duplicate key rows" in v for v in violations)

    def test_composite_key(self, tmp_path):
        # key = (campaign, date); one exact repeat -> 1 duplicate
        f = _csv(
            tmp_path,
            "campaign,date,spend\nc1,2024-01-01,10\nc1,2024-01-01,10\nc1,2024-01-02,5\n",
        )
        report = ve.profile(f, required=["campaign"], date_col="date", key_cols=["campaign", "date"])
        assert report["duplicate_keys"] == 1

    def test_date_range(self, tmp_path):
        f = _csv(tmp_path, "date,v\n2024-03-05,1\n2024-01-02,2\n2024-06-30,3\n")
        report = ve.profile(f, required=["date"], date_col="date", key_cols=[])
        assert report["date_range"] == {"min": "2024-01-02", "max": "2024-06-30"}

    def test_empty_file_is_violation(self, tmp_path):
        f = _csv(tmp_path, "a,b\n")  # header only, zero data rows
        report = ve.profile(f, required=["a"], date_col=None, key_cols=[])
        assert report["row_count"] == 0
        assert "file has zero data rows" in ve.evaluate(report)

    def test_clean_passes(self, tmp_path):
        f = _csv(tmp_path, "id,v\n1,a\n2,b\n3,c\n")
        report = ve.profile(f, required=["id", "v"], date_col=None, key_cols=["id"])
        assert ve.evaluate(report) == []


# ---------------------------------------------------------------------------
# CLI exit codes
# ---------------------------------------------------------------------------
class TestCLI:
    def _run(self, *args):
        return subprocess.run([sys.executable, str(_SCRIPT), *args], capture_output=True, text=True)

    def test_pass_exit_zero(self, tmp_path):
        f = _csv(tmp_path, "date,spend\n2024-01-01,10\n2024-01-02,20\n")
        res = self._run(str(f), "--required-cols", "date,spend", "--json")
        assert res.returncode == 0
        assert '"status": "OK"' in res.stdout

    def test_missing_required_exit_one(self, tmp_path):
        f = _csv(tmp_path, "date\n2024-01-01\n")
        res = self._run(str(f), "--required-cols", "date,spend")
        assert res.returncode == 1
        assert "BLOCKED" in res.stdout

    def test_duplicate_key_exit_one(self, tmp_path):
        f = _csv(tmp_path, "id,v\n1,a\n1,b\n")
        res = self._run(str(f), "--required-cols", "id", "--key-cols", "id")
        assert res.returncode == 1

    def test_missing_file_exit_one(self, tmp_path):
        res = self._run(str(tmp_path / "nope.csv"), "--required-cols", "id")
        assert res.returncode == 1
        assert "file not found" in res.stderr

    def test_json_extract_supported(self, tmp_path):
        f = tmp_path / "extract.json"
        f.write_text('[{"id": 1, "v": "a"}, {"id": 2, "v": "b"}]', encoding="utf-8")
        res = self._run(str(f), "--required-cols", "id,v", "--json")
        assert res.returncode == 0
        assert '"row_count": 2' in res.stdout
