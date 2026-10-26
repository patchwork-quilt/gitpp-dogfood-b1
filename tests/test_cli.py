import contextlib
import io
import json
import os
import tempfile
import unittest

import ferryctl


def run_cli(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = ferryctl.main(argv)
    return code, out.getvalue()


def write_snapshot(state):
    snap = {
        "surface": "ferry-ops",
        "branch": "gitpp/state",
        "derived_from": {
            "gitpp_state_tip": "a" * 40,
            "records": ["genesis"],
            "tool": "test",
            "fold_source": "test",
        },
        "counts": {
            "records": 1,
            "keys": len(state),
            "conflicts": 0,
            "orphans": 0,
        },
        "declared": {
            "task.claim.*": {"description": "claims"},
            "release.freeze": {"description": "freeze"},
            "deploy.hold": {"description": "hold"},
            "oncall.primary": {"description": "pager"},
            "berth.assignment": {"description": "berth"},
        },
        "state": state,
        "orphans": [],
    }
    f = tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(snap, f)
    f.close()
    return f.name


class TestSurfaceCommands(unittest.TestCase):
    """Against the committed snapshot (the tidy acceptance state)."""

    def test_surface_header_and_lines(self):
        code, out = run_cli(["surface"])
        self.assertEqual(code, 0)
        self.assertIn("ferry-ops surface — derived from gitpp/state @", out)
        self.assertIn("deploy.hold = true (winner hold-storm; losers: genesis)", out)
        self.assertIn("oncall.primary = rota-lead (winner oncall-rota)", out)
        self.assertIn("task.claim.dock-7 = agent-dockhand", out)
        self.assertIn("release.freeze = unset", out)

    def test_claims(self):
        code, out = run_cli(["claims"])
        self.assertEqual(code, 0)
        self.assertIn("dock-7", out)
        self.assertIn("agent-dockhand", out)

    def test_freeze_open(self):
        code, out = run_cli(["freeze"])
        self.assertEqual(code, 0)
        self.assertIn("releases open", out)

    def test_hold(self):
        code, out = run_cli(["hold"])
        self.assertEqual(code, 0)
        self.assertIn("deploys HELD (winner hold-storm)", out)

    def test_oncall(self):
        code, out = run_cli(["oncall"])
        self.assertEqual(code, 0)
        self.assertIn("rota-lead", out)

    def test_berth_reads_the_snapshot(self):
        # Whatever the committed snapshot declares is what the CLI
        # must report — no more, no less. (The berth key's history
        # is the surface episode recorded in RESULTS-B.md.)
        snap = ferryctl.surface.load_snapshot()
        code, out = run_cli(["berth"])
        self.assertEqual(code, 0)
        if "berth.assignment" not in snap["declared"]:
            self.assertIn("not declared", out)
        elif "berth.assignment" in snap["state"]:
            e = snap["state"]["berth.assignment"]
            self.assertIn(f"berth.assignment: {e['value']}", out)
        else:
            self.assertIn("declared but unset", out)


class TestStateFlag(unittest.TestCase):
    """--state points the CLI at another snapshot."""

    def setUp(self):
        self.path = write_snapshot(
            {
                "deploy.hold": {"value": False, "winner": "genesis", "losers": []},
                "release.freeze": {
                    "value": {"from": "2026-11-01", "to": "2026-11-03"},
                    "winner": "freeze-1",
                    "losers": [],
                },
                "berth.assignment": {
                    "value": "dock-3-spring",
                    "winner": "berth-spring",
                    "losers": [],
                },
            }
        )
        self.addCleanup(os.unlink, self.path)

    def test_hold_off(self):
        code, out = run_cli(["--state", self.path, "hold"])
        self.assertEqual(code, 0)
        self.assertIn("deploys running — hold is off (winner genesis)", out)

    def test_freeze_window(self):
        code, out = run_cli(["--state", self.path, "freeze"])
        self.assertEqual(code, 0)
        self.assertIn("releases FROZEN 2026-11-01 -> 2026-11-03", out)

    def test_berth_set(self):
        code, out = run_cli(["--state", self.path, "berth"])
        self.assertEqual(code, 0)
        self.assertIn("berth.assignment: dock-3-spring (record berth-spring)", out)

    def test_claims_empty(self):
        code, out = run_cli(["--state", self.path, "claims"])
        self.assertEqual(code, 0)
        self.assertIn("no claims on the board", out)


class TestTimetableCommands(unittest.TestCase):
    def test_sailings(self):
        code, out = run_cli(["sailings", "--boat", "kestrel"])
        self.assertEqual(code, 0)
        self.assertIn("kestrel", out)
        self.assertNotIn("osprey", out)

    def test_crew(self):
        code, out = run_cli(["crew"])
        self.assertEqual(code, 0)
        self.assertIn("skipper", out)

    def test_next_none_left(self):
        code, out = run_cli(["next", "south", "23:59"])
        self.assertEqual(code, 1)
        self.assertIn("no more crossings today", out)


if __name__ == "__main__":
    unittest.main()
