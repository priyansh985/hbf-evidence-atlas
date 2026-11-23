# HbF Evidence Atlas research protocol and design

**Status:** Planning handoff, 22 November 2026. This workspace holds the scientific research and design. The implementation belongs in the separate build workspace.

## Research question and audience

When a sickle cell study measures a change in γ-globin RNA, total fetal hemoglobin (HbF), HbF-positive red cells (F-cells), or a clinical outcome, what additional conclusions does that measurement support for the same group and time point? Which conclusions require another assay or a different study design?

The first reader is a researcher screening claims about HbF induction in sickle cell disease. Given a claim and its evidence, the atlas identifies what was measured, what can be compared, and the narrowest missing observation. It cites the figure, table, or supplement that supports the decision. The first release evaluates curated, structured claim cases. Researchers search and filter those cases by topic and context.

**Scientific hypothesis:** Some concordance between adjacent readouts persists within matched groups, yet the extent and direction vary by study context. **Engineering hypothesis:** Structured checks reduce unsupported endorsements compared with an AI reviewer given the same source excerpts. Either hypothesis can fail. The descriptive study remains useful if data are too sparse for the engineering benchmark.

## Scope and prior art

The pilot covers sickle cell disease, BCL11A-related interventions and hydroxyurea. Include human clinical cohorts, human erythroid models, and clearly identified disease-model studies. Use separate strata for model type. Sources must be public reports or authorized public datasets. Use published aggregate values and permitted metadata. The design centers on public secondary analysis and research-use evidence assessment. A few clinically relevant exa-cel examples anchor the endpoint checks. Thalassemia and other HbF modifiers belong in a later protocol revision.

