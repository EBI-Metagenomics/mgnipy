# mainly Enum constants for pydantic models
from enum import Enum

from pydantic import (
    TypeAdapter,
    ValidationError,
)


class SpecialEnum(Enum):
    def __str__(self):
        """Return the value of the enum member as a string."""
        return str(self.value)

    @classmethod
    def as_list(cls):
        """Return a list of the values of all enum members."""
        return [field.value for field in cls]

    @classmethod
    def validate(cls, input):
        """Validate the input against the enum values and return the corresponding enum member."""
        try:
            return TypeAdapter(cls).validate_python(input)
        except ValidationError as e:
            raise ValueError(f"Invalid {cls.__name__}: {input}") from e

    @classmethod
    def is_valid(cls, input):
        """Check if the input is a valid value for the enum."""
        try:
            cls.validate(input)
            return True
        except ValueError:
            return False

    @classmethod
    def as_one_str(cls, sep=","):
        """Return a string of all enum values joined by the specified separator."""
        return sep.join(field.value for field in cls)

    @classmethod
    def is_prefix_in(cls, input):
        """Check if the input string starts with any of the enum values (used for accession prefixes)."""
        return any(input.startswith(field.value) for field in cls)


class SupportedApiVersions(SpecialEnum):
    # V1 = 'v1' # TODO: add support for v1 endpoints
    V2 = "v2"
    LATEST = "latest"


class SupportedEndpoints(SpecialEnum):
    ANALYSES = "analyses"
    ANALYSIS = "analysis"
    ASSEMBLIES = "assemblies"
    ASSEMBLY = "assembly"
    GENOMES = "genomes"
    GENOME = "genome"
    PUBLICATIONS = "publications"
    PUBLLICATION = "publication"
    SAMPLES = "samples"
    SAMPLE = "sample"
    STUDIES = "studies"
    STUDY = "study"
    RUNS = "runs"
    RUN = "run"
    #    PRIVATE_DATA = "private_data"
    MISCELLANEOUS = "miscellaneous"
    #    AUTHENTICATION = "authentication"
    BIOMES = "biomes"  # miscellaneous
    BIOME = "biome"


# class


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
