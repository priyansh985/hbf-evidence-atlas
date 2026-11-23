"""Evaluation tests: split overlap and leakage, per-case scoring, aggregate metrics."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from hbf_atlas.evaluate import (
    Case,
    Evaluation,
    Prediction,
    SplitManifest,
    evaluate,
)
from hbf_atlas.models import SupportDecision


class SplitManifestTests(unittest.TestCase):
    def test_overlap_empty_when_disjoint(self):
        split = SplitManifest(holdout_groups=["g1", "g2"], train_groups=["g3"])
        self.assertEqual(split.check_overlap(), [])

    def test_overlap_sorted_when_intersecting(self):
        split = SplitManifest(
            holdout_groups=["g2", "g1", "g3"], train_groups=["g1", "g2", "g4"]
        )
        self.assertEqual(split.check_overlap(), ["g1", "g2"])


class EvaluateTests(unittest.TestCase):
    def _split(self, holdout):
        return SplitManifest(holdout_groups=holdout, train_groups=[])

    def test_duplicate_predictions_rejected(self):
        split = self._split(["g1"])
        cases = [Case("c1", "g1", SupportDecision.SUPPORTED)]
        predictions = [
            Prediction("c1", predicted=SupportDecision.SUPPORTED),
            Prediction("c1", predicted=SupportDecision.CONTRADICTED),
        ]
        with self.assertRaises(ValueError):
            evaluate(cases, predictions, split)

    def test_group_overlap_rejected(self):
        split = SplitManifest(holdout_groups=["g1"], train_groups=["g1"])
        self.assertTrue(split.check_overlap())
        with self.assertRaises(ValueError):
            evaluate([Case("c1", "g1", SupportDecision.SUPPORTED)], [], split)

    def test_missing_predictions_recorded(self):
        split = self._split(["g1"])
        cases = [Case("c1", "g1", SupportDecision.SUPPORTED)]
        evaluation = evaluate(cases, [], split)
        self.assertEqual(evaluation.missing_predictions, ["c1"])

    def test_unsupported_endorsement_rate(self):
        split = self._split(["g1"])
        cases = [
            Case("c1", "g1", SupportDecision.INSUFFICIENT),
            Case("c2", "g1", SupportDecision.CONTRADICTED),
            Case("c3", "g1", SupportDecision.INSUFFICIENT),
        ]
        predictions = [
            Prediction("c1", predicted=SupportDecision.SUPPORTED),
            Prediction("c2", predicted=SupportDecision.SUPPORTED),
            Prediction("c3", predicted=SupportDecision.INSUFFICIENT),
        ]
        evaluation = evaluate(cases, predictions, split)
        self.assertAlmostEqual(
            evaluation.metrics["unsupported_endorsement_rate"], 2 / 3
        )

    def test_supported_claim_acceptance(self):
        split = self._split(["g1"])
        cases = [
            Case("c1", "g1", SupportDecision.SUPPORTED),
            Case("c2", "g1", SupportDecision.SUPPORTED),
        ]
        predictions = [
            Prediction("c1", predicted=SupportDecision.SUPPORTED),
            Prediction("c2", predicted=SupportDecision.INSUFFICIENT),
        ]
        evaluation = evaluate(cases, predictions, split)
        self.assertAlmostEqual(
            evaluation.metrics["supported_claim_acceptance"], 0.5
        )

    def test_abstention_rate(self):
        split = self._split(["g1"])
        cases = [Case("c1", "g1", SupportDecision.SUPPORTED)]
        predictions = [Prediction("c1", abstained=True)]
        evaluation = evaluate(cases, predictions, split)
        self.assertEqual(evaluation.abstentions, 1)
        self.assertAlmostEqual(evaluation.metrics["abstention_rate"], 1.0)

    def test_reference_supported_excluded_from_unsupported(self):
        split = self._split(["g1"])
        cases = [
            Case("c1", "g1", SupportDecision.SUPPORTED),
            Case("c2", "g1", SupportDecision.SUPPORTED),
        ]
        predictions = [
            Prediction("c1", predicted=SupportDecision.SUPPORTED),
            Prediction("c2", predicted=SupportDecision.SUPPORTED),
        ]
        evaluation = evaluate(cases, predictions, split)
        self.assertIsNone(evaluation.metrics["unsupported_endorsement_rate"])


if __name__ == "__main__":
    unittest.main()
