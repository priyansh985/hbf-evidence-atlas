"""Loading and validation of atlas corpus records.

The corpus directory holds one JSON list per record type (``sources.json``,
``observations.json``, ``claims.json``, ``reviews.json``) plus a
``data_version.txt`` single-line version string.
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

from hbf_atlas.models import (
    Claim,
    Context,
    Corpus,
    Direction,
    EvidenceState,
    Issue,
    Observation,
    Review,
    Severity,
    Source,
)

_MISSING_VERSION = "unset"


def load_corpus(directory: Path) -> Corpus:
    """Read the corpus files in ``directory`` and return them as a Corpus.

    All lists are sorted by record ID for deterministic ordering. Raises
    ``FileNotFoundError`` for missing files and ``ValueError`` for malformed
    files or records.
    """
    directory = Path(directory)
    sources = [_load_source(obj) for obj in _read_json_list(directory / "sources.json")]
    observations = [_load_observation(obj) for obj in _read_json_list(directory / "observations.json")]
    claims = [_load_claim(obj) for obj in _read_json_list(directory / "claims.json")]
    reviews = [_load_review(obj) for obj in _read_json_list(directory / "reviews.json")]
    data_version = _read_version(directory / "data_version.txt")
    corpus = Corpus(
        data_version=data_version,
        sources=sources,
        observations=observations,
        claims=claims,
        reviews=reviews,
    )
    corpus.sources.sort(key=lambda source: source.source_id)
    corpus.observations.sort(key=lambda obs: obs.obs_id)
    corpus.claims.sort(key=lambda claim: claim.claim_id)
    corpus.reviews.sort(key=lambda review: review.review_id)
    return corpus


def validate_corpus(corpus: Corpus) -> list[Issue]:
    """Return validation issues sorted by (record_id, field)."""
    issues: list[Issue] = []
    source_ids = {source.source_id for source in corpus.sources}

    seen: set[str] = set()
    for source in corpus.sources:
        if source.source_id in seen:
            issues.append(
                Issue(
                    Severity.ERROR,
                    source.source_id,
                    "source_id",
                    f"duplicate source ID {source.source_id!r}",
                )
            )
        seen.add(source.source_id)

    seen = set()
    for obs in corpus.observations:
        if obs.obs_id in seen:
            issues.append(
                Issue(
                    Severity.ERROR,
                    obs.obs_id,
                    "obs_id",
                    f"duplicate observation ID {obs.obs_id!r}",
                )
            )
        seen.add(obs.obs_id)
        if obs.source_id not in source_ids:
            issues.append(
                Issue(
                    Severity.ERROR,
                    obs.obs_id,
                    "source_id",
                    f"observation {obs.obs_id!r} links to unknown source {obs.source_id!r}",
                )
            )
        issues.extend(_observation_issues(obs))

    seen = set()
    for claim in corpus.claims:
        if claim.claim_id in seen:
            issues.append(
                Issue(
                    Severity.ERROR,
                    claim.claim_id,
                    "claim_id",
                    f"duplicate claim ID {claim.claim_id!r}",
                )
            )
        seen.add(claim.claim_id)

    seen = set()
    for review in corpus.reviews:
        if review.review_id in seen:
            issues.append(
                Issue(
                    Severity.ERROR,
                    review.review_id,
                    "review_id",
                    f"duplicate review ID {review.review_id!r}",
                )
            )
        seen.add(review.review_id)

    return sorted(issues, key=lambda issue: (issue.record_id, issue.field))


def _observation_issues(obs: Observation) -> list[Issue]:
    """Return issues for one observation's denominator and observed value."""
    issues: list[Issue] = []
    denominator = obs.denominator
    if isinstance(denominator, bool):
        issues.append(
            Issue(
                Severity.ERROR,
                obs.obs_id,
                "denominator",
                f"invalid denominator {denominator!r}: expected a positive integer or an evidence state",
            )
        )
    elif isinstance(denominator, int):
        if denominator < 1:
            issues.append(
                Issue(
                    Severity.ERROR,
                    obs.obs_id,
                    "denominator",
                    f"invalid denominator {denominator}: must be a positive integer",
                )
            )
    elif isinstance(denominator, EvidenceState):
        if obs.value is not None:
            issues.append(
                Issue(
                    Severity.ERROR,
                    obs.obs_id,
                    "denominator",
                    f"denominator is evidence state {denominator.value!r} while a value is set",
                )
            )
    # An observation whose value is observed must carry a unit.
    if obs.value is not None and obs.unit is None:
        issues.append(
            Issue(
                Severity.ERROR,
                obs.obs_id,
                "unit",
                f"observation {obs.obs_id!r} is observed but has no unit",
            )
        )
    return issues


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"corpus file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed JSON in {path}: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    for index, entry in enumerate(data):
        if not isinstance(entry, dict):
            raise ValueError(f"{path} entry {index} is not a JSON object")
    return data


