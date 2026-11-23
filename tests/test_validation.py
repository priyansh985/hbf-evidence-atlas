"""Validation tests: valid corpora pass; malformed ones produce ERROR issues."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from hbf_atlas.io import validate_corpus
from hbf_atlas.models import Corpus, Context, EvidenceState, Observation, Review, Severity, Source


def make_corpus() -> Corpus:
    """Build a valid Corpus."""
    source = Source(
        source_id="src-1",
        version="2026-11-01",
        url="https://example.org/sickle-cell-review-1",
        figure_table="Table 1",
    )
    observation = Observation(
        obs_id="obs-1",
        source_id="src-1",
        context=Context(study_group_id="grp-A", species="Homo sapiens", model="mouse-model"),
        readout_kind="gamma-globin-rna",
        assay={"name": "qRT-PCR", "definition": "gamma-globin mRNA / beta-actyl normalized"},
        value=0.42,
        unit="%",
        denominator=30,
        evidence_locator="Figure 3",
    )
    review = Review(
        review_id="rev-1",
        curator_id="cur-1",
        reviewer_ids=["rev-a", "rev-b"],
    )
    return Corpus(
        data_version="v0.1",
        sources=[source],
        observations=[observation],
        claims=[],
        reviews=[review],
    )


class TestValidation(unittest.TestCase):
    def test_valid_corpus_has_no_issues(self):
        self.assertEqual(validate_corpus(make_corpus()), [])

    def test_duplicate_obs_id_is_error(self):
        corpus = make_corpus()
        duplicate = Observation(
            obs_id=corpus.observations[0].obs_id,
            source_id=corpus.observations[0].source_id,
            context=corpus.observations[0].context,
            readout_kind="gamma-globin-rna",
            value=0.50,
            unit="%",
            denominator=10,
        )
        corpus.observations.append(duplicate)
        issues = validate_corpus(corpus)
        self.assertTrue(
            any(
                issue.severity is Severity.ERROR
                and issue.record_id == duplicate.obs_id
                and issue.field == "obs_id"
                for issue in issues
            ),
            msg=f"expected an ERROR issue on obs_id for {duplicate.obs_id}, got {issues}",
        )

    def test_missing_source_link_is_error(self):
        corpus = make_corpus()
        observation = corpus.observations[0]
        observation.source_id = "src-missing"
        issues = validate_corpus(corpus)
        self.assertTrue(
            any(
                issue.severity is Severity.ERROR
                and issue.record_id == observation.obs_id
                and issue.field == "source_id"
                for issue in issues
            ),
            msg=f"expected an ERROR issue on source_id, got {issues}",
        )

    def test_invalid_denominator_zero_is_error(self):
        corpus = make_corpus()
        observation = corpus.observations[0]
        observation.denominator = 0
        issues = validate_corpus(corpus)
        self.assertTrue(
            any(
                issue.severity is Severity.ERROR
                and issue.record_id == observation.obs_id
                and issue.field == "denominator"
                for issue in issues
            ),
            msg=f"expected an ERROR issue on denominator, got {issues}",
        )

    def test_denominator_as_state_with_value_set_is_issue(self):
        corpus = make_corpus()
        observation = corpus.observations[0]
        observation.denominator = EvidenceState.AMBIGUOUS
        issues = validate_corpus(corpus)
        self.assertTrue(
            any(
                issue.severity is Severity.ERROR
                and issue.record_id == observation.obs_id
                and issue.field == "denominator"
                for issue in issues
            ),
            msg=f"expected an ERROR issue on denominator, got {issues}",
        )

    def test_observed_without_unit_is_issue(self):
        corpus = make_corpus()
        observation = corpus.observations[0]
        observation.unit = None
        issues = validate_corpus(corpus)
        self.assertTrue(
            any(
                issue.severity is Severity.ERROR
                and issue.record_id == observation.obs_id
                and issue.field == "unit"
                for issue in issues
            ),
            msg=f"expected an ERROR issue on unit, got {issues}",
        )


if __name__ == "__main__":
    unittest.main()
