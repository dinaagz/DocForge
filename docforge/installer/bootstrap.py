"""`docforge install` — turns a checkout (or an extracted archive) into
a real user installation: creates the runtime layout, records the
version, writes a launcher on PATH."""
from __future__ import annotations

import os
import shutil
import stat
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, Optional

from .. import __version__
from . import layout, state


def _write_launcher_posix(target: Path, python: str, app_root: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    body = textwrap.dedent(f"""\
        #!/usr/bin/env bash
        # DocForge launcher (auto-generated). Do not edit.
        export DOCFORGE_ROOT="${{DOCFORGE_ROOT:-{app_root}}}"
        export PYTHONPATH="{app_root}${{PYTHONPATH:+:$PYTHONPATH}}"
        exec "{python}" -m docforge.cli "$@"
    """)
    target.write_text(body, encoding="utf-8")
    target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP
                 | stat.S_IXOTH)


def _write_launcher_windows(target: Path, python: str, app_root: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    body = textwrap.dedent(f"""\
        @echo off
        rem DocForge launcher (auto-generated). Do not edit.
        set "DOCFORGE_ROOT={app_root}"
        set "PYTHONPATH={app_root};%PYTHONPATH%"
        "{python}" -m docforge.cli %*
    """)
    target.write_text(body, encoding="utf-8")


def install(source: Optional[Path] = None,
            version: Optional[str] = None,
            python: Optional[str] = None) -> Dict[str, Any]:
    """Copy the current checkout (or a given source) into the versioned
    runtime and expose a `docforge` launcher on PATH.
    """
    app_source = Path(source) if source else Path(__file__).resolve().parents[2]
    ver = version or __version__
    python = python or sys.executable

    layout.ensure_layout()
    dest = layout.versions_dir() / ver
    if dest.exists():
        shutil.rmtree(dest)
    # Copy only the code — never user data.
    dest.mkdir(parents=True)
    for name in ("docforge", "scripts", "adapters", "config",
                  "requirements.txt", "LOOP.yaml", "DOCFORGE.md",
                  "AGENTS.md", "README.md", "CLAUDE.md",
                  "install.sh", "install.ps1", "bin"):
        src = app_source / name
        if not src.exists():
            continue
        target = dest / name
        if src.is_dir():
            shutil.copytree(src, target, dirs_exist_ok=True)
        else:
            shutil.copy2(src, target)

    # Launcher
    bin_dir = layout.bin_dir()
    bin_dir.mkdir(parents=True, exist_ok=True)
    if layout.is_windows():
        _write_launcher_windows(bin_dir / "docforge.cmd", python, dest)
    else:
        _write_launcher_posix(bin_dir / "docforge", python, dest)

    # Pointer + ledger
    layout.current_pointer().write_text(str(dest), encoding="utf-8")
    state.record_installed(ver, str(dest))

    # Migrations
    from .. import migrations
    applied = migrations.run_pending()

    return {"ok": True, "version": ver, "path": str(dest),
            "bin": str(bin_dir), "migrations": applied,
            "path_configured": _bin_on_path(bin_dir)}


def _bin_on_path(bin_dir: Path) -> bool:
    path = os.environ.get("PATH", "")
    return str(bin_dir) in path.split(os.pathsep)


def path_hint() -> str:
    b = layout.bin_dir()
    if layout.is_windows():
        return (f"Ajoutez `{b}` à votre PATH utilisateur : "
                f"`setx PATH \"{b};%PATH%\"` puis rouvrez PowerShell.")
    return (f"Ajoutez à votre shell rc : "
            f"`export PATH=\"{b}:$PATH\"`")
