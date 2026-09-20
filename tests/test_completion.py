"""Tests for the Completion Engine (evidence, score, regression, versioning, guard)."""
from __future__ import annotations

import pytest

from docforge.completion import (completion_guard, contract, evidence, gates,
                                  regression, score, versioning)


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(evidence, "COMPLETION_DIR", tmp_path / "c")
    monkeypatch.setattr(evidence, "EVIDENCE_PATH", tmp_path / "c" / "evidence.jsonl")
    monkeypatch.setattr(versioning, "VERSIONS_DIR", tmp_path / "v")
    monkeypatch.setattr(versioning, "VERSIONS_PATH", tmp_path / "v" / "versions.json")


def test_score_returns_ten_dimensions():
    s = score.compute({})
    assert s["n_dimensions"] >= 10
    assert 0 <= s["total"] <= 100


def test_score_reflects_given_metrics():
    s = score.compute({"completeness": 100, "correctness": 100})
    assert s["total"] > 50


def test_regression_flagged_on_score_drop():
    r = regression.check({"total": 90}, {"total": 60})
    assert r["regressed"] is True
    assert r["blocking"] is True


def test_regression_flagged_on_gate_flip():
    r = regression.check({"total": 80, "gates": {"A": "PASS"}},
                         {"total": 80, "gates": {"A": "FAIL"}})
    assert r["regressed"] is True


def test_no_regression_on_stable_state():
    r = regression.check({"total": 80, "gates": {"A": "PASS"}},
                         {"total": 82, "gates": {"A": "PASS"}})
    assert r["regressed"] is False


def test_versioning_keeps_best():
    versioning.reset()
    versioning.submit({"total": 70})
    versioning.submit({"total": 55})
    assert versioning.best()["total"] == 70


def test_versioning_promotes_higher():
    versioning.reset()
    versioning.submit({"total": 50})
    versioning.submit({"total": 90})
    assert versioning.best()["total"] == 90


def test_evidence_record_and_read():
    evidence.record("G-TEST", source="unit", result="ok")
    evidence.record("G-TEST", source="unit", result="ok")
    assert len(evidence.for_gate("G-TEST")) == 2


def test_contract_coverage_reports_missing():
    fake_contract = {"requirements": {
        "r1": {"status": "required", "gate": "G-1"},
        "r2": {"status": "required", "gate": "G-2"},
        "r3": {"status": "optional", "gate": "G-3"},
    }}
    cov = contract.coverage({"G-1": "PASS", "G-2": "FAIL"}, fake_contract)
    assert "r1" in cov["covered"]
    assert "r2" in cov["missing"]
    assert cov["total_required"] == 2


def test_guard_rejects_unknown_gate():
    r = completion_guard.evaluate(required_gates=["G-DOES-NOT-EXIST"])
    assert r["verdict"] == "NOT_DONE"
    assert any(u["reason"] == "gate not defined" for u in r["unmet"])
