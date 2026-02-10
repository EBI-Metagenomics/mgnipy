from enum import Enum


class AnnotationsKeggOrthologsAnalysesListFormat(str, Enum):
    CSV = "csv"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
