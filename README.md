# ferryctl — ferry operations, the ordinary way

A small fictional ferry-operations CLI. It keeps the day's sailings,
the crew rota, and the dock jobs for a two-boat harbour service, and
it is deliberately boring: plain Python, no services, state in JSON
files a human can read.

```sh
python3 ferryctl.py sailings            # today's crossings
python3 ferryctl.py sailings --boat kestrel
python3 ferryctl.py crew                # who is on which boat
python3 ferryctl.py jobs                # open dock jobs
python3 ferryctl.py hold "harbour fog"  # note a deploy-style hold (local only)
```

## Why this repo exists

It is the **dogfood repository for git.pp Mapping B** (declared
state surfaces). Several seats — humans and agents — work in this
repo at once, and they collide over a handful of coordination
questions that code review does not answer:

- who has claimed which dock job,
- whether releases are frozen,
- whether deploys are held, and why,
- who holds the pager.

Those keys are declared as a **surface**: [`surface.json`](https://github.com/patchwork-quilt/gitpp-dogfood-b1/blob/gitpp/state/surface.json)
on the orphan branch `gitpp/state`, with git.pp records beside it
in `records/`. Records land by ordinary git pushes, under each
seat's own credentials (Tier 1 — the gitpp-app derives the surface
into an advisory `git.pp surface` Check and writes nothing itself).
The pointer file [`.gitpp/surface.json`](.gitpp/surface.json) on
this branch is documentation only; the declaration itself lives on
`gitpp/state`, beside its records.

Proposals ride in pull requests as `.gitpp/proposals/*.json`: a
seat that wants to change the surface proposes the record in its
PR, where the preview Check shows what would win and what would
lose — and after merge, the record is landed onto `gitpp/state`
by the team's own push, exactly as it was proposed.

## Layout

```
ferryctl.py          the CLI (argparse, stdlib only)
ferryops/schedule.py sailings table + next-crossing logic
ferryops/crew.py     the rota
tests/               unittest, stdlib only
```
