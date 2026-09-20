"""Tests for the Audit Engine, Issue Registry, and Checklist."""
from __future__ import annotations

import pytest

from docforge.audit import checklist, issues, engine
from docforge.canonical import new_model


@pytest.fixture(autouse=True)
def _isolate_audit(monkeypatch, tmp_path):
    monkeypatch.setattr(issues, "AUDIT_DIR", tmp_path / "audits")
    monkeypatch.setattr(issues, "ISSUES_PATH", tmp_path / "audits" / "issues.jsonl")
    monkeypatch.setattr(checklist, "CHECKLIST_DIR", tmp_path / "cl")
    monkeypatch.setattr(checklist, "CURRENT_PATH", tmp_path / "cl" / "current.json")


def test_issue_new_rejects_invalid_severity():
    with pytest.raises(ValueError):
        issues.Issue.new(category="x", severity="BLABLA", description="d")


def test_save_and_load_issue():
    i = issues.Issue.new(category="test", severity="LOW",
                         description="probe")
    issues.save_issue(i)
    loaded = issues.load_issues()
    assert len(loaded) == 1
    assert loaded[0]["id"] == i.id


def test_engine_produces_issues_on_empty_model():
    ii = engine.run_audit(new_model())
    assert isinstance(ii, list)
    assert any(x.category == "metadata" for x in ii)


def test_engine_persists_when_asked():
    engine.run_audit(new_model(), persist=True)
    assert len(issues.load_issues()) >= 1


def test_checklist_built_from_registry():
    engine.run_audit(new_model(), persist=True)
    p = checklist.build_from_registry()
    assert p.exists()
    doc = checklist.load_current()
    assert doc["total"] >= 1
    assert doc["tasks"][0]["priority"] <= 3


def test_checklist_sorted_by_severity():
    issues.save_issue(issues.Issue.new(category="a", severity="LOW",
                                        description="low"))
    issues.save_issue(issues.Issue.new(category="a", severity="CRITICAL",
                                        description="crit"))
    checklist.build_from_registry()
    doc = checklist.load_current()
    assert doc["tasks"][0]["severity"] == "CRITICAL"
