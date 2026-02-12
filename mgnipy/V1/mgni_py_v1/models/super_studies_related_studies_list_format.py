from enum import Enum


class SuperStudiesRelatedStudiesListFormat(str, Enum):
    CSV = "csv"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
