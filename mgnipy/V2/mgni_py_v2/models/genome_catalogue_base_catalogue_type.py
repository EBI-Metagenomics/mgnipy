from enum import Enum

class GenomeCatalogueBaseCatalogueType(str, Enum):
    EUKARYOTES = "eukaryotes"
    PROKARYOTES = "prokaryotes"
    VIRUSES = "viruses"

    def __str__(self) -> str:
        return str(self.value)
