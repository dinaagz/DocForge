"""Tests for the installer CLI surface."""
from __future__ import annotations

from pathlib import Path

import pytest

from docforge.cli import build_parser


def test_parser_exposes_install_uninstall_update_version():
    parser = build_parser()
    cmds = set()
    for a in parser._actions:
        for c in getattr(a, "choices", {}) or {}:
            cmds.add(c)
    for n in ("install", "uninstall", "update", "version", "doctor", "init"):
        assert n in cmds, f"missing subcommand: {n}"


def test_parser_has_version_flag():
    parser = build_parser()
    flags = set()
    for a in parser._actions:
        flags.update(a.option_strings or [])
    assert "--version" in flags


def test_update_flags_are_present():
    parser = build_parser()
    upd = None
    for a in parser._actions:
        for name, sub in (getattr(a, "choices", {}) or {}).items():
            if name == "update":
                upd = sub
    assert upd is not None
    flags = set()
    for a in upd._actions:
        flags.update(a.option_strings or [])
    for f in ("--check", "--force", "--rollback", "--source", "--channel",
              "--archive", "--sha256"):
        assert f in flags, f"missing update flag: {f}"


def test_version_subcommand(monkeypatch, capsys):
    parser = build_parser()
    args = parser.parse_args(["version"])
    rc = args.func(args)
    assert rc == 0
    assert "DocForge" in capsys.readouterr().out


def test_update_check_runs(monkeypatch, capsys, tmp_path: Path):
    monkeypatch.setenv("DOCFORGE_HOME", str(tmp_path / "rt"))
    parser = build_parser()
    args = parser.parse_args(["update", "--check", "--source", "local:./"])
    rc = args.func(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "current" in out and "latest" in out
