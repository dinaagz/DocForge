"""Tests for extract_structure.py."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from inspect_docx import inspect
from extract_structure import extract, write_markdown_report
from common import save_state


def test_extract_finds_sections(sample_docx, tmp_path):
    manifest = inspect(sample_docx)
    save_state("document_manifest", manifest)

    proposal = extract(manifest)
    assert proposal["total_sections_detected"] > 0
    assert len(proposal["sections"]) > 0


def test_extract_preserves_heading_ids(sample_docx):
    manifest = inspect(sample_docx)
    proposal = extract(manifest)

    for sec in proposal["sections"]:
        if sec["heading_id"]:
            assert sec["heading_id"].startswith("P")


def test_markdown_report(sample_docx, tmp_path):
    manifest = inspect(sample_docx)
    proposal = extract(manifest)

    md_path = tmp_path / "report.md"
    write_markdown_report(proposal, md_path)

    assert md_path.exists()
    content = md_path.read_text()
    assert "Structure Extraction Report" in content
    assert "Existing Sections" in content
