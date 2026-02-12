from enum import Enum


class PipelineVersions(str, Enum):
    V5 = "V5"
    V6 = "V6"

    def __str__(self) -> str:
        return str(self.value)
