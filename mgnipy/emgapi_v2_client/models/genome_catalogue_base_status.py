from enum import Enum

class GenomeCatalogueBaseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    READY = "ready"
    RETIRED = "retired"

    def __str__(self) -> str:
        return str(self.value)
