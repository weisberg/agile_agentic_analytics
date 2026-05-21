#!/usr/bin/env python3
"""Lightweight CSV/TSV profiler for lead-analyst data-quality audits.

The script intentionally uses only the Python standard library so it can run in
fresh plugin installs without dependency setup. It is not a replacement for
pandas or warehouse-native profiling; it gives the analyst a quick evidence pack.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def sniff_dialect(path: Path, sample_size: int = 8192) -> csv.Dialect:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        sample = handle.read(sample_size)
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t|;")
    except csv.Error:
        return csv.excel


def profile(path: Path, max_examples: int) -> dict[str, Any]:
    dialect = sniff_dialect(path)
    missing: Counter[str] = Counter()
    distinct: dict[str, set[str]] = defaultdict(set)
    examples: dict[str, list[str]] = defaultdict(list)
    duplicate_rows = 0
    seen_rows: set[tuple[tuple[str, str], ...]] = set()
    row_count = 0

    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle, dialect=dialect)
        columns = reader.fieldnames or []
        for row in reader:
            row_count += 1
            normalized = tuple(sorted((key, value or "") for key, value in row.items()))
            if normalized in seen_rows:
                duplicate_rows += 1
            else:
                seen_rows.add(normalized)

            for column in columns:
                value = (row.get(column) or "").strip()
                if value == "":
                    missing[column] += 1
                    continue
                if len(distinct[column]) < 1001:
                    distinct[column].add(value)
                if len(examples[column]) < max_examples and value not in examples[column]:
                    examples[column].append(value)

    return {
        "path": str(path),
        "row_count": row_count,
        "column_count": len(columns),
        "columns": columns,
        "duplicate_full_rows": duplicate_rows,
        "missing": {column: missing[column] for column in columns},
        "distinct_count_capped_1001": {column: len(distinct[column]) for column in columns},
        "examples": {column: examples[column] for column in columns},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="CSV/TSV file to profile.")
    parser.add_argument("--max-examples", type=int, default=3)
    args = parser.parse_args()

    print(json.dumps(profile(args.path, args.max_examples), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
