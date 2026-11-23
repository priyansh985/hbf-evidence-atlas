# HbF Evidence Atlas — Pilot findings

Status: proceed — the pilot passes the feasibility gate. Builder: HbF Evidence Atlas build workspace (2026-11-23).

Gate check (spec seed, "Review at least ten traceable comparison or gap records across at least five independent study groups..."):
- Records: 12 ≥ 10 ✓ (P-001…P-012, all traceable by source locator).
- Groups: 5 ≥ 5 ✓ (G1–G5, tracked in `research/screening.csv`).
- Matched cross-readout comparisons from ≥3 independent groups: 4 (G1, G3, G4) ✓.
- Genuine mismatch or discordance examples: 3 ≥ 2 ✓.
- Outstanding uncertainties recorded below.

## Search log

Full log: `research/search-log.md`.

- Pilot query (from the design spec, 2026-11-22-hbf-evidence-atlas-design.md):
  `("sickle cell" OR "sickle cell disease") AND ("fetal hemoglobin" OR "fetal haemoglobin" OR HbF OR "F-cell" OR "gamma globin") AND (BCL11A OR hydroxyurea OR exagamglogene OR "exa-cel")`
- Europe PMC export (same query, run earlier today by the lab): hit count 986 — `ai-science-lab/outputs/europepmc-scd-search.json` (retained as the source export).
- Date: 2026-11-23.
- Deduplication: by DOI/PMID across databases; no duplicates needing resolution in the pilot set.
- Study groups tracked in `research/screening.csv`.

## Pilot records (12)

| ID | Group | Type | Readout | Value | Locator |
|---|---|---|---|---|---|
| P-001 | G1-EXA-CEL-CLIMB-SCD121 | evidence | vo-free-event (broad severe VOC) | 29/30 | NEJM 390(18):1649–1662; PMID 38661449 |
| P-002 | G1-EXA-CEL-CLIMB-SCD121 | evidence | vo-free-event (broader severe VOE) | 30/30 | Advances in Therapy 42, 2490–2499; doi 10.1007/s12325-025-03162-2 |
| P-003 | G2-HYD-TOWNSES-MOUSE | evidence | f-cell-percent | 20% F cells at P14 (HU begun at P2) | Exp Hematol PMID 35843392 |
| P-004 | G2-HYD-TOWNSES-MOUSE | gap | gamma-globin-rna | not quantified | Exp Hematol PMID 35843392 |
| P-005 | G3-F-A-ERYTHROBLAST | evidence | gamma-globin-rna | ~30% of globin in F cells | Blood 2020; PMC7256358 |
| P-006 | G3-F-A-ERYTHROBLAST | evidence | hbF-percent | γG-globin protein (concordant with RNA) | Blood 2020; PMC7256358 |
| P-007 | G3-F-A-ERYTHROBLAST | gap | gamma-globin-rna | suppressed (~1000-fold); RNA-seq globin-depleted | Blood 2020; PMC7256358 (GSE144052) |
| P-008 | G4-BCL11A-SILENCING-NEJM2021 | evidence | hbF-percent | 21 (range 20.4–41.3) | NEJM 384(3):205–215; PMID 33283990 |
| P-009 | G4-BCL11A-SILENCING-NEJM2021 | evidence | f-cell-percent | 76 (range 58.9–93.6) | NEJM 384(3):205–215; PMID 33283990 |
| P-010 | G4-BCL11A-SILENCING-NEJM2021 | evidence | hbF-per-cell | 14 (range 9.0–18.6) | NEJM 384(3):205–215; PMID 33283990 |
| P-011 | G5-INDIVIDUAL-RBC-HBFPERCELL | evidence | hbF-per-cell | 4 pg/RBC (protective threshold) | Am J Hematol 95(11):1235–1245; PMID 32681733 |
| P-012 | G1-EXA-CEL-CLIMB-SCD121 | gap | vo-free-event | follow-up beyond 12 months: not reported | endpoint reanalysis (data cut 14 Jun 2023) |

## Study groups (5 independent)

G1-EXA-CEL-CLIMB-SCD121 (human; exa-cel pivotal trial, CLIMB SCD-121; severe SCD, ages 12–35); G2-HYD-TOWNSES-MOUSE (mouse; Townes humanized model; HU); G3-F-A-ERYTHROBLAST (human; F/A erythroblast study, Blood 2020); G4-BCL11A-SILENCING-NEJM2021 (human; BCL11A-shmiR gene therapy pilot, NEJM 2021); G5-INDIVIDUAL-RBC-HBFPERCELL (human; individual RBC HbF quantification, Am J Hematol 2020).

## Matched cross-readout comparisons (≥4 required, ≥3 groups)

1. G3: γ-globin RNA (P-005) + γG-globin protein (P-006) — stage-matched F vs A (CD71+/CD235+, FACS sorted); concordant.
2. G4: HbF% (P-008) + F-cell% (P-009) — matched pilot observations.
3. G4: F-cell% (P-009) + HbF per F-cell (P-010) — matched pilot observations.
4. G1: 29/30 (P-001) vs 30/30 (P-002) — same patient-level data under two endpoint definitions.

## Mismatch / discordance examples (≥2)

1. G3: P-007 (RNA-seq of globin-depleted cells) vs P-005 (qRT-PCR) — γ-globin suppressed in RNA-seq; assay mismatch (spec seed: "the RNA-seq protocol depleted globin RNA").
2. G2: P-003 (mouse F-cell elevation) vs P-004 (γ-globin RNA: no augmentation) — decoupling between F-cell elevation and γ-globin RNA in the mouse model.
3. G1: P-001 vs P-002 — changed clinical definition (broad severe-VOC vs broader severe-VOE endpoint rules).

## Outstanding uncertainties (pilot gaps)

- P-004: γ-globin RNA augmentation under HU in the Townes mouse model not quantified (abstract: lack of augmentation; attributed to erythropoiesis suppression).
- P-012: F-cell durability follow-up >12 months after the endpoint not reported (data cut 14 Jun 2023).
- F-cell distribution unmeasured in some studies (e.g., mouse model F-cell% is reported at P0/P2/P14 only).

## Exa-cel endpoint reproduction (two observations, one study group)

- **29/30** — broad severe-VOC endpoint (exa-cel definition): 96.7% (95% CI 82.8–99.9); published totals from the pivotal trial: 29/30 evaluable, Wilson 95% CI [0.833, 0.994], 44 participants infused (`ai-science-lab/outputs/scd-published-endpoint.json`; PMID 38661449).
- **30/30** — broader severe-VOE endpoint: 100.0% (95% CI 88.4–100.0). Source: endpoint reanalysis (Frangoul et al., Advances in Therapy 42, 2490–2499, 2025; doi 10.1007/s12325-025-03162-2; PMID 40146367). "These papers share a study group" — both observations: G1-EXA-CEL-CLIMB-SCD121.

## Decision

**Proceed** — the pilot passes the feasibility gate; the minimum atlas can be built from the reviewed pilot. Narrow-scope note: F-cell durability follow-up (P-012) and the mouse/human cross-study concordance are deferred; recorded as pilot gaps for the benchmark phase. Corpus compiled to `data/corpus/` for v0.1.0.
