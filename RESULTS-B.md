# RESULTS-B — Mapping B live acceptance, ferry-ops surface

*Run 2026-10-23 (UTC) against the real gitpp-app (Mapping B merged and
deployed) on this repo. Every drill was a real push; every verdict below
was read back from the check-runs API (Check name `git.pp surface`, all
conclusions neutral). Branch `probe/proposals` was deleted after
drill 3.*

**Verdict: PASS with one un-designed side effect (drill 4).** All
surface Checks arrived promptly on their pushes — including both
force-pushes — with no delivery lag and no re-pushes.

## Drills

| # | Drill | Push | Check | Verdict | Decisive line (quoted) |
|---|---|---|---|---|---|
| 1 | Control: add `hold-storm` (deploy.hold=true) to `gitpp/state` | `78ac430` | 120182247512 | PASS | Body opens: "This Check derives the declared coordination surface only — the keys named in `surface.json` on `gitpp/state`. It did not read or analyse this repository's code, and it says nothing about whether the code merges cleanly." State: "`deploy.hold` = true — winner `hold-storm`", "`oncall.primary` = rota-lead", "`task.claim.dock-7` = agent-dockhand", each key with its declaration description printed. |
| 2 | Undeclared key: add `typo-1` (sets `deploy.hld`) | `2985b51` | 120182463853 | PASS | "record `typo-1` (in `records/typo.json`) — none of its effect keys are declared in surface.json (sets `deploy.hld`); it did not derive" — and the derived state was identical to drill 1. |
| 3 | Proposals preview on `probe/proposals` (`claim-steal`, `freeze-1`) | `0d12026` | 120182663759 | PASS (expectation corrected, see surprises) | Title: "git.pp surface — ferry-ops, preview: what lands if these proposals do". Landed state printed first, proposals under "In flight — proposed records (not landed)", union under "State if these proposals land — a separate derivation". `freeze-1` — "would win; no contention". |
| 4 | Retire `deploy.hold` from surface.json | `9d2923f` | 120182901327 | PARTIAL — Retired mechanics as designed; orphan cascade not designed (see surprises) | "record `genesis` … key(s) `deploy.hold` were declared before and are not declared now; the record did not derive. Preserved on `gitpp/state`; re-declaring the key revives it exactly as it was" (same for `hold-storm`). |
| 5A | Restore `deploy.hold` (normal commit) | `eda4c96` | 120183145652 | PASS | Retired section gone; "5 landed records · 3 keys · 1 conflict(s) · 0 orphan(s)"; full state back, genesis deriving again. |
| 5B | Force-push rewrite of `gitpp/state` without `claim-dock-7` | `fbc7535` | 120183356363 | PASS | "1 record(s) derived on 2026-10-23T01:11:21.766Z are absent from `gitpp/state` at `fbc7535`: `claim-dock-7` — the branch history was rewritten or records were deleted" |
| 6 | Final tidy restore (force-push; original surface.json; records genesis + claim-dock-7 + oncall-rota + hold-storm; typo-1 dropped) | `2213399` | 120183562248 | PASS | "4 landed records · 3 keys · 1 conflict(s) · 0 orphan(s)" with the full state; and the mechanism firing once more, verbatim: "1 record(s) derived on 2026-10-23T01:12:02.679Z are absent from `gitpp/state` at `2213399`: `typo-1` — the branch history was rewritten or records were deleted" |

## Independent verification (drill 1)

The state tip's records were folded locally with the gitpp-action
renderer (`fold.mjs`), independently of the App. Local fold: 4 records ·
3 keys · 1 conflict · 0 orphans; state `deploy.hold` = true (winner
`hold-storm`), `oncall.primary` = rota-lead, `task.claim.dock-7` =
agent-dockhand; the one conflict (deploy.hold, loser genesis) identical.
**The App's surface Check and the independent fold agree exactly.**
(All records on the branch at that point set declared keys only, so the
declaration filter changed nothing — the comparison tests the fold, and
drills 2–4 test the filter.)

## Accounting (observed)

- Pushes by the run: 7 drill pushes (6 to `gitpp/state`, 1 to
  `probe/proposals`) + 1 branch deletion + the write-up pushes to main.
