from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Iterator,
    List,
    Literal,
    Optional,
)

from bigtree import (
    Tree,
)

from mgnipy._models.config import MgnipyConfig
from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.core import MGnifier
from mgnipy.V2.endpoints import (
    BETWEEN_RESOURCE_RELATIONSHIPS,
    PARENT_CHILD_RESOURCES,
    WITHIN_RESOURCE_RELATIONSHIPS,
)
from mgnipy.V2.mixins import BiomesTreeMixin

if TYPE_CHECKING:
    from mgnipy.V2.query_set import QuerySet


class MGnifyList(MGnifier):
    """generic"""

    def __init__(
        self,
        resource: Literal[
            "biomes",
            "studies",
            "samples",
            "runs",
            "genomes",
            "analyses",
            "assemblies",
            "publications",
            "catalogues",
        ],
        *,
        config: Optional[dict] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # init mgnifier
        super().__init__(
            resource=resource,
            params=params,
            config=config,
            **kwargs,
        )

        self.child_resource: str = PARENT_CHILD_RESOURCES.get(self.resource, None)

    @property
    def _next_rel_module(self) -> SupportedEndpoints:
        """
        Get the next resource name based on the relationship name
        """
        # check
        if len(self.list_relationships) == 0:
            raise AttributeError(f"{self.resource} does not have any linked resources.")

        # quick check
        # quick check
        assert [self.child_resource] == self.list_relationships(), (
            "Should only be be parent to detail endpoint: "
            f"{self.child_resource}, but got {self.list_relationships()}"
        )

        detail_endpoint = WITHIN_RESOURCE_RELATIONSHIPS[self.resource][
            self.child_resource
        ]
        return detail_endpoint

    def iter_details(self, fetch: bool = False) -> Iterator["QuerySet"]:
        """
        Lazily iterate over child detail proxies.

        Parameters
        ----------
        fetch : bool
            Whether to immediately fetch each detail after creating the proxy.

        Returns
        -------
        Iterator of QuerySet
            An iterator that yields child detail proxies.

        Example
        -------
        for sample in samples.iter_details():
            sample.get()
        """
        for acc in self.results_ids or []:
            yield self.get_detail(self._resolve_id_param(acc), fetch=fetch)

    def collect_details(
        self,
        *,
        fetch: bool = False,
        by_accession: bool = False,
    ) -> list["QuerySet"] | dict[str, "QuerySet"]:
        """
        Collect child detail proxies into a list or dict.

        Parameters
        ----------
        fetch : bool
            Whether to immediately fetch the details after creating the proxies.
        by_accession : bool
            Whether to return a dict keyed by accession instead of a list.

        Returns
        -------
        list of QuerySet or dict of str to QuerySet
            A list or dict of child detail proxies.

        Example
        -------
        samples.collect_details(fetch=True, by_accession=True)


        """

        items: list["QuerySet"] = []
        for item in self.iter_details(fetch=fetch):
            items.append(item)

        if by_accession:
            return {x.accession: x for x in items if x.accession is not None}
        return items

    def __iter__(self) -> Iterator["QuerySet"]:
        return self.iter_details()

    async def __aiter__(self) -> AsyncIterator["QuerySet"]:
        async for item in self.aiter_details():
            yield item

    async def aiter_details(self, fetch: bool = False) -> AsyncIterator["QuerySet"]:
        for acc in self.results_accessions or []:
            yield await self.aget_detail(self._resolve_id_param(acc), fetch=fetch)

    async def acollect_details(
        self,
        *,
        fetch: bool = False,
        by_accession: bool = False,
        concurrency: Optional[int] = None,
        hide_progress: bool = False,
    ) -> list["QuerySet"] | dict[str, "QuerySet"]:
        acc_params = [
            self._resolve_id_param(acc) for acc in (self.results_accessions or [])
        ]

        async def _worker(access_param):
            child = await self.aget_detail(access_param, fetch=fetch)
            return child

        items = await self.exec.map_with_concurrency(
            items=acc_params,
            worker=_worker,
            concurrency=concurrency,
            hide_progress=hide_progress,
        )

        if by_accession:
            return {
                x.accession: x
                for x in items
                if x is not None and x.accession is not None
            }
        return items

    def __getitem__(self, key: int | str) -> "QuerySet":
        """
        Allow index or accession-based access to child details.
        Default is not lazy and will fetch immediately, but can be configured to return proxies without fetching.
        """
        return self.get_detail(
            self._resolve_id_param(key),
            fetch=True,
        )

    def get_detail(
        self,
        access_param: dict[str, str],
        fetch: bool = True,
    ) -> "QuerySet":
        """
        Get detail proxy for a specific accession/pubmed_id/catalogue_id.

        Parameters
        ----------
        access_param : dict[str, str]
            A dictionary containing the necessary parameter to identify the detail resource,
            such as {"accession": "MGYS00001234"} or {"biome_lineage": "root"}.
        resource_name : Optional[str]
            The name of the resource to get the next instance of. If None, will use the first or only linked resource.
        fetch : bool
            Whether to immediately fetch the detail after creating the proxy.


        Returns
        -------
        QuerySet
            A proxy for the next resource.

        Examples
        -------
        sample = samples.get_detail({"accession": "MGYS00001234"})
        """

        child = self._clone(resource=self.child_resource, **access_param)
        child.endpoint_module = self._next_rel_module
        if fetch:
            child.get(safety=False)
        return child

    async def aget_detail(
        self,
        access_param: dict[str, str],
        fetch: bool = True,
    ) -> "QuerySet":
        """
        Async version of get_detail.
        Get detail proxy for a specific accession/pubmed_id/catalogue_id.

        Examples
        -------
        sample = await samples.aget_detail({"accession": "MGYS00001234"})
        """
        child = self._clone(resource=self.child_resource, **access_param)
        child.endpoint_module = self._next_rel_module
        if fetch:
            await child.aget(safety=False)
        return child


class MGnifyDetail(MGnifier):
    """waht"""

    def __init__(
        self,
        resource: Literal[
            "biome",
            "study",
            "sample",
            "run",
            "genome",
            "analysis",
            "assembly",
            "publication",
            "catalogue",
        ],
        id: str,
        config: Optional[MgnipyConfig] = None,
        **kwargs,
    ):
        self._config = config

        # init MGnifier without id first
        super().__init__(resource=resource, config=self._config, **kwargs)
        # then add it to param
        self._params.update({self.id_param_key: id})

    def _next_rel_module(self, name: str) -> SupportedEndpoints:
        """
        Get the next resource name based on the relationship name
        """
        if name in self.list_relationships():
            return BETWEEN_RESOURCE_RELATIONSHIPS[self.resource][
                SupportedEndpoints.validate(name)
            ]

        raise AttributeError(f"{self.resource} does not have linked resource: {name!r}")

    def __getattr__(self, name: str):
        # if is a supported relationship
        if name in self.list_relationships():

            access_param = self._resolve_id_param(self.identifier)

            return self.get_list(
                resource=name,
                access_param=access_param,
                fetch=False,
            )

    def get_list(
        self,
        resource: Literal[
            "biomes",
            "studies",
            "samples",
            "runs",
            "genomes",
            "analyses",
            "assemblies",
            "publications",
            "catalogues",
        ],
        access_param: dict[str, str],
        fetch: bool = True,
        explain: bool = False,
    ) -> "QuerySet":
        """
        Get list proxy for a specific accession/pubmed_id/catalogue_id detail.

        Parameters
        ----------
        resource : str
            Valid child resource name e.g. in list_relationships(), such as "samples" for a study detail, or "analyses" for a run detail.
        access_param : dict[str, str]
            A dictionary containing the necessary parameter to identify the detail resource,
            such as {"accession": "MGYS00001234"} or {"biome_lineage": "root"}.
        fetch : bool
            Whether to immediately fetch the detail after creating the proxy.
        explain : bool
            Whether to print example URLs that would be called.
        Returns
        -------
        QuerySet
            A proxy for the next resource.

        Examples
        -------
        samples = study.get_list("samples", {"accession": "MGYS00001234"})
        """

        child = MGnifyList(resource=resource, config=self._config, **access_param)
        child.endpoint_module = self._next_rel_module(resource)
        if explain:
            child.explain()
        if fetch:
            child.get(safety=False)
        return child

    async def aget_list(
        self,
        resource: Literal[
            "biomes",
            "studies",
            "samples",
            "runs",
            "genomes",
            "analyses",
            "assemblies",
            "publications",
            "catalogues",
        ],
        access_param: dict[str, str],
        fetch: bool = True,
        explain: bool = False,
    ) -> "QuerySet":
        """
        Get list proxy for a specific accession/pubmed_id/catalogue_id detail.

        Parameters
        ----------
        resource : str
            Valid child resource name e.g. in list_relationships(), such as "samples" for a study detail, or "analyses" for a run detail.
        access_param : dict[str, str]
            A dictionary containing the necessary parameter to identify the detail resource,
            such as {"accession": "MGYS00001234"} or {"biome_lineage": "root"}.
        fetch : bool
            Whether to immediately fetch the detail after creating the proxy.

        Returns
        -------
        QuerySet
            A proxy for the next resource.

        Examples
        -------
        samples = await study.aget_list("samples", {"accession": "MGYS00001234"})
        """

        child = self._clone(resource=resource, config=self._config, **access_param)
        child.endpoint_module = self._next_rel_module(resource)
        if explain:
            child.explain()
        if fetch:
            await child.aget(safety=False)
        return child


class Analyses(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[MgnipyConfig] = None,
        **kwargs,
    ):

        super().__init__(resource="analyses", params=params, config=config, **kwargs)


class Runs(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[MgnipyConfig] = None,
        **kwargs,
    ):

        super().__init__(resource="runs", params=params, config=config, **kwargs)


class Samples(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[MgnipyConfig] = None,
        **kwargs,
    ):

        super().__init__(resource="samples", params=params, config=config, **kwargs)


class Studies(MGnifyList):

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(resource="studies", **kwargs)


class Biomes(MGnifyList, BiomesTreeMixin):

    def __init__(self, **kwargs):
        super().__init__(resource="biomes", **kwargs)

    @property
    def lineages(self) -> List[str]:
        if self._results is None:
            raise RuntimeError(
                "No data available to get lineages. Please run get() first."
            )
        return self.results_ids

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


class Assemblies(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="assemblies", params=params, **kwargs)


class Genomes(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # TODO
        super().__init__(resource="genomes", params=params, **kwargs)


class Publications(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="publications", params=params, **kwargs)


class Catalogues(MGnifyList):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="catalogues", params=params, **kwargs)


class StudyDetail(MGnifyDetail):
    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        **kwargs,
    ):

        super().__init__(
            resource="study",
            id=id or accession,
            **kwargs,
        )


