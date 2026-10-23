"""The day's crossings for the two-boat service.

One dict per crossing: departs (HH:MM, harbour time), boat, from,
to. The table is the timetable as published; weather holds are a
coordination matter and deliberately not modelled here.
"""

SAILINGS = [
    {"departs": "06:10", "boat": "kestrel", "from": "north", "to": "south"},
    {"departs": "06:40", "boat": "osprey", "from": "south", "to": "north"},
    {"departs": "07:25", "boat": "kestrel", "from": "south", "to": "north"},
    {"departs": "08:05", "boat": "osprey", "from": "north", "to": "south"},
    {"departs": "09:00", "boat": "kestrel", "from": "north", "to": "south"},
    {"departs": "10:15", "boat": "osprey", "from": "south", "to": "north"},
    {"departs": "12:30", "boat": "kestrel", "from": "south", "to": "north"},
    {"departs": "14:45", "boat": "osprey", "from": "north", "to": "south"},
    {"departs": "16:20", "boat": "kestrel", "from": "north", "to": "south"},
    {"departs": "18:05", "boat": "osprey", "from": "south", "to": "north"},
    {"departs": "19:40", "boat": "kestrel", "from": "south", "to": "north"},
    {"departs": "21:15", "boat": "osprey", "from": "north", "to": "south"},
]


def sailings(boat=None):
    """All crossings, optionally for one boat, in departure order."""
    return [s for s in SAILINGS if boat is None or s["boat"] == boat]


def next_sailing(pier, time):
    """The first crossing leaving `pier` at or after `time` (HH:MM)."""
    for s in SAILINGS:
        if s["from"] == pier and s["departs"] >= time:
            return s
    return None
