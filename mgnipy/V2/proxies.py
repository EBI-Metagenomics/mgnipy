from typing import (
    Any,
    List,
    Literal,
    Optional,
)

from bigtree import (
    Tree,
)

from mgnipy._models.CONSTANTS import (
    SupportedEndpoints,
)
from mgnipy.V2.core import MGnifier


class ResourceProxy(MGnifier):
    """generic"""

    def __init__(
        self,
        *,
        resource: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # init mgnifier
        super().__init__(
            resource=resource,
            params=params,
            **kwargs,
        )

    def _spawn(self, *, resource: Optional[str] = None, **params):
        target_resource = resource or self.resource
        proxy_cls = ENDPOINT_PROXIES[SupportedEndpoints(target_resource)]
        # If no specialized proxy exists, keep generic behavior
        if proxy_cls is ResourceProxy:
            return ResourceProxy(resource=target_resource, **params)
        return proxy_cls(**params)


class Analyses(ResourceProxy):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):

        super().__init__(resource="analyses", params=params, **kwargs)


class Runs(ResourceProxy):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):

        super().__init__(resource="runs", params=params, **kwargs)


class Samples(ResourceProxy):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):

        super().__init__(resource="samples", params=params, **kwargs)


class Studies(ResourceProxy):

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="studies", params=params, **kwargs)


class Biomes(ResourceProxy):

    def __init__(self, **kwargs):
        super().__init__(resource="biomes", **kwargs)

    @property
    def lineages(self) -> List[str]:
        if self._results is None:
            raise RuntimeError(
                "No data available to get lineages. Please run get() first."
            )
        return self.results_biome_lineages

    @property
    def tree(self) -> Tree:
        """
        Convert the biomes metadata to a tree structure for visualization or analysis.

        Returns
        -------
        Tree
            A tree representation of the biomes and their relationships.
        """
        # TODO generate nodes first
        return Tree.from_list(self.lineages, sep=":")

    def show_tree(
        self,
        method: Literal[
            "compact",
            "show",
            "print",
            "horizontal",
            "hshow",
            "h",
            "hprint",
            "vertical",
            "vshow",
            "v",
            "vprint",
        ] = "compact",
    ):
        if method in ["compact", "show", "print"]:
            # TODO print_tree(self._tree)
            self.tree.show()
        elif method in ["horizontal", "hshow", "h", "hprint"]:
            self.tree.hshow()
        elif method in ["vertical", "vshow", "v", "vprint"]:
            self.tree.vshow()
        else:
            raise ValueError(
                f"Invalid method: {method}. "
                "Supported methods: 'compact', 'show', 'print', "
                "'horizontal', 'hshow', 'h', 'hprint', "
                "'vertical', 'vshow', 'v', 'vprint'."
            )


class Assemblies(ResourceProxy):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="assemblies", params=params, **kwargs)


class Genomes(ResourceProxy):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # TODO
        super().__init__(resource="genomes", params=params, **kwargs)


ENDPOINT_PROXIES = {
    SupportedEndpoints.BIOMES: Biomes,
    SupportedEndpoints.STUDIES: Studies,
    SupportedEndpoints.SAMPLES: Samples,
    SupportedEndpoints.RUNS: Runs,
    SupportedEndpoints.ANALYSES: Analyses,
    SupportedEndpoints.GENOMES: Genomes,
    SupportedEndpoints.ASSEMBLIES: Assemblies,
    None: ResourceProxy,  # default proxy if no specific class is defined
}
