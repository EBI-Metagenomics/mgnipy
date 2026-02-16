from importlib import metadata
from platformdirs import user_cache_dir

APPNAME = "mgnipy"
APPAUTHOR = "MGnify"
CACHE_DIR = user_cache_dir(APPNAME, APPAUTHOR)

__version__ = metadata.version(APPNAME)

# TODO: at init cache the list of biomes

"""A client library for accessing MGnify API"""

from ..client import (
    AuthenticatedClient,
    Client,
)

__all__ = (
    "AuthenticatedClient",
    "Client",
)
