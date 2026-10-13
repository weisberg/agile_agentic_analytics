#!/usr/bin/env python3
"""Real-model CLI smoke test using synthetic files in a temporary directory."""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=("auto", "mps", "cpu"), default="auto")
    args = parser.parse_args()

    def run(*arguments):
        result = subprocess.run(
            [sys.executable, "-m", "gemsearch", *arguments], check=False, capture_output=True, text=True
        )
        if result.returncode:
            raise RuntimeError(result.stderr)
        return json.loads(result.stdout)

    with tempfile.TemporaryDirectory(prefix="gemsearch-smoke-") as temp:
        root = Path(temp) / "documents"
        root.mkdir()
        (root / "retention.md").write_text(
            "# Account renewal review\nFalling product engagement and unresolved support tickets "
            "signal customers who may cancel their subscriptions.\n",
            encoding="utf-8",
        )
        (root / "cooking.txt").write_text("Lentil soup recipe: simmer vegetables and lentils for dinner.\n")
        before = {p.name: p.read_bytes() for p in root.iterdir()}
        common = ["--root", str(root), "--db", str(Path(temp) / "cache/index.sqlite3")]
        doctor = run("doctor", "--device", args.device)
        indexed = run("index", *common, "--device", args.device)
        assert indexed["indexed"] == 2 and not indexed["issues"]
        query = "How can we identify churn risk?"
        for mode in ("semantic", "hybrid"):
            found = run("search", query, *common, "--mode", mode, "--device", args.device)
            assert found["hits"][0]["path"] == "retention.md", found
        lexical = run("search", "lentils", *common, "--mode", "lexical")
        assert lexical["hits"][0]["path"] == "cooking.txt"
        repeated = run("index", *common, "--device", args.device)
        assert repeated["unchanged"] == 2 and repeated["indexed"] == 0
        assert before == {p.name: p.read_bytes() for p in root.iterdir()}
        print(
            json.dumps(
                {
                    "ok": True,
                    "doctor": doctor,
                    "checks": [
                        "direct Python inference",
                        "semantic synonym retrieval",
                        "hybrid ranking",
                        "lexical search",
                        "incremental indexing",
                        "source files unchanged",
                    ],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
