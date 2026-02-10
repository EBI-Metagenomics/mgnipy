from enum import Enum


class CatalogueTypeEnum(str, Enum):
    EUKARYOTES = "eukaryotes"
    PROKARYOTES = "prokaryotes"
    VIRUSES = "viruses"

    def __str__(self) -> str:
        return str(self.value)
