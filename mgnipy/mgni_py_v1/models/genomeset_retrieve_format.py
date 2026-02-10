from enum import Enum


class GenomesetRetrieveFormat(str, Enum):
    CSV = "csv"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
