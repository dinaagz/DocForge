"""Tests for the improvement loop and completion contract module."""
from __future__ import annotations

import pytest

from docforge.completion import evidence, versioning
from docforge.improvement.loop import run_bounded


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(evidence, "COMPLETION_DIR", tmp_path / "c")
    monkeypatch.setattr(evidence, "EVIDENCE_PATH", tmp_path / "c" / "evidence.jsonl")
    monkeypatch.setattr(versioning, "VERSIONS_DIR", tmp_path / "v")
    monkeypatch.setattr(versioning, "VERSIONS_PATH", tmp_path / "v" / "versions.json")


def test_loop_terminates_within_budget():
    r = run_bounded(max_iterations=2)
    assert r["terminal"] is True
    assert r["iterations"] <= 2
    assert r["reason"] in {"DONE", "STAGNATION", "BUDGET", "OSCILLATION"}


def test_loop_records_best_version():
    r = run_bounded(max_iterations=2)
    assert r["best"] is not None
    assert 0 <= r["best"]["total"] <= 100
