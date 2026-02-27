# mainly Enum constants for pydantic models
from enum import Enum


class SpecialEnum(Enum):
    def __str__(self):
        return str(self.value)


class SupportedApiVersions(SpecialEnum):
    # V1 = 'v1' # TODO: add support for v1 endpoints
    V2 = "v2"
    LATEST = "latest"


class SupportedEndpoints(SpecialEnum):
    ANALYSES = "analyses"
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
    PRJEB = "PRJEB"
    PRJNA = "PRJNA"


class SamplesPrefixes(SpecialEnum):
    SRS = "SRS"
    ERS = "ERS"
    SAMEA = "SAMEA"
    SAMN = "SAMN"


class AnalysesPrefixes(SpecialEnum):
    MGYA = "MGYA"


class RunsPrefixes(SpecialEnum):
    SRR = "SRR"
    ERR = "ERR"


class GenomesPrefixes(SpecialEnum):
    MGYG = "MGYG"


class AssemblyPrefixes(SpecialEnum):
    ERZ = "ERZ"


class BiomesPrefixes(SpecialEnum):
    ROOT = "root"
