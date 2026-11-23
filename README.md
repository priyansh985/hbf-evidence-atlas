# HbF Evidence Atlas — build workspace

A searchable, reproducible evidence atlas for sickle cell disease: it turns published
measurements about γ-globin RNA, total HbF, F-cell %, HbF-per-cell and clinical
outcomes into a checked, traceable case set — what was measured, what can be compared,
the narrowest missing observation, and the cited source locator.

Build state: **Phases 0–6 of the build plan complete** — research pilot, validation/
comparison rules, static atlas report (Three.js + GSAP + vanilla JS), rules-only
benchmark evaluation, and the interactive web dashboard. `py -m unittest discover -s tests -v` → 34 tests OK.

---

## Purpose

Sickle-cell researchers screening claims about HbF induction need a way to answer, for a
given claim and its evidence: what was measured, at what time point and in which study
group, with what denominator and endpoint definition, and how does it compare with adjacent
readouts or contexts? The atlas answers this from a versioned corpus of evidence records
and ships the deterministic export (`out/atlas-report/`) plus a benchmark of curated claim
cases.

## Scope

- **In scope:** the versioned evidence corpus (`data/`), the Python package
  (`src/hbf_atlas/`), the static HTML atlas report (`out/atlas-report/`), the benchmark
  (`benchmark/`), the evaluation report (`reports/evaluation.md`), and the build
  documentation (`docs/superpowers/`).
- **Out of scope (later phases):** AI-arm execution — frozen inputs in
  `benchmark/ai-arm-inputs.json` are ready (authorized online evaluation only); the
  benchmark publication review (deferred — single-reviewer pilot); a web framework — the
  report is static HTML and runs offline and dependency-free.

## Tech stack

- **Language:** Python 3.12+, stdlib only (`unittest`, `json`, `csv`, `pathlib`).
- **JS (3):** Vanilla JavaScript (report/dashboard interactivity: search, filters,
  evidence details); Three.js (interactive dimension map, in the report and the
  dashboard); GSAP (report/dashboard animations/micro-interactions).
- **Vendored assets:** Three.js 0.187.0 (`vendor/three.min.js` — ES-module build, plus
  `vendor/three.core.js`) and GSAP 3.15.1 (`vendor/gsap.min.js`), recorded in
  `vendor/versions.json`.
- **Tests:** stdlib `unittest`; `py -m unittest discover -s tests -v`.
- **CLI:** `py -m hbf_atlas validate <corpus_dir>`,
  `py -m hbf_atlas build-report <corpus_dir> <output_dir>` and
  `py -m hbf_atlas build-dashboard <corpus_dir> <output_dir>`.

## Layout

- `src/hbf_atlas/` — package: `models.py` (record dataclasses + explicit-unknown
  vocabulary), `io.py` (`load_corpus`, `validate_corpus`), `compare.py`
  (`assess_comparison`), `report.py` (`export_corpus`), `dashboard.py`
  (`export_dashboard`), `evaluate.py` (`evaluate`), `__main__.py` (CLI),
  `static/` (report + dashboard assets + vendor).
- `dashboard/` — interactive web dashboard (`index.html`, `dashboard.js`, `style.css`,
  `atlas-data.json`, `vendor/`).
- `data/corpus/` — the compiled corpus: `sources.json`, `observations.json`,
  `claims.json`, `reviews.json`, `data_version.txt` (= 0.1.0).
- `data/pilot/` — pilot evidence records: `pilot-001.json` … `pilot-012.json`.
- `research/` — `search-log.md`, `screening.csv`, `pilot-findings.md`.
- `benchmark/` — `cases.json` (26 cases), `labels.md` (reference labels + reviewer
  rationales), `split.json` (frozen split + leakage/near-duplicate audit),
  `predictions-rules.json` (rules-only baseline), `evaluation.json` (serialized Evaluation),
  `ai-arm-inputs.json` (frozen AI-arm inputs, pending authorized online evaluation),
  `rules_baseline.py`.
- `reports/evaluation.md` — evaluation report (counts, metrics, error table, what was learned).
- `out/atlas-report/` — built atlas export: `index.html`, `data.json`, `vendor/`,
  `atlas.js`, `style.css`.
- `tests/` — unit tests: `test_validation.py`, `test_comparison.py`, `test_report.py`,
  `test_dashboard.py`, `test_evaluate.py`.
