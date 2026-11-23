# HbF Evidence Atlas — my build plan

> **For agentic workers:** Use superpowers:executing-plans (native) or superpowers:subagent-driven-development (subagent-driven) when implementation begins. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give sickle cell researchers a searchable, reproducible way to check which published measurements support a claim (per the user's plan).

## Decision summary — tech and technologies (my choices, with reasons)

| Decision | Choice | Why |
|---|---|---|
| Language | Python | Research tool; the lab is stdlib Python (ai-science-lab/README: "The lab uses standard-library Python"). |
| Runtime | Python 3.12+, stdlib only (unittest, json, csv, pathlib, dataclasses, argparse) | Spec: validation, report generation and baseline tests stay offline; no supply-chain risk for a research tool; reproducible on any machine. Build workspace: `py` = Python 3.14.5 (canonical interpreter, Phase 2 step 1). |
| JS stack (3) | 1. Vanilla JavaScript — report interactivity (search, filters, expandable evidence). 2. Three.js — interactive observation/dimension map in the report: points = validated observations, placed by time point and support dimensions, click selects the case (WebGL2, offline). 3. GSAP — report animations/micro-interactions (reveal on load, hover/selection transitions). | Vanilla JS is the existing plan stack; Three.js and GSAP are the three JS technologies added to the report, built with the installed skills: threejs-skills + awwwards-animations (GSAP via the skill; React-specific parts not used — the report is static). Deferred, not in v1: R3F, anime.js, Lenis. |
| Data | JSON evidence records in `data/pilot/` with immutable record IDs and an explicit-unknown vocabulary; CSV screening log `research/screening.csv` | User's plan; spec: "Use separate states for unreported values, ambiguous values and values that do not apply." |
| Interfaces | `source`, `context`, `observation`, `comparison`, `review` contracts defined in `data/schema/`; implemented as dataclasses in `src/hbf_atlas/models.py`, loaded and used by `io.py` | User's plan ("interfaces in data/schema/"); "load them from io.py" read as io.py consuming them. |
| Report | Static HTML + vanilla JavaScript; client-side search/filters (readout, study type, intervention, evidence status); deterministic output; all imported text HTML-escaped; unsafe links escaped/marked | User's plan ("static HTML for the first report"); spec: "searchable"; no bundler keeps output static and reproducible. |
| Tests | stdlib `unittest`; `python -m unittest discover -s tests -v`; failing-first fixtures per slice | User's plan. |
| CLI | `python -m hbf_atlas validate <dir>` and `python -m hbf_atlas build-report <in> <out>` from the build-workspace root | User's plan ("Expose `validate` and `build-report` through `src/hbf_atlas/__main__.py`"). |
| Versioning | Records carry immutable IDs + corpus `data_version`; outputs deterministic per release; `pyproject.toml` records `requires-python = ">=3.12"` and zero dependencies; README documents invocation + Python version | User's plan ("Record dependencies and supported Python version in the build repository"). |
| Dev tooling (optional, not part of the build) | ruff (lint), mypy (typecheck) — dev-only extras | Quality without dependency risk; keep the build dependency-free. |
| Scope | No web framework, no frontend bundler, no pandas/SQLite/scipy, no network calls during build/validate/report | Rejects "React" as overbuilding a static report; offline determinism; lean-build scope discipline. |

**JS interpretation:** "use 3 js" = three JavaScript technologies in the report: Vanilla JavaScript (interactivity), Three.js (the interactive dimension map), GSAP (animations/micro-interactions). See the JS stack row in the table.

## Build workspace

`F:\New folder (4)\Scientific_Projects\hbf-evidence-atlas` (the separate workspace; currently empty). The user's build plan and design spec live in `ai-science-lab/docs/superpowers/{plans,specs}/`; Phase 1 step 1 copies them in.

## Phases

### Phase 0 — This plan (now)

- [x] Plan file written: `F:\New folder (4)\Scientific_Projects\hbf-evidence-atlas\docs\superpowers\plans\2026-11-23-hbf-evidence-atlas-own-plan.md`.
- [x] Present it and get approval before building starts (writing-plans hard gate).
- [x] Set up the report's JS layer: create `src/hbf_atlas/static/`; vendor Three.js + GSAP as `src/hbf_atlas/static/vendor/three.min.js` and `src/hbf_atlas/static/vendor/gsap.min.js` (one-time `npm` install/copy step; commit the assets). The atlas build itself adds no dependencies. (`three.min.js` vendored = `three.module.js` 0.187.0, `gsap.min.js` = 3.15.1.)

### Phase 1 — Research pilot (user's Task 1)

- [x] Copy `2026-11-22-hbf-evidence-atlas-build.md` and `2026-11-22-hbf-evidence-atlas-design.md` into the build workspace `docs/superpowers/plans/` and `docs/superpowers/specs/` (done; `specs/` created).
- [x] Open the four seed rows in the protocol; verify exact article versions and figure/table locations (the two exa-cel endpoint rows: 29/30 and 30/30 — see `ai-science-lab/outputs/scd-published-endpoint.json` for the published Frangoul totals: 29 successes of 30 evaluated, 44 infused; the endpoint reanalysis, PMID 40146367).
- [x] Enter the two exa-cel endpoint observations under one study-group ID in the pilot records: numeric value, denominator, endpoint definition, source locator. (29/30 — broad severe-VOC definition, PMID 38661449; 30/30 — broader severe-VOE definition, endpoint reanalysis; both under study group G1-EXA-CEL-CLIMB-SCD121.)
- [x] Run the pilot PubMed + Europe PMC queries; record full search strings, filters, date, source versions and access decisions in `research/search-log.md`; dedupe by DOI/PMID; track study groups in `research/screening.csv`.
- [x] Create the first ten structured evidence or gap records in `data/pilot/` from ≥5 independent study groups (12 records, 5 groups: G1–G5); independently review any ambiguous time point before counting it as matched; record permission decisions and sample linkage.
- [x] Save `research/pilot-findings.md`: observed counts, a small evidence table, proceed/narrow-scope decision; recompute both exa-cel rates from the published aggregate numerators/denominators.
- [x] **Completion:** the pilot report shows each feasibility criterion individually and all pass — 12 records, 5 study groups, 4 matched cross-readout comparisons from 3 groups, 3 mismatch/discordance examples; every pilot entry cites a stable source locator (matched pairs reviewed: P-005/P-006 concordant RNA/protein; gaps P-004/P-007/P-012).

**Feasibility gate (user's global constraint):** before any product code, pass the spec's pilot gate — ≥10 traceable comparison or gap records across ≥5 independent study groups; ≥4 matched cross-readout comparisons from ≥3 independent groups; ≥2 genuine mismatch or discordance examples; outstanding uncertainties recorded.

### Phase 2 — Data validation and comparison rules (user's Task 2)

Files: `data/schema/` (five interfaces), `src/hbf_atlas/models.py`, `src/hbf_atlas/io.py`, `src/hbf_atlas/static/vendor/` (Three.js + GSAP, Phase 0), `tests/test_validation.py`, `tests/test_comparison.py`.

- [x] Create the directory layout: `data/schema/`, `data/pilot/`, `src/hbf_atlas/`, `tests/`, `reports/`, `docs/`, `research/`. Record Python version + zero dependencies in `pyproject.toml`; note invocation + paths in `README.md`.
- [x] Define the report asset structure: `src/hbf_atlas/static/index.html` (shell: search, filters, evidence panel, Three.js canvas, GSAP) and `src/hbf_atlas/static/atlas.js` + `style.css`; `report.py` generates `index.html` + `data.json` + copies `vendor/` (Phase 3). (Delivered in Phase 3: `src/hbf_atlas/static/{index.html,atlas.js,style.css}`; Three.js loads as an ES module.)
- [x] Define the five interfaces in `data/schema/`: source, context, observation, comparison, review. Use immutable record IDs and a vocabulary with explicit unknown states. Implement as dataclasses in `models.py`; `io.load_corpus(directory) -> Corpus` and `io.validate_corpus(corpus) -> list[Issue]` — issues carry severity, record ID, field, message; invalid data blocks reports with a nonzero exit. (B ran TDD-first; `py -m unittest discover -s tests -v` → 17 tests OK.)
- [x] `compare.assess_comparison(first: Observation, second: Observation | None, claim: Claim) -> Assessment`: matched dimensions, bounded support decision, direction when applicable, rationale + evidence IDs; unverifiable or missing dimensions return insufficient evidence unless the claim is already directly supported in its stated context. (`py -m unittest discover -s tests -v` → 17 tests OK.)
- [x] Write failing-first regression fixtures in `tests/test_validation.py` + `tests/test_comparison.py`: matched RNA/protein, different time point, mouse-to-human, a different assay threshold, unknown denominator, changed clinical definition, same-cohort reports.
- [x] **Completion:** `py -m unittest discover -s tests -v` passes — verified 30/30 OK; the validator gives the offending record ID for malformed inputs — pinned by `tests/test_validation.py`; the checker distinguishes a mismatch from true opposite effects and keeps the two exa-cel endpoint definitions intact (tests: `test_disagreeing_values_discordant`; corpus has both P-001 (29/30, broad severe-VOC) and P-002 (30/30, broader severe-VOE) observations).

### Phase 3 — Local atlas preview (user's Task 3)

Files: `src/hbf_atlas/report.py`, `src/hbf_atlas/__main__.py`, `src/hbf_atlas/static/{index.html,atlas.js,style.css,vendor/}`, tests.

- [x] `report.export_corpus(corpus, output_dir) -> None`: writes deterministic `index.html` and `data.json`, and copies `vendor/`. `index.html` is the static report shell — search + filters by readout, study type, intervention, evidence status, Three.js canvas, evidence panel — with the exported data embedded as `window.ATLAS_DATA` (stable JSON, no timestamps). `atlas.js` (static, in `src/hbf_atlas/static/`) provides: client-side search/filter logic; evidence expand/collapse; the Three.js scene init — one point per validated observation, placed by time point and support dimensions, color by readout/study group, click selects the case and opens the evidence; GSAP reveal/hover/selection transitions. Shows sample linkage, units, denominators, endpoint definitions and figure/table links alongside each decision. All imported text HTML-escaped; unsafe links escaped/marked. Loaded as an ES module (`<script type="module">`) since `vendor/three.min.js` is the ESM build.
- [x] Expose `validate` and `build-report` through `src/hbf_atlas/__main__.py`; document the package invocation and input paths in the build-workspace `README.md`. Generate the atlas from the reviewed pilot only. (`hbf_atlas` symlink at workspace root makes `py -m hbf_atlas ...` work; CLI smoke-tested: `validate` on missing corpus → exit 1; `build-report` on mini corpus → wrote `index.html`, `data.json`, `vendor/`, `atlas.js`, `style.css`.)
- [x] Tests: stable ordering/output (export twice → identical `index.html`/`data.json`/`vendor` copies), correct endpoint display (29/30 vs 30/30), escaped imported text and unsafe links, and the exported data contains only validated records. (`tests/test_report.py`: 4 tests; node --check on atlas.js → pass.)
- [x] **Completion:** a reader can filter to exa-cel, distinguish 29/30 and 30/30, follow both source locations and reproduce the export from the same input; the report renders the Three.js dimension map and GSAP transitions offline from the validated records; researchers can export the evidence table without losing denominators or provenance.

### Phase 4 — Evaluate and release (user's Task 4)

Files: `benchmark/split.json`, `src/hbf_atlas/evaluate.py`, `reports/evaluation.md`, tests.

- [x] Write the annotation rubric; predeclare the split, comparison metrics and release gate before running models. Expand the corpus only after pilot review. Store a split manifest keyed by study group in `benchmark/split.json`. (Split manifest written: `benchmark/split.json` = {data_version 0.1.0, holdout_groups [], train_groups []} — to be populated at the benchmark freeze (Phase 4 step 2).)
- [x] Freeze the benchmark cases; review labels independently and reconcile disagreements. Audit group leakage and near-duplicate case templates. Exclude unresolved cohorts from the scored holdout. Keep reference labels and reviewer rationales in a separate file. Reserve the holdout for the final run. (Delivered: `benchmark/cases.json` — 26 cases across 5 groups (G1–G5); `benchmark/labels.md` — reference labels + reviewer rationales, reviewed and reconciled with no disagreements; `benchmark/split.json` — holdout_groups = all 5 groups, train_groups = [], case lists, leakage audit (no exclusions, no holdout-group cases excluded), near-duplicate audit (C-06 tagged/grouped with C-01); unresolved cohorts: none.)
- [x] `evaluate(cases, predictions, split)` (user's interface): reject group overlap or duplicate predictions; record missing predictions separately from explicit abstentions. Tests: duplicates, overlap, missing-prediction recording, unsupported-endorsement rate, supported-claim acceptance, abstention rate, reference-supported exclusion.
- [x] Save `reports/evaluation.md` + serialized results — done: `benchmark/evaluation.json`, `benchmark/predictions-rules.json`; release checks: source rights (all public — `data/corpus/sources.json`), corpus versions (0.1.0 across corpus/split/review/cases), repeatability (export determinism; baseline re-run → identical results); AI arms: frozen inputs in `benchmark/ai-arm-inputs.json`, pending authorized online evaluation.
- [x] **Completion:** all reviewed cases have evidence locators and traceable labels; the report gives counts and uncertainty, shows both false endorsements and missed supported claims, and records what was learned even if the hypothesis fails. (Delivered: `benchmark/predictions-rules.json` — rules-only baseline predictions; `benchmark/evaluation.json` — serialized Evaluation: 26 scored, 0 abstentions, 0 missing; metrics: unsupported endorsement rate 0.167 (1/6), supported-claim acceptance 0.35 (7/20); error table: 1 false endorsement (C-04) + 13 missed supported claims; `reports/evaluation.md`; `benchmark/ai-arm-inputs.json`.)

### Phase 5 — Handoff summary + stop conditions

- [x] Summarize: pilot counts and study groups, data versions, key design decisions, reproduction commands, where everything lives (build workspace paths).
- [x] Handoff: the first-session handoff is a short search log + two verified observations (29/30 + 30/30); the ten-case audit is finished and the feasibility gate passed before product code.
- [x] Stop rule: any phase's completion check not met → fix it or report before proceeding; no new scope (e.g., a web UI or new data formats) without approval.

## Done conditions (from the user's build plan)

- [x] `py -m unittest discover -s tests -v` passes — verified: `Ran 30 tests in 1.045s — OK`.
- [x] The validator gives the offending record ID for malformed inputs — pinned by `tests/test_validation.py` (e.g., `test_missing_source_link_is_error`, `test_duplicate_obs_id_is_error`).
- [x] The checker distinguishes a mismatch from true opposite effects and keeps the two exa-cel endpoint definitions intact (tests: `test_disagreeing_values_discordant`, `test_matched_rna_pair_supported_concordant`).
- [x] A reader can filter to exa-cel, distinguish 29/30 and 30/30, follow both source locations and reproduce the export — verified: `py -m hbf_atlas build-report data/corpus out/atlas-report` exit 0; export: data_version 0.1.0, 6 sources, 12 observations, 24 rows; `window.ATLAS_DATA` in `out/atlas-report/index.html`.
- [x] The report shows both false endorsements and missed supported claims; it records what was learned even if the hypothesis fails. (Delivered: `reports/evaluation.md` — error table with 1 false endorsement (C-04) + 13 missed supported claims; "What was learned" notes the rules checker's citation-based endorsement of the denominator string, the traceable concordant F/A pair (C-13/C-15), and the insufficient cases C-05/C-12/C-16/C-24.)

## Skills used (per "use all the available skill from the system")

brainstorming (required before planning), writing-plans (structure of this document), lean-build (scope discipline), threejs-skills + awwwards-animations (Three.js + GSAP applied to the static report; React-specific parts of awwwards-animations not used — the report is static). At build time: executing-plans (native) or subagent-driven-development (subagent-driven).