A focused scan located [IthaPhen](https://doi.org/10.1097/HS9.0000000000000922) for genotype–phenotype curation, [SciFact-Open](https://aclanthology.org/2022.findings-emnlp.347/) for claim verification, [biomedical contradiction analysis](https://doi.org/10.1016/j.jbi.2019.103275) for identifying contextual differences, and a [same-cohort SCD endpoint comparison](https://doi.org/10.1007/s12325-025-03162-2). The proposed contribution combines an HbF-specific, figure-level corpus with explicit comparison decisions and a benchmark testing a model's ability to preserve those decisions. Worldwide originality remains unverified. Before a public novelty claim, log focused PubMed, Europe PMC, OpenAlex, GitHub and Zenodo searches and record the closest systems by scope, data and evaluation.

## Review protocol

1. **Find records.** Start with PubMed and Europe PMC, from inception through the recorded search date. Pilot query: `("sickle cell" OR "sickle cell disease") AND ("fetal hemoglobin" OR "fetal haemoglobin" OR HbF OR "F-cell" OR "gamma globin") AND (BCL11A OR hydroxyurea OR exagamglogene OR "exa-cel")`. Translate syntax for each database and save exact strings, filters, dates, hit counts and exports. Search references and citing papers from the seed set. Track open-access filtering explicitly. Use [PRISMA-ScR](https://www.prisma-statement.org/scoping) and [PRISMA-S](https://www.prisma-statement.org/prisma-search) as reporting guides.
2. **Screen sources.** Include primary studies with an eligible context, a defined comparison and a locatable measurement, as well as reanalyses of endpoint definitions. Use reviews for discovery. Preserve single-measurement studies as evidence-gap cases. Log exclusions and deduplicate by DOI/PMID. Link reports sharing a cohort or experimental series under one study-group ID. When overlap is unresolved, keep the reports visible as provisional evidence and exclude them from independent study-group counts and the scored holdout.
3. **Extract evidence.** Capture values, units, denominators, baselines or comparators, assay details and time points before grading the claim. Record whether quantities were reported or defensibly derived, including the formula. Use separate states for unreported values, ambiguous values and values that do not apply. Preserve null and adverse findings.
4. **Review labels.** Use an explicit rubric. A reviewer records source location and rationale. A second reviewer independently labels all evaluation cases and a sample of atlas entries, then reconciles disagreements with an adjudicator or documented consensus. Report pre-consensus agreement and keep a change log. A solo pilot can release a provisional descriptive atlas. Defer scored benchmark publication and the model improvement gate until independent labels are available.

### Evidence and decision model

| Record | Required information |
|---|---|
| Source | Source ID, DOI or accession, version, stable URL, figure/table/panel or section, permission status |
| Context | Study-group ID, species and model, cohort or sample group, intervention as published, comparator, stage or follow-up window, available genotype and transfusion context |
| Observation | Readout kind, assay, reported value and unit, denominator and experimental unit when applicable, uncertainty, direction, evidence locator |
| Comparison | Observation IDs, target claim, match status by dimension, clinical event definition, decision, rationale and missing observation |
| Review | Curator and review IDs, adjudication state, corpus version, reason for revision |

First readouts are γ-globin RNA, total HbF percentage, F-cell percentage, HbF per cell, and freedom from a defined vaso-occlusive event. Preserve full assay or event definitions in addition to normalized names. Same study group alone cannot establish that observations came from the same samples. An unreported pairing, assay threshold, denominator or time window stays unknown.

Label **claim support** separately from **biological direction**. Claim support can be direct support, direct contradiction, or insufficient evidence. Example: RNA alone gives insufficient evidence for a claim about clinical crises. Direction is concordant, discordant, or indeterminate and applies only where there is a defensible matched comparison. A change in event definition is an endpoint mismatch. A statistically inconclusive result is indeterminate unless the study supplies a prespecified equivalence criterion that supports a no-material-change conclusion.

### Verified seed sources

| Seed | First use |
|---|---|
| [Hydroxyurea mouse-model study](https://pubmed.ncbi.nlm.nih.gov/35843392/) | Capture how persistent F-cell elevation and sustained RNA induction diverged in this model. Confirm exact pairing and time windows from the paper before assigning a direction label. |
| [F- and A-erythroblast study](https://pmc.ncbi.nlm.nih.gov/articles/PMC7256358/) | Figure 1 shows concordant qRT-PCR and western blot findings in sorted cells. Evaluate it as an association. Separate RNA-seq and proteomics runs used different days, and the RNA-seq protocol depleted globin RNA. |
| [Exa-cel pivotal trial](https://pubmed.ncbi.nlm.nih.gov/38661449/) and [endpoint reanalysis](https://doi.org/10.1007/s12325-025-03162-2) | Reproduce 29/30 and 30/30 from the published totals under the two event rules. These papers share a study group. |
| [Quantification of HbF in individual red cells](https://doi.org/10.1002/ajh.25937) and [BCL11A silencing pilot](https://pubmed.ncbi.nlm.nih.gov/33283990/) | Distinguish total HbF, the fraction of positive cells, directly measured per-cell HbF and derived quantities. |

## Analysis and decision gates

**Feasibility gate:** Review at least ten traceable comparison or gap records across at least five independent study groups. Require at least four matched cross-readout comparisons from at least three independent groups and at least two genuine mismatch or discordance examples. Record the counts and outstanding uncertainties. If the matched-data threshold falls short, begin with a descriptive methods and evidence-gap map. Reopen protocol scope before widening eligibility.

**Scientific output:** Report which readout pairs were measured together, matched denominators, agreement and disagreement by study group and model type, and unreported measurements. Use published aggregate data to reproduce one result, starting with the 29/30 and 30/30 endpoint example. Summarize within-study directions by pair. Avoid pooling incompatible outcomes. Report how conclusions change when unclear pairings are excluded. Dataset availability, selective reporting, small samples and dependence across reports constrain inference. The pilot thresholds serve feasibility and have no statistical power interpretation.

**Benchmark:** Target 80 reviewed cases across 20 study groups if the pilot supports it. Keep at least 20 cases from six independent groups in a holdout, with every report and edited claim from any one underlying group on the same side of the split. Include positively supported claims and real unsupported, contradictory and ambiguous claims. Any intentionally edited wording is tagged and grouped with its source. Compare the same frozen AI model with identical excerpts in both arms. The second arm also receives human-extracted evidence fields and checker output generated from frozen rules. Keep gold labels and curator rationales in a separate file that neither system sees. This tests assistance given curated inputs. Automatic extraction from unseen papers would need its own evaluation. Run a rules-only baseline. Report unsupported endorsement rate, supported-claim acceptance and indeterminate/abstention frequency, with counts and study-group uncertainty where defensible. Improvement requires fewer unsupported endorsements without sacrificing more than 10 percentage points of supported-claim acceptance. That is an initial product gate. Mark sparse estimates as exploratory.

**Metric definitions:** Unsupported endorsement rate is the fraction of reference-insufficient or reference-contradicted cases that the system calls supported. Report both reference categories separately as well. Supported-claim acceptance uses only reference-supported cases. Record abstentions and execution failures separately. Compare changes case by case, and resample whole study groups for intervals only when the holdout has enough groups to support a useful estimate. Publish raw counts for every reported rate.

## Release and handoff

Deliver a versioned export, search and screening log, citation index, annotation rubric, methods report, and reproducible evaluation instructions. Redistribute original annotations and permitted translations of measurements. Reference third-party text and figures by locator unless rights permit redistribution. User decisions so far are to proceed with planning and build elsewhere. The pilot scope, file formats, thresholds and review sequence are proposed defaults for the build handoff.