- `docs/superpowers/` — `plans/` (user's build plan + my checkbox-tracked plan),
  `specs/` (research protocol + design).

## How to use

### 1. Run the test suite (34 tests)

    py -m unittest discover -s tests -v

Expect `Ran 34 tests ... OK`.

### 2. Validate the corpus

    py -m hbf_atlas validate data/corpus

Prints validation issues (none for the current corpus) and exits 0.

### 3. Build the atlas report

    py -m hbf_atlas build-report data/corpus out/atlas-report

Writes `out/atlas-report/{index.html, data.json, vendor/, atlas.js, style.css}`. The export
is deterministic (stable ordering, no timestamps) — rebuilding to another directory yields
identical `index.html`/`data.json`.

### 4. Use the report — open `out/atlas-report/index.html` in a browser

- Search (top box) and filters: by readout, study type (human/mouse), intervention and
  evidence status (supported/contradicted/insufficient).
- The two exa-cel endpoint observations — **29/30** (broad severe-VOC; PMID 38661449) and
  **30/30** (broader severe-VOE; endpoint reanalysis, PMID 40146367) — are distinct rows in
  study group G1-EXA-CEL-CLIMB-SCD121.
- Click a row: the evidence panel shows the claim, the decision (support, direction,
  rationale), and the observation details (value, unit, denominator, time point, sample
  linkage, endpoint definition) plus source links (http/https only; unsafe links shown as
  plain text).
- The Three.js canvas renders the dimension map (points by time point + support, sized by
  denominator, colored by readout/study group).

### 5. Re-run the rules-only benchmark evaluation

```powershell
$env:PYTHONPATH = "F:\New folder (4)\Scientific_Projects\hbf-evidence-atlas"; py benchmark/rules_baseline.py
```

(The script lives in `benchmark/`, so `src/` is added via `PYTHONPATH`.) It writes
`benchmark/predictions-rules.json` (baseline predictions) and `benchmark/evaluation.json`
(the serialized Evaluation) and is deterministic — re-running produces identical results.

## Interactive dashboard

The interactive web dashboard (`dashboard/`) is an interactive version of the static atlas
report: a search box, four filters (readout, study type, intervention, evidence status), a
searchable case table with an evidence panel, and a Three.js map of the observations. Build
it with:

    py -m hbf_atlas build-dashboard data/corpus dashboard

then open `dashboard/index.html` in a browser (offline; the export embeds the data as
`window.ATLAS_DATA`). How to use it:

- **Search** — filters claims, values, locators and all fields (case-insensitive).
- **Filters** — by readout, study type (human/mouse), intervention and evidence status
  (supported/contradicted/insufficient).
- **Case table** — click a row to open the evidence panel: claim, decision status/direction/
  rationale, observation (value, unit, denominator, time point, sample linkage, endpoint
  definition) and source links (http/https only; unsafe links shown as plain text).
- **Three.js map** — the canvas places each observation by its time point (x) and support
  level (y), colored by readout kind, sized by denominator; click a point to select the
  case (hover highlights).

How researchers use the atlas: the same screening workflow as the static report — filter and
search the cases; each row shows the claim, its readout/value/unit/denominator and the
evidence status; the panel shows the full decision with the source locator. The dashboard
makes cross-readout patterns visible at a glance: the concordant matched pairs (e.g. RNA +
protein in the F/A study), the exa-cel endpoint definitions (29/30 vs 30/30), and the
decoupled patterns (e.g. the hydroxyurea mouse-model gap: F cells sustained while gamma-globin
RNA is unmeasured).

## Results so far

- **Research pilot (Phase 1):** 12 records (P-001–P-012) across 5 independent study groups
  (G1–G5); feasibility gate passed — 12 records ≥ 10, 5 groups ≥ 5, 4 matched cross-readout
  comparisons from 3 groups, 3 mismatch/discordance examples. Exa-cel rates recomputed from
  published totals: 29/30 = 96.7% (95% CI 82.8–99.9); 30/30 = 100.0% (95% CI 88.4–100.0).
  Decision: **proceed**. See `research/pilot-findings.md`.
- **Atlas (Phases 2–3):** `out/atlas-report/` — data_version 0.1.0, 6 sources, 12
  observations, 2 claims, 24 rows; `window.ATLAS_DATA` embedded in `index.html`.
- **Interactive dashboard (Phase 6):** `dashboard/` — built with
  `py -m hbf_atlas build-dashboard data/corpus dashboard` (3 JS: Vanilla/Three.js/GSAP).
- **Benchmark (Phase 4):** 26 cases across 5 groups (holdout = all, `benchmark/split.json`);
  reference labels reviewed and reconciled (`benchmark/labels.md`); rules-only baseline run
  — metrics: unsupported endorsement rate 0.167 (1/6 — false endorsement C-04), supported-
  claim acceptance 0.35 (7/20), 0 abstentions, 0 missing predictions; error table (1 false
  endorsement + 13 missed supported claims) in `reports/evaluation.md`. AI arms frozen in
  `benchmark/ai-arm-inputs.json` (pending authorized online evaluation).

## Reference documents

- My plan (checkbox-tracked): `docs/superpowers/plans/2026-11-23-hbf-evidence-atlas-own-plan.md`
- User's build plan: `docs/superpowers/plans/2026-11-22-hbf-evidence-atlas-build.md`
- Design spec / research protocol: `docs/superpowers/specs/2026-11-22-hbf-evidence-atlas-design.md`
  (also at `ai-science-lab/docs/superpowers/specs/`)
- Pilot: `research/search-log.md`, `research/screening.csv`, `research/pilot-findings.md`
- Interactive dashboard: `dashboard/`, `src/hbf_atlas/dashboard.py`,
  `src/hbf_atlas/static/dashboard/`

## Versioning

- Corpus: `data/corpus/data_version.txt` = 0.1.0 — consistent with `benchmark/split.json`
  (`data_version`), `data/corpus/reviews.json` (`corpus_version`), and the report export
  (`out/atlas-report/data.json` `data_version`).
- Records: immutable IDs (`source_id`, `obs_id`, `claim_id`, `review_id`); benchmark claims
  are frozen (BC-01…BC-26).
- Generated outputs: deterministic per corpus version.

---

*Build workspace for the HbF Evidence Atlas — phases 0–5 complete as of 2026-11-23;
`py -m unittest discover -s tests -v` → 30 tests OK.*
