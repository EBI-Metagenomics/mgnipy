# mainly Enum constants for pydantic models
from enum import Enum

class SpecialEnum(Enum):
    def __str__(self):
        return str(self.value)

class SupportedApiVersions(SpecialEnum):
    V1 = 'v1'
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
