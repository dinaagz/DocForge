"""Tests for inspect_docx.py."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from inspect_docx import inspect


def test_inspect_counts_paragraphs(sample_docx):
    manifest = inspect(sample_docx)
    assert manifest["statistics"]["paragraph_count"] > 0
    assert len(manifest["paragraphs"]) == manifest["statistics"]["paragraph_count"]


def test_inspect_detects_headings(sample_docx):
    manifest = inspect(sample_docx)
    assert manifest["statistics"]["heading_count"] > 0
    headings = manifest["headings"]
    assert any("Introduction" in h["text"] for h in headings)


def test_inspect_assigns_stable_ids(sample_docx):
    manifest = inspect(sample_docx)
    ids = [p["id"] for p in manifest["paragraphs"]]
    # IDs should be unique
    assert len(ids) == len(set(ids))
    # IDs should follow P000000 format
    assert all(p["id"].startswith("P") and len(p["id"]) == 7 for p in manifest["paragraphs"])


def test_inspect_computes_hashes(sample_docx):
    manifest = inspect(sample_docx)
    for p in manifest["paragraphs"]:
        assert "text_hash" in p
        assert len(p["text_hash"]) == 16


def test_inspect_catalogs_styles(sample_docx):
    manifest = inspect(sample_docx)
    assert len(manifest["styles_used"]) > 0
