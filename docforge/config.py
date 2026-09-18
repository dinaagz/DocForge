"""Configuration loader for DocForge.

Layered: defaults → .docforge/config/*.yaml → legacy config/document_config.yaml
(if present) → env overrides. YAML is optional per-file.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

from .paths import CONFIG_DIR, LEGACY_CONFIG_PATH, PROFILES_DIR


DEFAULTS: Dict[str, Any] = {
    "identity": {"name": "DocForge", "version": "0.1.0"},
    "document": {"name": "", "type": "auto", "language": "fr"},
    "language": {"default": "fr", "auto_detect": True, "locale": "fr-FR"},
    "style": {
        "language": "fr",
        "tone": "professionnel",
        "voice": "neutre",
        "personality": "neutre",
        "formality": "élevée",
        "audience": "général",
        "preserve_author_voice": True,
    },
    "processing": {
        "max_local_iterations": 5,
        "max_global_iterations": 5,
        "concurrency": 4,
        "continue_on_failure": True,
        "step_timeout": 600,
    },
    "quality": {
        "checks": ["unicode", "layout", "integrity", "coherence", "pdf_visual"],
    },
    "output": {"docx": True, "pdf": True, "report": True, "report_language": "fr"},
    "providers": {"preferred": ["claude-code", "codex", "gemini", "cursor",
                                 "qwen", "opencode", "generic"]},
    "profile": "academic",
}


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _merge(base: Dict[str, Any], over: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config() -> Dict[str, Any]:
    cfg = dict(DEFAULTS)
    for name in ("document", "style", "language", "quality", "providers"):
        cfg = _merge(cfg, {name: _load_yaml(CONFIG_DIR / f"{name}.yaml").get(name, _load_yaml(CONFIG_DIR / f"{name}.yaml"))})
    # Legacy config bridge
    legacy = _load_yaml(LEGACY_CONFIG_PATH)
    if legacy:
        cfg = _merge(cfg, {
            "document": legacy.get("document", {}),
            "language": {"locale": legacy.get("language", {}).get("locale", cfg["language"]["locale"])},
            "processing": legacy.get("processing", {}),
            "output": legacy.get("output", {}),
        })
    # Env overrides (DOCFORGE_PROFILE, DOCFORGE_CONCURRENCY)
    if os.environ.get("DOCFORGE_PROFILE"):
        cfg["profile"] = os.environ["DOCFORGE_PROFILE"]
    if os.environ.get("DOCFORGE_CONCURRENCY"):
        try:
            cfg["processing"]["concurrency"] = int(os.environ["DOCFORGE_CONCURRENCY"])
        except ValueError:
            pass
    # Merge profile
    prof_path = PROFILES_DIR / f"{cfg['profile']}.yaml"
    if prof_path.exists():
        cfg = _merge(cfg, _load_yaml(prof_path))
    return cfg
