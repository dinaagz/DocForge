"""Tests for the Universal Document Kernel."""
from __future__ import annotations

from pathlib import Path

import pytest

from docforge import formats
from docforge.formats.base import NotAvailable


def test_available_includes_docx_txt_markdown():
    a = set(formats.available())
    assert {"docx", "txt", "markdown"}.issubset(a)


def test_declared_includes_stubs():
    d = set(formats.declared())
    assert {"xlsx", "pdf", "pptx", "html", "odt", "csv"}.issubset(d)


def test_stub_adapters_declare_not_implemented():
    for name in ("xlsx", "pdf", "pptx", "html", "odt", "csv"):
        ad = formats.get(name)
        assert ad.implemented is False
        assert ad.capabilities == []


def test_stub_operations_raise_not_available(tmp_path: Path):
    ad = formats.get("xlsx")
    with pytest.raises(NotAvailable):
        ad.inspect(tmp_path / "missing.xlsx")


def test_txt_roundtrip(tmp_path: Path):
    p = tmp_path / "sample.txt"
    p.write_text("Un.\n\nDeux.\n", encoding="utf-8")
    ad = formats.get("txt")
    info = ad.inspect(p)
    assert info["lines"] >= 3
    data = ad.extract(p)
    assert len(data["paragraphs"]) == 2


def test_markdown_headings(tmp_path: Path):
    p = tmp_path / "sample.md"
    p.write_text("# A\n\ncontent\n\n## B\n\nx\n", encoding="utf-8")
    ad = formats.get("markdown")
    data = ad.extract(p)
    assert len(data["headings"]) == 2


def test_markdown_heading_jump_flagged(tmp_path: Path):
    p = tmp_path / "sample.md"
    p.write_text("# A\n\n### C jumped\n", encoding="utf-8")
    ad = formats.get("markdown")
    v = ad.validate(p)
    assert any(i["kind"] == "heading_jump" for i in v["issues"])
