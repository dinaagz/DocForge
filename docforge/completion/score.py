"""Score Engine — 10-dimension scorecard, total /100.

Dimensions come from `.docforge/completion/SCORECARD.yaml` when present,
otherwise fall back to a hard-coded default. Sub-scores can be supplied
in `metrics`; missing dimensions default to 50 (unknown), never 100.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from ..paths import DOCFORGE_DIR, ensure_layout

SCORECARD_PATH = DOCFORGE_DIR / "completion" / "SCORECARD.yaml"

DEFAULT_DIMENSIONS: List[str] = [
    "completeness", "correctness", "consistency", "language",
    "structure", "formatting", "visual_quality", "integrity",
    "requirement_coverage", "verification_quality",
]


def _load_dimensions() -> List[str]:
    ensure_layout()
    if not SCORECARD_PATH.exists():
        return list(DEFAULT_DIMENSIONS)
    with open(SCORECARD_PATH, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh) or {}
    dims = list((doc.get("dimensions") or {}).keys())
    return dims or list(DEFAULT_DIMENSIONS)


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, float(x)))


def compute(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Compute per-dimension score (0..100) and total (weighted mean).

    `metrics` may include dimension names as keys with a numeric 0..100
    value. Anything missing scores 50 (unknown), so total ≤ 100 without
    complete evidence.
    """
    dims = _load_dimensions()
    per: Dict[str, float] = {}
    for d in dims:
        raw = metrics.get(d, 50)
        try:
            per[d] = _clamp(float(raw))
        except (TypeError, ValueError):
            per[d] = 50.0
    total = sum(per.values()) / len(per) if per else 0.0
    return {"dimensions": per, "total": round(total, 2),
            "n_dimensions": len(per)}


def ensure_scorecard() -> Path:
    """Write default SCORECARD.yaml if missing (idempotent)."""
    ensure_layout()
    if SCORECARD_PATH.exists():
        return SCORECARD_PATH
    SCORECARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "version": "1.0.0",
        "scale": 100,
        "dimensions": {d: {"weight": 1} for d in DEFAULT_DIMENSIONS},
    }
    SCORECARD_PATH.write_text(yaml.safe_dump(doc, sort_keys=False,
                                             allow_unicode=True),
                              encoding="utf-8")
    return SCORECARD_PATH
