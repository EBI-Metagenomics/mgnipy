# mainly Enum constants for pydantic models
from enum import Enum

from pydantic import (
    TypeAdapter,
    ValidationError,
)


class SpecialEnum(Enum):
    def __str__(self):
        return str(self.value)

    @classmethod
    def as_list(cls):
        return [field.value for field in cls]

    @classmethod
    def validate(cls, input):
        try:
            return TypeAdapter(cls).validate_python(input)
        except ValidationError as e:
            raise ValueError(f"Invalid {cls.__name__}: {input}") from e

    @classmethod
    def is_valid(cls, input):
        try:
            cls.validate(input)
            return True
        except ValueError:
            return False

    @classmethod
    def as_one_str(cls, sep=","):
        return sep.join(field.value for field in cls)

    @classmethod
    def is_prefix_in(cls, input):
        return any(input.startswith(field.value) for field in cls)


class SupportedApiVersions(SpecialEnum):
    # V1 = 'v1' # TODO: add support for v1 endpoints
    V2 = "v2"
    LATEST = "latest"


class SupportedEndpoints(SpecialEnum):
    ANALYSES = "analyses"
    ASSEMBLIES = "assemblies"
    GENOMES = "genomes"
    PUBLICATIONS = "publications"
    SAMPLES = "samples"
    STUDIES = "studies"
    #    PRIVATE_DATA = "private_data"
    #    MISCELLANEOUS = "miscellaneous"
    #    AUTHENTICATION = "authentication"
    BIOMES = "biomes"  # miscellaneous


class StudiesPrefixes(SpecialEnum):
    MGYS = "MGYS"
    ERP = "ERP"
    PRJ = "PRJ"


class SamplesPrefixes(SpecialEnum):
    SRS = "SRS"
    ERS = "ERS"
    SAM = "SAM"


class AnalysesPrefixes(SpecialEnum):
    MGYA = "MGYA"


class RunsPrefixes(SpecialEnum):
    SRR = "SRR"
    ERR = "ERR"


class GenomesPrefixes(SpecialEnum):
    MGYG = "MGYG"


class AssembliesPrefixes(SpecialEnum):
    ERZ = "ERZ"
    GCA = "GCA"


class BiomesPrefixes(SpecialEnum):
    ROOT = "root"
