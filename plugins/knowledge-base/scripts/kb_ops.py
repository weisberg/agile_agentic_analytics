#!/usr/bin/env python3
"""Deterministic operating-system checks for the knowledge-base plugin.

The individual KB skills describe workflows. This script provides the shared
audit, routing, retrieval, graph, citation, source, privacy, dashboard, and
checkpoint machinery those workflows can call from tests, CI, or agent runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only in under-provisioned envs.
    yaml = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
INDEX_FILENAME = "INDEX.jsonl"
DEFAULT_ROUTING_EVAL = PLUGIN_ROOT / "references/routing-eval.jsonl"
DEFAULT_RETRIEVAL_BENCHMARK = PLUGIN_ROOT / "references/benchmarks/retrieval-benchmarks.jsonl"

REQUIRED_PAGE_FIELDS = ("id", "title", "description")
RELATION_FIELDS = ("related", "depends_on", "mentions", "backlinks", "conflicts_with")
SECRET_PATTERNS = {
    "api_key": re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    "aws_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "absolute_user_path": re.compile(r"/Users/[^/\s]+/"),
}
FACT_HINT = re.compile(
    r"(\b\d{4}-\d{2}-\d{2}\b|\b\d+(?:\.\d+)?%?\b|\b(is|are|was|were|will|must|requires|"
    r"decided|launched|met|founded|works at|invested|owns|supports)\b)",
    re.IGNORECASE,
)
SOURCE_CITATION = re.compile(r"\[Source:\s*[^\]]+\]")


@dataclass
class Issue:
    code: str
    message: str
    file: str | None = None
    severity: str = "error"
    hint: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }
        if self.file:
            payload["file"] = self.file
        if self.hint:
            payload["hint"] = self.hint
        return payload


@dataclass
class ParsedMarkdown:
    path: Path
    relative_path: str
    metadata: dict[str, Any]
    body: str
    has_frontmatter: bool
    raw_frontmatter: str = ""
    issues: list[Issue] = field(default_factory=list)

    @property
    def doc_id(self) -> str | None:
        value = self.metadata.get("id")
        return value if isinstance(value, str) and value.strip() else None


def json_print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=False))


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def root_path(value: str | None) -> Path:
    return Path(value or ".").expanduser().resolve()


def load_yaml_mapping(raw: str, path: Path) -> tuple[dict[str, Any], Issue | None]:
    if yaml is None:
        return {}, Issue(
            code="YAML_UNAVAILABLE",
            message="PyYAML is required for frontmatter parsing.",
            file=repo_relative(path),
            hint="Install PyYAML or run through the repository test environment.",
        )
    try:
        parsed = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        return {}, Issue(
            code="INVALID_YAML",
            message=f"Invalid YAML frontmatter: {exc}",
            file=repo_relative(path),
            hint="Repair frontmatter syntax before indexing.",
        )
    if not isinstance(parsed, dict):
        return {}, Issue(
            code="FRONTMATTER_NOT_MAPPING",
            message="Frontmatter must parse to a mapping.",
            file=repo_relative(path),
        )
    return parsed, None


def parse_markdown(path: Path, root: Path) -> ParsedMarkdown:
    rel = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8")
    if "\x00" in text:
        return ParsedMarkdown(
            path=path,
            relative_path=rel,
            metadata={},
            body=text,
            has_frontmatter=False,
            issues=[Issue(code="NULL_BYTE", message="Markdown file contains a null byte.", file=rel)],
        )

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return ParsedMarkdown(path=path, relative_path=rel, metadata={}, body=text, has_frontmatter=False)

    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        return ParsedMarkdown(
            path=path,
            relative_path=rel,
            metadata={},
            body=text,
            has_frontmatter=False,
            issues=[Issue(code="MISSING_FRONTMATTER_CLOSE", message="Missing closing frontmatter fence.", file=rel)],
        )

    raw = "".join(lines[1:closing_index])
    body = "".join(lines[closing_index + 1 :])
    metadata, issue = load_yaml_mapping(raw, path)
    issues = [issue] if issue else []
    return ParsedMarkdown(
        path=path,
        relative_path=rel,
        metadata=metadata,
        body=body,
        has_frontmatter=True,
        raw_frontmatter=raw,
        issues=issues,
    )


def iter_markdown(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if path.is_file()
        and INDEX_FILENAME not in path.parts
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
    )


def parse_documents(root: Path) -> list[ParsedMarkdown]:
    return [parse_markdown(path, root) for path in iter_markdown(root)]


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def load_index(root: Path) -> list[dict[str, Any]]:
    index_path = root / INDEX_FILENAME
    if not index_path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{index_path}:{line_number}: invalid JSONL: {exc}") from exc
        if isinstance(payload, dict):
            records.append(payload)
    return records


def read_skill_frontmatter(skill_file: Path) -> dict[str, Any]:
    parsed = parse_markdown(skill_file, skill_file.parent)
    return parsed.metadata


def skill_inventory(plugin_root: Path) -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []
    for skill_file in sorted((plugin_root / "skills").glob("*/SKILL.md")):
        metadata = read_skill_frontmatter(skill_file)
        extras = [
            repo_relative(path) for path in skill_file.parent.rglob("*") if path.is_file() and path.name != "SKILL.md"
        ]
        skills.append(
            {
                "slug": skill_file.parent.name,
                "path": repo_relative(skill_file),
                "name": metadata.get("name"),
                "description": metadata.get("description"),
                "triggers": normalize_list(metadata.get("triggers")),
                "tools": normalize_list(metadata.get("tools")),
                "mutating": bool(metadata.get("mutating", False)),
                "writes_pages": bool(metadata.get("writes_pages", False)),
                "line_count": len(skill_file.read_text(encoding="utf-8").splitlines()),
                "supporting_files": extras,
            }
        )
    return skills


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[Issue]]:
    rows: list[dict[str, Any]] = []
    issues: list[Issue] = []
    if not path.exists():
        return rows, [
            Issue(code="MISSING_JSONL", message=f"Missing JSONL file: {repo_relative(path)}", file=repo_relative(path))
        ]
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("//"):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            issues.append(Issue(code="INVALID_JSONL", message=f"Line {line_number}: {exc}", file=repo_relative(path)))
            continue
        if not isinstance(payload, dict):
            issues.append(
                Issue(
                    code="JSONL_NOT_OBJECT", message=f"Line {line_number} is not an object.", file=repo_relative(path)
                )
            )
            continue
        rows.append(payload)
    return rows, issues


def resolver_check(plugin_root: Path, routing_eval: Path) -> dict[str, Any]:
    skills = skill_inventory(plugin_root)
    skill_by_slug = {skill["slug"]: skill for skill in skills}
    fixtures, issues = load_jsonl(routing_eval)

    fixture_counts: dict[str, int] = {slug: 0 for slug in skill_by_slug}
    seen_intents: set[str] = set()
    for fixture in fixtures:
        intent = str(fixture.get("intent", "")).strip()
        expected = str(fixture.get("expected_skill", "")).strip()
        if not intent:
            issues.append(
                Issue(
                    code="ROUTING_EMPTY_INTENT",
                    message="Routing fixture has no intent.",
                    file=repo_relative(routing_eval),
                )
            )
        elif intent.casefold() in seen_intents:
            issues.append(
                Issue(
                    code="ROUTING_DUPLICATE_INTENT",
                    message=f"Duplicate routing intent: {intent}",
                    file=repo_relative(routing_eval),
                    severity="warn",
                )
            )
        seen_intents.add(intent.casefold())

        if expected not in skill_by_slug:
            issues.append(
                Issue(
                    code="ROUTING_UNKNOWN_SKILL",
                    message=f"Fixture expects unknown skill: {expected}",
                    file=repo_relative(routing_eval),
                )
            )
        else:
            fixture_counts[expected] += 1
        for ambiguous in normalize_list(fixture.get("ambiguous_with")):
            if ambiguous not in skill_by_slug:
                issues.append(
                    Issue(
                        code="ROUTING_UNKNOWN_AMBIGUOUS_SKILL",
                        message=f"Fixture references unknown ambiguous skill: {ambiguous}",
                        file=repo_relative(routing_eval),
                    )
                )

    for skill in skills:
        if not skill["description"]:
            issues.append(
                Issue(code="SKILL_NO_DESCRIPTION", message=f"{skill['slug']} has no description.", file=skill["path"])
            )
        if not skill["triggers"]:
            issues.append(
                Issue(
                    code="SKILL_NO_TRIGGERS",
                    message=f"{skill['slug']} has no triggers.",
                    file=skill["path"],
                    severity="warn",
                )
            )
        if fixture_counts[skill["slug"]] == 0:
            issues.append(
                Issue(
                    code="SKILL_NO_ROUTING_FIXTURE",
                    message=f"{skill['slug']} has no routing fixture.",
                    file=skill["path"],
                    severity="warn",
                )
            )

    return {
        "ok": not any(issue.severity == "error" for issue in issues),
        "skills": len(skills),
        "fixtures": len(fixtures),
        "fixture_counts": fixture_counts,
        "issues": [issue.as_dict() for issue in issues],
    }


def frontmatter_audit(root: Path) -> dict[str, Any]:
    docs = parse_documents(root)
    issues: list[Issue] = []
    by_id: dict[str, ParsedMarkdown] = {}

    for doc in docs:
        issues.extend(doc.issues)
        if not doc.has_frontmatter:
            issues.append(
                Issue(code="MISSING_FRONTMATTER", message="Markdown file has no frontmatter.", file=doc.relative_path)
            )
            continue
        for field_name in REQUIRED_PAGE_FIELDS:
            if not doc.metadata.get(field_name):
                issues.append(
                    Issue(
                        code="MISSING_REQUIRED_FIELD",
                        message=f"Missing required field: {field_name}",
                        file=doc.relative_path,
                    )
                )
        if doc.doc_id:
            if doc.doc_id in by_id:
                issues.append(Issue(code="DUPLICATE_ID", message=f"Duplicate id: {doc.doc_id}", file=doc.relative_path))
            by_id[doc.doc_id] = doc

        source = doc.metadata.get("source")
        if isinstance(source, str) and source.strip():
            source_path = (doc.path.parent / source).resolve()
            try:
                source_path.relative_to(root)
            except ValueError:
                issues.append(
                    Issue(
                        code="SOURCE_ESCAPES_ROOT",
                        message=f"Source escapes vault root: {source}",
                        file=doc.relative_path,
                    )
                )
            if not source_path.exists():
                issues.append(
                    Issue(
                        code="BROKEN_SOURCE", message=f"Source target does not exist: {source}", file=doc.relative_path
                    )
                )

    known_ids = set(by_id)
    for doc in docs:
        for field_name in RELATION_FIELDS:
            for target in normalize_list(doc.metadata.get(field_name)):
                if "://" in target:
                    continue
                if target not in known_ids:
                    issues.append(
                        Issue(
                            code="DANGLING_REFERENCE",
                            message=f"{field_name} references missing id: {target}",
                            file=doc.relative_path,
                            severity="warn",
                        )
                    )

    index_ids = {str(record.get("id")) for record in load_index(root) if record.get("id")}
    doc_ids = known_ids
    if index_ids and index_ids != doc_ids:
        for missing in sorted(doc_ids - index_ids):
            issues.append(
                Issue(
                    code="STALE_INDEX_MISSING_DOC",
                    message=f"Document id missing from index: {missing}",
                    file=INDEX_FILENAME,
                    severity="warn",
                )
            )
        for extra in sorted(index_ids - doc_ids):
            issues.append(
                Issue(
                    code="STALE_INDEX_EXTRA_DOC",
                    message=f"Index id has no document: {extra}",
                    file=INDEX_FILENAME,
                    severity="warn",
                )
            )

    return {
        "ok": not any(issue.severity == "error" for issue in issues),
        "root": str(root),
        "documents": len(docs),
        "ids": len(known_ids),
        "issues": [issue.as_dict() for issue in issues],
    }


def citation_audit(root: Path) -> dict[str, Any]:
    issues: list[Issue] = []
    checked_lines = 0
    for doc in parse_documents(root):
        in_code = False
        for line_number, raw_line in enumerate(doc.body.splitlines(), start=1):
            line = raw_line.strip()
            if line.startswith("```"):
                in_code = not in_code
                continue
            if in_code or not line or line.startswith("#") or line.startswith("|") or line.startswith("---"):
                continue
            if len(line) < 30:
                continue
            checked_lines += 1
            if FACT_HINT.search(line) and not SOURCE_CITATION.search(line):
                issues.append(
                    Issue(
                        code="UNCITED_FACT_CANDIDATE",
                        message=f"Possible factual claim without inline [Source: ...] citation at line {line_number}.",
                        file=doc.relative_path,
                        severity="warn",
                        hint=line[:180],
                    )
                )
    return {
        "ok": True,
        "root": str(root),
        "checked_lines": checked_lines,
        "issues": [issue.as_dict() for issue in issues],
    }


def graph_audit(root: Path) -> dict[str, Any]:
    docs = parse_documents(root)
    by_id = {doc.doc_id: doc for doc in docs if doc.doc_id}
    issues: list[Issue] = []
    edges: list[dict[str, str]] = []

    for doc in docs:
        if not doc.doc_id:
            continue
        for field_name in RELATION_FIELDS:
            for target in normalize_list(doc.metadata.get(field_name)):
                edges.append({"from": doc.doc_id, "to": target, "type": field_name})
                if "://" not in target and target not in by_id:
                    issues.append(
                        Issue(
                            code="GRAPH_DANGLING_EDGE",
                            message=f"{field_name} points to missing id: {target}",
                            file=doc.relative_path,
                            severity="warn",
                        )
                    )

    related_edges = {(edge["from"], edge["to"]) for edge in edges if edge["type"] == "related"}
    backlink_edges = {(edge["from"], edge["to"]) for edge in edges if edge["type"] == "backlinks"}
    mention_edges = {(edge["from"], edge["to"]) for edge in edges if edge["type"] == "mentions"}
    for source, target in sorted(related_edges):
        if "://" in target or target not in by_id:
            continue
        if (target, source) not in related_edges:
            issues.append(
                Issue(
                    code="GRAPH_ONE_WAY_RELATED",
                    message=f"Related edge is one-way: {source} -> {target}",
                    file=by_id[source].relative_path,
                    severity="warn",
                )
            )
    for source, target in sorted(mention_edges):
        if "://" in target or target not in by_id:
            continue
        if (target, source) not in backlink_edges and (target, source) not in related_edges:
            issues.append(
                Issue(
                    code="GRAPH_MISSING_BACKLINK",
                    message=f"Mention lacks reciprocal backlink or related edge: {source} -> {target}",
                    file=by_id[source].relative_path,
                    severity="warn",
                )
            )

    return {
        "ok": True,
        "nodes": len(by_id),
        "edges": len(edges),
        "issues": [issue.as_dict() for issue in issues],
    }


def raw_source_audit(root: Path) -> dict[str, Any]:
    issues: list[Issue] = []
    raw_sources = 0
    redirect_pointers = 0
    for doc in parse_documents(root):
        source = doc.metadata.get("source")
        source_url = doc.metadata.get("source_url")
        raw_pointer = doc.metadata.get("raw_pointer") or doc.metadata.get("raw")
        if source:
            raw_sources += 1
            source_path = (doc.path.parent / str(source)).resolve()
            if not source_path.exists():
                issues.append(
                    Issue(code="RAW_SOURCE_MISSING", message=f"Source file missing: {source}", file=doc.relative_path)
                )
        if source_url:
            raw_sources += 1
        if isinstance(raw_pointer, dict) and raw_pointer.get("target"):
            redirect_pointers += 1
        elif isinstance(raw_pointer, str) and raw_pointer:
            redirect_pointers += 1
    return {
        "ok": not any(issue.severity == "error" for issue in issues),
        "raw_sources": raw_sources,
        "redirect_pointers": redirect_pointers,
        "issues": [issue.as_dict() for issue in issues],
    }


def privacy_audit(root: Path) -> dict[str, Any]:
    issues: list[Issue] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == INDEX_FILENAME or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(root).as_posix()
        for code, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                issues.append(
                    Issue(
                        code=f"PRIVACY_{code.upper()}", message=f"Sensitive-looking content matched {code}.", file=rel
                    )
                )
    return {
        "ok": not any(issue.severity == "error" for issue in issues),
        "issues": [issue.as_dict() for issue in issues],
    }


def score_record(record: dict[str, Any], query: str) -> float:
    terms = [term for term in re.split(r"\W+", query.casefold()) if term]
    if not terms:
        return 1.0
    weights = {"title": 8, "description": 6, "tags": 4, "aliases": 4, "id": 2, "category": 1}
    score = 0.0
    for field_name, weight in weights.items():
        haystack = json.dumps(record.get(field_name), ensure_ascii=False).casefold()
        score += sum(haystack.count(term) * weight for term in terms)
    return score


def query_vault(root: Path, query: str, limit: int, include_body: bool) -> dict[str, Any]:
    records = load_index(root)
    scored = []
    for record in records:
        score = score_record(record, query)
        if score > 0:
            enriched = dict(record)
            enriched["score"] = score
            if include_body and record.get("file"):
                file_path = root / str(record["file"])
                if file_path.exists() and file_path.suffix == ".md":
                    parsed = parse_markdown(file_path, root)
                    enriched["body_preview"] = parsed.body.strip()[:1200]
            scored.append(enriched)
    scored.sort(key=lambda item: (-float(item.get("score", 0)), str(item.get("id", ""))))
    results = scored[:limit]
    return {
        "ok": True,
        "root": str(root),
        "query": query,
        "total": len(scored),
        "results": results,
        "confidence": "high" if results and results[0].get("score", 0) >= 6 else "medium" if results else "low",
        "gaps": []
        if results
        else ["No indexed metadata matched. Try rebuilding INDEX.jsonl or improving descriptions/tags."],
    }


def retrieval_benchmark(root: Path, benchmark_file: Path, limit: int) -> dict[str, Any]:
    rows, issues = load_jsonl(benchmark_file)
    runs: list[dict[str, Any]] = []
    passed = 0
    for row in rows:
        query = str(row.get("query", "")).strip()
        expected_ids = normalize_list(row.get("expected_ids") or row.get("expected_id"))
        if not query:
            issues.append(
                Issue(
                    code="BENCHMARK_EMPTY_QUERY",
                    message="Benchmark row has no query.",
                    file=repo_relative(benchmark_file),
                )
            )
            continue
        if not expected_ids:
            issues.append(
                Issue(
                    code="BENCHMARK_NO_EXPECTED_IDS",
                    message=f"Benchmark row has no expected ids: {query}",
                    file=repo_relative(benchmark_file),
                )
            )
            continue
        result = query_vault(root, query, limit, include_body=False)
        actual_ids = [str(item.get("id")) for item in result["results"] if item.get("id")]
        missing = [expected_id for expected_id in expected_ids if expected_id not in actual_ids]
        hit = not missing
        if hit:
            passed += 1
        runs.append(
            {
                "query": query,
                "expected_ids": expected_ids,
                "actual_ids": actual_ids,
                "hit": hit,
                "missing_ids": missing,
                "mode": row.get("mode", "metadata"),
                "notes": row.get("notes", ""),
            }
        )
    total = len(runs)
    recall = passed / total if total else 0.0
    if total == 0:
        issues.append(
            Issue(
                code="BENCHMARK_NO_RUNS", message="No benchmark rows could be run.", file=repo_relative(benchmark_file)
            )
        )
    for run in runs:
        if not run["hit"]:
            issues.append(
                Issue(
                    code="BENCHMARK_MISS",
                    message=f"Query missed expected ids: {run['query']}",
                    file=repo_relative(benchmark_file),
                    hint=", ".join(run["missing_ids"]),
                )
            )
    return {
        "ok": not any(issue.severity == "error" for issue in issues),
        "root": str(root),
        "benchmark_file": repo_relative(benchmark_file),
        "limit": limit,
        "passed": passed,
        "total": total,
        "recall": recall,
        "runs": runs,
        "issues": [issue.as_dict() for issue in issues],
    }


def dashboard(root: Path, plugin_root: Path, routing_eval: Path) -> dict[str, Any]:
    sections = {
        "frontmatter": frontmatter_audit(root),
        "citations": citation_audit(root),
        "graph": graph_audit(root),
        "raw_sources": raw_source_audit(root),
        "privacy": privacy_audit(root),
        "resolver": resolver_check(plugin_root, routing_eval),
    }
    issue_counts = {name: len(section.get("issues", [])) for name, section in sections.items()}
    error_counts = {
        name: sum(1 for issue in section.get("issues", []) if issue.get("severity") == "error")
        for name, section in sections.items()
    }
    return {
        "ok": not any(error_counts.values()),
        "root": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scorecard": {
            name: {
                "issues": issue_counts[name],
                "errors": error_counts[name],
                "status": "red" if error_counts[name] else "yellow" if issue_counts[name] else "green",
            }
            for name in sections
        },
        "sections": sections,
    }


def maintenance_plan(root: Path, plugin_root: Path, routing_eval: Path) -> dict[str, Any]:
    report = dashboard(root, plugin_root, routing_eval)
    actions: list[dict[str, str]] = []
    priority = {
        "frontmatter": "Run frontmatter-guard; repair required fields, broken sources, duplicate IDs, and stale index.",
        "privacy": "Run privacy-security before indexing, publishing, or exporting sensitive pages.",
        "raw_sources": "Run raw-source; restore missing source assets or replace with redirect pointers.",
        "graph": "Run graph-ops; resolve dangling and one-way relationship edges.",
        "citations": "Run citation-fixer; add inline [Source: ...] citations or mark unverifiable claims.",
        "resolver": "Run resolver; add routing fixtures and tighten ambiguous triggers.",
    }
    for name, guidance in priority.items():
        score = report["scorecard"][name]
        if score["issues"]:
            actions.append({"area": name, "status": score["status"], "action": guidance})
    return {
        "ok": True,
        "root": str(root),
        "actions": actions,
        "dashboard": report["scorecard"],
    }


def write_checkpoint(
    root: Path, job: str, state: str, completed: str, remaining: str, validation: str
) -> dict[str, Any]:
    checkpoint_dir = root / ".kb" / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", job.casefold()).strip("-") or "kb-job"
    path = checkpoint_dir / f"{slug}.json"
    payload = {
        "job": job,
        "state": state,
        "completed": [item for item in completed.split(",") if item],
        "remaining": [item for item in remaining.split(",") if item],
        "validation": validation,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"ok": True, "path": str(path), "checkpoint": payload}


def normalize_event(input_path: Path, provider: str, event_type: str) -> dict[str, Any]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    raw_text = json.dumps(payload, sort_keys=True)
    digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()[:16]
    title = payload.get("title") or payload.get("subject") or payload.get("name") or f"{provider} {event_type}"
    occurred = payload.get("occurred_at") or payload.get("date") or payload.get("timestamp")
    return {
        "ok": True,
        "envelope": {
            "schema_version": "kb-source-envelope/v1",
            "idempotency_key": f"{provider}:{event_type}:{digest}",
            "provider": provider,
            "event_type": event_type,
            "source_uri": payload.get("url") or payload.get("source_uri") or f"{provider}://{digest}",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "occurred_at": occurred,
            "actor": payload.get("actor", {}),
            "privacy": payload.get("privacy", {"scope": "personal", "contains_pii": False, "contains_secret": False}),
            "raw": {
                "hash": f"sha256:{hashlib.sha256(raw_text.encode('utf-8')).hexdigest()}",
                "mime": "application/json",
            },
            "routing": payload.get("routing", {}),
            "entities": payload.get("entities", {"people": [], "companies": [], "concepts": []}),
            "content": {"title": title, "text": payload.get("text") or payload.get("body") or ""},
        },
    }


def validate_schedule(path: Path) -> dict[str, Any]:
    metadata, issue = load_yaml_mapping(path.read_text(encoding="utf-8"), path)
    issues = [issue] if issue else []
    for required in ("name", "cadence", "timezone", "max_runtime_minutes", "prompt"):
        if not metadata.get(required):
            issues.append(
                Issue(
                    code="SCHEDULE_MISSING_FIELD",
                    message=f"Missing schedule field: {required}",
                    file=repo_relative(path),
                )
            )
    if metadata.get("max_runtime_minutes"):
        try:
            runtime = int(metadata["max_runtime_minutes"])
        except (TypeError, ValueError):
            issues.append(
                Issue(
                    code="SCHEDULE_RUNTIME_INVALID",
                    message="max_runtime_minutes must be an integer.",
                    file=repo_relative(path),
                )
            )
        else:
            if runtime > 240:
                issues.append(
                    Issue(
                        code="SCHEDULE_RUNTIME_TOO_LONG",
                        message="max_runtime_minutes should be <= 240.",
                        file=repo_relative(path),
                        severity="warn",
                    )
                )
    return {
        "ok": not any(item and item.severity == "error" for item in issues),
        "schedule": metadata,
        "issues": [item.as_dict() for item in issues if item],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Knowledge Base operating-system utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inv = subparsers.add_parser("skill-inventory")
    inv.add_argument("--plugin-root", default=str(PLUGIN_ROOT))

    resolver = subparsers.add_parser("resolver-check")
    resolver.add_argument("--plugin-root", default=str(PLUGIN_ROOT))
    resolver.add_argument("--routing-eval", default=str(DEFAULT_ROUTING_EVAL))

    for command in ("frontmatter-audit", "citation-audit", "graph-audit", "raw-source-audit", "privacy-audit"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--root", required=True)

    query = subparsers.add_parser("query")
    query.add_argument("query")
    query.add_argument("--root", required=True)
    query.add_argument("--limit", type=int, default=5)
    query.add_argument("--include-body", action="store_true")

    bench = subparsers.add_parser("retrieval-benchmark")
    bench.add_argument("--root", required=True)
    bench.add_argument("--benchmark-file", default=str(DEFAULT_RETRIEVAL_BENCHMARK))
    bench.add_argument("--limit", type=int, default=5)

    dash = subparsers.add_parser("dashboard")
    dash.add_argument("--root", required=True)
    dash.add_argument("--plugin-root", default=str(PLUGIN_ROOT))
    dash.add_argument("--routing-eval", default=str(DEFAULT_ROUTING_EVAL))

    maintain = subparsers.add_parser("maintenance-plan")
    maintain.add_argument("--root", required=True)
    maintain.add_argument("--plugin-root", default=str(PLUGIN_ROOT))
    maintain.add_argument("--routing-eval", default=str(DEFAULT_ROUTING_EVAL))

    checkpoint = subparsers.add_parser("checkpoint")
    checkpoint.add_argument("--root", required=True)
    checkpoint.add_argument("--job", required=True)
    checkpoint.add_argument("--state", default="in_progress")
    checkpoint.add_argument("--completed", default="")
    checkpoint.add_argument("--remaining", default="")
    checkpoint.add_argument("--validation", default="not-run")

    event = subparsers.add_parser("normalize-event")
    event.add_argument("--input", required=True)
    event.add_argument("--provider", required=True)
    event.add_argument("--event-type", required=True)

    schedule = subparsers.add_parser("validate-schedule")
    schedule.add_argument("--file", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "skill-inventory":
        json_print({"ok": True, "skills": skill_inventory(root_path(args.plugin_root))})
        return 0
    if args.command == "resolver-check":
        payload = resolver_check(root_path(args.plugin_root), root_path(args.routing_eval))
        json_print(payload)
        return 0 if payload["ok"] else 1
    if args.command == "frontmatter-audit":
        payload = frontmatter_audit(root_path(args.root))
    elif args.command == "citation-audit":
        payload = citation_audit(root_path(args.root))
    elif args.command == "graph-audit":
        payload = graph_audit(root_path(args.root))
    elif args.command == "raw-source-audit":
        payload = raw_source_audit(root_path(args.root))
    elif args.command == "privacy-audit":
        payload = privacy_audit(root_path(args.root))
    elif args.command == "query":
        payload = query_vault(root_path(args.root), args.query, args.limit, args.include_body)
    elif args.command == "retrieval-benchmark":
        payload = retrieval_benchmark(root_path(args.root), root_path(args.benchmark_file), args.limit)
    elif args.command == "dashboard":
        payload = dashboard(root_path(args.root), root_path(args.plugin_root), root_path(args.routing_eval))
    elif args.command == "maintenance-plan":
        payload = maintenance_plan(root_path(args.root), root_path(args.plugin_root), root_path(args.routing_eval))
    elif args.command == "checkpoint":
        payload = write_checkpoint(
            root_path(args.root), args.job, args.state, args.completed, args.remaining, args.validation
        )
    elif args.command == "normalize-event":
        payload = normalize_event(root_path(args.input), args.provider, args.event_type)
    elif args.command == "validate-schedule":
        payload = validate_schedule(root_path(args.file))
    else:
        raise AssertionError(args.command)

    json_print(payload)
    return 0 if payload.get("ok", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
