"""Tests for the newly added DocForge CLI commands."""
from __future__ import annotations

from docforge.cli import build_parser


NEEDED = {
    "init", "run", "status", "audit", "plan", "verify", "score",
    "improve", "report", "final-audit", "inspect", "structure",
    "language", "format", "layout", "visual", "tables", "figures",
    "formulas", "references", "interview",
}


def test_parser_declares_universal_commands():
    parser = build_parser()
    cmds = set()
    for a in parser._actions:
        for choice in getattr(a, "choices", {}) or {}:
            cmds.add(choice)
    missing = NEEDED - cmds
    assert not missing, f"missing subcommands: {sorted(missing)}"


def test_status_command_runs(capsys):
    parser = build_parser()
    args = parser.parse_args(["status"])
    rc = args.func(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "D O C F O R G E" in out
