from enum import Enum

class GenomeCatalogueListStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    READY = "ready"
    RETIRED = "retired"

    def __str__(self) -> str:
        return str(self.value)
