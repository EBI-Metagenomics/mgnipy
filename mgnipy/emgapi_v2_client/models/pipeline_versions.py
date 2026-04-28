from enum import Enum


class PipelineVersions(str, Enum):
    V1 = "V1"
    V2 = "V2"
    V3 = "V3"
    V4 = "V4"
    V4_1 = "V4.1"
    V5 = "V5"
    V6 = "V6"
    V6_1 = "V6.1"

    def __str__(self) -> str:
        return str(self.value)
