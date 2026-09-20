"""Markdown adapter — read/write + heading-based structure extraction."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from . import register
from .base import NotAvailable, UniversalDocumentAdapter

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


class MarkdownAdapter(UniversalDocumentAdapter):
    format_name = "markdown"
    extensions = [".md", ".markdown"]
    implemented = True
    capabilities = ["parse", "inspect", "extract", "normalize", "render",
                    "modify", "export", "validate"]

    def parse(self, path: Path) -> Dict[str, Any]:
        return self.extract(path)

    def inspect(self, path: Path) -> Dict[str, Any]:
        text = path.read_text(encoding="utf-8", errors="replace")
        return {"path": str(path), "bytes": path.stat().st_size,
                "lines": len(text.splitlines()),
                "headings": len(_HEADING_RE.findall(text))}

    def extract(self, path: Path) -> Dict[str, Any]:
        text = path.read_text(encoding="utf-8", errors="replace")
        headings: List[Dict[str, Any]] = []
        for i, m in enumerate(_HEADING_RE.finditer(text)):
            level = len(m.group(1))
            title = m.group(2).strip()
            headings.append({"id": f"H{i+1:04d}", "level": level,
                             "title": title, "offset": m.start()})
        paragraphs = [
            {"id": f"P{i+1:06d}", "type": "paragraph", "content": p.strip()}
            for i, p in enumerate(text.split("\n\n")) if p.strip()
        ]
        return {"headings": headings, "paragraphs": paragraphs, "raw": text}

    def normalize(self, model: Dict[str, Any]) -> Dict[str, Any]:
        return model

    def render(self, model: Dict[str, Any], out: Path) -> Path:
        parts: List[str] = []
        for h in model.get("headings", []):
            parts.append(("#" * int(h.get("level", 1))) + " "
                         + str(h.get("title", "")))
        for p in model.get("paragraphs", []):
            parts.append(p.get("content", "") if isinstance(p, dict)
                         else str(p))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
        return out

    def modify(self, path: Path, ops: List[Dict[str, Any]]) -> Path:
        text = path.read_text(encoding="utf-8", errors="replace")
        for op in ops:
            if op.get("kind") == "replace":
                text = text.replace(op["from"], op["to"])
            else:
                raise NotAvailable(f"markdown.modify unknown op: {op.get('kind')}")
        path.write_text(text, encoding="utf-8")
        return path

    def export(self, path: Path, out: Path, format: str = "") -> Path:
        out.parent.mkdir(parents=True, exist_ok=True)
        if format.lower() in ("", "md", "markdown"):
            out.write_text(path.read_text(encoding="utf-8", errors="replace"),
                           encoding="utf-8")
            return out
        raise NotAvailable(f"markdown export to {format} not supported")

    def validate(self, path: Path) -> Dict[str, Any]:
        text = path.read_text(encoding="utf-8", errors="replace")
        issues: List[Dict[str, Any]] = []
        # Basic: no jumps of more than 1 heading level from the top.
        prev = 0
        for m in _HEADING_RE.finditer(text):
            level = len(m.group(1))
            if prev and level > prev + 1:
                issues.append({"kind": "heading_jump",
                               "from": prev, "to": level,
                               "title": m.group(2).strip()})
            prev = level
        return {"issues": issues, "ok": not issues}


register(MarkdownAdapter())
