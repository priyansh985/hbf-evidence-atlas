"""Deterministic static-report export for the HbF evidence atlas.

``export_corpus`` writes the local preview of the atlas:

- ``index.html`` — the static shell from ``static/index.html`` with the
  full export embedded as ``window.ATLAS_DATA``.  The dump is escaped so
  ``&``, ``<`` and ``>`` become ``\\u0026``, ``\\u003c`` and ``\\u003e``; the
  report therefore runs fully offline and imported text cannot break out
  of the script context.
- ``data.json`` — the full export (``sort_keys=True, indent=2`` plus a
  trailing newline).
- ``vendor/`` — a copy of ``static/vendor/``.
- ``atlas.js`` and ``style.css`` — copies of the static assets.

Ordering is stable everywhere and no timestamps are emitted, so two
exports of the same corpus are byte-identical.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from hbf_atlas.compare import assess_comparison
from hbf_atlas.models import (
    Assessment,
    Claim,
    Context,
    Corpus,
    EvidenceState,
    Observation,
    Review,
    Source,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"


def _source_dict(source: Source) -> dict:
    return {
        "source_id": source.source_id,
        "version": source.version,
        "url": source.url,
        "figure_table": source.figure_table,
        "permission_status": source.permission_status.value,
    }


def _context_dict(context: Context) -> dict:
    return {
        "study_group_id": context.study_group_id,
        "species": context.species,
        "model": context.model,
        "cohort": context.cohort,
        "intervention": context.intervention,
        "comparator": context.comparator,
        "stage": context.stage,
        "genotype": context.genotype,
        "transfusion_context": context.transfusion_context,
        "sample_linkage": context.sample_linkage,
    }


def _observation_dict(obs: Observation) -> dict:
    denominator = obs.denominator
    if isinstance(denominator, EvidenceState):
        denominator = denominator.value
    return {
        "obs_id": obs.obs_id,
        "source_id": obs.source_id,
        "context": _context_dict(obs.context),
        "readout_kind": obs.readout_kind,
        "assay": obs.assay,
        "value": obs.value,
        "unit": obs.unit,
        "denominator": denominator,
        "time_point": obs.time_point,
        "sample_linkage": obs.sample_linkage,
        "uncertainty": obs.uncertainty,
        "direction": obs.direction.value if obs.direction is not None else None,
        "evidence_locator": obs.evidence_locator,
    }


def _claim_dict(claim: Claim) -> dict:
    return {
        "claim_id": claim.claim_id,
        "text": claim.text,
        "claim_type": claim.claim_type,
    }


def _assessment_dict(assessment: Assessment) -> dict:
    return {
        "first_id": assessment.first_id,
        "second_id": assessment.second_id,
        "matched_dimensions": list(assessment.matched_dimensions),
        "support": assessment.support.value,
        "direction": assessment.direction.value if assessment.direction is not None else None,
        "rationale": assessment.rationale,
        "observation_ids": list(assessment.observation_ids),
    }


def _review_dict(review: Review) -> dict:
    return {
        "review_id": review.review_id,
        "curator_id": review.curator_id,
        "reviewer_ids": list(review.reviewer_ids),
        "adjudication_state": review.adjudication_state,
        "corpus_version": review.corpus_version,
        "reason_for_revision": review.reason_for_revision,
    }


def build_export(corpus: Corpus) -> dict:
    """Return the deterministic export dictionary for ``corpus``.

    The export contains ``data_version``, full ``sources``, ``observations``,
    ``claims`` and ``reviews`` records, one ``cases`` entry per claim
    (sorted by claim ID, each with one assessment per observation sorted by
    ``first_id``), and flattened ``rows`` (sorted by ``(claim_id, obs_id)``)
    with claim text, the observation, its source and its assessment.
    """
    sources_by_id = {source.source_id: source for source in corpus.sources}
    observations = sorted(corpus.observations, key=lambda obs: obs.obs_id)
    observations_by_id = {obs.obs_id: obs for obs in observations}
    claims = sorted(corpus.claims, key=lambda claim: claim.claim_id)

    cases = []
    rows = []
    for claim in claims:
        assessments = sorted(
            (assess_comparison(obs, None, claim) for obs in observations),
            key=lambda assessment: assessment.first_id,
        )
        cases.append(
            {
                "claim": _claim_dict(claim),
                "assessments": [_assessment_dict(assessment) for assessment in assessments],
            }
        )
        for assessment in assessments:
            obs = observations_by_id[assessment.first_id]
            rows.append(
                {
                    "claim_id": claim.claim_id,
                    "claim_text": claim.text,
                    "claim_type": claim.claim_type,
                    "obs_id": obs.obs_id,
                    "source": _source_dict(sources_by_id[obs.source_id]),
                    "obs": _observation_dict(obs),
                    "assessment": _assessment_dict(assessment),
                }
            )
    rows.sort(key=lambda row: (row["claim_id"], row["obs_id"]))

    return {
        "data_version": corpus.data_version,
        "sources": [_source_dict(source) for source in sorted(corpus.sources, key=lambda s: s.source_id)],
        "observations": [_observation_dict(obs) for obs in observations],
        "claims": [_claim_dict(claim) for claim in claims],
        "reviews": [_review_dict(review) for review in sorted(corpus.reviews, key=lambda r: r.review_id)],
        "cases": cases,
        "rows": rows,
    }


def _escape_script_json(text: str) -> str:
    """Escape ``&``, ``<`` and ``>`` so the dump cannot break out of a script context."""
    return text.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")


def export_corpus(corpus: Corpus, output_dir: Path) -> None:
    """Write the deterministic static atlas report for ``corpus`` to ``output_dir``.

    Creates ``output_dir`` and writes ``index.html``, ``data.json``,
    ``vendor/``, ``atlas.js`` and ``style.css``.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    export = build_export(corpus)

    template = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    embedded = _escape_script_json(json.dumps(export, sort_keys=True))
    (output_dir / "index.html").write_text(template.replace("__ATLAS_DATA__", embedded), encoding="utf-8")

    (output_dir / "data.json").write_text(json.dumps(export, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    vendor_dst = output_dir / "vendor"
    if vendor_dst.exists():
        shutil.rmtree(vendor_dst)
    shutil.copytree(STATIC_DIR / "vendor", vendor_dst)

    for name in ("atlas.js", "style.css"):
        shutil.copy2(STATIC_DIR / name, output_dir / name)
