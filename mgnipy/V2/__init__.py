BASE_URL = "https://www.ebi.ac.uk/"

from .client import (
    AuthenticatedClient,
    Client,
)

__all__ = (
    "AuthenticatedClient",
    "Client",
)
