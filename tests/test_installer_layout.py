"""Tests for the installer filesystem layout."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from docforge.installer import layout


def test_env_override_wins(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DOCFORGE_HOME", str(tmp_path / "runtime"))
    assert layout.runtime_root() == tmp_path / "runtime"


def test_versions_dir_relative_to_root(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DOCFORGE_HOME", str(tmp_path / "r"))
    assert layout.versions_dir() == tmp_path / "r" / "versions"


def test_bin_dir_env_override(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DOCFORGE_BIN", str(tmp_path / "bin"))
    assert layout.bin_dir() == tmp_path / "bin"


def test_ensure_layout_creates_all(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DOCFORGE_HOME", str(tmp_path / "r"))
    monkeypatch.setenv("DOCFORGE_BIN", str(tmp_path / "b"))
    layout.ensure_layout()
    for d in (layout.runtime_root(), layout.versions_dir(),
              layout.cache_dir(), layout.state_dir(), layout.bin_dir()):
        assert d.exists()


def test_describe_returns_paths_and_os(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DOCFORGE_HOME", str(tmp_path / "r"))
    d = layout.describe()
    assert set(d) >= {"runtime_root", "versions_dir", "bin_dir", "os", "arch"}
