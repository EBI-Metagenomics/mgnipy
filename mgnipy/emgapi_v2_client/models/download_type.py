from enum import Enum


class DownloadType(str, Enum):
    ANALYSIS_RO_CRATE = "Analysis RO Crate"
    CODING_SEQUENCES = "Coding Sequences"
    FUNCTIONAL_ANALYSIS = "Functional analysis"
    GENOME_ANALYSIS = "Genome analysis"
    NON_CODING_RNAS = "non-coding RNAs"
    OTHER = "Other"
    QUALITY_CONTROL = "Quality control"
    SEQUENCE_DATA = "Sequence data"
    STATISTICS = "Statistics"
    TAXONOMIC_ANALYSIS = "Taxonomic analysis"

    def __str__(self) -> str:
        return str(self.value)
