from enum import Enum


class GenomesetGenomesListFormat(str, Enum):
    CSV = "csv"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
