"""A client library for accessing MGnify API"""

from __future__ import annotations

from .client import AuthenticatedClient, Client

__all__ = (
    "AuthenticatedClient",
    "Client",
)
