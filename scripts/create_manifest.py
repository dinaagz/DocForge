#!/usr/bin/env python3
"""
create_manifest.py — Create chapter_status.json from locked structure.

After the human validates the structure proposal, the locked structure
is used to build the per-chapter processing manifest.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

from common import get_logger, log_event, now_iso, save_state, load_state

logger = get_logger("manifest")


def build_chapter_status(locked: Dict[str, Any]) -> Dict[str, Any]:
    chapters: List[Dict[str, Any]] = []
    for sec in locked.get("sections", []):
        chapters.append({
            "id": sec["id"],
            "title": sec["title"],
            "level": sec.get("level", 1),
            "heading_paragraph_id": sec.get("paragraph_id"),
            "first_paragraph_id": sec.get("first_paragraph_id"),
            "last_paragraph_id": sec.get("last_paragraph_id"),
            "status": "NOT_PROCESSED",
            "iterations": 0,
            "last_step": None,
            "issues": [],
        })

    return {
        "created_at": now_iso(),
        "total_chapters": len(chapters),
        "chapters": chapters,
    }


def main() -> int:
    locked = load_state("structure_locked")
    if not locked:
        logger.error("structure_locked.json not found — validate structure first")
        print(json.dumps({"error": "structure_locked.json not found"}))
        return 1

    status = build_chapter_status(locked)
    save_state("chapter_status", status)
    log_event("CHAPTER_MANIFEST_CREATED", total=status["total_chapters"])
    logger.info("Chapter manifest created — %d chapters", status["total_chapters"])
    print(json.dumps({"status": "ok", "chapters": status["total_chapters"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
