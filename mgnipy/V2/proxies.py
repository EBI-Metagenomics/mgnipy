from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    ClassVar,
    Iterator,
    Literal,
    Optional,
)

from mgnipy._models.config import MgnipyConfig
from mgnipy._models.CONSTANTS import (
    SupportedEndpoints,
)
from mgnipy.V2.core import MGnifier
from mgnipy.V2.endpoints import (
    BETWEEN_RESOURCE_RELATIONSHIPS,
    PARENT_CHILD_RESOURCES,
    WITHIN_RESOURCE_RELATIONSHIPS,
)
from mgnipy.V2.mixins import BiomesTreeMixin

if TYPE_CHECKING:
    from mgnipy.V2.query_set import QuerySet

ListResource = Literal[
    "biomes",
    "studies",
    "samples",
    "runs",
    "analyses",
    "genomes",
    "assemblies",
    "publications",
    "catalogues",
]

DetailResource = Literal[
    "biome",
    "study",
    "sample",
    "run",
    "analysis",
    "genome",
    "assembly",
    "publication",
    "catalogue",
]


class MGnifyList(MGnifier):
    RESOURCE: ClassVar[Optional[ListResource]] = None

    def __init__(
        self,
        *,
        config: Optional[dict] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # Accept accidental "resource" in kwargs, but do not expose it in signature
        passed_resource = kwargs.pop("resource", None)
        resolved_resource = self.RESOURCE or passed_resource

        if resolved_resource is None:
            raise TypeError(
                "`resource` is required for base MGnifyList; "
                "use a concrete subclass like Analyses/Runs/... "
                f"or pass a resource param: {ListResource!r}"
            )

        if self.RESOURCE is not None and passed_resource not in (
            None,
            self.RESOURCE,
        ):
            raise ValueError(
                f"Conflicting resource: expected {self.RESOURCE!r}, got {passed_resource!r}"
            )

        super().__init__(
            resource=resolved_resource,
            params=params,
            config=config,
            **kwargs,
        )
        self.child_resource: str = PARENT_CHILD_RESOURCES.get(self.resource, None)

    def __call__(self, **kwargs) -> "MGnifyList":
        """
        Allow calling the list proxy to create a new instance with updated params.
        This is useful for refining the query with new parameters without having to re-specify the resource or config.

        Examples
        -------
        # Example 1: Using call to update params
        gut_studies = MG.studies(search="gut")
        # Example 2: Using params
        cancer_studies = MG.studies(params={"search": "cancer"})

        Note
        ----
        if "params" is included in kwargs, it will be used as the new params.
        Otherwise, all kwargs will be treated as params.
        """
        params = kwargs.pop("params", None) or {}
        # Merge with params, giving precedence to kwargs
        params.update(kwargs)

        return self.__class__(config=self.config.model_dump(mode="json"), params=params)

    @property
    def _next_rel_module(self) -> Callable:
        """
        Get the next relationship module for the child resource.
        This is used to determine which API endpoint the child proxy should use.
        """
        # check
        if len(self.list_relationships()) == 0:
            raise AttributeError(f"{self.resource} does not have any linked resources.")

        # quick check
        assert (
            len(self.list_relationships()) == 1
            and self.child_resource.value == self.list_relationships()[0]
        ), (
            "Should only be be parent to detail endpoint: "
            f"{self.child_resource!r}, but got {self.list_relationships()[0]!r}"
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
        for acc in self.results_ids or []:
            yield await self.aget_detail(self._resolve_id_param(acc), fetch=fetch)

    async def acollect_details(
        self,
        *,
        fetch: bool = False,
        by_accession: bool = False,
        concurrency: Optional[int] = None,
        hide_progress: bool = False,
    ) -> list["QuerySet"] | dict[str, "QuerySet"]:
        acc_params = [self._resolve_id_param(acc) for acc in (self.results_ids or [])]

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

        detail_cls = V2_ENDPOINT_DETAIL_PROXIES.get(self.child_resource)
        if not detail_cls:
            raise ValueError(
                f"Unsupported child resource for detail: {self.child_resource}"
            )

        child = detail_cls(**access_param)
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
        detail_cls = V2_ENDPOINT_DETAIL_PROXIES.get(self.child_resource)
        if not detail_cls:
            raise ValueError(
                f"Unsupported child resource for detail: {self.child_resource}"
            )
        child = detail_cls(**access_param)
        child.endpoint_module = self._next_rel_module
        if fetch:
            await child.aget(safety=False)
        return child


class MGnifyDetail(MGnifier):
    RESOURCE: ClassVar[Optional[DetailResource]] = None

    def __init__(
        self,
        id: str,
        config: Optional[MgnipyConfig] = None,
        **kwargs,
    ):

        passed_resource = kwargs.pop("resource", None)
        resolved_resource = self.RESOURCE or passed_resource

        if resolved_resource is None:
            raise TypeError(
                "`resource` is required for base MGnifyDetail; "
                "init a concrete subclass like Biome/Study/Sample... "
                f"or pass as a resource param: {DetailResource!r}"
            )

        if self.RESOURCE is not None and passed_resource not in (
            None,
            self.RESOURCE,
        ):
            raise ValueError(
                f"Conflicting resource: expected {self.RESOURCE!r}, got {passed_resource!r}"
            )

        # init MGnifier without id first
        super().__init__(resource=resolved_resource, config=config, **kwargs)
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

        proxy_cls = V2_ENDPOINT_LIST_PROXIES.get(SupportedEndpoints.validate(resource))
        if not proxy_cls:
            raise ValueError(f"Unsupported resource: {resource}")
        child = proxy_cls(config=self.config.model_dump(mode="json"), **access_param)
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

        proxy_cls = V2_ENDPOINT_LIST_PROXIES.get(SupportedEndpoints.validate(resource))
        if not proxy_cls:
            raise ValueError(f"Unsupported resource: {resource}")
        child = proxy_cls(config=self.config.model_dump(mode="json"), **access_param)
        child.endpoint_module = self._next_rel_module(resource)
        if explain:
            child.explain()
        if fetch:
            await child.aget(safety=False)
        return child


class Analyses(MGnifyList):
    RESOURCE: ClassVar[Literal["analyses"]] = "analyses"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[MgnipyConfig] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)


class Runs(MGnifyList):

    RESOURCE: ClassVar[Literal["runs"]] = "runs"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[MgnipyConfig] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)


