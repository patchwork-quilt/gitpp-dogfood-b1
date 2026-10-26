#!/usr/bin/env node
// derive-snapshot.mjs — regenerate surface-state.json, the derived
// snapshot of the ferry-ops coordination surface that ferryctl reads.
//
// The snapshot is DERIVED, never hand-written: this tool folds the
// records on the gitpp/state branch through the same code the
// gitpp-app runs live — the fold engine and the Mapping B surface
// derivation (validateSurface + applyDeclarationGate + derive),
// extracted from the app's worker.js exactly the way the app's own
// harness (surface.test.mjs) extracts it.
//
// Usage:
//   node tools/derive-snapshot.mjs \
//     --state-dir <checkout of gitpp/state> \
//     --worker    <path to gitpp-app worker.js> \
//     --tip       <full sha of the gitpp/state tip> \
//     --fold-source "<provenance label for the fold code>" \
//     --out       <output path>
//
// Exits non-zero on any refusal (invalid declaration, duplicate or
// malformed record): a snapshot that cannot be derived is not
// written.
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

function arg(name) {
  const i = process.argv.indexOf(`--${name}`);
  if (i < 0 || i + 1 >= process.argv.length) {
    console.error(`missing --${name}`);
    process.exit(2);
  }
  return process.argv[i + 1];
}

const stateDir = arg("state-dir");
const workerPath = arg("worker");
const tip = arg("tip");
const foldSource = arg("fold-source");
const outPath = arg("out");

// ---- extract the app core slice (same markers as the app harness) --
const src = readFileSync(workerPath, "utf8");
const start = src.indexOf("/*TEST-EXTRACT:core*/");
const end = src.indexOf("export default");
if (start < 0 || end < 0 || end < start) {
  console.error("TEST-EXTRACT:core marker or export default not found in worker.js");
  process.exit(1);
}
const slicePath = join(tmpdir(), `gitpp-snapshot-slice-${process.pid}.mjs`);
writeFileSync(
  slicePath,
  src.slice(start, end) +
    "\n;globalThis.__api = { validateSurface, applyDeclarationGate, derive, pickWinnerId, settersOf, effectsOf };\n",
);
await import(slicePath);
const api = globalThis.__api;

// ---- load the declaration and the records ---------------------------
const decl = JSON.parse(readFileSync(join(stateDir, "surface.json"), "utf8"));
const v = api.validateSurface(decl);
if (v.error) {
  console.error(`surface.json refused: ${v.error}`);
  process.exit(1);
}
const surface = v.surface;

const recordFiles = readdirSync(join(stateDir, "records"))
  .filter((f) => f.endsWith(".json"))
  .sort();
const entries = [];
const seenIds = new Set();
for (const f of recordFiles) {
  let record;
  try {
    record = JSON.parse(readFileSync(join(stateDir, "records", f), "utf8"));
  } catch (e) {
    console.error(`records/${f}: malformed JSON (${e.message})`);
    process.exit(1);
  }
  if (typeof record.id !== "string" || record.id.length === 0) {
    console.error(`records/${f}: record has no string id`);
    process.exit(1);
  }
  if (seenIds.has(record.id)) {
    console.error(`records/${f}: duplicate record id ${record.id}`);
    process.exit(1);
  }
  seenIds.add(record.id);
  entries.push({ record, file: `records/${f}` });
}

// ---- derive ----------------------------------------------------------
const gate = api.applyDeclarationGate(surface, entries, []);
if (gate.fullyRejected.length > 0) {
  console.error(
    `records rejected by the declaration gate: ${gate.fullyRejected.map((r) => r.id).join(", ")}`,
  );
  process.exit(1);
}
const out = api.derive(gate.kept);
const byId = new Map(gate.kept.map((r) => [String(r.id), r]));
const setters = api.settersOf(gate.kept, out.orphans);
const conflictByKey = new Map(out.conflicts.map((c) => [c.key, c]));

const state = {};
for (const k of Object.keys(out.state).sort()) {
  const conflict = conflictByKey.get(k);
  const winner = conflict
    ? conflict.winner
    : api.pickWinnerId(setters.get(k), byId);
  state[k] = {
    value: out.state[k],
    winner,
    losers: conflict ? conflict.losers : [],
  };
}

const declared = {};
for (const p of surface.patterns) {
  declared[p.pattern] = { description: p.description };
}

const snapshot = {
  surface: surface.name,
  branch: "gitpp/state",
  derived_from: {
    gitpp_state_tip: tip,
    records: entries.map((e) => e.record.id),
    tool: "tools/derive-snapshot.mjs (this repo)",
    fold_source: foldSource,
  },
  counts: {
    records: entries.length,
    keys: Object.keys(state).length,
    conflicts: out.conflicts.length,
    orphans: out.orphans.length,
  },
  declared,
  state,
  orphans: out.orphans,
};

writeFileSync(outPath, JSON.stringify(snapshot, null, 2) + "\n");
console.log(
  `snapshot written: ${entries.length} records · ${snapshot.counts.keys} keys · ` +
    `${snapshot.counts.conflicts} conflict(s) · ${snapshot.counts.orphans} orphan(s) @ ${tip.slice(0, 7)}`,
);
