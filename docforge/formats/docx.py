"""DOCX adapter — delegates to the deterministic scripts already in place."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

from ..paths import OUTPUT_DIR, WORK_DIR
from ..workers._scripts import run_script
from . import register
from .base import NotAvailable, UniversalDocumentAdapter


class DocxAdapter(UniversalDocumentAdapter):
    format_name = "docx"
    extensions = [".docx"]
    implemented = True
    capabilities = ["parse", "inspect", "extract", "modify", "export",
                    "validate", "render"]

    def parse(self, path: Path) -> Dict[str, Any]:
        return self.inspect(path)

    def inspect(self, path: Path) -> Dict[str, Any]:
        rc, out, err = run_script("inspect_docx.py", str(path))
        return {"rc": rc, "stderr": err.strip(),
                "stdout_head": out[:400] if out else ""}

    def extract(self, path: Path) -> Dict[str, Any]:
        inspection = WORK_DIR / "inspection" / "paragraphs.json"
        if not inspection.exists():
            self.inspect(path)
        data: Dict[str, Any] = {}
        if inspection.exists():
            try:
                data = json.loads(inspection.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = {}
        return data

    def normalize(self, model: Dict[str, Any]) -> Dict[str, Any]:
        return model

    def render(self, model: Dict[str, Any], out: Path) -> Path:
        raise NotAvailable("docx: render-from-canonical is not implemented; "
                           "use modify() on an existing file")

    def modify(self, path: Path, ops: List[Dict[str, Any]]) -> Path:
        for op in ops:
            kind = op.get("kind")
            if kind == "apply_styles":
                run_script("apply_styles.py", str(path))
            elif kind == "update_fields":
                run_script("update_fields.py", str(path))
            elif kind == "apply_structure":
                run_script("apply_structure.py")
            else:
                raise NotAvailable(f"docx.modify unknown op: {kind}")
        return path

    def export(self, path: Path, out: Path, format: str = "pdf") -> Path:
        out.parent.mkdir(parents=True, exist_ok=True)
        if format.lower() == "pdf":
            rc, _, err = run_script("export_pdf.py", str(path))
            if rc != 0:
                raise NotAvailable(f"docx→pdf export failed: {err.strip()}")
            candidates = list(OUTPUT_DIR.glob(f"{path.stem}.pdf"))
            if candidates:
                return candidates[0]
            return out
        if format.lower() in ("docx", ""):
            shutil.copy2(path, out)
            return out
        raise NotAvailable(f"docx export to {format} not supported")

    def validate(self, path: Path) -> Dict[str, Any]:
        rc, out, err = run_script("validate_layout.py", str(path))
        try:
            data = json.loads(out) if out else {}
        except json.JSONDecodeError:
            data = {}
        return {"rc": rc, "issues": data.get("issues", []), "raw": data,
                "stderr": err.strip()}


register(DocxAdapter())
