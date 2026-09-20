"""002_completion_engine — provisions the completion engine directory."""
from __future__ import annotations

ID = "002_completion_engine"
DESCRIPTION = "Provision .docforge/completion/ (evidence store)."


def apply() -> None:
    from ..paths import DOCFORGE_DIR, ensure_layout
    ensure_layout()
    (DOCFORGE_DIR / "completion").mkdir(parents=True, exist_ok=True)
    (DOCFORGE_DIR / "audits").mkdir(parents=True, exist_ok=True)
    (DOCFORGE_DIR / "checklists").mkdir(parents=True, exist_ok=True)
    (DOCFORGE_DIR / "scores").mkdir(parents=True, exist_ok=True)
