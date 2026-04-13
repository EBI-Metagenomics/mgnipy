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
from mgnipy.V2.datasets import MGazine
from mgnipy.V2.mgni_py_v2.api.studies import (
    list_mgnify_study_samples,
)

SUPPORTED_RELATIONSHIPS = {
    SupportedEndpoints.BIOMES: [SupportedEndpoints.STUDIES],
    SupportedEndpoints.STUDIES: [
        SupportedEndpoints.ANALYSES,
        SupportedEndpoints.SAMPLES,
    ],
    SupportedEndpoints.SAMPLES: [SupportedEndpoints.RUNS],
    SupportedEndpoints.RUNS: [SupportedEndpoints.ANALYSES],
    SupportedEndpoints.ASSEMBLIES: [
        SupportedEndpoints.ANALYSES,
        SupportedEndpoints.GENOMES,
    ],
}


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

    def __call__(self, **kwargs):
        return self.filter(**kwargs)

    @property
    def accession(self):
        return self._params.get("accession", None)


class Analyses(ResourceProxy):
    def __init__(
        self,
        *,
        # study_accession: Optional[str] = None,
        # assembly_accession: Optional[str] = None,
        accession: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # if study_accession and assembly_accession:
        #     raise ValueError(
        #         "Can provide either study_accession or assembly_accession, or neither, but not both."
        #     )

        super().__init__(
            resource="analyses", params=params, accession=accession, **kwargs
        )


class Runs(ResourceProxy):
    def __init__(
        self,
        *,
        accession: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        pass  # TODO


class Samples(ResourceProxy):
    def __init__(
        self,
        *,
        accession: Optional[str] = None,
        study_accession: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        _one_acc = accession or study_accession

        if _one_acc:  # TODO validate accession format
            # init mgnifier
            super().__init__(
                resource="samples", accession=_one_acc, params=params, **kwargs
            )
            # get the endpoint module
            self.endpoint_module = list_mgnify_study_samples
        else:
            # if no acc then default to core list all samples endpoint
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


DEFAULT_LINKED_PROXY_CONFIG = {
    SupportedEndpoints.BIOMES: Studies,
    SupportedEndpoints.STUDIES: Samples,
    SupportedEndpoints.SAMPLES: None,  # TODO: Runs
    SupportedEndpoints.ANALYSES: MGazine,
    SupportedEndpoints.GENOMES: None,
    SupportedEndpoints.ASSEMBLIES: Analyses,
}
