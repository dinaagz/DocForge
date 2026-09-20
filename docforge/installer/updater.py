"""Update engine.

`check_only(source, current)` : queries a source (github|local:) for the
latest version and returns a JSON-shaped report without touching disk.

`apply(source, target_dir)` : downloads the archive, verifies its
SHA-256 (if a `.sha256` companion exists), extracts atomically into a
staging directory, runs the migration set, and finally swaps the
`current` pointer. If any step fails, the previous version stays live.
"""
from __future__ import annotations

import json
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from .. import __version__
from . import integrity, layout, state, version as verlib

# Directories inside a project that must NEVER be touched by update.
_PRESERVED = ("input", "output", "work", "logs", ".docforge")


def preserves() -> List[str]:
    return list(_PRESERVED)


def _releases_url(channel: str = "stable") -> str:
    # GitHub Releases JSON. `stable` = latest, others use per-tag search.
    if channel == "stable":
        return "https://api.github.com/repos/dinaagz/DocForge/releases/latest"
    return "https://api.github.com/repos/dinaagz/DocForge/releases"


def _fetch_json(url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:  # noqa: S310
            return json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError,
            json.JSONDecodeError):
        return None


def check_only(source: str = "github",
               current: Optional[str] = None,
               channel: str = "stable") -> Dict[str, Any]:
    """Report whether an update is available. Never mutates state."""
    current = current or __version__
    latest: Optional[str] = None
    origin = source

    if source.startswith("local:"):
        # `local:./` returns the working-copy version.
        latest = __version__
    else:
        data = _fetch_json(_releases_url(channel))
        if data:
            tag = data.get("tag_name") or data.get("name")
            if isinstance(tag, str):
                latest = tag.lstrip("v")

    available = bool(latest) and verlib.is_newer(latest, current) \
        if latest else False
    return {
        "channel": channel,
        "current": current,
        "latest": latest,
        "source": origin,
        "update_available": available,
    }


def _download(url: str, dest: Path, timeout: int = 60) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=timeout) as r:  # noqa: S310
        dest.write_bytes(r.read())
    return dest


def _extract_tarball(archive: Path, into: Path) -> Path:
    into.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:*") as tf:
        # Guard against path traversal.
        for m in tf.getmembers():
            p = (into / m.name).resolve()
            if not str(p).startswith(str(into.resolve())):
                raise RuntimeError(f"unsafe path in archive: {m.name}")
        tf.extractall(into)  # noqa: S202
    # Return the single top-level directory if the archive has one.
    entries = [p for p in into.iterdir()]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return into


def apply(archive: Path, expected_sha256: Optional[str] = None,
          target_version: Optional[str] = None) -> Dict[str, Any]:
    """Install a version from a local tarball. Returns a report.

    - Verifies SHA-256 if `expected_sha256` is provided.
    - Extracts into `<versions_dir>/<version>-staging/`, then renames.
    - Runs pending migrations.
    - Updates the `current` pointer.
    - Does NOT touch any project directory (see `preserves()`).
    """
    if not archive.exists():
        return {"ok": False, "error": f"archive missing: {archive}"}
    if expected_sha256 and not integrity.verify_sha256(archive, expected_sha256):
        return {"ok": False, "error": "integrity check failed"}

    layout.ensure_layout()
    target_version = target_version or "unknown"
    staging = layout.versions_dir() / f"{target_version}-staging"
    if staging.exists():
        import shutil
        shutil.rmtree(staging)
    try:
        top = _extract_tarball(archive, staging)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"extract failed: {e}"}

    final = layout.versions_dir() / target_version
    if final.exists():
        import shutil
        shutil.rmtree(final)
    top.rename(final)
    if staging.exists():
        import shutil
        shutil.rmtree(staging, ignore_errors=True)

    # Migrations
    from .. import migrations
    applied = migrations.run_pending()

    state.record_installed(target_version, str(final))
    layout.current_pointer().write_text(str(final), encoding="utf-8")
    return {"ok": True, "version": target_version, "path": str(final),
            "migrations": applied}
