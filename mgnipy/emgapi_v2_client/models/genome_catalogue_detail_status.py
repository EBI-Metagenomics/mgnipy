from __future__ import annotations

from enum import Enum


class GenomeCatalogueDetailStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    READY = "ready"
    RETIRED = "retired"

    def __str__(self) -> str:
        return str(self.value)
