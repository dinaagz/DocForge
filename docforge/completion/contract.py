"""Contract Engine — load CONTRACT.yaml and compute coverage."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from ..paths import DOCFORGE_DIR, ensure_layout

CONTRACT_PATH = DOCFORGE_DIR / "project" / "CONTRACT.yaml"


def load_contract(path: Path = CONTRACT_PATH) -> Dict[str, Any]:
    ensure_layout()
    if not path.exists():
        return {"requirements": {}}
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {"requirements": {}}


def required_requirements(contract: Dict[str, Any] | None = None
                           ) -> List[str]:
    c = contract or load_contract()
    return [k for k, v in (c.get("requirements") or {}).items()
            if v.get("status") == "required"]


def coverage(gate_results: Dict[str, str],
             contract: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Return which required requirements are covered by passing gates."""
    c = contract or load_contract()
    reqs = c.get("requirements") or {}
    covered: List[str] = []
    missing: List[str] = []
    for name, spec in reqs.items():
        if spec.get("status") != "required":
            continue
        gate = spec.get("gate")
        if gate and gate_results.get(gate) == "PASS":
            covered.append(name)
        else:
            missing.append(name)
    return {"covered": covered, "missing": missing,
            "total_required": len(covered) + len(missing)}
