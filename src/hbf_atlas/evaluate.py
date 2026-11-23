"""Benchmark evaluation: per-case predictions over holdout cases.

The benchmark splits corpus cases into holdout and train groups via a
predeclared :class:`SplitManifest`. Each holdout case carries a reference
support decision from the reviewed evidence (:class:`Case`); a model
prediction per case is collected as :class:`Prediction` and scored with
:func:`evaluate` into an :class:`Evaluation`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hbf_atlas.models import SupportDecision


@dataclass
class SplitManifest:
    """Group IDs reserved for the holdout vs. training split."""

    holdout_groups: list[str] = field(default_factory=list)
    train_groups: list[str] = field(default_factory=list)

    def check_overlap(self) -> list[str]:
        """Sorted set of group IDs in both holdout and train; empty when disjoint."""
        return sorted(set(self.holdout_groups) & set(self.train_groups))


@dataclass
class Case:
    """One benchmark case with its reference support decision."""

    case_id: str
    group_id: str
    reference: SupportDecision


@dataclass
class Prediction:
    """A model's prediction for a case.

    `predicted` is None or `abstained` marks a case the model declined to
    score: an explicit abstention or a record without a usable decision.
    """

    case_id: str
    predicted: SupportDecision | None = None
    abstained: bool = False


@dataclass
class Evaluation:
    """Aggregate result of evaluating predictions on holdout cases."""

    holdout_group_ids: list[str]
    total_cases: int
    scored_cases: int
    metrics: dict[str, float | None]
    per_case: list[dict]
    missing_predictions: list[str]
    abstentions: int


def evaluate(
    cases: list[Case], predictions: list[Prediction], split: SplitManifest
) -> Evaluation:
    """Score predictions on the holdout cases and aggregate the metrics.

    Rejects a split with group overlap between holdout and train and
    duplicate predictions (same case_id twice). Holdout cases are sorted by
    case_id; per-case status is "scored" (prediction exists, not abstained,
    predicted is not None), "abstained" (prediction record exists but
    carries no usable decision), or "missing" (no prediction record).
    """
    overlap = split.check_overlap()
    if overlap:
        raise ValueError(f"holdout/train group overlap: {overlap}")

    seen: set[str] = set()
    for prediction in predictions:
        if prediction.case_id in seen:
            raise ValueError(
                f"duplicate prediction for case_id {prediction.case_id!r}"
            )
        seen.add(prediction.case_id)
    predictions_by_case = {p.case_id: p for p in predictions}

    holdout_groups = set(split.holdout_groups)
    holdout = sorted(
        (case for case in cases if case.group_id in holdout_groups),
        key=lambda case: case.case_id,
    )

    unsupported_denominator = 0  # scored, reference in {INSUFFICIENT, CONTRADICTED}
    unsupported_numerator = 0  # ... and predicted == SUPPORTED
    acceptance_denominator = 0  # scored, reference == SUPPORTED
    acceptance_numerator = 0  # ... and predicted == SUPPORTED
    per_case: list[dict] = []
    missing_predictions: list[str] = []
    scored_cases = 0
    abstentions = 0

    for case in holdout:
        prediction = predictions_by_case.get(case.case_id)
        if prediction is None:
            status = "missing"
            predicted = None
            abstained = False
            missing_predictions.append(case.case_id)
        else:
            scored_cases += 1
            predicted = prediction.predicted
            abstained = prediction.abstained or predicted is None
            status = "abstained" if abstained else "scored"
            if abstained:
                abstentions += 1
            else:
                if case.reference in (
                    SupportDecision.INSUFFICIENT,
                    SupportDecision.CONTRADICTED,
                ):
                    unsupported_denominator += 1
                    if predicted == SupportDecision.SUPPORTED:
                        unsupported_numerator += 1
                if case.reference == SupportDecision.SUPPORTED:
                    acceptance_denominator += 1
                    if predicted == SupportDecision.SUPPORTED:
                        acceptance_numerator += 1
        per_case.append(
            {
                "case_id": case.case_id,
                "group_id": case.group_id,
                "reference": case.reference,
                "predicted": predicted,
                "abstained": abstained,
                "has_prediction": prediction is not None,
                "status": status,
            }
        )

    metrics = {
        "unsupported_endorsement_rate": (
            unsupported_numerator / unsupported_denominator
            if unsupported_denominator
            else None
        ),
        "supported_claim_acceptance": (
            acceptance_numerator / acceptance_denominator
            if acceptance_denominator
            else None
        ),
        "abstention_rate": abstentions / scored_cases if scored_cases else None,
        "missing_prediction_rate": (
            len(missing_predictions) / scored_cases if scored_cases else None
        ),
    }
    return Evaluation(
        holdout_group_ids=sorted({case.group_id for case in holdout}),
        total_cases=len(holdout),
        scored_cases=scored_cases,
        metrics=metrics,
        per_case=per_case,
        missing_predictions=missing_predictions,
        abstentions=abstentions,
    )
