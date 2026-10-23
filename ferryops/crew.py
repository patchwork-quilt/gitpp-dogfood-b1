"""The crew rota: who is on which boat, in which role.

Seat names, not people — the rota names the seat that is filled,
and the coordination surface (see the repo README) is where a
seat's current holder is claimed.
"""

ROTA = [
    {"boat": "kestrel", "skipper": "skipper-a", "deck": "deckhand-1"},
    {"boat": "osprey", "skipper": "skipper-b", "deck": "deckhand-2"},
]


def rota_lines():
    return [
        f"{r['boat']:<8} skipper {r['skipper']}, deck {r['deck']}" for r in ROTA
    ]
