from enum import Enum

class ListMgnifyGenomesOrderType0(str, Enum):
    ACCESSION = "accession"
    COMPLETENESS = "completeness"
    CONTAMINATION = "contamination"
    LENGTH = "length"
    NUM_GENOMES_TOTAL = "num_genomes_total"
    VALUE_1 = "-accession"
    VALUE_10 = ""
    VALUE_3 = "-length"
    VALUE_5 = "-completeness"
    VALUE_7 = "-contamination"
    VALUE_9 = "-num_genomes_total"

    def __str__(self) -> str:
        return str(self.value)
