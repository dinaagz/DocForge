"""Filesystem layout for DocForge — one place, no duplicates."""
from __future__ import annotations

import os
from pathlib import Path


def _root() -> Path:
    env = os.environ.get("DOCFORGE_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


ROOT = _root()
DOCFORGE_DIR = ROOT / ".docforge"

CORE_DIR = DOCFORGE_DIR / "core"
AGENTS_DIR = DOCFORGE_DIR / "agents"
SKILLS_DIR = DOCFORGE_DIR / "skills"
PROVIDERS_DIR = DOCFORGE_DIR / "providers"
CONNECTORS_DIR = DOCFORGE_DIR / "connectors"
PROFILES_DIR = DOCFORGE_DIR / "profiles"
CONFIG_DIR = DOCFORGE_DIR / "config"
STATE_DIR = DOCFORGE_DIR / "state"
MEMORY_DIR = DOCFORGE_DIR / "memory"
MODEL_DIR = DOCFORGE_DIR / "model"
RUNTIME_DIR = DOCFORGE_DIR / "runtime"
SCHEMAS_DIR = DOCFORGE_DIR / "schemas"
CHAT_DIR = DOCFORGE_DIR / "chat"

# Legacy directories preserved from Loop (still used by deterministic scripts)
LEGACY_STATE_DIR = ROOT / "state"
LEGACY_CONFIG_PATH = ROOT / "config" / "document_config.yaml"
INPUT_DIR = ROOT / "input"
WORK_DIR = ROOT / "work"
OUTPUT_DIR = ROOT / "output"
LOGS_DIR = ROOT / "logs"
SCRIPTS_DIR = ROOT / "scripts"

CANONICAL_PATH = MODEL_DIR / "canonical_document.json"
EVENTS_LOG = MEMORY_DIR / "events.jsonl"
MANUAL_REVIEW_PATH = STATE_DIR / "manual_review.json"


def ensure_layout() -> None:
    for p in (
        DOCFORGE_DIR, CORE_DIR, AGENTS_DIR, SKILLS_DIR, PROVIDERS_DIR,
        CONNECTORS_DIR, PROFILES_DIR, CONFIG_DIR, STATE_DIR, MEMORY_DIR,
        MODEL_DIR, RUNTIME_DIR, SCHEMAS_DIR, CHAT_DIR,
        INPUT_DIR, WORK_DIR, OUTPUT_DIR, LOGS_DIR,
    ):
        p.mkdir(parents=True, exist_ok=True)
