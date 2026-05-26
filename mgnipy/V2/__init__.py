from ..emgapi_v2_client.client import AuthenticatedClient, Client
from .core import MGnifier
from .proxies.analyses import Analyses
from .proxies.assemblies import Assemblies
from .proxies.biomes import Biomes
from .proxies.catalogues import Catalogues
from .proxies.genomes import Genomes
from .proxies.publications import Publications
from .proxies.runs import Runs
from .proxies.samples import Samples
from .proxies.studies import Studies

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
