from enum import Enum


class TypeEnum(str, Enum):
    ISOLATE = "isolate"
    MAG = "mag"

    def __str__(self) -> str:
        return str(self.value)
