from enum import Enum


class AnnotationsInterproIdentifiersListFormat(str, Enum):
    CSV = "csv"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
