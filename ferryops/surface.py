"""The derived coordination surface, as ferryctl reads it.

The surface itself lives on the `gitpp/state` branch: a declaration
(`surface.json`) plus git.pp records. This module never reads that
branch. It reads `surface-state.json` — a snapshot of the derived
state, committed on main, regenerated from the branch by
`tools/derive-snapshot.mjs` (which folds the records through the
same derivation code the gitpp-app runs live; the snapshot's
`derived_from` block names the branch tip it came from).

So the chain is: records land by ordinary git -> the fold derives
state -> a snapshot is committed here -> this CLI answers from the
snapshot. The gitpp-app's `git.pp surface` Check derives the same
state live on every push; the two readers agree by construction,
and RESULTS-B.md records the checks that prove it.
"""
import json
import os

SNAPSHOT_NAME = "surface-state.json"


def default_snapshot_path():
    """surface-state.json beside the ferryops package (repo root)."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        SNAPSHOT_NAME,
    )


def load_snapshot(path=None):
    """Load a surface snapshot (default: the repo's committed one)."""
    with open(path or default_snapshot_path(), encoding="utf-8") as f:
        return json.load(f)


def fmt_value(value):
    """Render a surface value the way the surface itself spells it."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def declared_patterns(snap):
    """Declared key patterns, in declaration order."""
    return list(snap["declared"].keys())


def entry(snap, key):
    """The derived entry for a concrete key, or None if unset."""
    return snap["state"].get(key)


def is_declared(snap, key):
    """True if a concrete key is covered by some declared pattern."""
    for pattern in snap["declared"]:
        if pattern.endswith(".*"):
            if key.startswith(pattern[:-1]):
                return True
        elif pattern == key:
            return True
    return False


def claims(snap):
    """The claims board: [(task-id, seat, winner-record-id), ...]."""
    board = []
    for key in sorted(snap["state"]):
        if key.startswith("task.claim."):
            e = snap["state"][key]
            board.append((key[len("task.claim."):], e["value"], e["winner"]))
    return board


def surface_lines(snap):
    """The whole board, one line per declared key, declaration order.

    Family patterns print once per concrete key they cover (or a
    single "no keys set" line); exact keys print set or unset.
    """
    lines = []
    for pattern in declared_patterns(snap):
        if pattern.endswith(".*"):
            covered = [
                k for k in sorted(snap["state"]) if k.startswith(pattern[:-1])
            ]
            if not covered:
                lines.append(f"{pattern}  (no keys set)")
            for key in covered:
                lines.append(state_line(snap, key))
        else:
            lines.append(state_line(snap, pattern))
    return lines


def state_line(snap, key):
    e = entry(snap, key)
    if e is None:
        return f"{key} = unset"
    line = f"{key} = {fmt_value(e['value'])} (winner {e['winner']}"
    if e["losers"]:
        line += f"; losers: {', '.join(e['losers'])}"
    return line + ")"
