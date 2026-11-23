"""Phase 4: rules-only baseline predictions + evaluation run (frozen rules).

The rules-only baseline: for each benchmark case, run the frozen structural
checker (`assess_comparison(first=primary_observation, second=None, claim)`)
and record the assessment support as the predicted support. Missing
predictions are recorded separately from explicit abstentions (none here).

Writes:
  - benchmark/predictions-rules.json — the rules-only baseline predictions
  - benchmark/evaluation.json        — the serialized Evaluation
  - benchmark/ai-arm-inputs.json     — frozen inputs for the AI arms (pending
                                       authorized online evaluation)
"""

import dataclasses
import json
from pathlib import Path

from hbf_atlas.compare import assess_comparison
from hbf_atlas.evaluate import Case, Prediction, SplitManifest, evaluate
from hbf_atlas.io import load_corpus
from hbf_atlas.models import Claim, SupportDecision

ROOT = Path("F:/New folder (4)/Scientific_Projects/hbf-evidence-atlas")


def _jsonify(obj):
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _jsonify(v) for k, v in vars(obj).items()}
    if isinstance(obj, SupportDecision):
        return obj.value
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    return obj


def main() -> int:
    corpus = load_corpus(ROOT / "data" / "corpus")
    obs_by_id = {o.obs_id: o for o in corpus.observations}

    cases = json.loads((ROOT / "benchmark" / "cases.json").read_text(encoding="utf-8"))
    cases.sort(key=lambda c: c["case_id"])

    eval_cases: list[Case] = []
    predictions: list[Prediction] = []
    checker_outputs: list[dict] = []
    for rec in cases:
        eval_cases.append(
            Case(case_id=rec["case_id"], group_id=rec["group_id"],
                 reference=SupportDecision(rec["reference_support"]))
        )
        claim = Claim(claim_id=rec["claim_id"], text=rec["claim_text"])
        predicted = SupportDecision.INSUFFICIENT
        checker = {"case_id": rec["case_id"], "support": "insufficient",
                   "rationale": "no primary observation for the rules checker",
                   "observation_ids": []}
        if rec["primary_observation_id"]:
            primary = obs_by_id.get(rec["primary_observation_id"])
            if primary is not None:
                assessment = assess_comparison(primary, None, claim)
                predicted = assessment.support
                checker = {"case_id": rec["case_id"], "support": predicted.value,
                           "rationale": assessment.rationale,
                           "observation_ids": assessment.observation_ids}
        predictions.append(Prediction(case_id=rec["case_id"], predicted=predicted, abstained=False))
        checker_outputs.append(checker)

    groups = sorted({c["group_id"] for c in cases})
    split = SplitManifest(holdout_groups=tuple(groups), train_groups=())
    evaluation = evaluate(eval_cases, predictions, split)

    pred_rows = [
        {"case_id": p.case_id, "predicted": p.predicted.value if p.predicted else None,
         "abstained": p.abstained}
        for p in predictions
    ]
    (ROOT / "benchmark" / "predictions-rules.json").write_text(
        json.dumps(pred_rows, indent=2) + "\n", encoding="utf-8")

    eval_dict = _jsonify(evaluation)
    eval_dict["holdout_group_ids"] = list(split.holdout_groups)
    (ROOT / "benchmark" / "evaluation.json").write_text(
        json.dumps(eval_dict, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    arm_inputs = {
        "status": "frozen — pending authorized online evaluation",
        "data_version": "0.1.0",
        "holdout_groups": groups,
        "arm_1": {
            "name": "AI arm 1 — identical excerpts, same frozen AI model",
            "model": "<frozen AI model ID — to be authorized online>",
            "prompt": ("You are a reviewer checking claim support in sickle cell disease. "
                       "For each case, decide the claim support from the excerpts: reply with the "
                       "support status (supported / contradicted / insufficient) and a short rationale."),
            "excerpts": [{"case_id": c["case_id"], "claim_text": c["claim_text"],
                          "evidence_locators": c["evidence_locators"]} for c in cases],
        },
        "arm_2": {
            "name": "AI arm 2 — human-extracted evidence fields + checker output from frozen rules",
            "model": "<same frozen AI model — pending authorization>",
            "prompt": ("You are a reviewer checking claim support in sickle cell disease. Each case includes "
                       "the claim text, human-extracted evidence fields, and the checker output from frozen rules. "
                       "Decide the claim support; reply with the status (supported / contradicted / insufficient) "
                       "and a short rationale."),
            "excerpts": [
                {"case_id": c["case_id"], "claim_text": c["claim_text"],
                 "evidence_locators": c["evidence_locators"],
                 "evidence_fields": _jsonify(obs_by_id[c["primary_observation_id"]]) if c["primary_observation_id"] else None}
                for c in cases
            ],
            "checker_outputs": checker_outputs,
        },
    }
    (ROOT / "benchmark" / "ai-arm-inputs.json").write_text(
        json.dumps(arm_inputs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("cases:", len(cases), "groups:", len(groups))
    print("metrics:", evaluation.metrics)
    print("per_case:")
    for pc in evaluation.per_case:
        print(" ", pc["case_id"], pc["reference"].value, "->", pc["predicted"], pc["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
