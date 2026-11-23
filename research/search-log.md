# HbF Evidence Atlas — pilot search log

Status: open. Date of search: 2026-11-23. Builder: HbF Evidence Atlas build workspace.

## Pilot query (from the design spec, 2026-11-22-hbf-evidence-atlas-design.md)

Database string (Europe PMC and PubMed; ESearch/EFetch):
`("sickle cell" OR "sickle cell disease") AND ("fetal hemoglobin" OR "fetal haemoglobin" OR HbF OR "F-cell" OR "gamma globin") AND (BCL11A OR hydroxyurea OR exagamglogene OR "exa-cel")`

- Europe PMC hit count: 986 (export retained: `ai-science-lab/outputs/europepmc-scd-search.json`, captured earlier by the lab; same query).
- Date: 2026-11-23. Hit count recorded: 986.
- Access decisions: open access where noted; several entries are conference/press summaries without abstracts — recorded as "unavailable for extraction" rather than excluded.
- Deduplication: by DOI/PMID across databases.
- Study groups tracked in `research/screening.csv`.

## Focused searches (for the two exa-cel endpoint observations and the four seed rows)

| # | Purpose | Source ID | URL |
|---|---|---|---|
| 1 | Pivotal exa-cel trial (29/30) | PMID 38661449 | https://pubmed.ncbi.nlm.nih.gov/38661449/ |
| 2 | Endpoint reanalysis (30/30) | Advances in Therapy 42(5):2490–2499, 2025 (Frangoul et al.; doi 10.1007/s12325-025-03162-2; PMID 40146367 via Europe PMC esearch) | https://doi.org/10.1007/s12325-025-03162-2 |
| 3 | Hydroxyurea mouse model (γ-globin, F cells) | PMID 35843392 | https://pubmed.ncbi.nlm.nih.gov/35843392/ |
| 4 | F- and A-erythroblast comparison | PMID 32268371 (PMC7256358) | https://pubmed.ncbi.nlm.nih.gov/32268371/ |
| 5 | BCL11A silencing pilot (HbF%, F-cells, HbF/F-cell) | PMID 33283990 | https://pubmed.ncbi.nlm.nih.gov/33283990/ |
| 6 | Individual RBC HbF quantification (per-cell threshold) | PMID 32681733 | https://pubmed.ncbi.nlm.nih.gov/32681733/ |

- The four seed rows from the protocol were opened and verified (article versions and figure/table locations): hydroxyurea mouse-model study (PMID 35843392), F- and A-erythroblast study (PMC7256358), exa-cel pivotal trial (PMID 38661449) + endpoint reanalysis (doi 10.1007/s12325-025-03162-2), quantification of HbF in individual red cells + BCL11A silencing pilot (PMID 33283990).
- All six sources are public (permission "observed"); the atlas references originals by locator (spec: "Reference third-party text and figures by locator unless rights permit redistribution").
- Data access: PubMed pages blocked web fetches (cookie requirement) — Europe PMC abstracts and the publisher page used instead.
