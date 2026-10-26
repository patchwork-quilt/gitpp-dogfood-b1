import copy
import unittest

from ferryops import surface


def synthetic(**overrides):
    snap = {
        "surface": "ferry-ops",
        "branch": "gitpp/state",
        "derived_from": {
            "gitpp_state_tip": "0" * 40,
            "records": [],
            "tool": "test",
            "fold_source": "test",
        },
        "counts": {"records": 0, "keys": 0, "conflicts": 0, "orphans": 0},
        "declared": {
            "task.claim.*": {"description": "claims"},
            "release.freeze": {"description": "freeze"},
            "deploy.hold": {"description": "hold"},
            "oncall.primary": {"description": "pager"},
            "berth.assignment": {"description": "berth"},
        },
        "state": {},
        "orphans": [],
    }
    snap.update(overrides)
    return snap


class TestCommittedSnapshot(unittest.TestCase):
    """The snapshot on main is real derived state, not a fixture:
    these are the values the acceptance record (RESULTS-B.md)
    established for the tidy gitpp/state tip."""

    @classmethod
    def setUpClass(cls):
        cls.snap = surface.load_snapshot()

    def test_provenance_names_a_tip(self):
        tip = self.snap["derived_from"]["gitpp_state_tip"]
        self.assertEqual(len(tip), 40)

    def test_counts(self):
        c = self.snap["counts"]
        self.assertEqual(c["records"], len(self.snap["derived_from"]["records"]))
        self.assertEqual(c["keys"], len(self.snap["state"]))
        self.assertEqual(c["orphans"], 0)

    def test_hold_is_on_via_hold_storm(self):
        e = surface.entry(self.snap, "deploy.hold")
        self.assertIs(e["value"], True)
        self.assertEqual(e["winner"], "hold-storm")
        self.assertEqual(e["losers"], ["genesis"])

    def test_claims_board(self):
        self.assertEqual(
            surface.claims(self.snap),
            [("dock-7", "agent-dockhand", "claim-dock-7")],
        )

    def test_oncall(self):
        e = surface.entry(self.snap, "oncall.primary")
        self.assertEqual(e["value"], "rota-lead")

    def test_freeze_unset(self):
        self.assertIsNone(surface.entry(self.snap, "release.freeze"))


class TestQueries(unittest.TestCase):
    def test_fmt_value(self):
        self.assertEqual(surface.fmt_value(True), "true")
        self.assertEqual(surface.fmt_value(False), "false")
        self.assertEqual(surface.fmt_value({"b": 1, "a": 2}), '{"a": 2, "b": 1}')
        self.assertEqual(surface.fmt_value("rota-lead"), "rota-lead")

    def test_is_declared(self):
        snap = synthetic()
        self.assertTrue(surface.is_declared(snap, "task.claim.anything"))
        self.assertTrue(surface.is_declared(snap, "deploy.hold"))
        self.assertFalse(surface.is_declared(snap, "deploy.hld"))
        self.assertFalse(surface.is_declared(snap, "task.claims.x"))

    def test_family_with_no_keys_set(self):
        lines = surface.surface_lines(synthetic())
        self.assertIn("task.claim.*  (no keys set)", lines)
        self.assertIn("release.freeze = unset", lines)

    def test_state_line_names_losers(self):
        snap = synthetic(
            state={
                "deploy.hold": {
                    "value": True,
                    "winner": "hold-storm",
                    "losers": ["genesis"],
                }
            }
        )
        self.assertEqual(
            surface.state_line(snap, "deploy.hold"),
            "deploy.hold = true (winner hold-storm; losers: genesis)",
        )

    def test_claims_sorted_by_task(self):
        snap = synthetic(
            state={
                "task.claim.b-task": {"value": "s2", "winner": "r2", "losers": []},
                "task.claim.a-task": {"value": "s1", "winner": "r1", "losers": []},
            }
        )
        self.assertEqual(
            surface.claims(snap),
            [("a-task", "s1", "r1"), ("b-task", "s2", "r2")],
        )

    def test_snapshot_is_not_mutated_by_queries(self):
        snap = synthetic()
        before = copy.deepcopy(snap)
        surface.surface_lines(snap)
        surface.claims(snap)
        self.assertEqual(snap, before)


if __name__ == "__main__":
    unittest.main()
