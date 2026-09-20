"""Filesystem layout for the DocForge runtime installation.

Application (runtime) and user data (projects) are strictly separated.
"""
from __future__ import annotations

import os
import platform
from pathlib import Path


def is_windows() -> bool:
    return platform.system().lower().startswith("win")


def runtime_root() -> Path:
    """Root of the DocForge runtime installation for the current user."""
    env = os.environ.get("DOCFORGE_HOME")
    if env:
        return Path(env)
    if is_windows():
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return Path(base) / "DocForge"
    return Path.home() / ".docforge"


def versions_dir() -> Path:
    return runtime_root() / "versions"


def venv_dir() -> Path:
    return runtime_root() / "venv"


def cache_dir() -> Path:
    return runtime_root() / "cache"


def state_dir() -> Path:
    return runtime_root() / "state"


def bin_dir() -> Path:
    """Directory that must be on PATH to expose `docforge`."""
    env = os.environ.get("DOCFORGE_BIN")
    if env:
        return Path(env)
    if is_windows():
        return runtime_root() / "bin"
    return Path.home() / ".local" / "bin"


def current_pointer() -> Path:
    """File pointing to the active version directory."""
    return runtime_root() / "current"


def ensure_layout() -> None:
    for p in (runtime_root(), versions_dir(), cache_dir(), state_dir(),
              bin_dir()):
        p.mkdir(parents=True, exist_ok=True)


def describe() -> dict:
    return {
        "runtime_root": str(runtime_root()),
        "versions_dir": str(versions_dir()),
        "venv_dir": str(venv_dir()),
        "cache_dir": str(cache_dir()),
        "state_dir": str(state_dir()),
        "bin_dir": str(bin_dir()),
        "current_pointer": str(current_pointer()),
        "os": platform.system(),
        "arch": platform.machine(),
    }
