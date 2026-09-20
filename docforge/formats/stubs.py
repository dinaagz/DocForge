"""Declarative stubs for formats whose runtime is not implemented yet.

Rule: no fake capability. Each stub sets `implemented = False` and
`capabilities = []`. Every operational method raises `NotAvailable` with
a clear message. Callers can inspect availability via
`docforge.formats.available()`.
"""
from __future__ import annotations

from . import register
from .base import UniversalDocumentAdapter


def _stub(name: str, exts):
    class _Stub(UniversalDocumentAdapter):
        format_name = name
        extensions = list(exts)
        implemented = False
        capabilities: list = []
    _Stub.__name__ = f"{name.capitalize()}StubAdapter"
    return _Stub


for _name, _exts in (
    ("xlsx", [".xlsx", ".xlsm"]),
    ("pdf", [".pdf"]),
    ("pptx", [".pptx"]),
    ("html", [".html", ".htm"]),
    ("odt", [".odt"]),
    ("csv", [".csv", ".tsv"]),
):
    register(_stub(_name, _exts)())
