from .core import Mgnifier
from .metadata import (
    AnalysesProxy,
    BiomesProxy,
    GenomesProxy,
    SamplesProxy,
    StudiesProxy,
)
from .mgni_py_v2.client import (
    AuthenticatedClient,
    Client,
)

__all__ = (
    "Mgnifier",
    "BiomesProxy",
    "StudiesProxy",
    "SamplesProxy",
    "AnalysesProxy",
    "GenomesProxy",
    "Client",
    "AuthenticatedClient",
)
