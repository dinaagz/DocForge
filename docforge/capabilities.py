"""Detect what the current execution environment can actually do.

Never assumes; always probes. The scheduler adapts to the result.
"""
from __future__ import annotations

import os
import shutil
from typing import Any, Dict


def detect() -> Dict[str, Any]:
    caps: Dict[str, Any] = {
        "filesystem": True,  # we can only run here if fs works
        "shell": shutil.which("bash") is not None or os.name == "nt",
        "git": shutil.which("git") is not None,
        "python": True,
        "docx_engine": _mod_ok("docx"),
        "pdf_engine": shutil.which("libreoffice") is not None or shutil.which("soffice") is not None,
        "parallel_agents": True,  # thread scheduler works everywhere
        "background": False,
        "scheduled": False,
        "mcp": os.path.exists(os.path.join(os.getcwd(), ".mcp.json")),
    }
    caps["providers"] = _detect_providers()
    return caps


def _mod_ok(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


def _detect_providers() -> Dict[str, bool]:
    # Provider CLI presence probes (best effort; absence is not an error)
    return {
        "claude-code": shutil.which("claude") is not None,
        "codex": shutil.which("codex") is not None,
        "gemini": shutil.which("gemini") is not None,
        "cursor": shutil.which("cursor-agent") is not None,
        "qwen": shutil.which("qwen") is not None,
        "opencode": shutil.which("opencode") is not None,
        "generic": True,
    }
