"""Completion Guard — refuses DONE without evidence.

Doctrine (rule §11): NO CLAIM OF COMPLETION WITHOUT EVIDENCE.

`evaluate()` checks:
  1. every required gate exists and passes (or an explicit ABANDON with
     a non-empty reason is registered),
  2. every required requirement in CONTRACT.yaml is covered,
  3. no critical regression is pending.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from ..events import emit
from . import contract, evidence, gates, regression, versioning


def evaluate(required_gates: Optional[Iterable[str]] = None
             ) -> Dict[str, Any]:
    """Return {verdict: DONE|NOT_DONE|DONE_WITH_REVIEW, unmet, evidence_count}."""
    all_gates = gates.load_gates()
    known_ids = {g["id"] for g in all_gates if g.get("id")}
    if required_gates is None:
        required_ids = [g["id"] for g in all_gates
                         if g.get("required") and g.get("id")]
    else:
        required_ids = list(required_gates)

    unmet: List[Dict[str, Any]] = []
    passed: List[str] = []
    for gid in required_ids:
        if gid not in known_ids:
            unmet.append({"gate": gid, "reason": "gate not defined"})
            continue
        result = gates.evaluate(gid, record_evidence=False)
        if result["verdict"] == "PASS":
            passed.append(gid)
        else:
            unmet.append({"gate": gid, "reason": result.get("reason") or
                          "FAIL", "output_tail": result.get("output", "")[-500:]})

    # Contract coverage
    gate_results = {g["id"]: ("PASS" if g["id"] in passed else "FAIL")
                    for g in all_gates if g.get("id")}
    cov = contract.coverage(gate_results)

    # Regression against best
    prev = versioning.best()
    cur = versioning.state().get("current")
    reg = regression.check(prev or {}, cur or {}) if (prev and cur) else {
        "regressed": False, "blocking": False, "reasons": []}

    verdict = "DONE"
    if unmet or cov["missing"] or reg["blocking"]:
        verdict = "NOT_DONE"

    total_evidence = len(list(_all_evidence()))
    result = {
        "verdict": verdict,
        "required_total": len(required_ids),
        "passed": passed,
        "unmet": unmet,
        "contract_coverage": cov,
        "regression": reg,
        "evidence_count": total_evidence,
    }
    emit("GUARD_EVALUATED", verdict=verdict, unmet=len(unmet),
         missing_reqs=len(cov["missing"]))
    return result


def _all_evidence():
    from .evidence import _iter  # noqa: WPS437
    return _iter()
