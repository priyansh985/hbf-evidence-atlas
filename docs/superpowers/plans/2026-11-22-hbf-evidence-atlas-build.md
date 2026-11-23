# HbF Evidence Atlas implementation plan

> **For the build workspace:** Use the executing-plans skill when implementation begins. Steps use checkboxes for tracking.

**Goal** Give sickle cell researchers a searchable, reproducible way to check which published measurements support a claim.

**Architecture** Use versioned records and a deterministic Python comparison tool. Generate a searchable local report and data export from the same records. Keep model evaluation separate so the atlas runs offline.

**Tech stack** Python 3.12, standard-library unittest, CSV for screening and JSON for evidence records, static HTML for the first report.

**Spec** [Research protocol and design](../specs/2026-11-22-hbf-evidence-atlas-design.md)

## Global constraints

- Start in the separate build workspace. Pass the feasibility gate before creating product code.
- Use public aggregate evidence and permitted metadata. Preserve stable source, study-group and observation IDs.
- Retain source context, units and thresholds. Represent uncertainty and unavailable values explicitly.
- Keep data validation, report generation and baseline tests offline. Pin model, prompts and inputs for any separately authorized online evaluation.

## Review focus

| Risk | Check and owning task |
|---|---|
| Follow-up papers share a cohort | One group ID and one evaluation split, tasks 1 and 4 |
| Missing fields accidentally treated as a match | Explicit unknown state and insufficient support test, task 2 |
| Similar endpoint labels hide different event definitions | Same-cohort 29/30 and 30/30 fixture, tasks 2 and 3 |
| Imported citations contain HTML | Escaping test for text and unsafe links, task 3 |
| A system abstains on everything | Report acceptance of supported claims and abstention alongside unsupported endorsements, task 4 |

## Interfaces and responsibility

| File | Interface or responsibility |
|---|---|
| `src/hbf_atlas/io.py` | `load_corpus(directory: Path) -> Corpus` and `validate_corpus(corpus: Corpus) -> list[Issue]`. Each issue includes severity, record ID, field and message. Invalid data blocks reports with a nonzero exit. |
| `src/hbf_atlas/compare.py` | `assess_comparison(first: Observation, second: Observation | None, claim: Claim) -> Assessment`. A missing second record can represent an evidence gap. Return matched dimensions, support, optional direction, rationale and observation IDs. |
| `src/hbf_atlas/report.py` | `export_corpus(corpus: Corpus, output_dir: Path) -> None`. Writes deterministic JSON and one local HTML table. |
| `src/hbf_atlas/evaluate.py` | `evaluate(cases: list[Case], predictions: list[Prediction], split: SplitManifest) -> Evaluation`. Reject group overlap or duplicate predictions. Record missing predictions separately from explicit abstentions. |

## Milestones

| Milestone | Estimate | Acceptance |
|---|---|---|
| Research pilot | 1–2 working days | Ten evidence or gap records with source locators, scored against the protocol gate |
| Minimum atlas | 3–5 working days after the gate | Local searchable table, evidence details, cited decisions and deterministic export |
| Benchmark pilot | 1–2 further weeks, subject to reviewer availability | Frozen split, reviewed labels, three baselines and grouped error analysis |

These estimates assume one builder, accessible full texts, and a second reviewer for benchmark labels. 

## Task 1. Start the research pilot

- [ ] Copy this plan and protocol into the build workspace. Before creating code, open the four seed rows in the protocol and verify exact article versions and figure or table locations.
- [ ] Run the PubMed and Europe PMC queries using the installed skills. Record exports, full search strings, date, source versions and access decisions in `research/search-log.md`. Deduplicate and track study groups in `research/screening.csv`.
- [ ] Create the first ten structured evidence or gap records in `data/pilot/` from at least five independent study groups. Independently review any ambiguous time point before counting it as matched. Record permission decisions and sample linkage.
- [ ] Save `research/pilot-findings.md` with the observed counts, a small evidence table, and the proceed or narrow-scope decision. Recompute both exa-cel rates from the published aggregate numerators and denominators.

