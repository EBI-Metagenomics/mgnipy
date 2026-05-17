from ..emgapi_v2_client.client import (
    AuthenticatedClient,
    Client,
)
from .core import MGnifier
from .proxies import (
    Analyses,
    Assemblies,
    Biomes,
    Catalogues,
    Genomes,
    Publications,
    Runs,
    Samples,
    Studies,
)

__all__ = (
    "MGnifier",
    "Assemblies",
    "Catalogues",
    "Publications",
    "Runs",
    "Biomes",
    "Studies",
    "Samples",
    "Analyses",
    "Genomes",
    "Client",
    "AuthenticatedClient",
)
