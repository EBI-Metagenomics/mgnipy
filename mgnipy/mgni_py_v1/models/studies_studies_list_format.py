from enum import Enum


class StudiesStudiesListFormat(str, Enum):
    CSV = "csv"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
