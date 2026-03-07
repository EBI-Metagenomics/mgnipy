from enum import Enum


class ListMgnifyPublicationsOrderType0(str, Enum):
    PUBLISHED_YEAR = "published_year"
    VALUE_1 = "-published_year"
    VALUE_2 = ""

    def __str__(self) -> str:
        return str(self.value)
