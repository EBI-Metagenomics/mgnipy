from enum import Enum


class GenomesSearchGatherCreateFormat(str, Enum):
    CSV = "csv"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
