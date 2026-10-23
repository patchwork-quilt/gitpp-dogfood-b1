#!/usr/bin/env python3
"""ferryctl — a small ferry-operations CLI.

Reads the sailing table and rota from ferryops/, prints what the
harbour is doing today. Stdlib only; there is nothing to install.
"""
import argparse
import sys

from ferryops.crew import rota_lines
from ferryops.schedule import next_sailing, sailings


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ferryctl", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_sail = sub.add_parser("sailings", help="list today's crossings")
    p_sail.add_argument("--boat", choices=["kestrel", "osprey"], default=None)

    sub.add_parser("crew", help="print the crew rota")

    p_next = sub.add_parser("next", help="the next crossing from a pier")
    p_next.add_argument("pier", choices=["north", "south"])
    p_next.add_argument("time", help="from time, HH:MM")

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
