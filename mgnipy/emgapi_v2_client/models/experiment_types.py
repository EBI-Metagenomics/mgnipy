from enum import Enum


class ExperimentTypes(str, Enum):
    AMPLI = "AMPLI"
    ASSEM = "ASSEM"
    HYASS = "HYASS"
    LRASS = "LRASS"
    METAB = "METAB"
    METAG = "METAG"
    METAT = "METAT"
    UNKNO = "UNKNO"

    def __str__(self) -> str:
        return str(self.value)
