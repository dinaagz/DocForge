"""Tests for the installer version comparison utility."""
from __future__ import annotations

import pytest

from docforge.installer.version import compare, is_newer, parse


def test_parse_stable():
    assert parse("0.2.0") == (0, 2, 0, "", 0)


def test_parse_pre_release():
    major, minor, patch, kind, num = parse("1.0.0-rc1")
    assert (major, minor, patch, kind, num) == (1, 0, 0, "rc", 1)


def test_parse_v_prefix():
    assert parse("v0.2.0") == (0, 2, 0, "", 0)


def test_parse_rejects_garbage():
    with pytest.raises(ValueError):
        parse("not-a-version")


def test_compare_orders_by_semver():
    assert compare("0.2.0", "0.1.9") == 1
    assert compare("0.2.0", "0.2.0") == 0
    assert compare("0.2.0", "0.3.0") == -1
    assert compare("1.0.0", "0.99.99") == 1


def test_pre_release_orders_below_stable():
    assert compare("1.0.0", "1.0.0-rc1") == 1
    assert compare("1.0.0-rc2", "1.0.0-rc1") == 1
    assert compare("1.0.0-beta", "1.0.0-rc1") == -1


def test_is_newer():
    assert is_newer("0.3.0", "0.2.0")
    assert not is_newer("0.2.0", "0.2.0")
    assert not is_newer("0.1.0", "0.2.0")
