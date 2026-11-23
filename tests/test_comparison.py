"""Comparison tests: matched dimensions and bounded support decisions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from hbf_atlas.compare import assess_comparison
from hbf_atlas.models import Claim, Context, Direction, EvidenceState, Observation, SupportDecision


def make_obs(
    obs_id,
    *,
    readout_kind="gamma-globin-rna",
    value=0.42,
    unit="%",
    study_group_id="grp-A",
    species="Homo sapiens",
    model=None,
    time_point=None,
    sample_linkage=None,
    assay=None,
    denominator=30,
    direction=None,
    evidence_locator="Figure 3",
):
    return Observation(
        obs_id=obs_id,
        source_id="src-1",
        context=Context(study_group_id=study_group_id, species=species, model=model),
        readout_kind=readout_kind,
        assay=assay if assay is not None else {"name": "qRT-PCR", "definition": "gamma-globin mRNA / beta-actyl"},
        value=value,
        unit=unit,
        denominator=denominator,
        time_point=time_point,
        sample_linkage=sample_linkage,
        direction=direction,
        evidence_locator=evidence_locator,
    )


def make_claim(claim_id="claim-1", text="The RNA level increased."):
    return Claim(claim_id=claim_id, text=text)


class TestComparison(unittest.TestCase):
    def test_matched_rna_pair_supported_concordant(self):
        first = make_obs("obs-1")
        second = make_obs("obs-2")
        assessment = assess_comparison(first, second, make_claim())
        self.assertEqual(assessment.support, SupportDecision.SUPPORTED)
        self.assertEqual(assessment.direction, Direction.CONCORDANT)
        self.assertEqual(assessment.first_id, "obs-1")
        self.assertEqual(assessment.second_id, "obs-2")
        self.assertEqual(assessment.observation_ids, ["obs-1", "obs-2"])
        for dimension in ("readout_kind", "study_group_id", "species", "value", "denominator"):
            self.assertIn(dimension, assessment.matched_dimensions)

    def test_different_time_point_insufficient(self):
        first = make_obs("obs-1", time_point="day 14")
        second = make_obs("obs-2", time_point="day 28")
        assessment = assess_comparison(first, second, make_claim())
        self.assertEqual(assessment.support, SupportDecision.INSUFFICIENT)
        self.assertNotIn("time_point", assessment.matched_dimensions)

    def test_mouse_to_human_insufficient(self):
        first = make_obs("obs-1", species="Mus musculus")
        second = make_obs("obs-2", species="Homo sapiens")
        assessment = assess_comparison(first, second, make_claim())
        self.assertEqual(assessment.support, SupportDecision.INSUFFICIENT)
        self.assertNotIn("species", assessment.matched_dimensions)

    def test_different_assay_threshold_insufficient(self):
        first = make_obs("obs-1", assay={"name": "qRT-PCR", "threshold": "3%"})
        second = make_obs("obs-2", assay={"name": "qRT-PCR", "threshold": "5%"})
        assessment = assess_comparison(first, second, make_claim())
        self.assertEqual(assessment.support, SupportDecision.INSUFFICIENT)
        self.assertNotIn("assay", assessment.matched_dimensions)

    def test_unknown_denominator_insufficient(self):
        first = make_obs("obs-1")
        second = make_obs("obs-2", denominator=EvidenceState.UNKNOWN, value=None)
        assessment = assess_comparison(first, second, make_claim())
        self.assertEqual(assessment.support, SupportDecision.INSUFFICIENT)
        self.assertNotIn("denominator", assessment.matched_dimensions)

    def test_changed_clinical_definition_insufficient(self):
        first = make_obs("obs-1", evidence_locator="Figure 3")
        second = make_obs("obs-2", evidence_locator="Supplementary Table 2")
        assessment = assess_comparison(first, second, make_claim())
        self.assertEqual(assessment.support, SupportDecision.INSUFFICIENT)

    def test_same_cohort_matched_reports(self):
        first = make_obs("obs-1", sample_linkage="sl-1")
        second = make_obs("obs-2", sample_linkage="sl-1")
        assessment = assess_comparison(first, second, make_claim())
        self.assertEqual(assessment.support, SupportDecision.SUPPORTED)
        self.assertIn("study_group_id", assessment.matched_dimensions)
        self.assertIn("sample_linkage", assessment.matched_dimensions)

    def test_different_sample_linkage_insufficient(self):
        first = make_obs("obs-1", sample_linkage="sl-1")
        second = make_obs("obs-2", sample_linkage="sl-2")
        assessment = assess_comparison(first, second, make_claim())
        self.assertEqual(assessment.support, SupportDecision.INSUFFICIENT)
        self.assertNotIn("sample_linkage", assessment.matched_dimensions)

    def test_directly_cited_single_observation_supported(self):
        first = make_obs("obs-1", evidence_locator="Figure 3")
        claim = make_claim(text="Figure 3 reports a gamma-globin RNA level of 0.42 in the mouse model.")
        assessment = assess_comparison(first, None, claim)
        self.assertEqual(assessment.support, SupportDecision.SUPPORTED)
        self.assertIsNone(assessment.direction)
        self.assertEqual(assessment.observation_ids, ["obs-1"])
        self.assertIsNone(assessment.second_id)

    def test_single_observation_not_directly_cited_insufficient(self):
        first = make_obs("obs-1")
        claim = make_claim(text="Some other finding.")
        assessment = assess_comparison(first, None, claim)
        self.assertEqual(assessment.support, SupportDecision.INSUFFICIENT)

    def test_disagreeing_values_discordant(self):
        first = make_obs("obs-1", value=0.42)
        second = make_obs("obs-2", value=0.10)
        assessment = assess_comparison(first, second, make_claim())
        self.assertEqual(assessment.support, SupportDecision.CONTRADICTED)
        self.assertEqual(assessment.direction, Direction.DISCORDANT)


if __name__ == "__main__":
    unittest.main()
