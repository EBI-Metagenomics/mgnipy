import logging

logger = logging.getLogger(__name__)
from typing import Optional

from mgnipy.emgapi_v2_client import AuthenticatedClient, Client
from mgnipy._models.config import MGnipyConfig


def init_httpx_client(
    config: Optional[MGnipyConfig] = None,
    **httpx_kwargs,
) -> Client | AuthenticatedClient:
    """
    Initialize and return a MGnify API client instance (authenticated or not).

    Returns
    -------
    Client
        Configured MGnify API client.

    Example
    -------
    >>> # Initialize an http client (doctest skipped)
    >>> executor = QueryExecutor(qs)  # doctest: +SKIP
    >>> executor._init_client()  # doctest: +SKIP
    """

    if config is None:
        # default config but without cache
        config = MGnipyConfig(cache_dir=None)

    if not isinstance(config, MGnipyConfig):
        raise TypeError(
            f"Expected config to be an instance of MGnipyConfig, got {type(config)}"
        )

    _url: str = str(config.base_url)

    # MAIN
    if config.auth_token:
        logger.info("Initializing client with provided auth token.")
        return AuthenticatedClient(
            base_url=_url,
            token=config.auth_token,
            **httpx_kwargs,
        )

    return Client(
        base_url=_url,
        **httpx_kwargs,
    )
