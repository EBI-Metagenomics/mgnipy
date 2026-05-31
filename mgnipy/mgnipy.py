import logging

logger = logging.getLogger(__name__)
from typing import Optional

from mgnipy._models.config import MGnipyConfig, to_mgnipy_config
from mgnipy._models.constants.CONSTANTS import SupportedEndpoints
from mgnipy.V2.proxies import (
    V2_ENDPOINT_DETAIL_PROXIES,
    V2_ENDPOINT_LIST_PROXIES,
)

V2_ALL_PROXIES = V2_ENDPOINT_DETAIL_PROXIES | V2_ENDPOINT_LIST_PROXIES


class MGnipy:
    """
    Main class for interacting with the MGnify API.
    Provides methods to access different resources (e.g., studies, samples, analyses) and their details,
    as well as utility methods for listing resources and describing endpoints.

    Parameters
    ----------
    config : MGnipyConfig or dict, optional
        Configuration for MGnipy, either as an MGnipyConfig instance or a dictionary of configuration parameters (default is None).
    **config_kwargs
        Additional keyword arguments to pass to the MGnipyConfig constructor if config is not provided.
        For example, cache_dir can be specified as a keyword argument. e.g. MGnipy(cache_dir="/path/to/cache")

    Examples
    --------
    >>> MG = MGnipy(cache_dir="/path/to/cache")
    >>> print(MG.cache_dir)
    /path/to/cache
    """

    def __init__(
        self,
        config: Optional[MGnipyConfig | dict] = None,
        **config_kwargs,
    ):

        self._config: MGnipyConfig = (
            to_mgnipy_config(config) if config else MGnipyConfig(**config_kwargs)
        )

        self._endpoints = self.list_resources()

    def __getattr__(self, name: str):

        if name == "cache_dir":
            return self._config.cache_dir

        endpoint = SupportedEndpoints.validate(name)

        if endpoint in V2_ENDPOINT_LIST_PROXIES:

            list_cls = V2_ENDPOINT_LIST_PROXIES[endpoint]
            return list_cls(config=self._config)

        if endpoint in V2_ENDPOINT_DETAIL_PROXIES:
            detail_cls = V2_ENDPOINT_DETAIL_PROXIES[endpoint]

            # Return a callable so required args like accession/biome_lineage
            # are provided when user calls MG.study(...), MG.biome(...), etc.
            def _detail_factory(id: Optional[str] = None, **kwargs):
                return detail_cls(id=id, config=self._config, **kwargs)

            return _detail_factory

        raise AttributeError(f"{type(self).__name__} has no attribute {name!r}")

    def list_resources(self):
        return SupportedEndpoints.as_list()

    def describe_resource(
        self, resource: str, as_dict: bool = False
    ) -> dict[str, str] | None:
        """
        Provides a description of the endpoint from the openapi documentation i.e., https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json

        Parameters
        ----------
        resource : str
            The name of the resource to describe.
        as_dict : bool, optional
            Whether to return the description as a dictionary mapping parameter names to their descriptions (default is False).

        Returns
        -------
        dict of str to str or None
            A dictionary mapping parameter names to their descriptions if as_dict is True, otherwise None.

        """
        try:
            endpoint = SupportedEndpoints.validate(resource)
        except ValueError:
            logger.error(
                f"Resource '{resource}' is not supported. Supported resources are: {', '.join(self.list_resources())}"
            )
            return None

        proxy_cls = V2_ALL_PROXIES[endpoint]
        logger.debug(f"Using proxy class {proxy_cls} to describe resource '{resource}'")
        proxy = proxy_cls(config=self._config)
        return proxy.emgapi_handler.describe_endpoint(as_dict=as_dict)

    def describe_resources(
        self, resource: Optional[str] = None, as_dict: bool = False
    ) -> dict[str, str] | None:
        """
        Provides a description of the endpoint from the openapi documentation i.e., https://www.ebi.ac.uk/metagenomics/api/v2/openapi.json

        Parameters
        ----------
        resource : str, optional
            The name of the resource to describe.
        as_dict : bool, optional
            Whether to return the description as a dictionary mapping parameter names to their descriptions (default is False).

        Returns
        -------
        dict of str to str or None
            A dictionary mapping parameter names to their descriptions if as_dict is True, otherwise None.

        """

        if resource is not None:
            return self.describe_resource(resource, as_dict=as_dict)

        descriptions = {}
        for endpoint in SupportedEndpoints:
            desc = self.describe_resource(endpoint.value, as_dict=as_dict)
            if desc is not None:
                descriptions[endpoint.value] = desc
        return descriptions

    def clear_subcaches(self) -> None:
        """
        Clear the cache for a specific resource or all resources.

        Parameters
        ----------
        resource : str, optional
            The name of the resource to clear the cache for. If None, clears the cache for all resources (default is None).
        """

        if self.cache_dir is None:
            return

        if self.cache_dir.exists():

            logger.warning(f"Clearing ALL cache subdirectories in {self.cache_dir}")
            # for each cache subdir
            for cache_key in self.cache_dir.iterdir():
                if cache_key.is_dir():
                    logger.debug(f"Processing cache subdirectory {cache_key}")

                    # !!!! additional check of folder setup just in case?
                    # !!!! to avoid accidentally deleting something important if cache_dir is misconfigured
                    # all files in cache should either be named 'mgnipy_manifest.json' or 'mgnipy_page_*.json' for page results
                    if not all(
                        cache_file.name == "mgnipy_manifest.json"
                        or (
                            cache_file.name.startswith("mgnipy_page_")
                            and cache_file.suffix == ".json"
                        )
                        for cache_file in cache_key.iterdir()
                    ):
                        raise RuntimeError(
                            f"Cache subdirectory {cache_key} contains unexpected files, "
                            "aborting cache clearing to avoid potential data loss. "
                            "Please check the cache directory configuration and contents. "
                            f"Please check the given cache_dir path and file contents: {self.cache_dir}"
                        )

                    for cache_file in cache_key.iterdir():
                        # try clearning file by file
                        # extra check just in case
                        if cache_file.name == "mgnipy_manifest.json" or (
                            cache_file.name.startswith("mgnipy_page_")
                            and cache_file.suffix == ".json"
                        ):
                            try:
                                logger.debug(f"Clearing cache file {cache_file}")
                                cache_file.unlink()
                            except Exception:
                                logger.warning(
                                    f"Failed to delete cache file: {cache_file}"
                                )

                    # now try to delete subdir itself
                    try:
                        cache_key.rmdir()
                    except Exception:
                        logger.warning(f"Failed to delete cache directory: {cache_key}")
                else:  # don't delete the auth token cache which is not in a dir
                    logger.info(f"Skipping non-directory cache item: {cache_key}")
        else:
            logger.info(
                f"Cache directory {self.cache_dir} does not exist, nothing to clear."
            )

    def __str__(self):
        return f"MGnipy(config={self._config})"
