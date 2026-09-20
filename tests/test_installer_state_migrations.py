"""Tests for the installer state ledger and migration runner."""
from __future__ import annotations

from pathlib import Path

import pytest

from docforge import migrations
from docforge.installer import rollback, state, uninstaller


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DOCFORGE_HOME", str(tmp_path / "runtime"))
    monkeypatch.setenv("DOCFORGE_STATE_DIR", str(tmp_path / "runtime" / "state"))
    monkeypatch.setenv("DOCFORGE_BIN", str(tmp_path / "runtime" / "bin"))
    state.reset_versions()
    state.reset_migrations()


def test_record_and_read_installed():
    state.record_installed("0.1.0", "/opt/df/0.1.0")
    state.record_installed("0.2.0", "/opt/df/0.2.0")
    assert state.current_version() == "0.2.0"
    assert set(state.installed_versions()) == {"0.1.0", "0.2.0"}


def test_forget_updates_current():
    state.record_installed("0.1.0", "/a")
    state.record_installed("0.2.0", "/b")
    state.forget_installed("0.2.0")
    assert state.current_version() == "0.1.0"


def test_migrations_are_ordered_and_idempotent():
    first = migrations.run_pending()
    assert first == sorted(first)
    assert migrations.run_pending() == []


def test_migrations_registry_ids_unique():
    reg = migrations.registry()
    ids = [m["id"] for m in reg]
    assert len(ids) == len(set(ids))
    assert all(m["apply"] is None or callable(m["apply"]) for m in reg)


def test_rollback_requires_multiple_versions():
    assert not rollback.can_rollback()
    state.record_installed("0.1.0", "/a")
    assert not rollback.can_rollback()
    state.record_installed("0.2.0", "/b")
    assert rollback.can_rollback()
    r = rollback.rollback()
    assert r["ok"] is True
    assert r["current"] == "0.1.0"


def test_rollback_rejects_unknown_target():
    state.record_installed("0.1.0", "/a")
    state.record_installed("0.2.0", "/b")
    r = rollback.rollback(to="9.9.9")
    assert r["ok"] is False


def test_uninstall_plan_preserves_user_data():
    plan = uninstaller.plan_uninstall()
    for entry in plan["remove"]:
        assert "input" not in entry
        assert "output" not in entry
        assert "work" not in entry
    assert plan["user_data_preserved"]
