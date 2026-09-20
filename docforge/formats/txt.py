"""Plain text adapter — read/write text, basic audit."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from . import register
from .base import NotAvailable, UniversalDocumentAdapter


class TxtAdapter(UniversalDocumentAdapter):
    format_name = "txt"
    extensions = [".txt"]
    implemented = True
    capabilities = ["parse", "inspect", "extract", "normalize", "render",
                    "modify", "export", "validate"]

    def parse(self, path: Path) -> Dict[str, Any]:
        return self.extract(path)

    def inspect(self, path: Path) -> Dict[str, Any]:
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        return {"path": str(path), "bytes": path.stat().st_size,
                "lines": len(lines), "chars": len(text)}

    def extract(self, path: Path) -> Dict[str, Any]:
        text = path.read_text(encoding="utf-8", errors="replace")
        paragraphs = [
            {"id": f"P{i+1:06d}", "type": "paragraph", "content": p.strip()}
            for i, p in enumerate(text.split("\n\n")) if p.strip()
        ]
        return {"paragraphs": paragraphs, "raw": text}

    def normalize(self, model: Dict[str, Any]) -> Dict[str, Any]:
        return model

    def render(self, model: Dict[str, Any], out: Path) -> Path:
        paras = model.get("paragraphs") or []
        body = "\n\n".join(
            p.get("content", "") if isinstance(p, dict) else str(p)
            for p in paras)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
        return out

    def modify(self, path: Path, ops: List[Dict[str, Any]]) -> Path:
        text = path.read_text(encoding="utf-8", errors="replace")
        for op in ops:
            if op.get("kind") == "replace":
                text = text.replace(op["from"], op["to"])
            elif op.get("kind") == "append":
                text = text + op.get("text", "")
            else:
                raise NotAvailable(f"txt.modify unknown op: {op.get('kind')}")
        path.write_text(text, encoding="utf-8")
        return path

    def export(self, path: Path, out: Path, format: str = "") -> Path:
        out.parent.mkdir(parents=True, exist_ok=True)
        if format.lower() in ("", "txt"):
            out.write_text(path.read_text(encoding="utf-8",
                                          errors="replace"),
                           encoding="utf-8")
            return out
        raise NotAvailable(f"txt export to {format} not supported")

    def validate(self, path: Path) -> Dict[str, Any]:
        issues: List[Dict[str, Any]] = []
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            issues.append({"kind": "encoding", "detail": str(e)})
            text = ""
        if "\t" in text:
            issues.append({"kind": "tab_char",
                           "detail": "hard tabs present"})
        return {"issues": issues, "ok": not issues}


register(TxtAdapter())
