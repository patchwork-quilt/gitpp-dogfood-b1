#!/usr/bin/env python3
"""ferryctl — a small ferry-operations CLI.

Two kinds of truth live here. The timetable and the rota are this
repo's own data (ferryops/schedule.py, ferryops/crew.py). The
coordination questions — who has claimed which dock job, whether
releases are frozen, whether deploys are held, who holds the
pager, which berth the fleet is assigned — belong to the declared
surface on the `gitpp/state` branch, and are answered from the
derived snapshot committed beside this file (surface-state.json;
see ferryops/surface.py for the chain).

Stdlib only; there is nothing to install.
"""
import argparse
import os
import sys

from ferryops.crew import rota_lines
from ferryops.schedule import next_sailing, sailings
from ferryops import surface


def _snapshot(args):
    path = args.state or os.environ.get("FERRYCTL_STATE")
    return surface.load_snapshot(path)


def cmd_surface(args):
    snap = _snapshot(args)
    d = snap["derived_from"]
    c = snap["counts"]
    print(
        f"{snap['surface']} surface — derived from {snap['branch']} "
        f"@ {d['gitpp_state_tip'][:7]} "
        f"({c['records']} records · {c['keys']} keys · "
        f"{c['conflicts']} conflict(s) · {c['orphans']} orphan(s))"
    )
    for line in surface.surface_lines(snap):
        print(line)
    return 0


def cmd_claims(args):
    board = surface.claims(_snapshot(args))
    if not board:
        print("no claims on the board")
        return 0
    for task, seat, winner in board:
        print(f"{task:<12} {seat} (record {winner})")
    return 0


def cmd_freeze(args):
    snap = _snapshot(args)
    e = surface.entry(snap, "release.freeze")
    if e is None:
        print("releases open — no freeze window on the surface")
        return 0
    v = e["value"]
    if isinstance(v, dict) and "from" in v and "to" in v:
        print(f"releases FROZEN {v['from']} -> {v['to']} (winner {e['winner']})")
    else:
        print(f"release.freeze = {surface.fmt_value(v)} (winner {e['winner']})")
    return 0


def cmd_hold(args):
    snap = _snapshot(args)
    e = surface.entry(snap, "deploy.hold")
    if e is None:
        print("deploy.hold is unset on the surface")
        return 0
    if e["value"] is True:
        print(f"deploys HELD (winner {e['winner']})")
    elif e["value"] is False:
        print(f"deploys running — hold is off (winner {e['winner']})")
    else:
        print(f"deploy.hold = {surface.fmt_value(e['value'])} (winner {e['winner']})")
    return 0


def cmd_oncall(args):
    snap = _snapshot(args)
    e = surface.entry(snap, "oncall.primary")
    if e is None:
        print("oncall.primary is unset — nobody holds the pager")
        return 0
    print(f"oncall.primary: {e['value']} (record {e['winner']})")
    return 0


def cmd_berth(args):
    snap = _snapshot(args)
    if not surface.is_declared(snap, "berth.assignment"):
        print("berth.assignment is not declared on the surface")
        return 0
    e = surface.entry(snap, "berth.assignment")
    if e is None:
        print("berth.assignment is declared but unset")
        return 0
    print(f"berth.assignment: {e['value']} (record {e['winner']})")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ferryctl", description=__doc__)
    parser.add_argument(
        "--state",
        default=None,
        help="read this surface snapshot instead of the committed "
        "surface-state.json (or set FERRYCTL_STATE)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_sail = sub.add_parser("sailings", help="list today's crossings")
    p_sail.add_argument("--boat", choices=["kestrel", "osprey"], default=None)

    sub.add_parser("crew", help="print the crew rota")

    p_next = sub.add_parser("next", help="the next crossing from a pier")
    p_next.add_argument("pier", choices=["north", "south"])
    p_next.add_argument("time", help="from time, HH:MM")

    sub.add_parser("surface", help="the whole coordination board, derived")
    sub.add_parser("claims", help="who has claimed which dock job")
    sub.add_parser("freeze", help="whether releases are frozen")
    sub.add_parser("hold", help="whether deploys are held")
    sub.add_parser("oncall", help="who holds the pager")
    sub.add_parser("berth", help="the fleet's assigned berth")

    args = parser.parse_args(argv)

    if args.command == "sailings":
        for s in sailings(boat=args.boat):
            print(f"{s['departs']}  {s['boat']:<8} {s['from']} -> {s['to']}")
    elif args.command == "crew":
        for line in rota_lines():
            print(line)
    elif args.command == "next":
        s = next_sailing(args.pier, args.time)
        if s is None:
            print("no more crossings today")
            return 1
        print(f"{s['departs']}  {s['boat']} from {s['from']}")
    elif args.command == "surface":
        return cmd_surface(args)
    elif args.command == "claims":
        return cmd_claims(args)
    elif args.command == "freeze":
        return cmd_freeze(args)
    elif args.command == "hold":
        return cmd_hold(args)
    elif args.command == "oncall":
        return cmd_oncall(args)
    elif args.command == "berth":
        return cmd_berth(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