def _read_version(path: Path) -> str:
    if not path.is_file():
        return _MISSING_VERSION
    text = path.read_text(encoding="utf-8").strip()
    return text or _MISSING_VERSION


def _require(obj: dict[str, Any], key: str) -> Any:
    if obj.get(key) is None:
        raise ValueError(f"missing required field {key!r}")
    return obj[key]


def _optional_enum(value: Any, enum_cls: type[Enum], default: Any = None) -> Any:
    if value is None:
        return default
    return enum_cls(value)


def _load_source(obj: dict[str, Any]) -> Source:
    return Source(
        source_id=_require(obj, "source_id"),
        version=_require(obj, "version"),
        url=_require(obj, "url"),
        figure_table=obj.get("figure_table"),
        permission_status=_optional_enum(obj.get("permission_status"), EvidenceState, EvidenceState.OBSERVED),
    )


def _load_context(obj: dict[str, Any]) -> Context:
    return Context(
        study_group_id=_require(obj, "study_group_id"),
        species=_require(obj, "species"),
        model=obj.get("model"),
        cohort=obj.get("cohort"),
        intervention=obj.get("intervention"),
        comparator=obj.get("comparator"),
        stage=obj.get("stage"),
        genotype=obj.get("genotype"),
        transfusion_context=obj.get("transfusion_context"),
        sample_linkage=obj.get("sample_linkage"),
    )


def _load_denominator(value: Any) -> int | EvidenceState | None:
    if value is None:
        return None
    if isinstance(value, EvidenceState):
        return value
    if isinstance(value, bool):
        raise ValueError(f"denominator must be a positive integer or an evidence state, got {value!r}")
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        return EvidenceState(value)
    raise ValueError(f"denominator must be a positive integer or an evidence state, got {value!r}")


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid numeric value: {value!r}") from exc


def _load_observation(obj: dict[str, Any]) -> Observation:
    return Observation(
        obs_id=_require(obj, "obs_id"),
        source_id=_require(obj, "source_id"),
        context=_load_context(_require(obj, "context")),
        readout_kind=_require(obj, "readout_kind"),
        assay=obj.get("assay"),
        value=_as_float(obj.get("value")),
        unit=obj.get("unit"),
        denominator=_load_denominator(obj.get("denominator")),
        time_point=obj.get("time_point"),
        sample_linkage=obj.get("sample_linkage"),
        uncertainty=_as_float(obj.get("uncertainty")),
        direction=_optional_enum(obj.get("direction"), Direction),
        evidence_locator=obj.get("evidence_locator"),
    )


def _load_claim(obj: dict[str, Any]) -> Claim:
    return Claim(
        claim_id=_require(obj, "claim_id"),
        text=_require(obj, "text"),
        claim_type=obj.get("claim_type"),
    )


def _load_review(obj: dict[str, Any]) -> Review:
    reviewer_ids = obj.get("reviewer_ids")
    if reviewer_ids is not None and not isinstance(reviewer_ids, list):
        raise ValueError("reviewer_ids must be a list of strings")
    return Review(
        review_id=_require(obj, "review_id"),
        curator_id=_require(obj, "curator_id"),
        reviewer_ids=list(reviewer_ids) if reviewer_ids is not None else [],
        adjudication_state=obj.get("adjudication_state"),
        corpus_version=obj.get("corpus_version"),
        reason_for_revision=obj.get("reason_for_revision"),
    )
