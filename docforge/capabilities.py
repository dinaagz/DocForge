"""Detect what the current execution environment can actually do.

Never assumes; always probes. The scheduler adapts to the result.
"""
from __future__ import annotations

import os
import shutil
from typing import Any, Dict

# Single source of truth: canonical provider name → CLI binary to probe.
# Reused by docforge.installer.doctor so the binary list is never
# duplicated.
PROVIDER_BINARIES: Dict[str, str] = {
    "claude-code": "claude",
    "codex": "codex",
    "gemini": "gemini",
    "cursor": "cursor-agent",
    "qwen": "qwen",
    "opencode": "opencode",
}


def detect() -> Dict[str, Any]:
    providers = _detect_providers()
    caps: Dict[str, Any] = {
        "filesystem": True,  # we can only run here if fs works
        "shell": shutil.which("bash") is not None or os.name == "nt",
        "git": shutil.which("git") is not None,
        "python": True,
        "docx_engine": _mod_ok("docx"),
        "pdf_engine": shutil.which("libreoffice") is not None or shutil.which("soffice") is not None,
        "parallel_agents": True,  # thread scheduler works everywhere
        "background": _any_provider_supports("background", providers),
        "scheduled": _any_provider_supports("scheduled", providers),
        "mcp": os.path.exists(os.path.join(os.getcwd(), ".mcp.json")),
    }
    caps["providers"] = providers
    return caps


def _any_provider_supports(capability: str, providers: Dict[str, bool]) -> bool:
    """Check if any available provider declares a capability."""
    from .providers.registry import get as get_provider
    for name, present in providers.items():
        if not present:
            continue
        adapter = get_provider(name)
        if adapter and capability in getattr(adapter, "capabilities", []):
            return True
    return False


def _mod_ok(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


def _detect_providers() -> Dict[str, bool]:
    # Provider CLI presence probes (best effort; absence is not an error)
    result = {name: shutil.which(binary) is not None
              for name, binary in PROVIDER_BINARIES.items()}
    result["generic"] = True
    return result
