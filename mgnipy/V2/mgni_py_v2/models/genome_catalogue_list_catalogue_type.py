from enum import Enum

class GenomeCatalogueListCatalogueType(str, Enum):
    EUKARYOTES = "eukaryotes"
    PROKARYOTES = "prokaryotes"
    VIRUSES = "viruses"

    def __str__(self) -> str:
        return str(self.value)
