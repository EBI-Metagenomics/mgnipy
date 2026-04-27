from typing import Optional

from mgnipy._models.config import MgnipyConfig
from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.proxies import (
    V2_ENDPOINT_DETAIL_PROXIES,
    V2_ENDPOINT_LIST_PROXIES,
)

V2_ALL_PROXIES = V2_ENDPOINT_DETAIL_PROXIES | V2_ENDPOINT_LIST_PROXIES


class MGnipy:
    """ """

    def __init__(self, **config):
        self._config = MgnipyConfig(**config)
        self._endpoints = self.list_resources()

    def __getattr__(self, name: str):
        endpoint = SupportedEndpoints.validate(name)

        if endpoint in V2_ENDPOINT_LIST_PROXIES:

            list_cls = V2_ENDPOINT_LIST_PROXIES[endpoint]
            return list_cls(config=self._config.model_dump(mode="json"))

        if endpoint in V2_ENDPOINT_DETAIL_PROXIES:
            detail_cls = V2_ENDPOINT_DETAIL_PROXIES[endpoint]

            # Return a callable so required args like accession/biome_lineage
            # are provided when user calls MG.study(...), MG.biome(...), etc.
            def _detail_factory(id: Optional[str] = None, **kwargs):
                return detail_cls(
                    id=id, config=self._config.model_dump(mode="json"), **kwargs
                )

            return _detail_factory

        raise AttributeError(
            f"{type(self).__name__} has no endpoint attribute {name!r}"
        )

    def list_resources(self):
        return [endpoint.value for endpoint in SupportedEndpoints]

    def describe_resource(
        self, resource: str, as_dict: bool = False
    ) -> dict[str, str] | None:
        """
        Describe the supported parameters for a given resource by parsing the docstring of the corresponding endpoint module.

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
            print(
                f"Resource '{resource}' is not supported. Supported resources are: {', '.join(self.list_resources())}"
            )
            return None

        proxy_cls = V2_ALL_PROXIES[endpoint]
        proxy = proxy_cls(config=self._config.model_dump(mode="json"))
        return proxy.describe_endpoint(as_dict=as_dict)

    def describe_resources(
        self, resource: Optional[str] = None, as_dict: bool = False
    ) -> dict[str, str] | None:

        if resource is not None:
            return self.describe_resource(resource, as_dict=as_dict)

        descriptions = {}
        for endpoint in SupportedEndpoints:
            desc = self.describe_resource(endpoint.value, as_dict=as_dict)
            if desc is not None:
                descriptions[endpoint.value] = desc
        return descriptions
