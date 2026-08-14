from enum import Enum

class GenomeType(str, Enum):
    ISOLATE = "Isolate"
    MAG = "MAG"

    def __str__(self) -> str:
        return str(self.value)
