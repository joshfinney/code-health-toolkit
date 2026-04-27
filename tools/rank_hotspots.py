#!/usr/bin/env python3
"""Rank code-health hotspots from deterministic audit reports."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class FileScore:
    path: str
    loc: int = 0
    complexity_points: float = 0.0
    complexity_findings: int = 0
    ruff_findings: int = 0
    pyright_errors: int = 0
    pyright_warnings: int = 0
    vulture_points: float = 0.0
    vulture_findings: int = 0
    duplicate_points: float = 0.0
    duplicate_regions: int = 0
    coverage_percent: float | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def score(self) -> float:
        coverage_penalty = 0.0
        if self.coverage_percent is not None:
            coverage_penalty = max(0.0, 80.0 - self.coverage_percent) * 1.2

        return (
            self.loc * 0.12
            + self.complexity_points
            + self.ruff_findings * 4.0
            + self.pyright_errors * 10.0
            + self.pyright_warnings * 4.0
            + self.vulture_points
            + self.duplicate_points
            + coverage_penalty
        )


def normalise_path(path: str) -> str:
    path = path.replace("\\", "/")
    marker = "/src/"
    if marker in path:
        return "src/" + path.split(marker, 1)[1]
    marker = "/tests/"
    if marker in path:
        return "tests/" + path.split(marker, 1)[1]
    return path.lstrip("./")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists() or path.stat().st_size == 0:
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def get_score(scores: dict[str, FileScore], path: str) -> FileScore:
    key = normalise_path(path)
    if key not in scores:
        scores[key] = FileScore(path=key)
    return scores[key]


def parse_radon_raw(audit_dir: Path, scores: dict[str, FileScore]) -> None:
    raw = load_json(audit_dir / "radon-raw.json", {})
    if not isinstance(raw, dict):
        return

    for path, metrics in raw.items():
        if not isinstance(metrics, dict):
            continue
        score = get_score(scores, path)
        score.loc = int(metrics.get("loc") or metrics.get("sloc") or 0)


def parse_radon_complexity(audit_dir: Path, scores: dict[str, FileScore]) -> None:
    data = load_json(audit_dir / "radon-cc.json", {})
    if not isinstance(data, dict):
        return

    for path, blocks in data.items():
        if not isinstance(blocks, list):
            continue
        file_score = get_score(scores, path)
        for block in blocks:
            if not isinstance(block, dict):
                continue
            complexity = int(block.get("complexity") or 0)
            if complexity >= 10:
                file_score.complexity_findings += 1
                file_score.complexity_points += (complexity - 8) * 4


def parse_ruff(audit_dir: Path, scores: dict[str, FileScore]) -> None:
    data = load_json(audit_dir / "ruff.json", [])
    if not isinstance(data, list):
        return

    for finding in data:
        if not isinstance(finding, dict):
            continue
        filename = finding.get("filename")
        if filename:
            get_score(scores, filename).ruff_findings += 1


def parse_pyright(audit_dir: Path, scores: dict[str, FileScore]) -> None:
    data = load_json(audit_dir / "pyright.json", {})
    diagnostics = data.get("generalDiagnostics", []) if isinstance(data, dict) else []

    for diagnostic in diagnostics:
        if not isinstance(diagnostic, dict):
            continue
        path = diagnostic.get("file")
        if not path:
            continue
        severity = diagnostic.get("severity")
        file_score = get_score(scores, path)
        if severity == "error":
            file_score.pyright_errors += 1
        else:
            file_score.pyright_warnings += 1


VULTURE_RE = re.compile(
    r"^(?P<path>.*?\.py):\d+:\s.*\((?P<confidence>\d+)% confidence"
)


def parse_vulture(audit_dir: Path, scores: dict[str, FileScore]) -> None:
    path = audit_dir / "vulture.txt"
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = VULTURE_RE.match(line.strip())
        if not match:
            continue
        confidence = int(match.group("confidence"))
        file_score = get_score(scores, match.group("path"))
        file_score.vulture_findings += 1
        file_score.vulture_points += max(0, confidence - 50) / 5


def candidate_jscpd_reports(audit_dir: Path) -> list[Path]:
    return [
        audit_dir / "jscpd" / "jscpd-report.json",
        audit_dir / "jscpd-report.json",
    ]


def duplicate_size(duplicate: dict[str, Any]) -> int:
    if isinstance(duplicate.get("lines"), int):
        return int(duplicate["lines"])
    first_file = duplicate.get("firstFile")
    if isinstance(first_file, dict):
        start = first_file.get("start") or first_file.get("startLoc", {}).get("line")
        end = first_file.get("end") or first_file.get("endLoc", {}).get("line")
        if isinstance(start, int) and isinstance(end, int) and end >= start:
            return end - start + 1
    return 10


def duplicate_paths(duplicate: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in ("firstFile", "secondFile"):
        value = duplicate.get(key)
        if isinstance(value, dict) and value.get("name"):
            paths.append(str(value["name"]))
        elif isinstance(value, str):
            paths.append(value)
    return paths


def parse_jscpd(audit_dir: Path, scores: dict[str, FileScore]) -> None:
    report = next((path for path in candidate_jscpd_reports(audit_dir) if path.exists()), None)
    if report is None:
        return

    data = load_json(report, {})
    duplicates = data.get("duplicates", []) if isinstance(data, dict) else []
    if not isinstance(duplicates, list):
        return

    for duplicate in duplicates:
        if not isinstance(duplicate, dict):
            continue
        size = duplicate_size(duplicate)
        for path in duplicate_paths(duplicate):
            file_score = get_score(scores, path)
            file_score.duplicate_regions += 1
            file_score.duplicate_points += size * 1.5


COVERAGE_RE = re.compile(
    r"^(?P<path>(src|tests)/\S+\.py)\s+\d+\s+\d+(?:\s+\d+\s+\d+)?\s+(?P<percent>\d+)%"
)


def parse_coverage(audit_dir: Path, scores: dict[str, FileScore]) -> None:
    path = audit_dir / "coverage.txt"
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = COVERAGE_RE.match(line.strip())
        if not match:
            continue
        file_score = get_score(scores, match.group("path"))
        file_score.coverage_percent = float(match.group("percent"))


def build_scores(audit_dir: Path) -> dict[str, FileScore]:
    scores: dict[str, FileScore] = {}
    parse_radon_raw(audit_dir, scores)
    parse_radon_complexity(audit_dir, scores)
    parse_ruff(audit_dir, scores)
    parse_pyright(audit_dir, scores)
    parse_vulture(audit_dir, scores)
    parse_jscpd(audit_dir, scores)
    parse_coverage(audit_dir, scores)
    return scores


def score_to_dict(score: FileScore) -> dict[str, Any]:
    return {
        "path": score.path,
        "score": round(score.score, 2),
        "loc": score.loc,
        "complexity_findings": score.complexity_findings,
        "ruff_findings": score.ruff_findings,
        "pyright_errors": score.pyright_errors,
        "pyright_warnings": score.pyright_warnings,
        "vulture_findings": score.vulture_findings,
        "duplicate_regions": score.duplicate_regions,
        "coverage_percent": score.coverage_percent,
    }


def render_markdown(rows: list[FileScore], limit: int) -> str:
    selected = rows[:limit]
    lines = [
        "# Code-Health Hotspots",
        "",
        "Ranked from deterministic audit evidence. Treat this as a triage queue, not an automatic refactor order.",
        "",
        "| Rank | File | Score | LOC | Complexity | Ruff | Pyright | Vulture | Dupes | Coverage |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for index, score in enumerate(selected, start=1):
        pyright_total = score.pyright_errors + score.pyright_warnings
        coverage = "" if score.coverage_percent is None else f"{score.coverage_percent:.0f}%"
        lines.append(
            "| {rank} | `{path}` | {score:.1f} | {loc} | {complexity} | {ruff} | "
            "{pyright} | {vulture} | {dupes} | {coverage} |".format(
                rank=index,
                path=score.path,
                score=score.score,
                loc=score.loc,
                complexity=score.complexity_findings,
                ruff=score.ruff_findings,
                pyright=pyright_total,
                vulture=score.vulture_findings,
                dupes=score.duplicate_regions,
                coverage=coverage,
            )
        )

    lines.extend(
        [
            "",
            "## How to use this",
            "",
            "Pick one file from the top of the list. Before refactoring, read the tests, add characterisation coverage where behaviour is unclear, then make one bounded change.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-dir", default=".audit", type=Path)
    parser.add_argument("--limit", default=25, type=int)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--output-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scores = build_scores(args.audit_dir)
    rows = sorted(scores.values(), key=lambda item: item.score, reverse=True)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps([score_to_dict(row) for row in rows], indent=2) + "\n",
            encoding="utf-8",
        )

    markdown = render_markdown(rows, args.limit)
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

