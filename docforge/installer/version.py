"""Semantic version parsing and comparison — no third-party dependency."""
from __future__ import annotations

import re
from typing import Tuple

_RE = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:-(?P<pre>[0-9A-Za-z\.-]+))?"
    r"(?:\+[0-9A-Za-z\.-]+)?$"
)


def parse(v: str) -> Tuple[int, int, int, str, int]:
    """Return (major, minor, patch, pre_kind, pre_num).

    Stable release → pre_kind = "" and pre_num = 0.
    Pre-releases (dev, alpha, beta, rc) are ranked in that order.
    """
    m = _RE.match(v.strip().lstrip("v"))
    if not m:
        raise ValueError(f"invalid version: {v!r}")
    major = int(m.group("major"))
    minor = int(m.group("minor"))
    patch = int(m.group("patch"))
    pre = m.group("pre") or ""
    kind, num = "", 0
    if pre:
        pm = re.match(r"(dev|alpha|beta|rc)\.?(\d*)", pre)
        if pm:
            kind = pm.group(1)
            num = int(pm.group(2) or 0)
        else:
            kind = pre
    return major, minor, patch, kind, num


_KIND_ORDER = {"": 4, "rc": 3, "beta": 2, "alpha": 1, "dev": 0}


def compare(a: str, b: str) -> int:
    """Return 1 if a > b, -1 if a < b, 0 if equal."""
    pa = parse(a)
    pb = parse(b)
    if pa[:3] != pb[:3]:
        return (pa[:3] > pb[:3]) - (pa[:3] < pb[:3])
    ka = _KIND_ORDER.get(pa[3], -1)
    kb = _KIND_ORDER.get(pb[3], -1)
    if ka != kb:
        return (ka > kb) - (ka < kb)
    return (pa[4] > pb[4]) - (pa[4] < pb[4])


def is_newer(candidate: str, current: str) -> bool:
    return compare(candidate, current) > 0
