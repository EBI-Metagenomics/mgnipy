from typing import Optional

from mgnipy._models.config import MgnipyConfig
from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.proxies import (
    V2_ENDPOINT_DETAIL_PROXIES,
    V2_ENDPOINT_LIST_PROXIES,
)


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

    def describe_resources(self):
        # TODO from the API docs
        # this should be prioritized more because it can be used
        # by agents / skills?
        # ALSO include a link to openapi.json spec (maybe a curl)
        pass
