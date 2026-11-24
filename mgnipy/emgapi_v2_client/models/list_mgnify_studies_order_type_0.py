from enum import Enum


class ListMgnifyStudiesOrderType0(str, Enum):
    ACCESSION = "accession"
    UPDATED_AT = "updated_at"
    VALUE_1 = "-accession"
    VALUE_3 = "-updated_at"
    VALUE_4 = ""

    def __str__(self) -> str:
        return str(self.value)
