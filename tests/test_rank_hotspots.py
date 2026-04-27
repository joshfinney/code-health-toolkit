from pathlib import Path

from tools.rank_hotspots import build_scores, render_markdown


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_scores_combines_audit_signals(tmp_path: Path) -> None:
    audit_dir = tmp_path / ".audit"
    write(
        audit_dir / "radon-raw.json",
        '{"src/app/service.py": {"loc": 300}, "src/app/small.py": {"loc": 20}}',
    )
    write(
        audit_dir / "radon-cc.json",
        '{"src/app/service.py": [{"complexity": 18}, {"complexity": 4}]}',
    )
    write(
        audit_dir / "ruff.json",
        '[{"filename": "src/app/service.py"}, {"filename": "src/app/small.py"}]',
    )
    write(
        audit_dir / "pyright.json",
        '{"generalDiagnostics": [{"file": "src/app/service.py", "severity": "error"}]}',
    )
    write(
        audit_dir / "vulture.txt",
        "src/app/service.py:12: unused function 'old' (90% confidence, 8 lines)\n",
    )
    write(
        audit_dir / "coverage.txt",
        "src/app/service.py                 100     60     40%\n",
    )

    scores = build_scores(audit_dir)

    assert scores["src/app/service.py"].score > scores["src/app/small.py"].score
    assert scores["src/app/service.py"].loc == 300
    assert scores["src/app/service.py"].pyright_errors == 1


def test_render_markdown_contains_ranked_rows(tmp_path: Path) -> None:
    audit_dir = tmp_path / ".audit"
    write(audit_dir / "radon-raw.json", '{"src/app/service.py": {"loc": 300}}')

    rows = sorted(build_scores(audit_dir).values(), key=lambda item: item.score, reverse=True)
    markdown = render_markdown(rows, limit=10)

    assert "# Code-Health Hotspots" in markdown
    assert "`src/app/service.py`" in markdown

