# mainly Enum constants for pydantic models
from enum import Enum


class SupportedApiVersions(Enum):
    V2 = "v2"
    LATEST = "latest"


class SupportedEndpoints(Enum):
    ANALYSES = "analyses"
    GENOMES = "genomes"
    PUBLICATIONS = "publications"
    SAMPLES = "samples"
    STUDIES = "studies"
    PRIVATE_DATA = "private_data"
    MISCELLANEOUS = "miscellaneous"
    AUTHENTICATION = "authentication"