class SampleDetail(MGnifyDetail):
    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        **kwargs,
    ):

        super().__init__(
            resource="sample",
            id=id or accession,
            **kwargs,
        )


class RunDetail(MGnifyDetail):
    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        **kwargs,
    ):

        super().__init__(
            resource="run",
            id=id or accession,
            **kwargs,
        )


class AnalysisDetail(MGnifyDetail):
    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        **kwargs,
    ):

        super().__init__(
            resource="analysis",
            id=id or accession,
            **kwargs,
        )


class GenomeDetail(MGnifyDetail):
    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        **kwargs,
    ):

        super().__init__(
            resource="genome",
            id=id or accession,
            **kwargs,
        )


class AssemblyDetail(MGnifyDetail):
    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        **kwargs,
    ):

        super().__init__(
            resource="assembly",
            id=id or accession,
            **kwargs,
        )


class BiomeDetail(MGnifyDetail, BiomesTreeMixin):
    def __init__(
        self,
        id: Optional[str] = None,
        *,
        biome_lineage: Optional[str] = None,
        **kwargs,
    ):

        super().__init__(
            resource="biome",
            id=id or biome_lineage,
            **kwargs,
        )


class PublicationDetail(MGnifyDetail):
    def __init__(
        self,
        id: Optional[str] = None,
        *,
        pubmed_id: Optional[str] = None,
        **kwargs,
    ):

        super().__init__(
            resource="publication",
            id=id or pubmed_id,
            **kwargs,
        )


class CatalogueDetail(MGnifyDetail):
    def __init__(
        self,
        id: Optional[str] = None,
        *,
        catalogue_id: Optional[str] = None,
        **kwargs,
    ):

        super().__init__(
            resource="catalogue",
            id=id or catalogue_id,
            **kwargs,
        )
