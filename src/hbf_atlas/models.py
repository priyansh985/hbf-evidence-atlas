"""Data contracts for the HbF evidence atlas.

Every record carries an immutable ID. Fields that a source did not report,
that are ambiguous, do not apply, or cannot be determined are spelled out
explicitly via EvidenceState.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EvidenceState(str, Enum):
    """Explicit vocabulary for evidence fields that are not plainly observed."""

    OBSERVED = "observed"
    UNREPORTED = "unreported"
    AMBIGUOUS = "ambiguous"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    """Severity of a validation issue."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SupportDecision(str, Enum):
    """Outcome of checking a claim against observations."""

    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    INSUFFICIENT = "insufficient"


class Direction(str, Enum):
    """Biological direction of an agreed comparison."""

    CONCORDANT = "concordant"
    DISCORDANT = "discordant"
    INDETERMINATE = "indeterminate"


@dataclass
class Source:
    """A published or accessible report or dataset behind an observation."""

    source_id: str  # immutable record ID (DOI or accession)
    version: str
    url: str
    figure_table: str | None = None
    permission_status: EvidenceState = EvidenceState.OBSERVED


@dataclass
class Context:
    """Conditions under which observations were made."""

    study_group_id: str  # immutable
    species: str
    model: str | None = None
    cohort: str | None = None
    intervention: str | None = None
    comparator: str | None = None
    stage: str | None = None  # stage or follow-up window
    genotype: str | None = None
    transfusion_context: str | None = None
    sample_linkage: str | None = None


@dataclass
class Observation:
    """One measured readout for a context."""

    obs_id: str  # immutable
    source_id: str
    context: Context
    readout_kind: str  # 'gamma-globin-rna' | 'hbF-percent' | 'f-cell-percent' | 'hbF-per-cell' | 'vo-free-event'
    assay: dict[str, str] | None = None  # full assay definition
    value: float | None = None
    unit: str | None = None
    denominator: int | EvidenceState | None = None  # experimental-unit count, or a state when not an integer
    time_point: str | None = None
    sample_linkage: str | None = None
    uncertainty: float | None = None
    direction: Direction | None = None
    evidence_locator: str | None = None  # figure/table/panel/section


@dataclass
class Claim:
    """A research claim being checked against observations."""

    claim_id: str  # immutable
    text: str
    claim_type: str | None = None


@dataclass
class Assessment:
    """Outcome of checking a claim against observations."""

    first_id: str
    second_id: str | None = None
    matched_dimensions: list[str] = field(default_factory=list)
    support: SupportDecision = SupportDecision.INSUFFICIENT
    direction: Direction | None = None
    rationale: str = ""
    observation_ids: list[str] = field(default_factory=list)


@dataclass
class Issue:
    """A validation finding on a corpus record."""

    severity: Severity
    record_id: str
    field: str
    message: str


@dataclass
class Review:
    """A curator's review of a corpus record."""

    review_id: str  # immutable
    curator_id: str
    reviewer_ids: list[str]
    adjudication_state: str | None = None
    corpus_version: str | None = None
    reason_for_revision: str | None = None


@dataclass
class Corpus:
    """An immutable-by-ID collection of atlas records."""

    data_version: str
    sources: list[Source] = field(default_factory=list)
    observations: list[Observation] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    reviews: list[Review] = field(default_factory=list)
