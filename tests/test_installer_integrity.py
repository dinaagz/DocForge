"""Tests for the SHA-256 integrity helpers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from docforge.installer.integrity import (load_manifest, sha256_file,
                                            verify_manifest, verify_sha256)


def test_sha256_matches_reference(tmp_path: Path):
    p = tmp_path / "sample.bin"
    p.write_bytes(b"hello world")
    assert sha256_file(p) == hashlib.sha256(b"hello world").hexdigest()


def test_verify_sha256_accepts_correct(tmp_path: Path):
    p = tmp_path / "sample.bin"
    p.write_bytes(b"content")
    assert verify_sha256(p, sha256_file(p))


def test_verify_sha256_rejects_wrong(tmp_path: Path):
    p = tmp_path / "sample.bin"
    p.write_bytes(b"content")
    assert not verify_sha256(p, "deadbeef" * 8)


def test_verify_sha256_empty_hash_is_false(tmp_path: Path):
    p = tmp_path / "sample.bin"
    p.write_bytes(b"x")
    assert not verify_sha256(p, "")


def test_manifest_json_roundtrip(tmp_path: Path):
    a = tmp_path / "a.bin"
    a.write_bytes(b"aaa")
    b = tmp_path / "b.bin"
    b.write_bytes(b"bbb")
    manifest = tmp_path / "SHA256SUMS.json"
    manifest.write_text(json.dumps({
        "a.bin": sha256_file(a), "b.bin": sha256_file(b),
    }), encoding="utf-8")
    m = load_manifest(manifest)
    results = verify_manifest(tmp_path, m)
    assert results == {"a.bin": True, "b.bin": True}


def test_manifest_two_column_text(tmp_path: Path):
    a = tmp_path / "a.bin"
    a.write_bytes(b"aaa")
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(f"{sha256_file(a)}  a.bin\n", encoding="utf-8")
    m = load_manifest(manifest)
    assert list(m.keys()) == ["a.bin"]
    assert verify_manifest(tmp_path, m) == {"a.bin": True}
