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
    "private_studies",
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
    """Base class for MGnify list endpoints.

    Concrete subclasses bind a specific list resource such as studies, samples,
    or analyses. Calling the proxy returns a new instance with merged filters.
    """

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
        """Return a cloned list proxy with updated parameters.

        Parameters
        ----------
        **kwargs
            Query parameters to merge into the current parameter set. If
            ``params`` is supplied, it replaces the current parameters before
            the remaining keyword arguments are merged in.

        Returns
        -------
        MGnifyList
            A new proxy instance with the same resource and updated filters.

        Examples
        --------
        >>> from mgnipy.V2.proxies import Studies
        >>> studies = Studies(params={"search": "gut"}, config={})  # doctest: +SKIP
        >>> studies(search="soil")  # doctest: +SKIP
        """
        params = kwargs.pop("params", None) or {}
        # Merge with params, giving precedence to kwargs
        params.update(kwargs)

        return self.__class__(config=self.config.model_dump(mode="json"), params=params)

    def __len__(self) -> int:
        """Return the number of child details based on results.

        Examples
        --------
        >>> from mgnipy.V2.proxies import Studies  # doctest: +SKIP
        >>> studies = Studies(config={})  # doctest: +SKIP
        >>> len(studies)  # doctest: +SKIP
        """
        return len(self.results_ids or [])

    def _reset_detail_iterator(self) -> None:
        """
        Initialize or reset the internal state for iterating over MGnifyDetails
        """
        # if refresh:
        #     try:
        #         self.exec.first()
        #     except Exception:
        #         pass
        self._detail_ids = list(self.results_ids or [])
        self._detail_index = 0
        self._last_successful_detail = None

    def get_detail(
        self,
    ) -> Optional["MGnifyDetail"]:
        """
        Get the next MGnifyDetail based on current _detail_index.
        Updates `_last_successful_detail` on success.

        Returns
        -------
        MGnifyDetail or None
             The next detail proxy, or None if no more details to iterate.

        Example
        -------
        >>> from mgnipy.V2.proxies import Studies  # doctest: +SKIP
        >>> studies = Studies(search="tomato")  # doctest: +SKIP
        >>> studies.bulk_fetch()  # doctest: +SKIP
        >>> first_detail = studies.get_detail()  # doctest: +SKIP
        >>> second_detail = studies.get_detail()  # doctest: +SKIP
        """
        if not hasattr(self, "_detail_ids"):
            self._reset_detail_iterator()

        if self._detail_index >= len(self._detail_ids):
            # nothing left to iter
            return None

        # otherwise return next MGnifyDetail in the list
        the_id = self._detail_ids[self._detail_index]
        child = self._single_detail(self._resolve_id_param(the_id))
        # update counters
        self._detail_index += 1
        self._last_successful_detail = self._detail_index - 1
        return child

    async def aget_detail(self) -> "MGnifyDetail":
        """
        Async variant of `get_detail`.

        Returns
        -------
        MGnifyDetail or None
             The next detail proxy, or None if no more details to iterate.

        """
        if not hasattr(self, "_detail_ids"):
            self._reset_detail_iterator()

        if self._detail_index >= len(self._detail_ids):
            return None

        the_id = self._detail_ids[self._detail_index]
        child = await self._asingle_detail(self._resolve_id_param(the_id))

        self._detail_index += 1
        self._last_successful_detail = self._detail_index - 1
        return child

    def continue_detail_iterator(
        self, start_index: Optional[int] = None
    ) -> "MGnifyList":
        """
        Continue iterating for MGnifyDetails from `start_index` or the next index after the last successful detail.

        Parameters
        ----------
        start_index : int, optional
             The index to continue from. If None, will continue from the next index after the last successful detail, or 0 if no successful detail yet.

        Returns
        -------
        MGnifyList
            The current instance with the detail iterator reset to the specified index.

        """
        # ensure the detail ids are initialized
        if not hasattr(self, "_detail_ids"):
            self._reset_detail_iterator()

        # if start_index is not provided
        if start_index is None:
            # if no successful detail yet, start from the beginning
            if getattr(self, "_last_successful_detail", None) is None:
                start_index = 0
            # otherwise continue from the next index after the last successful detail
            else:
                start_index = self._last_successful_detail + 1

        # validate start_index
        if not (0 <= start_index <= len(self._detail_ids)):
            raise ValueError("start_index out of range")

        self._detail_index = start_index
        return self

    def resume_detail_iterator(self) -> "MGnifyList":
        """
        Resume from the element after the last successful MGnifyDetail fetch.

        Returns
        -------
        MGnifyList
            The current instance with the detail iterator reset to the specified index.

        Raises
        ------
        RuntimeError
            If there is no last successful detail to resume from.
        """
        if getattr(self, "_last_successful_detail", None) is None:
            raise RuntimeError("No last successful detail to resume from")
        return self.continue_detail_iterator(self._last_successful_detail + 1)

    @property
    def _detail_endpoint(self) -> Callable:
        """
        Return the endpoint module for the child/detail endpoint.

        Returns
        -------
        Callable
            The endpoint function or module used by the child resource.
            E.g., mgnipy.emgapi_v2_client.studies.get_study_detail

        Examples
        --------
        >>> from mgnipy.V2.proxies import Studies  # doctest: +SKIP
        >>> studies = Studies()  # doctest: +SKIP
        >>> studies._detail_endpoint

        """  # check
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

    def iter_details(self, fetch: bool = True) -> Iterator["QuerySet"]:
        """Yield child detail proxies one by one.

        Parameters
        ----------
        fetch : bool, default=True
            If ``True``, fetch each detail immediately after creating the
            proxy.

        Returns
        -------
        Iterator[QuerySet]
            Iterator over child detail proxies.

        Examples
        --------
        >>> from mgnipy.V2.proxies import Studies  # doctest: +SKIP
        >>> studies = Studies(config={})  # doctest: +SKIP
        >>> next(studies.iter_details())  # doctest: +SKIP
        """
        for acc in self.results_ids or []:
            yield self._single_detail(self._resolve_id_param(acc), fetch=fetch)

    def _single_detail(
        self,
        access_param: dict[str, str],
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

        Returns
        -------
        MGnifyDetail
            A proxy for the child/detail for the given id

        Examples
        -------
        sample = samples._single_detail({"accession": "MGYS00001234"})
        """

        detail_cls = V2_ENDPOINT_DETAIL_PROXIES.get(self.child_resource)
        if not detail_cls:
            raise ValueError(
                f"Unsupported child resource for detail: {self.child_resource}"
            )

        child = detail_cls(**access_param)
        child.endpoint_module = self._detail_endpoint
        child.get()
        return child

    def collect_details(
        self,
        *,
        fetch: bool = True,
        by_id: bool = False,
    ) -> list["QuerySet"] | dict[str, "QuerySet"]:
        """Collect child detail proxies into a list or mapping.

        Parameters
        ----------
        fetch : bool, default=True
            If ``True``, fetch each detail immediately after creating the
            proxy.
        by_id : bool, default=False
            If ``True``, return a dictionary keyed by identifier.

        Returns
        -------
        list[QuerySet] or dict[str, QuerySet]
            Child detail proxies, optionally keyed by identifier.

        Examples
        --------
        >>> from mgnipy.V2.proxies import Studies  # doctest: +SKIP
        >>> studies = Studies(config={})  # doctest: +SKIP
        >>> studies.collect_details(by_id=True)  # doctest: +SKIP
        """
        items: list["QuerySet"] = []
        for item in self.iter_details(fetch=fetch):
            items.append(item)

        if by_id:
            return {x.identifier: x for x in items if x.identifier is not None}
        return items

    async def aiter_details(self, fetch: bool = True) -> AsyncIterator["QuerySet"]:
        """
        Async version of iter_details.

        Parameters
        ----------
        fetch : bool
            Whether to immediately fetch each detail after creating the proxy.

        Returns
        -------
        AsyncIterator of QuerySet
            An async iterator that yields child detail proxies.
        """
        for acc in self.results_ids or []:
            yield await self._asingle_detail(self._resolve_id_param(acc), fetch=fetch)

    async def acollect_details(
        self,
        *,
        fetch: bool = True,
        by_id: bool = False,
        concurrency: Optional[int] = None,
        hide_progress: bool = False,
    ) -> list["QuerySet"] | dict[str, "QuerySet"]:
        acc_params = [self._resolve_id_param(acc) for acc in (self.results_ids or [])]

        async def _worker(access_param):
            child = await self._asingle_detail(access_param, fetch=fetch)
            return child

        items = await self.exec.map_with_concurrency(
            items=acc_params,
            worker=_worker,
            concurrency=concurrency,
            hide_progress=hide_progress,
        )

        if by_id:
            return {
                x.identifier: x
                for x in items
                if x is not None and x.identifier is not None
            }
        return items

    def __getitem__(self, key: int | str) -> "QuerySet":
        """
        Allow index or accession-based access to child details.
        Default is not lazy and will fetch immediately, but can be configured to return proxies without fetching.
        """
        return self._single_detail(
            self._resolve_id_param(key),
        )

    async def _asingle_detail(
        self,
        access_param: dict[str, str],
        fetch: bool = True,
    ) -> "QuerySet":
        """
        Async version of _single_detail.
        Get detail proxy for a specific accession/pubmed_id/catalogue_id.

        Examples
        -------
        sample = await samples._asingle_detail({"accession": "MGYS00001234"})
        """
        detail_cls = V2_ENDPOINT_DETAIL_PROXIES.get(self.child_resource)
        if not detail_cls:
            raise ValueError(
                f"Unsupported child resource for detail: {self.child_resource}"
            )
        child = detail_cls(**access_param)
        child.endpoint_module = self._detail_endpoint
        if fetch:
            await child.aget(safety=False)
        return child

    def page_size(self, n: int) -> "QuerySet":
        """
        Set the page size for paginated API calls.

        Parameters
        ----------
        n : int

        Returns
        -------
        QuerySet
            A new QuerySet instance with the updated page size parameter.
        """
        if not isinstance(n, int) or n <= 0:
            raise ValueError("Page size must be a positive integer.")

        # make a copy of current instance
        new_qs = self._clone(page_size=n)
        return new_qs


class MGnifyDetail(MGnifier):
    RESOURCE: ClassVar[Optional[DetailResource]] = None

    def __init__(
        self,
        id: str,
        config: Optional[dict] = None,
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

    @property
    def identifier(self) -> Optional[str]:
        """Get the identifier value from the query parameters.

        Used for constructing URLs to related resources.

        Returns
        -------
        str or None
            The identifier value, or ``None`` if not set.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies", accession="MGYS000000001", config={})  # doctest: +SKIP
        >>> query.identifier  # doctest: +SKIP
        """
        try:
            return self.params[self.id_param_key]
        except KeyError:
            raise AttributeError(
                f"Identifier key '{self.id_param_key}' not found in parameters for resource '{self.resource}'."
            ) from None

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
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)


class Runs(MGnifyList):

    RESOURCE: ClassVar[Literal["runs"]] = "runs"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
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


class PrivateStudies(MGnifyList):

    RESOURCE: ClassVar[Literal["private_studies"]] = "private_studies"

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
        biome_lineage: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or biome_lineage,
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
    SupportedEndpoints.PUBLICATIONS: Publications,
    SupportedEndpoints.CATALOGUES: Catalogues,
    SupportedEndpoints.PRIVATE_STUDIES: PrivateStudies,
}

V2_ENDPOINT_DETAIL_PROXIES = {
    SupportedEndpoints.ANALYSIS: AnalysisDetail,
    SupportedEndpoints.RUN: RunDetail,
    SupportedEndpoints.SAMPLE: SampleDetail,
    SupportedEndpoints.STUDY: StudyDetail,
    SupportedEndpoints.BIOME: BiomeDetail,
    SupportedEndpoints.ASSEMBLY: AssemblyDetail,
    SupportedEndpoints.GENOME: GenomeDetail,
    SupportedEndpoints.PUBLICATION: PublicationDetail,
    SupportedEndpoints.CATALOGUE: CatalogueDetail,
    SupportedEndpoints.ANNOTATIONS: None,  # "MGazine",
}
