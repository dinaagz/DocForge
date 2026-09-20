"""Tests for the installer doctor report."""
from __future__ import annotations

from pathlib import Path

import pytest

from docforge.installer import doctor


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DOCFORGE_HOME", str(tmp_path / "rt"))
    monkeypatch.setenv("DOCFORGE_BIN", str(tmp_path / "rt" / "bin"))


def test_check_all_returns_structured_report():
    r = doctor.check_all()
    assert set(r) >= {"version", "checks", "counts", "layout"}
    statuses = {c["status"] for c in r["checks"]}
    assert statuses <= {"OK", "WARNING", "MISSING", "ERROR"}
    assert len(r["checks"]) >= 6


def test_format_report_prints_summary():
    r = doctor.check_all()
    text = doctor.format_report(r)
    assert "DocForge Doctor" in text
    assert "Résumé" in text


def test_python_check_is_ok():
    r = doctor.check_all()
    named = {c["name"]: c for c in r["checks"]}
    assert named["Python version compatible"]["status"] == "OK"
