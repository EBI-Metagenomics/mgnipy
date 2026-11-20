from enum import Enum


class ListMgnifySamplesOrderType0(str, Enum):
    SAMPLE_TITLE = "sample_title"
    UPDATED_AT = "updated_at"
    VALUE_1 = "-sample_title"
    VALUE_3 = "-updated_at"
    VALUE_4 = ""

    def __str__(self) -> str:
        return str(self.value)
