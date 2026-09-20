"""Structured health checks — replaces the ad-hoc `capabilities.detect`."""
from __future__ import annotations

import os
import shutil
import sys
from typing import Any, Dict, List

from .. import __version__
from . import layout


def _mod(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


def _status(ok: bool, missing_is_warn: bool = False) -> str:
    if ok:
        return "OK"
    return "WARNING" if missing_is_warn else "MISSING"


def check_all() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    checks.append({"name": "DocForge", "status": "OK",
                   "detail": f"version {__version__}"})
    checks.append({"name": "Python", "status": "OK",
                   "detail": f"{sys.version_info.major}."
                             f"{sys.version_info.minor}."
                             f"{sys.version_info.micro}"})
    py_ok = sys.version_info >= (3, 9)
    checks.append({"name": "Python version compatible",
                   "status": "OK" if py_ok else "ERROR",
                   "detail": ">=3.9 required"})
    checks.append({"name": "Runtime root",
                   "status": "OK",
                   "detail": str(layout.runtime_root())})
    checks.append({"name": "PATH exposes bin_dir",
                   "status": "OK" if str(layout.bin_dir()) in os.environ.get("PATH", "").split(os.pathsep) else "WARNING",
                   "detail": str(layout.bin_dir())})

    # Format support
    for name, mod, warn in (("DOCX support", "docx", False),
                            ("YAML support", "yaml", False),
                            ("XML support", "lxml", False)):
        ok = _mod(mod)
        checks.append({"name": name,
                       "status": _status(ok, warn),
                       "detail": mod})

    # External tools (optional)
    for tool, warn in (("libreoffice", True), ("soffice", True),
                       ("pandoc", True), ("gs", True)):
        ok = shutil.which(tool) is not None
        checks.append({"name": f"tool: {tool}",
                       "status": _status(ok, missing_is_warn=True),
                       "detail": shutil.which(tool) or "not found"})

    # Providers (optional)
    for prov in ("claude", "codex", "gemini", "cursor-agent", "qwen",
                 "opencode"):
        ok = shutil.which(prov) is not None
        checks.append({"name": f"provider: {prov}",
                       "status": _status(ok, missing_is_warn=True),
                       "detail": shutil.which(prov) or "not installed"})

    counts = {"OK": 0, "WARNING": 0, "MISSING": 0, "ERROR": 0}
    for c in checks:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    return {"version": __version__, "checks": checks, "counts": counts,
            "layout": layout.describe()}


def format_report(report: Dict[str, Any]) -> str:
    lines: List[str] = [f"DocForge Doctor — v{report['version']}", ""]
    icons = {"OK": "✓", "WARNING": "!", "MISSING": "-", "ERROR": "✗"}
    for c in report["checks"]:
        icon = icons.get(c["status"], "?")
        lines.append(f"  {icon} {c['name']:<32s} {c['status']:<8s} "
                     f"{c.get('detail', '')}")
    lines.append("")
    counts = report["counts"]
    lines.append(f"Résumé : {counts.get('OK',0)} OK, "
                 f"{counts.get('WARNING',0)} warnings, "
                 f"{counts.get('MISSING',0)} manquants, "
                 f"{counts.get('ERROR',0)} erreurs")
    return "\n".join(lines)
