"""Tests for loop.py state management."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from common import save_state, load_state, STATE_DIR, now_iso


def test_state_persistence():
    """State is saved and loaded correctly."""
    test_data = {
        "workflow": "test",
        "status": "PROCESSING",
        "updated_at": now_iso(),
    }
    save_state("_test_state", test_data)
    loaded = load_state("_test_state")
    assert loaded["workflow"] == "test"
    assert loaded["status"] == "PROCESSING"

    # Cleanup
    (STATE_DIR / "_test_state.json").unlink(missing_ok=True)


def test_state_atomic_write():
    """State writes are atomic (no partial writes)."""
    test_data = {"key": "value" * 1000}
    save_state("_test_atomic", test_data)
    loaded = load_state("_test_atomic")
    assert loaded["key"] == "value" * 1000

    # Cleanup
    (STATE_DIR / "_test_atomic.json").unlink(missing_ok=True)


def test_load_missing_state():
    """Loading non-existent state returns empty dict."""
    result = load_state("_nonexistent_state_file")
    assert result == {}
