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
    AssembliesPrefixes,
    StudiesPrefixes,
    SupportedEndpoints,
)
from mgnipy.V2.core import MGnifier
from mgnipy.V2.datasets import DatasetBuilder
from mgnipy.V2.mgni_py_v2.api.analyses import (
    list_analyses_for_assembly,
)
from mgnipy.V2.mgni_py_v2.api.studies import (
    list_mgnify_study_analyses,
    list_mgnify_study_samples,
)


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
        super().__init__(resource=resource, params=params, **kwargs)

        if SupportedEndpoints.is_valid(self._resource):
            self._linked_proxy_module = DEFAULT_LINKED_PROXY_CONFIG.get(
                SupportedEndpoints(self._resource), None
            )
        else:
            self._linked_proxy_module = None

    @property
    def linked_proxy_module(self):
        return self._linked_proxy_module

    @property
    def accession(self):
        return self._params.get("accession", None)

    def __getitem__(self, key):
        """
        Get a linked proxy object based on the provided key.
        The key can be an integer index, a slice, or a valid accession string (or lineage for biomes).
        """

        if self.linked_proxy_module is not None:

            results_list = list(self._unpageinate_results())

            # next proxy
            if isinstance(key, str) and key in self.results_accessions:
                return self.linked_proxy_module(accession=key)
            elif isinstance(key, int) and self.results_accessions:
                return self.linked_proxy_module(
                    accession=results_list[key]["accession"]
                )
            elif isinstance(key, slice) and self.results_accessions:
                return [
                    self.linked_proxy_module(accession=record["accession"])
                    for record in results_list[key]
                ]
            elif self.results_accessions is None:
                raise RuntimeError(
                    "No accessions available for indexing. "
                    "E.g., run get() first to retrieve metadata and accessions."
                )
            else:
                raise KeyError(
                    f"Invalid key: {key}. "
                    "Key must be an integer index, a slice, or a valid accession string."
                )
        else:
            # to mgnifier's __getitem__
            super().__getitem__(key)


class AnalysesProxy(ResourceProxy):
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
        if accession is not None:
            # determine endpoint module based on given accession type
            self._auto_endpoint_based_on_accession_prefix()

    def _auto_endpoint_based_on_accession_prefix(self):
        # if self.accession is None:
        #     self.resource = "analyses"
        if StudiesPrefixes.is_prefix_in(self.accession):
            self.endpoint_module = list_mgnify_study_analyses
        elif AssembliesPrefixes.is_prefix_in(self.accession):
            self.endpoint_module = list_analyses_for_assembly
        else:
            raise ValueError(f"Invalid accession: {self.accession}. ")

    def filter(
        self,
        **filters,
    ):
        """
        Update the parameters for the API call to filter results.

        Parameters
        ----------
        **filters
            Keyword arguments corresponding to the supported parameters for the current resource.
            These will be used to filter the results returned by the API.

        Returns
        -------
        MGnifier
            A new MGnifier instance with updated parameters for filtering results.
        """
        # make a copy of current instance
        new_mg = self._clone()
        # but with updates to params
        new_mg._params.update(filters)
        if "accession" in filters:
            new_mg._auto_endpoint_based_on_accession_prefix()
        return new_mg


class SamplesProxy(ResourceProxy):
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


class StudiesProxy(ResourceProxy):

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="studies", params=params, **kwargs)


class BiomesProxy(ResourceProxy):

    def __init__(self, **kwargs):
        super().__init__(resource="biomes", **kwargs)

    def __getitem__(self, key) -> list[StudiesProxy] | StudiesProxy:
        """
        Get a linked proxy object based on the provided key.
        The key can be an integer index, a slice, or a valid accession string (or lineage for biomes).
        """

        if self.linked_proxy_module is not None:

            results_list = list(self._unpageinate_results())

            # next proxy
            if isinstance(key, str) and key in self.lineages:
                return self.linked_proxy_module(accession=key)
            elif isinstance(key, int) and self.lineages:
                return self.linked_proxy_module(accession=results_list[key]["lineage"])
            elif isinstance(key, slice) and self.lineages:
                return [
                    self.linked_proxy_module(accession=record["lineage"])
                    for record in results_list[key]
                ]
            elif self.lineages is None:
                raise RuntimeError(
                    "No lineages available for indexing. "
                    "E.g., run get() first to retrieve."
                )
            else:
                raise KeyError(
                    f"Invalid key: {key}. "
                    "Key must be an integer index, a slice, or a valid lineage string."
                )
        else:
            # to mgnifier's __getitem__
            super().__getitem__(key)

    @property
    def lineages(self) -> List[str]:
        if self._results is None:
            raise RuntimeError(
                "No data available to get lineages. " "Please run get() first."
            )
        return self.to_pandas()["lineage"].to_list()

    @property
    def tree(self) -> Tree:
        """
        Convert the biomes metadata to a tree structure for visualization or analysis.

        Returns
        -------
        Tree
            A tree representation of the biomes and their relationships.
        """
        if self._results is None:
            raise RuntimeError(
                "No data available to convert to tree. " "Please run get() first."
            )
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


class AssembliesProxy(ResourceProxy):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="assemblies", params=params, **kwargs)


class GenomesProxy(ResourceProxy):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # TODO
        super().__init__(resource="genomes", params=params, **kwargs)


DEFAULT_LINKED_PROXY_CONFIG = {
    SupportedEndpoints.BIOMES: StudiesProxy,
    SupportedEndpoints.STUDIES: SamplesProxy,
    SupportedEndpoints.SAMPLES: None,  # TODO: RunsProxy
    SupportedEndpoints.ANALYSES: DatasetBuilder,
    SupportedEndpoints.GENOMES: None,
    SupportedEndpoints.ASSEMBLIES: AnalysesProxy,
}
