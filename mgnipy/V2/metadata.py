import itertools
from typing import (
    Any,
    List,
    Literal,
    Optional,
)
from bigtree import (
    Tree,
)
from copy import deepcopy
from mgnipy.V2.core import Mgnifier
from mgnipy.V2.datasets import DatasetBuilder
from mgnipy.V2.mgni_py_v2.api.studies import (
    list_mgnify_study_analyses,
    list_mgnify_study_samples,
)
from mgnipy.V2.mgni_py_v2.api.analyses import (
    list_analyses_for_assembly,
)
from mgnipy._models.CONSTANTS import (
    SupportedEndpoints,
    StudiesPrefixes,
    AssembliesPrefixes,
)


class ResourceProxy(Mgnifier):
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

        if SupportedEndpoints.is_valid(resource):
            self._linked_proxy_module = DEFAULT_LINKED_PROXY_CONFIG.get(
                SupportedEndpoints(resource), None
            )

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

        if self._linked_proxy_module is not None:

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
        study_accession: Optional[str] = None,
        assembly_accession: Optional[str] = None,
        accession: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        if study_accession and assembly_accession:
            raise ValueError(
                "Can provide either study_accession or assembly_accession, or neither, but not both."
            )

        # give priority to accession
        _one_acc = accession or study_accession or assembly_accession

        # init mgnifier with accession
        super().__init__(accession=_one_acc, params=params, **kwargs)

        # determine endpoint module based on given accession type
        if StudiesPrefixes.starts_with(_one_acc):
            # list all analyses for given study accession
            self.endpoint_module = list_mgnify_study_analyses
        elif AssembliesPrefixes.starts_with(_one_acc):
            # list all analyses for given assembly accession
            self.endpoint_module = list_analyses_for_assembly
        elif _one_acc is None:
            # if None then default to core list all analyses endpoint
            super().__init__(resource="analyses", params=params, **kwargs)
        else:  # if accession provided but doesn't match known prefixes
            raise ValueError(f"Invalid accession: {_one_acc}. ")


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
            super().__init__(accession=_one_acc, params=params, **kwargs)
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

    def __getitem__(self, key) -> List[StudiesProxy] | StudiesProxy:
        # temporary override of unpageinate_results
        def _unpageinate_results(self):
            return itertools.chain.from_iterable(
                [
                    [
                        deepcopy(item).update({"acccession": item.get("lineage", None)})
                        or deepcopy(item)
                        for item in sublist
                    ]
                    for sublist in self._results
                ]
            )

        super().__getitem__(key)

    @property
    def lineages(self) -> List[str]:
        if self._results is None:
            raise RuntimeError(
                "No data available to get lineages. " "Please run get() first."
            )
        return self.to_pandas()["lineage"].to_list()

    @property
    def accessions(self) -> List[str]:
        # accessions == lineages, since biomes dont have accessions
        return self.lineages

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


class GenomesProxy(Mgnifier):
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
