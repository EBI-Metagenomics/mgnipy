from enum import Enum


class AnalysesInterproIdentifiersListFormat(str, Enum):
    CSV = "csv"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