- `git.pp surface` Checks observed via the check-runs API: the 7 drill
  Checks in the table, plus Check **120183853608** on the first write-up
  push (`13c91a9`, "4 landed records · 3 keys · 1 conflict(s) · 0
  orphan(s)") — an as-landed Check on an ordinary main push under
  `preview: "full"`, which is the trigger matrix working as designed.
  (The first write-up commit's markdown was mangled by a shell heredoc
  on its way to the repo — backtick-quoted spans were executed as
  commands during the write; the correction commit that restored this
  file produced one more surface Check of the same shape.)

## Surprises

1. **Drill 4 orphan cascade (un-designed).** Retiring `deploy.hold` —
   genesis's only effect — stopped genesis from deriving at all, so
   its descendants `claim-dock-7` and `oncall-rota` became orphans and
   the surface fell to "0 keys · 2 orphan(s)": `oncall.primary` and
   `task.claim.dock-7` vanished from state even though their keys were
   still declared. Nothing was silent (Retired named the records,
   Orphans named the children, state honestly showed unset), and
   restoring the key revived everything exactly. But the design
   presents key retirement as a per-key event; in practice, retiring
   the key that anchors the root record retires the whole tree beneath
   it. A root record whose effects are all retired probably should keep
   its anchor role in the ancestry graph even while its effects stay
   retired.
2. **Drill 3 verdict vs expectation.** The drill brief guessed
   `claim-steal` "would lose to `claim-dock-7`". It **would win** — and
   the Check is right: `claim-steal`'s parent is `claim-dock-7`, and
   within a kind a record that descends from a rival supersedes it.
   Supersession is how a claim is handed over; the brief's guess, not
   the App, was wrong.
3. **Basis-line intermittency.** "surface last changed" printed a
   timestamp on drills 1, 4, 5A, 6 but "at an unknown time" on drills
   2, 3, 5B. The tip sha in the basis line was correct every time; only
   the changed-at lookup intermittently missed. Cosmetic, unexplained
   from outside.
4. **The history manifest counts rejected records.** `typo-1` never
   derived (drill 2 rejected it), yet the final restore named it as
   "derived on … absent". The manifest evidently holds every record id
   present at the last derivation, derived or not. The naming still
   worked exactly when it mattered (drill 5B); the word "derived"
   slightly overclaims for rejected records.

## Addendum — re-drill after the retire-anchor fix (2026-10-23 UTC)

The three deviations above were fixed in gitpp-app PR #8 (branch
`fix/surface-retire-anchor`, deployed from the branch for this
re-drill; harness `bun surface.test.mjs` 64 passed, 0 failed,
including new S8 = this drill's scenario, S9 = never-declared
control, S10 = check_suite-driven basis time). The drills below
re-ran against the deployed fix on this repo.

| Step | Push | Check | Verdict |
|---|---|---|---|
| Retire `deploy.hold` again | `581167e` | 120186211532 | **PASS** — "4 landed records · 2 keys · 0 conflict(s) · **0 orphan(s)**" (drill 4 read 0 keys · 2 orphans). State kept `oncall.primary` = rota-lead and `task.claim.dock-7` = agent-dockhand; genesis + hold-storm listed under Retired; the retired key absent from state. |
| Restore `deploy.hold` (normal commit) | `a85241b` | 120186378569 | **PASS** — full state back: `deploy.hold` = true (winner `hold-storm`), 3 keys · 1 conflict · 0 orphans, no Retired section. |
| Remove `hold-storm` (history-wording probe) | `3b979f2` | 120186563696 | **PASS** — the History integrity line fired in the new wording: "1 record(s) **present in the surface** on 2026-10-23T01:21:54.353Z are absent from `gitpp/state` at `3b979f2`: `hold-storm` — the branch history was rewritten or records were deleted". |
| Restore `hold-storm` — branch tidy | `f9a4a1b` | 120186717129 | **PASS** — "4 landed records · 3 keys · 1 conflict(s) · 0 orphan(s)", `deploy.hold` = true, no History section. `gitpp/state` ends at `f9a4a1b` with the original surface.json (all four keys) and the original four records. |

On the basis line: every re-drill Check carried a real "surface
last changed" timestamp. The intermittency's root cause (found in
the code, fixed in the same PR): the time came from the webhook
payload or the discovery cache — a push payload carries
`head_commit.timestamp`, a check_suite payload carries none, and
whichever twin won the per-commit claim decided whether the time
existed (a null could also be cached and inherited by a later
probe-path derivation). The time is now read from the tip commit
itself whenever no payload or cache supplied one.

## Addendum — re-check after the retired-line wording fix (2026-10-23 UTC)

One line of wording remained imprecise after PR #8: the Retired
line for a fully-retired record still said "the record did not
derive", when since PR #8 the record anchors its descendants and
only its effects stop deriving. Fixed in gitpp-app PR #9 (branch
`fix/retired-line-wording`, deployed from the branch for this
re-check; harness `bun surface.test.mjs` 65 passed, 0 failed, S8
gaining a pinned assertion on the new wording). The partial
(mixed-record) Retired line renders unchanged.

| Step | Push | Check | Verdict |
|---|---|---|---|
| Retire `deploy.hold` once more | `354ee8f` | 120187802201 | **PASS** — "4 landed records · 2 keys · 0 conflict(s) · 0 orphan(s)"; state kept `oncall.primary` = rota-lead and `task.claim.dock-7` = agent-dockhand. The Retired line for genesis, verbatim: "record `genesis` (in `records/genesis.json`) — key(s) `deploy.hold` were declared before and are not declared now; its effects did not derive, but the record still anchors its descendants. Preserved on `gitpp/state`; re-declaring the key revives its effects exactly as they were" (same line for `hold-storm`). |
| Restore `deploy.hold` (normal commit) — branch tidy | `063bbfe` | 120188015170 | **PASS** — "4 landed records · 3 keys · 1 conflict(s) · 0 orphan(s)", `deploy.hold` = true (winner `hold-storm`), no Retired section. `gitpp/state` ends at `063bbfe` with the original surface.json (all four keys) and the original four records. |
