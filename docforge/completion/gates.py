"""Gates — load GATES.yaml, evaluate a gate honestly, record the evidence.

A gate has a CHECK (Python or shell) and an EXPECT regex. It passes only
when the process exits 0 (shell) or does not raise (python), AND when
combined stdout matches EXPECT. Otherwise it fails. No auto-pass.
"""
from __future__ import annotations

import io
import re
import subprocess
import sys
import textwrap
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..events import emit
from ..paths import DOCFORGE_DIR, ROOT, ensure_layout
from . import evidence

GATES_PATH = DOCFORGE_DIR / "completion" / "GATES.yaml"


def load_gates(path: Path = GATES_PATH) -> List[Dict[str, Any]]:
    ensure_layout()
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh) or {}
    return list(doc.get("gates") or [])


def _find(gate_id: str) -> Optional[Dict[str, Any]]:
    for g in load_gates():
        if g.get("id") == gate_id:
            return g
    return None


def evaluate(gate_id: str, *, record_evidence: bool = True
             ) -> Dict[str, Any]:
    """Run a gate and return {gate, verdict PASS/FAIL, reason, output}."""
    g = _find(gate_id)
    if g is None:
        return {"gate": gate_id, "verdict": "FAIL",
                "reason": "unknown gate", "output": ""}

    check = g.get("check") or {}
    expect = g.get("expect") or ""
    kind = check.get("kind", "shell")
    output = ""
    ok_rc = True
    err_msg = ""

    if kind == "python":
        code = textwrap.dedent(check.get("code", ""))
        buf = io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(buf):
                exec(compile(code, f"<gate:{gate_id}>", "exec"),
                     {"__name__": "__main__"})
            output = buf.getvalue()
        except Exception as e:  # noqa: BLE001
            ok_rc = False
            output = buf.getvalue()
            err_msg = f"{type(e).__name__}: {e}"
    elif kind == "shell":
        cmd = check.get("command") or ""
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True,
                               text=True, cwd=str(ROOT), timeout=600)
            output = (r.stdout or "") + (r.stderr or "")
            ok_rc = (r.returncode == 0)
        except Exception as e:  # noqa: BLE001
            ok_rc = False
            err_msg = str(e)
    else:
        return {"gate": gate_id, "verdict": "FAIL",
                "reason": f"unknown check kind: {kind}", "output": ""}

    matched = bool(re.search(expect, output)) if expect else True
    verdict = "PASS" if (ok_rc and matched) else "FAIL"
    reason = ""
    if not ok_rc:
        reason = f"check errored: {err_msg}"
    elif not matched:
        reason = f"expect regex did not match: {expect!r}"

    result = {"gate": gate_id, "verdict": verdict, "reason": reason,
              "output": output[-4000:], "required": bool(g.get("required"))}
    if record_evidence:
        evidence.record(gate=gate_id, source="gates.evaluate",
                        result=verdict, conclusion=reason or "check ran")
    emit("GATE_EVALUATED", gate=gate_id, verdict=verdict)
    return result


def evaluate_all(record_evidence: bool = True) -> Dict[str, Dict[str, Any]]:
    return {g["id"]: evaluate(g["id"], record_evidence=record_evidence)
            for g in load_gates() if g.get("id")}
