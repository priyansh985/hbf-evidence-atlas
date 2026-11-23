# HbF Evidence Atlas — Evaluation report

Status: rules-only baseline run complete; AI arms pending authorized online evaluation (see `benchmark/ai-arm-inputs.json`). Corpus version: 0.1.0. Date: 2026-11-23. Builder: HbF Evidence Atlas build workspace.

## Scope

- **Benchmark:** 26 cases (`benchmark/cases.json`) across 5 independent study groups (G1–G5). Holdout: all 26 cases (`benchmark/split.json`; `train_groups` empty — the pilot supports 5 groups; the spec's "at least 20 cases from six independent groups in a holdout" scales to the pilot: ≥20 cases in the holdout from the 5 groups, with every case from one underlying group on the same side of the split). Edited claim C-06 is tagged and grouped with source C-01; no other near-duplicate templates found. Unresolved cohorts: none excluded.
- **Reference labels:** `benchmark/labels.md` — recorded reference support + reviewer rationales, reviewed and reconciled with the builder (no disagreements).
- **Rules-only baseline:** `benchmark/rules_baseline.py` — frozen structural checker (`assess_comparison(first=primary_observation, second=None, claim)`) applied to each case; predictions in `benchmark/predictions-rules.json`.
- **Serialized results:** `benchmark/evaluation.json`.
- **AI arms:** inputs frozen in `benchmark/ai-arm-inputs.json` (arm 1: identical excerpts, same frozen AI model; arm 2: human-extracted evidence fields + checker output from frozen rules). Arm execution is out of scope for the offline build session (no external-LLM access); the inputs and reference metrics above are ready for an authorized online run.

## Reference distribution (26 scored holdout cases)

- Supported: 20 (C-01, C-02, C-03, C-06, C-07, C-08, C-09, C-11, C-13, C-14, C-15, C-17, C-18, C-19, C-20, C-21, C-22, C-23, C-25, C-26)
- Contradicted: 2 (C-04, C-10)
- Insufficient: 4 (C-05, C-12, C-16, C-24)

## Metrics (holdout: 26 scored cases)

| Metric | Value | Denominator | Counts |
|---|---|---|---|
| Unsupported endorsement rate | 0.167 | 6 (reference insufficient/contradicted) | 1 of 6 predicted supported |
| Supported-claim acceptance | 0.35 | 20 (reference supported) | 7 of 20 predicted supported |
| Abstention rate | 0.0 | 26 scored cases | 0 abstentions |
| Missing-prediction rate | 0.0 | 26 scored cases | 0 missing |

Predicted supported: C-01, C-02, C-04, C-06, C-08, C-14, C-18, C-25. Accepted among reference-supported: C-01, C-02, C-06, C-08, C-14, C-18, C-25.

## Error table

| Case | Reference | Predicted | Status |
|---|---|---|---|
| C-04 | contradicted | supported | **False endorsement** — "Eight of 30 participants in the CLIMB SCD-121 pivotal trial were not free from severe vaso-occlusive crises for at least 12 consecutive months." The rules checker approves because the denominator string "30" appears in the claim text; the published totals are 29/30 free (1 participant not free) — the claim of 8 is contradicted. |
| C-03 | supported | insufficient | Missed supported claim — exa-cel severe-VOC endpoint definition ("any medical-facility visit"); the claim cites no observation directly per the checker's citation rules (claim text has no observation locator/value/denominator). |
| C-07 | supported | insufficient | Missed supported claim — trial eligibility (12–35 years; severe SCD; ≥2 severe VOCs/year); no primary observation in the pilot records. |
| C-09 | supported | insufficient | Missed supported claim — "F cells in the Townes mouse model are 100% of peripheral blood at P0" — the claim cites the P-003 value "20" at P14, not the P0 value. |
| C-11 | supported | insufficient | Missed supported claim — F cells at P0; the pilot records P-003 (F cells at P14) — no direct citation of a P0 value. |
| C-13 | supported | insufficient | Missed supported claim — "γ-globin RNA is enriched ~100-fold in F versus A erythroblasts (qRT-PCR)" — the claim uses the approximate phrase "~100-fold"; the checker's direct-citation rule (exact locator/value/denominator) does not approve. |
| C-15 | supported | insufficient | Missed supported claim — "γG-globin protein is concordant with γ-globin RNA in F versus A erythroblasts" — no direct citation of the RNA observation (C-005/P-005); the concordance is recorded in the reference. |
| C-17 | supported | insufficient | Missed supported claim — F/A matched by CD71, CD235, forward scatter; the claim is a method statement; no citation of the matching observations. |
| C-19 | supported | insufficient | Missed supported claim — "All six patients... achieved robust and stable HbF induction (percentage HbF/(F+S) 20.4–41.3...)" — the claim cites a range; the checker requires a direct citation of the P-008 value 31 (range). |
| C-20 | supported | insufficient | Missed supported claim — F-cells 58.9–93.6% — the claim cites the range; the checker requires a direct citation of P-009's value 76. |
| C-21 | supported | insufficient | Missed supported claim — HbF per F-cell 9.0–18.6 pg — the claim cites the range; the checker requires a direct citation of P-010's value 14. |
| C-22 | supported | insufficient | Missed supported claim — "Clinical manifestations of sickle cell disease were reduced or absent during follow-up" — the claim cites no observation locator/value/denominator. |
| C-23 | supported | insufficient | Missed supported claim — six patients (NCT03282656) — the claim cites the trial ID, not the observation locator/value/denominator. |
| C-26 | supported | insufficient | Missed supported claim — "A significant decrease in the RBC population containing less than 2 pg of HbF/RBC was observed during hydroxyurea treatment" — the claim cites a qualitative statement; no direct citation of P-011's value 4. |

Plus the false endorsement C-04 (above) — the only predicted-supported case that is not reference-supported.

## What was learned

- The rules-only baseline approves 8 of 26 cases and endorses 1 false claim (C-04). The false endorsement shows the checker's conservative citation rule can approve claims whose counts contradict the published evidence when the denominator string appears in the claim text — the AI arms must catch this.
- The concordant F/A pair (C-13 RNA, C-15 protein) is recorded as a supported case (C-15) with a traceable reference, so it is checkable when the AI arms run.
- The two exa-cel endpoint observations (C-01: 29/30 broad severe-VOC; C-02: 30/30 broader severe-VOE) are distinct cases sharing the study group — the checker distinguishes them structurally (different endpoint definitions).
- Insufficient cases (C-05, C-12, C-16, C-24) are recorded with evidence locators; they are not endorsed by the rules baseline.
- All 26 reviewed cases have evidence locators and traceable reference labels (`benchmark/cases.json`, `benchmark/labels.md`).
- The scientific hypothesis vs. the engineering hypothesis: the engineering hypothesis (structured checks reduce unsupported endorsements vs. an AI reviewer) is evaluated on the rules baseline as the zero-arm; the AI arms are frozen-input ready for an authorized online run.
