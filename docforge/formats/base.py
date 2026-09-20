"""UniversalDocumentAdapter — abstract interface for any document format.

A functional adapter sets `implemented = True` and declares its
capabilities in `capabilities`. A declarative stub keeps
`implemented = False` and `capabilities = []`; every operational method
raises `NotAvailable` with a clear message. This prevents fake claims.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class NotAvailable(NotImplementedError):
    """Raised by stub adapters — operation not implemented for this format."""


class UniversalDocumentAdapter:
    format_name: str = "abstract"
    extensions: List[str] = []
    implemented: bool = False
    capabilities: List[str] = []

    # ── lifecycle ─────────────────────────────────────────────
    def parse(self, path: Path) -> Dict[str, Any]:
        raise NotAvailable(f"{self.format_name}: parse not implemented")

    def inspect(self, path: Path) -> Dict[str, Any]:
        raise NotAvailable(f"{self.format_name}: inspect not implemented")

    def extract(self, path: Path) -> Dict[str, Any]:
        raise NotAvailable(f"{self.format_name}: extract not implemented")

    def normalize(self, model: Dict[str, Any]) -> Dict[str, Any]:
        raise NotAvailable(f"{self.format_name}: normalize not implemented")

    def render(self, model: Dict[str, Any], out: Path) -> Path:
        raise NotAvailable(f"{self.format_name}: render not implemented")

    def modify(self, path: Path, ops: List[Dict[str, Any]]) -> Path:
        raise NotAvailable(f"{self.format_name}: modify not implemented")

    def export(self, path: Path, out: Path, format: str = "") -> Path:
        raise NotAvailable(f"{self.format_name}: export not implemented")

    def validate(self, path: Path) -> Dict[str, Any]:
        raise NotAvailable(f"{self.format_name}: validate not implemented")

    # ── introspection ─────────────────────────────────────────
    def describe(self) -> Dict[str, Any]:
        return {
            "format": self.format_name,
            "extensions": list(self.extensions),
            "implemented": self.implemented,
            "capabilities": list(self.capabilities),
        }
