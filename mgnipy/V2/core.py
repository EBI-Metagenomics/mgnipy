from typing import (
    Any,
    Literal,
    Optional,
)

from mgnipy.V2.query_set import QuerySet


class MGnifier(QuerySet):
    """
    (Facade) MGnifier is the main class representing a queryable MGnify resource.
    It provides methods for fetching and navigating data from the MGnify API.
    """

    def __init__(
        self,
        resource: Literal[
            "biomes",
            "biome",
            "studies",
            "study",
            "samples",
            "sample",
            "runs",
            "run",
            "genomes",
            "genome",
            "analyses",
            "analysis",
            "assemblies",
            "assembly",
            "publications",
            "publication",
            "catalogues",
            "catalogue",
        ],
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource=resource, params=params, **kwargs)

    # forarding some user-facing QueryExecutor methods
    def get(self, *args, **kwargs):
        return self.exec.get(*args, **kwargs)

    async def aget(self, *args, **kwargs):
        return await self.exec.aget(*args, **kwargs)

    def page(self, *args, **kwargs):
        return self.exec.page(*args, **kwargs)

    async def apage(self, *args, **kwargs):
        return await self.exec.apage(*args, **kwargs)
