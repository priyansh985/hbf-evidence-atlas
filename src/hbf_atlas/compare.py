"""Comparison assessment: how a claim is supported by observations.

``assess_comparison`` compares two observations against a claim and returns
a bounded decision: SUPPORTED, CONTRADICTED or INSUFFICIENT, with direction
(CONCORDANT/DISCORDANT) when both observed values agree or disagree.
"""

from __future__ import annotations

from typing import Any

from hbf_atlas.models import (
    Assessment,
    Claim,
    Direction,
    EvidenceState,
    Observation,
    SupportDecision,
)

#: Shared-context dimensions compared by ``assess_comparison``.
DIMENSIONS = (
    "readout_kind",
    "study_group_id",
    "species",
    "model",
    "time_point",
    "sample_linkage",
    "assay",
    "value",
    "denominator",
)

#: Dimensions whose mismatch blocks SUPPORTED when set on both observations.
_BLOCKING_DIMENSIONS = (
    "study_group_id",
    "species",
    "model",
    "time_point",
    "sample_linkage",
    "assay",
    "denominator",
)


def assess_comparison(first: Observation, second: Observation | None, claim: Claim) -> Assessment:
    """Assess how ``claim`` is supported by ``first`` (and ``second`` when given).

    With ``second``: SUPPORTED when the readouts match, the observed values
    agree and the shared dimensions match; CONTRADICTED when the readouts
    match and the observed values disagree; otherwise INSUFFICIENT.
    Without ``second``: INSUFFICIENT unless the claim text directly cites the
    first observation (its evidence locator, its observed value or its
    denominator).
    """
    if second is None:
        return _assess_single(first, claim)
    return _assess_pair(first, second)


def _dim_value(obs: Observation, dim: str) -> Any:
    if dim == "readout_kind":
        return obs.readout_kind
    if dim in ("study_group_id", "species", "model"):
        return getattr(obs.context, dim, None)
    if dim in ("time_point", "sample_linkage"):
        return getattr(obs, dim, None)
    if dim == "assay":
        return obs.assay
    if dim == "value":
        return obs.value
    if dim == "denominator":
        return obs.denominator
    return None


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _dims_match(first: Observation, second: Observation, dim: str) -> bool:
    a = _dim_value(first, dim)
    b = _dim_value(second, dim)
    if a is None or b is None:
        return False
    if dim == "value":
        return a == b and first.unit == second.unit
    if dim == "denominator":
        return _is_int(a) and _is_int(b) and a == b
    return a == b


def _matched_dimensions(first: Observation, second: Observation) -> list[str]:
    return [dim for dim in DIMENSIONS if _dims_match(first, second, dim)]


def _values_agree(first: Observation, second: Observation) -> bool:
    return _dims_match(first, second, "value")


def _values_disagree(first: Observation, second: Observation) -> bool:
    if first.value is None or second.value is None:
        return False
    return not _dims_match(first, second, "value")


def _blocking_dimensions(first: Observation, second: Observation, matched: set[str]) -> list[str]:
    """Shared dimensions that are set on at least one side and not matched."""
    blocking = []
    for dim in _BLOCKING_DIMENSIONS:
        if dim in matched:
            continue
        if _dim_value(first, dim) is not None or _dim_value(second, dim) is not None:
            blocking.append(dim)
    return blocking


def _direction(first: Observation, second: Observation) -> Direction | None:
    if _values_agree(first, second):
        return Direction.CONCORDANT
    if _values_disagree(first, second):
        return Direction.DISCORDANT
    return None


def _directions_conflict(first: Observation, second: Observation) -> bool:
    return (
        first.direction is not None
        and second.direction is not None
        and first.direction != second.direction
    )


def _locator_changed(first: Observation, second: Observation) -> bool:
    return (
        first.evidence_locator is not None
        and second.evidence_locator is not None
        and first.evidence_locator != second.evidence_locator
    )


def _describe_value(obs: Observation) -> str:
    if obs.value is None:
        return "no observed value"
    return f"{obs.value} {obs.unit}".strip()


def _rationale(first: Observation, second: Observation, support: SupportDecision, matched: list[str]) -> str:
    if support is SupportDecision.SUPPORTED:
        return f"Readout kinds match and observed values agree: {_describe_value(first)} vs {_describe_value(second)}."
    if support is SupportDecision.CONTRADICTED:
        return f"Readout kinds match but observed values disagree: {_describe_value(first)} vs {_describe_value(second)}."
    if first.readout_kind != second.readout_kind:
        return f"Readout kinds differ: {first.readout_kind!r} vs {second.readout_kind!r}."
    if first.value is None or second.value is None:
        missing = [obs.obs_id for obs in (first, second) if obs.value is None]
        return f"Values not both observed (missing on {', '.join(missing)}); comparison is insufficient."
    blocking = _blocking_dimensions(first, second, set(matched))
    if blocking:
        return f"Values agree but {', '.join(blocking)} do not match between observations; comparison is insufficient."
    if _directions_conflict(first, second):
        return "Values agree but observation directions conflict; comparison is insufficient."
    return "Comparison is insufficient."


def _assess_pair(first: Observation, second: Observation) -> Assessment:
    matched = _matched_dimensions(first, second)
    direction = _direction(first, second)

    if first.readout_kind != second.readout_kind:
        support = SupportDecision.INSUFFICIENT
    elif _values_disagree(first, second):
        support = SupportDecision.CONTRADICTED
    elif not _values_agree(first, second):
        support = SupportDecision.INSUFFICIENT
    elif (
        _blocking_dimensions(first, second, set(matched))
        or _directions_conflict(first, second)
        or _locator_changed(first, second)
    ):
        support = SupportDecision.INSUFFICIENT
    else:
        support = SupportDecision.SUPPORTED

    return Assessment(
        first_id=first.obs_id,
        second_id=second.obs_id,
        matched_dimensions=matched,
        support=support,
        direction=direction,
        rationale=_rationale(first, second, support, matched),
        observation_ids=[first.obs_id, second.obs_id],
    )


def _assess_single(first: Observation, claim: Claim) -> Assessment:
    anchor = _directly_supported_by(claim, first)
    support = SupportDecision.SUPPORTED if anchor is not None else SupportDecision.INSUFFICIENT
    rationale = (
        f"Claim directly supported: claim text cites {anchor}."
        if anchor is not None
        else "No second observation to compare; claim not directly supported by the single observation."
    )
    return Assessment(
        first_id=first.obs_id,
        second_id=None,
        matched_dimensions=[],
        support=support,
        direction=None,
        rationale=rationale,
        observation_ids=[first.obs_id],
    )


def _directly_supported_by(claim: Claim, obs: Observation) -> str | None:
    """Return the citation if the claim text mentions the observation's locator, value or denominator."""
    text = (claim.text or "").lower()
    if not text:
        return None
    if obs.evidence_locator and obs.evidence_locator.lower() in text:
        return obs.evidence_locator
    for spelling in _value_spellings(obs.value):
        if spelling and spelling in text:
            return f"value {spelling}"
    if _is_int(obs.denominator) and str(obs.denominator) in text:
        return f"denominator {obs.denominator}"
    if isinstance(obs.denominator, EvidenceState) and obs.denominator.value in text:
        return f"denominator state {obs.denominator.value}"
    return None


def _value_spellings(value: float | None) -> tuple[str, ...]:
    if value is None:
        return ()
    spellings = [str(value)]
    try:
        rounded = f"{value:g}"
    except (TypeError, ValueError):
        return tuple(spellings)
    if rounded not in spellings:
        spellings.append(rounded)
    return tuple(spellings)