**Completion check:** The pilot report shows the feasibility criteria individually, including which criteria failed. A second reader can resolve every pilot entry to a specific source location.

## Task 2. Implement data validation and comparison rules

- [ ] In the build workspace, create `data/schema/`, `data/pilot/`, `src/hbf_atlas/`, `tests/`, `reports/`, and `docs/`. Keep corpus data and generated outputs versioned by release. Record dependencies and supported Python version in the build repository.
- [ ] Define source, context, observation, comparison and review interfaces in `data/schema/`. Use immutable record IDs and a vocabulary with explicit unknown states. Load them from `src/hbf_atlas/io.py`. Reject missing source links, duplicate IDs, broken references and invalid denominators.
- [ ] Define `assess_comparison(first, second, claim)` in `src/hbf_atlas/compare.py`. Return each match dimension, a bounded support decision, direction when applicable, and evidence IDs. For unverifiable or missing dimensions, return insufficient evidence unless the claim is already directly supported in its stated context.
- [ ] Write a failing regression fixture before each implementation slice in `tests/test_validation.py` and `tests/test_comparison.py`. Include matched RNA/protein, different time point, mouse-to-human, a different assay threshold, unknown denominator, changed clinical definition, and same-cohort reports.

**Completion check:** A clean run of `python -m unittest discover -s tests -v` passes. The validator gives the offending record ID for malformed inputs. The checker distinguishes a mismatch from true opposite effects and keeps the two exa-cel endpoint definitions intact.

## Task 3. Publish a local atlas preview

- [ ] Implement read-only export and rendering in `src/hbf_atlas/report.py`. Render search and filters for curated cases by readout, study type, intervention and evidence status. Show sample linkage, units, denominators, endpoint definitions and figure/table links alongside each decision. Escape all imported text used in HTML.
- [ ] Expose `validate` and `build-report` through `src/hbf_atlas/__main__.py`. Document the package invocation and input paths in the build workspace README. Export deterministic JSON and local HTML from the same validated records.
- [ ] Add tests for stable ordering and output, correct endpoint display, and escaped imported text and unsafe links. Generate the atlas from the reviewed pilot only.

**Completion check:** A reader can filter to exa-cel, distinguish 29/30 from 30/30, follow both source locations and reproduce the export from the same input. Researchers can export the evidence table without losing denominators or provenance.

## Task 4. Evaluate and release

- [ ] Write the annotation rubric and predeclare the split, comparison metrics and release gate before running models. Expand the corpus only after pilot review. Store a split manifest keyed by study group in `benchmark/split.json`.
- [ ] Freeze the benchmark cases, review labels independently, and reconcile disagreements. Audit group leakage and near-duplicate case templates. Exclude unresolved cohorts from the scored holdout. Keep reference labels and reviewer rationales in a separate file. Reserve the holdout for the final run.
- [ ] Evaluate the rules-only baseline and both AI arms with frozen inputs and model settings. Put evaluation logic under `src/hbf_atlas/evaluate.py`. Test missing predictions, class imbalance, abstention, study-group leakage, unsupported-claim denominators and accidental gold-label fields in either model input.
- [ ] Save `reports/evaluation.md`, an error table and serialized results. As part of the release check, verify links, source rights, corpus versions and repeatability. If the model improvement gate fails, publish the descriptive atlas and benchmark limitations. With a single reviewer, release only the provisional descriptive atlas and defer scored benchmark publication.

**Completion check:** All reviewed cases have evidence locators and traceable labels. The report gives counts and uncertainty, shows both false endorsements and missed supported claims, and records what was learned even if the hypothesis fails.

## First 45 minutes in the build workspace

1. Open the protocol and create the search log with its first PubMed query.
2. Enter the two exa-cel endpoint observations from the published reanalysis under one study-group ID.
3. Record each numerator, denominator, endpoint definition and source locator. Ask whether the evidence model can represent the pair without treating the endpoints as equivalent.

The expected handoff from the first session is a short search log and two verified observations. Finish the ten-case audit before sizing the product build.
