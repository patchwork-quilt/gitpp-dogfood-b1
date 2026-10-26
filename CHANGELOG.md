# Changelog

## Unreleased — the project build-out (2026-10-26)

The dogfood dressing becomes the project it was dressed as.

### Added

- **Surface commands in ferryctl**: `surface` (the whole derived
  board), `claims`, `freeze`, `hold`, `oncall`, `berth` — the CLI
  now answers the coordination questions its surface declares, from
  the committed snapshot. `--state <file>` (or `FERRYCTL_STATE`)
  reads a different snapshot.
- **`surface-state.json`** — the derived surface snapshot,
  generated from `gitpp/state` @ `c958ee9` (4 records · 3 keys ·
  1 conflict · 0 orphans) and committed on main.
- **`tools/derive-snapshot.mjs`** — the snapshot generator: folds
  the branch's records through the gitpp-app's own derivation
  (validateSurface + applyDeclarationGate + derive, extracted the
  way the app's harness extracts it) and refuses on invalid input.
- **`ferryops/surface.py`** — snapshot loading and board queries.
- **Tests**: 29 unittest cases (schedule, surface queries, CLI
  end-to-end against the committed snapshot and synthetic ones).
- **CI**: GitHub Actions running the suite plus CLI smoke commands
  on every push and pull request.
- **`docs/mapping-b.svg`** — the surface flow diagram, adapted from
  the gitpp-app's deployment page.
- **LICENSE** (MIT) and this changelog.

### Changed

- README rewritten to the three-altitude standard: a runnable
  example first (all outputs executed), then the model, then the
  declared surface in depth.
- Tracked `__pycache__` artifacts removed; `.gitignore` added.

## Origins

- **2026-10-22** — repo created as the Mapping B dogfood: ferry-ops
  CLI dressing on main, the declared surface on `gitpp/state`.
- **2026-10-23** — Mapping B live acceptance: seven drills against
  the real gitpp-app (control, undeclared key, proposals preview,
  key retirement, restore, force-push detection, tidy restore),
  then the retire-anchor and retired-line re-drills after
  gitpp-app PRs #8 and #9. The full record, Check by Check, is
  [`RESULTS-B.md`](RESULTS-B.md) — append-only, never rewritten.
