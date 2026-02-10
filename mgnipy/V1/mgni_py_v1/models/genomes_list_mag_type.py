from enum import Enum


class GenomesListMagType(str, Enum):
    ISOLATE = "isolate"
    MAG = "mag"

    def __str__(self) -> str:
        return str(self.value)