class Samples(MGnifyList):
    RESOURCE: ClassVar[Literal["samples"]] = "samples"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)


class Studies(MGnifyList):

    RESOURCE: ClassVar[Literal["studies"]] = "studies"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)


class Biomes(MGnifyList, BiomesTreeMixin):
    RESOURCE: ClassVar[Literal["biomes"]] = "biomes"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)


class Assemblies(MGnifyList):
    RESOURCE: ClassVar[Literal["assemblies"]] = "assemblies"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)


class Genomes(MGnifyList):
    RESOURCE: ClassVar[Literal["genomes"]] = "genomes"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)


class Publications(MGnifyList):
    RESOURCE: ClassVar[Literal["publications"]] = "publications"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(params=params, config=config, **kwargs)


class Catalogues(MGnifyList):
    RESOURCE: ClassVar[Literal["catalogues"]] = "catalogues"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(params=params, config=config, **kwargs)


class StudyDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["study"]] = "study"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or accession,
            config=config,
            **kwargs,
        )


class SampleDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["sample"]] = "sample"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or accession,
            config=config,
            **kwargs,
        )


class RunDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["run"]] = "run"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or accession,
            config=config,
            **kwargs,
        )


class AnalysisDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["analysis"]] = "analysis"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or accession,
            config=config,
            **kwargs,
        )


class GenomeDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["genome"]] = "genome"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or accession,
            config=config,
            **kwargs,
        )


class AssemblyDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["assembly"]] = "assembly"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or accession,
            config=config,
            **kwargs,
        )


class BiomeDetail(MGnifyDetail, BiomesTreeMixin):
    RESOURCE: ClassVar[Literal["biome"]] = "biome"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or accession,
            config=config,
            **kwargs,
        )


class PublicationDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["publication"]] = "publication"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or accession,
            config=config,
            **kwargs,
        )


class CatalogueDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["catalogue"]] = "catalogue"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or accession,
            config=config,
            **kwargs,
        )


V2_ENDPOINT_LIST_PROXIES = {
    SupportedEndpoints.ANALYSES: Analyses,
    SupportedEndpoints.RUNS: Runs,
    SupportedEndpoints.SAMPLES: Samples,
    SupportedEndpoints.STUDIES: Studies,
    SupportedEndpoints.BIOMES: Biomes,
    SupportedEndpoints.ASSEMBLIES: Assemblies,
    SupportedEndpoints.GENOMES: Genomes,
}

V2_ENDPOINT_DETAIL_PROXIES = {
    SupportedEndpoints.ANALYSIS: AnalysisDetail,
    SupportedEndpoints.RUN: RunDetail,
    SupportedEndpoints.SAMPLE: SampleDetail,
    SupportedEndpoints.STUDY: StudyDetail,
    SupportedEndpoints.BIOME: BiomeDetail,
    SupportedEndpoints.ASSEMBLY: AssemblyDetail,
    SupportedEndpoints.GENOME: GenomeDetail,
}
