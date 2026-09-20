"""SHA-256 integrity verification for downloaded archives."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict


def sha256_file(path: Path, chunk: int = 65536) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for buf in iter(lambda: fh.read(chunk), b""):
            h.update(buf)
    return h.hexdigest()


def verify_sha256(path: Path, expected: str) -> bool:
    if not expected:
        return False
    return sha256_file(path).lower() == expected.strip().lower()


def load_manifest(path: Path) -> Dict[str, str]:
    """Load `<file>: <sha256>` mapping (JSON or two-column text)."""
    text = path.read_text(encoding="utf-8")
    try:
        return {k: str(v).lower() for k, v in json.loads(text).items()}
    except json.JSONDecodeError:
        pass
    out: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            out[parts[1]] = parts[0].lower()
    return out


def verify_manifest(base: Path, manifest: Dict[str, str]) -> Dict[str, bool]:
    return {name: verify_sha256(base / name, expected)
            for name, expected in manifest.items()}
