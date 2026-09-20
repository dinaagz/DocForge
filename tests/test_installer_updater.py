"""Tests for the updater: preserves() and apply() rollback semantics."""
from __future__ import annotations

import io
import tarfile
from pathlib import Path

import pytest

from docforge.installer import state, updater


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DOCFORGE_HOME", str(tmp_path / "rt"))
    monkeypatch.setenv("DOCFORGE_STATE_DIR", str(tmp_path / "rt" / "state"))
    monkeypatch.setenv("DOCFORGE_BIN", str(tmp_path / "rt" / "bin"))
    state.reset_versions()
    state.reset_migrations()


def test_preserves_lists_user_directories():
    assert sorted(updater.preserves()) == [
        ".docforge", "input", "logs", "output", "work"]


def test_check_only_local_source_returns_shape():
    r = updater.check_only(source="local:./", current="0.2.0")
    assert set(r) >= {"current", "latest", "update_available", "channel", "source"}
    assert r["update_available"] is False


def test_apply_rejects_missing_archive(tmp_path: Path):
    r = updater.apply(tmp_path / "nope.tgz")
    assert r["ok"] is False


def _make_tarball(dest: Path, top: str, files: dict) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(dest, "w:gz") as tf:
        for name, content in files.items():
            data = content.encode() if isinstance(content, str) else content
            info = tarfile.TarInfo(name=f"{top}/{name}")
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return dest


def test_apply_installs_from_tarball(tmp_path: Path):
    archive = _make_tarball(
        tmp_path / "df.tgz", "docforge-0.3.0",
        {"marker.txt": "hello", "docforge/_version.py": "VERSION='0.3.0'"})
    r = updater.apply(archive, target_version="0.3.0")
    assert r["ok"] is True
    assert Path(r["path"]).exists()
    assert (Path(r["path"]) / "marker.txt").read_text() == "hello"
    assert state.current_version() == "0.3.0"


def test_apply_rejects_bad_sha256(tmp_path: Path):
    archive = _make_tarball(tmp_path / "df.tgz", "top", {"f": "x"})
    r = updater.apply(archive, expected_sha256="deadbeef" * 8,
                       target_version="0.3.0")
    assert r["ok"] is False
    assert "integrity" in r["error"]


def test_apply_rejects_path_traversal(tmp_path: Path):
    """Malicious tarball with `../` must be refused."""
    archive = tmp_path / "evil.tgz"
    with tarfile.open(archive, "w:gz") as tf:
        info = tarfile.TarInfo(name="../evil.txt")
        data = b"pwn"
        info.size = len(data)
        tf.addfile(info, io.BytesIO(data))
    r = updater.apply(archive, target_version="0.3.0")
    assert r["ok"] is False
    assert "unsafe" in r["error"]
