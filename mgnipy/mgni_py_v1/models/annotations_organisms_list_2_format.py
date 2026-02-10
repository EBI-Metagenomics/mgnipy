from enum import Enum


class AnnotationsOrganismsList2Format(str, Enum):
    CSV = "csv"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
