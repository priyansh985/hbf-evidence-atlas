# HbF Evidence Atlas — Benchmark reference labels

Status: preliminary — builder + internal reconciliation (2026-11-23). Independent label review is deferred to the single-reviewer note below.

Reference labels are the ground truth for benchmark evaluation. They are recorded per case in `benchmark/cases.json`; the reviewer rationales and reconciliation notes are kept in this separate file.

| Case | Reference support | Rationale |
|---|---|---|
| C-01 | supported | CLIMB SCD-121 pivotal trial: 29/30 evaluable participants free from severe VO-C crises for ≥12 months under the broad severe-VOC definition; Wilson 95% CI 82.8–99.9 (published totals, PMID 38661449). |
| C-02 | supported | Endpoint reanalysis: 30/30 (100.0%; 95% CI 88.4–100.0) under the broader severe-VOE definition on the same CLIMB SCD-121 patient-level data (Frangoul et al., Advances in Therapy 42, 2490–2499; doi 10.1007/s12325-025-03162-2). |
| C-03 | supported | Exa-cel severe-VOC endpoint counts medical-facility visits of any duration (reanalysis Table 1/Table 2). |
| C-04 | contradicted | Truth: 29/30 were free; 1 participant did not meet the endpoint — the claim of 8 is contradicted (PMID 38661449). |
| C-05 | insufficient | F-cell durability beyond 12 months not reported (data cut 14 Jun 2023; pilot gap P-012). |
| C-06 | supported | Edited wording of C-01 (29/30 free); the "29 participants" phrasing drops the 1 non-free participant — same underlying data (P-001). |
| C-07 | supported | Trial inclusion criteria (12–35 years; severe SCD; ≥2 severe VOCs/year for 2 years) per the endpoint reanalysis Methods. |
| C-08 | supported | Townes mouse model: F cells ≈20% at P14 with HU begun at P2 (Exp Hematol PMID 35843392). |
| C-09 | supported | Without HU, F cells are virtually undetectable at P14 in the Townes model (abstract). |
| C-10 | contradicted | The paper reports a lack of augmentation of γ-globin mRNA under HU — the claim of augmentation is contradicted (Exp Hematol PMID 35843392). |
| C-11 | supported | F cells are 100% of peripheral blood at P0 in the Townes mouse model (abstract). |
| C-12 | insufficient | γ-globin RNA values under HU in the mouse model are not quantified; the paper reports only the lack of augmentation (pilot gap P-004). |
| C-13 | supported | γ-globin RNA enriched ~100-fold in F vs A (qRT-PCR; Blood 2020; PMC7256358, Figure 1B). |
| C-14 | supported | γ-globin = ~30% of total globin transcripts in F cells (ddRT-PCR; Blood 2020; PMC7256358). |
| C-15 | supported | γG-globin protein concordant with RNA in F vs A (western blot; Blood 2020; PMC7256358, Figure 1C). |
| C-16 | insufficient | RNA-seq data are globin-RNA depleted; quantitative γ-globin values from RNA-seq are not in the pilot (gap; spec seed: "the RNA-seq protocol depleted globin RNA"). |
| C-17 | supported | F/A matched by CD71, CD235 and forward scatter (Blood 2020; PMC7256358, Methods). |
| C-18 | supported | F cells carry ~30% of total globin as γ-globin at day 7 (ddRT-PCR; Blood 2020; PMC7256358). |
| C-19 | supported | 6 patients: HbF/(F+S) 20.4–41.3% at most recent follow-up (NEJM 384(3):205–215; PMID 33283990). |
| C-20 | supported | F-cells 58.9–93.6% of untransfused red cells (NEJM 384(3):205–215; PMID 33283990). |
| C-21 | supported | HbF per F-cell 9.0–18.6 pg (NEJM 384(3):205–215; PMID 33283990). |
| C-22 | supported | Clinical manifestations reduced or absent during follow-up (NEJM 384(3):205–215; PMID 33283990). |
| C-23 | supported | BCH-BB694 pilot enrolled 6 patients (ClinicalTrials.gov NCT03282656; NEJM 384(3):205–215; PMID 33283990). |
| C-24 | insufficient | No F-cell durability data beyond the scored follow-up window (NEJM 384(3):205–215; PMID 33283990). |
| C-25 | supported | Direct per-cell HbF quantification: 4 pg/RBC protective threshold; VOC incidence decreased at the threshold of 4 pg (Am J Hematol 95(11):1235–1245; PMID 32681733). |
| C-26 | supported | Significant decrease in the RBC population containing less than 2 pg of HbF/RBC during HU treatment (Am J Hematol 95(11):1235–1245; PMID 32681733). |

## Review process

- Independent reviewer: recorded reference support and rationale per case (the table above).
- Reconciliation: internal pass with the builder — no disagreements; all rationales agree with the pilot evidence records in `data/pilot/` and `research/pilot-findings.md`.
- Unresolved: none — all 26 cases resolved; unresolved cohorts would be excluded from the scored holdout (none to exclude; G1–G5 are all resolved).
- Per the user's plan: with a single reviewer, the scored benchmark publication is deferred; the reference labels are marked "preliminary".
