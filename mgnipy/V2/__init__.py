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
    "Mgnifier",
    "BiomesMgnifier",
    "StudiesMgnifier",
    "SamplesMgnifier",
    "AnalysesMgnifier",
    "GenomesMgnifier",
    "Client",
    "AuthenticatedClient",
)

BASE_URL = "https://www.ebi.ac.uk/"
