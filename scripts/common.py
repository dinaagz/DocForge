"""Shared helpers used by every script in the pipeline."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "document_config.yaml"
STATE_DIR = PROJECT_ROOT / "state"
LOGS_DIR = PROJECT_ROOT / "logs"
INPUT_DIR = PROJECT_ROOT / "input"
WORK_DIR = PROJECT_ROOT / "work"
OUTPUT_DIR = PROJECT_ROOT / "output"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)

# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def load_state(name: str) -> Dict[str, Any]:
    """Load a JSON state file by name (without .json extension)."""
    p = STATE_DIR / f"{name}.json"
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_state(name: str, data: Dict[str, Any]) -> None:
    """Atomically save a JSON state file."""
    p = STATE_DIR / f"{name}.json"
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    tmp.replace(p)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger that writes to logs/<name>.log and stderr."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)

    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s")

    fh = logging.FileHandler(LOGS_DIR / f"{name}.log", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger

# ---------------------------------------------------------------------------
# Event journal
# ---------------------------------------------------------------------------

def log_event(event: str, **kwargs: Any) -> None:
    """Append one JSON-line to logs/events.jsonl."""
    entry = {"timestamp": now_iso(), "event": event, **kwargs}
    with open(LOGS_DIR / "events.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------------
# Paragraph ID & hashing
# ---------------------------------------------------------------------------

def paragraph_id(index: int) -> str:
    return f"P{index:06d}"


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

# ---------------------------------------------------------------------------
# Helpers for DOCX
# ---------------------------------------------------------------------------

def input_docx(cfg: Optional[Dict] = None) -> Path:
    if cfg is None:
        cfg = load_config()
    return INPUT_DIR / cfg["document"]["name"]
