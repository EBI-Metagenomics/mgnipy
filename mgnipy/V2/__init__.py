from ..emgapi_v2_client.client import (
    AuthenticatedClient,
    Client,
)
from .core import MGnifier
from .proxies.runs import Runs
from .proxies.studies import Studies
from .proxies.analyses import Analyses
from .proxies.samples import Samples
from .proxies.assemblies import Assemblies
from .proxies.genomes import Genomes
from .proxies.publications import Publications
from .proxies.biomes import Biomes
from .proxies.catalogues import Catalogues

from .datasets import MGazine

__all__ = (
    "MGazine",
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
