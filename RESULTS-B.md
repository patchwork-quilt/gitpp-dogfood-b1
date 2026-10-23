# RESULTS-B — Mapping B live acceptance, ferry-ops surface

*Run 2026-10-23 (UTC) against the real gitpp-app (Mapping B merged and
deployed) on this repo. Every drill was a real push; every verdict below
was read back from the check-runs API (Check name , all
conclusions neutral). Pushes and commits by the acceptance run; branch
 was deleted after drill 3.*

**Verdict: PASS with one un-designed side effect (drill 4).** All seven
surface Checks arrived promptly on their pushes — including both
force-pushes — with no delivery lag and no re-pushes.

## Drills

| # | Drill | Push | Check | Verdict | Decisive line (quoted) |
|---|---|---|---|---|---|
| 1 | Control: add  (deploy.hold=true) to  |  | 120182247512 | PASS | Body opens: "This Check derives the declared coordination surface only — the keys named in  on . It did not read or analyse this repository's code, and it says nothing about whether the code merges cleanly." State: " = true — winner ", " = rota-lead", " = agent-dockhand", each with its declaration description printed. |
| 2 | Undeclared key: add  (sets ) |  | 120182463853 | PASS | "record  (in ) — none of its effect keys are declared in surface.json (sets ); it did not derive" — and state was byte-identical to drill 1. |
| 3 | Proposals preview on  (, ) |  | 120182663759 | PASS (expectation corrected, see surprises) | Title: "git.pp surface — ferry-ops, preview: what lands if these proposals do". Landed state printed first, proposals under "In flight — proposed records (not landed)", union under "State if these proposals land — a separate derivation".  — "would win; no contention". |
| 4 | Retire  from surface.json |  | 120182901327 | PARTIAL — Retired mechanics as designed; orphan cascade not designed (see surprises) | "record  … key(s)  were declared before and are not declared now; the record did not derive. Preserved on ; re-declaring the key revives it exactly as it was" (same for ). |
| 5A | Restore  (normal commit) |  | 120183145652 | PASS | Retired section gone; "5 landed records · 3 keys · 1 conflict(s) · 0 orphan(s)"; full state back, genesis deriving again. |
| 5B | Force-push rewrite of  without  |  | 120183356363 | PASS | "1 record(s) derived on 2026-10-23T01:11:21.766Z are absent from  at :  — the branch history was rewritten or records were deleted" |
| 6 | Final tidy restore (force-push; original surface.json; records genesis + claim-dock-7 + oncall-rota + hold-storm; typo-1 dropped) |  | 120183562248 | PASS | "4 landed records · 3 keys · 1 conflict(s) · 0 orphan(s)" with the full state; and the mechanism firing once more, verbatim: "1 record(s) derived on 2026-10-23T01:12:02.679Z are absent from  at :  — the branch history was rewritten or records were deleted" |

## Independent verification (drill 1)

The state tip's records were folded locally with the gitpp-action
renderer (), independently of the App. Local fold: 4 records ·
3 keys · 1 conflict · 0 orphans; state  = true (winner
),  = rota-lead,  =
agent-dockhand; the one conflict (deploy.hold, loser genesis) identical.
**The App's surface Check and the independent fold agree exactly.**
(All records on the branch at that point set declared keys only, so the
declaration filter changed nothing — the comparison tests the fold, and
drills 2–4 test the filter.)

## Accounting (observed)

- Pushes by the run: 7 content pushes (6 to , 1 to
  ) + 1 branch deletion + this write-up push.
-  Checks observed via the check-runs API: 7 before this
  write-up (ids in the table) + the Check this write-up's own push
  produces under  — an as-landed Check on an ordinary
  main push, which is the trigger matrix working as designed.

## Surprises

1. **Drill 4 orphan cascade (un-designed).** Retiring  —
   genesis's only effect — stopped genesis from deriving at all, so
   its descendants  and  became orphans and
   the surface fell to "0 keys · 2 orphan(s)":  and
    vanished from state even though their keys were
   still declared. Nothing was silent (Retired named the records,
   Orphans named the children, state honestly showed unset), and
   restoring the key revived everything exactly. But the design
   presents key retirement as a per-key event; in practice, retiring
   the key that anchors the root record retires the whole tree beneath
   it. A root record whose effects are all retired probably should keep
   its anchor role in the ancestry graph even while its effects stay
   retired.
2. **Drill 3 verdict vs expectation.** The drill brief guessed
    "would lose to ". It **would win** — and
   the Check is right: 's parent is , and
   within a kind a record that descends from a rival supersedes it.
   Supersession is how a claim is handed over; the brief's guess, not
   the App, was wrong.
3. **Basis-line intermittency.** "surface last changed" printed a
   timestamp on drills 1, 4, 5A, 6 but "at an unknown time" on drills
   2, 3, 5B. The tip sha in the basis line was correct every time; only
   the changed-at lookup intermittently missed. Cosmetic, unexplained
   from outside.
4. **The history manifest counts rejected records.**  never
   derived (drill 2 rejected it), yet the final restore named it as
   "derived on … absent". The manifest evidently holds every record id
   present at the last derivation, derived or not. The naming still
   worked exactly when it mattered (drill 5B); the word "derived"
   slightly overclaims for rejected records.
