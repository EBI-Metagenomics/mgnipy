from .metadata import (
    AnalysesMgnifier,
    BiomesMgnifier,
    GenomesMgnifier,
    Mgnifier,
    SamplesMgnifier,
    StudiesMgnifier,
)
from .mgni_py_v2.client import (
    AuthenticatedClient,
    Client,
)

__all__ = (
    "AuthenticatedClient",
    "Client",
    "SamplesMgnifier",
    "GenomesMgnifier",
    "StudiesMgnifier",
    "BiomesMgnifier",
    "AnalysesMgnifier",
    "Mgnifier",
)

BASE_URL = "https://www.ebi.ac.uk/"
