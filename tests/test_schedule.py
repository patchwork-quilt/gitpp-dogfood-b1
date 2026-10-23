import unittest

from ferryops.schedule import next_sailing, sailings


class TestSchedule(unittest.TestCase):
    def test_table_is_ordered(self):
        times = [s["departs"] for s in sailings()]
        self.assertEqual(times, sorted(times))

    def test_boat_filter(self):
        boats = {s["boat"] for s in sailings(boat="kestrel")}
        self.assertEqual(boats, {"kestrel"})

    def test_next_sailing(self):
        s = next_sailing("north", "08:00")
        self.assertEqual(s["departs"], "08:05")
        self.assertEqual(s["boat"], "osprey")

    def test_next_sailing_none_left(self):
        self.assertIsNone(next_sailing("south", "23:59"))


if __name__ == "__main__":
    unittest.main()
