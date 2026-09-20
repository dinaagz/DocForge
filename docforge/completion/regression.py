"""Regression Engine — a rising total with a critical failure is NOT progress.

`check(prev, cur)` returns a dict:
  - regressed: bool
  - reasons: list[str]     (gates that flipped PASS→FAIL, dropped score, …)
  - blocking: bool         (regression involves a required gate)
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Set

_DEFAULT_DELTA = 5.0


def check(prev: Dict[str, Any], cur: Dict[str, Any],
          critical_delta: float = _DEFAULT_DELTA,
          required_gates: Iterable[str] = ()) -> Dict[str, Any]:
    reasons: List[str] = []
    blocking = False
    required_set: Set[str] = set(required_gates or ())

    prev_gates = (prev or {}).get("gates") or {}
    cur_gates = (cur or {}).get("gates") or {}
    for gid, prev_verdict in prev_gates.items():
        cur_verdict = cur_gates.get(gid)
        if prev_verdict == "PASS" and cur_verdict != "PASS":
            reasons.append(f"gate {gid} regressed: PASS → {cur_verdict}")
            if gid in required_set or not required_set:
                blocking = True

    prev_total = float((prev or {}).get("total", 0) or 0)
    cur_total = float((cur or {}).get("total", 0) or 0)
    if prev_total - cur_total > critical_delta:
        reasons.append(f"score dropped {prev_total} → {cur_total} "
                       f"(> {critical_delta})")
        blocking = True

    return {"regressed": bool(reasons), "blocking": blocking,
            "reasons": reasons}
