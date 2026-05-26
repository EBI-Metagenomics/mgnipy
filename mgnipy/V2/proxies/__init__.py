from __future__ import annotations

import logging
import re
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

import pandas as pd

from mgnipy._models.constants.CONSTANTS import (
    PipelineVersions,
    SupportedEndpoints,
)
from mgnipy.V2.core import ID_PARAM, MGnifier
from mgnipy.V2.endpoints import (
    BETWEEN_RESOURCE_RELATIONSHIPS,
    PARENT_CHILD_RESOURCES,
    WITHIN_RESOURCE_RELATIONSHIPS,
)

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

        self._collected_details: dict[str, "MGnifyDetail"] = {}
        self._collected_details_results: dict[str, dict] = {}
        self._collected_details_downloads: dict[str, list[dict[str, Any]]] = {}

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

        return self.__class__(config=self.config, params=params)

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
        logging.debug(
            f"Fetching detail for {self.child_resource!r} with id {the_id!r} (index {self._detail_index})"
        )
        child = self._single_detail(the_id)
        # update counters
        self._detail_index += 1
        self._last_successful_detail = self._detail_index - 1
        return child.page(1)

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
        child = await self._asingle_detail(the_id)

        self._detail_index += 1
        self._last_successful_detail = self._detail_index - 1
        return await child.apage(1)

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
        >>> from mgnipy.V2.proxies import Studies
        >>> studies = Studies()
        >>> studies._detail_endpoint
        <module 'mgnipy.emgapi_v2_client.api.studies.get_mgnify_study' from '/Users/phanthanourak/github/mgnipy/mgnipy/emgapi_v2_client/api/studies/get_mgnify_study.py'>
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

    @property
    def iter_details(self) -> Iterator[dict]:
        """
        Yield MGnifyDetail results one by one.

        Returns
        -------
        Iterator[dict]
            An iterator that yields MGnifyDetail results one by one, fetched on demand.

        Examples
        --------
        >>> from mgnipy.V2.proxies import Studies  # doctest: +SKIP
        >>> studies = Studies()  # doctest: +SKIP
        >>> result_dict = next(studies.iter_details)  # doctest: +SKIP
        """
        for acc in self.results_ids or []:
            yield self._single_detail(acc).page(1)

    @property
    async def aiter_details(self) -> AsyncIterator[dict]:
        """
        Async version of iter_details.

        Returns
        -------
        AsyncIterator[dict]
            An async iterator that yields MGnifyDetail results one by one, fetched on demand.
        """
        for acc in self.results_ids or []:
            child = await self._asingle_detail(acc)
            yield await child.apage(1)

    def _single_detail(
        self,
        key: str | int,
    ) -> "MGnifyDetail":
        """
        Get detail proxy for a specific accession/pubmed_id/catalogue_id.

        Parameters
        ----------
        key : str | int
            The identifier for the detail resource, or an integer index to look up the identifier from results_ids.

        Returns
        -------
        MGnifyDetail
            A proxy for the child/detail for the given key

        Examples
        -------
        sample = samples._single_detail(id="MGYS00001234")})
        """

        # get the child detail class e.g. SampleDetail for "samples" list resource
        detail_cls = V2_ENDPOINT_DETAIL_PROXIES.get(self.child_resource)()
        if not detail_cls:
            raise ValueError(
                f"Unsupported child resource for detail: {self.child_resource}"
            )
        logging.debug(
            f"Got detail class {detail_cls} for child resource {self.child_resource!r}"
        )

        # prep id param for given resource e.g. {"accession": "MGYS00001234"} or {"biome_lineage": "root"}
        custom_id_param_key = detail_cls.id_param_key
        id_param = self._resolve_id_param(key, param_name=custom_id_param_key)
        resolved_id = id_param[custom_id_param_key]
        logging.debug(f"Resolved id param for detail: {id_param}")

        # init detail proxy with id param
        child = detail_cls.filter(**id_param)
        logging.debug(f"Initialized detail proxy {child} with params {child.params!r}")
        # set endpoint module (might not be necessary actually)
        # child.endpoint_module = self._detail_endpoint

        # cache detail data mem
        self._collected_details_results[resolved_id] = child.page(1)
        self._collected_details[resolved_id] = child
        self._collected_details_downloads[resolved_id] = child.downloads
        return child

    async def _asingle_detail(
        self,
        key: int | str,
    ) -> "QuerySet":
        """
        Async version of _single_detail.
        Get MGnifyDetail for a specific accession/pubmed_id/catalogue_id.

        Parameters
        ----------
        key : int | str
            The identifier for the detail resource, or an integer index to look up the identifier from results_ids.

        Examples
        -------
        sample = await samples._asingle_detail({"accession": "MGYS00001234"})
        """
        detail_cls = V2_ENDPOINT_DETAIL_PROXIES.get(self.child_resource)()
        logging.debug(
            f"Got detail class {detail_cls} for child resource {self.child_resource!r}"
        )
        if not detail_cls:
            raise ValueError(
                f"Unsupported child resource for detail: {self.child_resource}"
            )
        custom_id_param_key = detail_cls.id_param_key
        id_param = self._resolve_id_param(key, param_name=custom_id_param_key)
        resolved_id = id_param[custom_id_param_key]
        logging.debug(f"Resolved id param for detail: {id_param}")
        child = detail_cls.filter(**id_param)
        child.endpoint_module = self._detail_endpoint

        # cache detail data mem
        self._collected_details_results[resolved_id] = await child.apage(1)
        self._collected_details[resolved_id] = child
        self._collected_details_downloads[resolved_id] = child.downloads

        return child

    @property
    def details(self) -> list[MGnifyDetail]:
        return self._collected_details

    @property
    def details_results(self) -> dict[str, dict]:
        return self._collected_details_results

    @property
    def details_df(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.details_results, orient="index")

    @property
    def details_downloads(self) -> list[dict[str, Any]] | None:
        return [
            item
            for sublist in self._collected_details_downloads.values()
            for item in sublist
        ]

    def __getitem__(self, key: int | str) -> "MGnifyDetail":
        """
        Allow index or accession-based access to child details.
        Default is not lazy and will fetch immediately, but can be configured to return proxies without fetching.
        """
        return self._single_detail(key)

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

        try:
            id_param_key = ID_PARAM[SupportedEndpoints.validate(resolved_resource)]
        except Exception:
            id_param_key = None
        logging.debug(
            f"Resolved id param key for {resolved_resource!r}: {id_param_key!r}"
        )

        # init MGnifier without id first
        super().__init__(
            resource=resolved_resource,
            config=config,
            **kwargs,
            **{id_param_key: id},
        )
        # then add it to param
        # self._params.update({self.id_param_key: id})

    def _clone(self, **param_overrides) -> "MGnifyDetail":
        """
        Overriding QuerySet._clone to handle accession/id extraction and proper initialization of detail proxies.

        Parameters
        ----------
        **param_overrides
            Keyword arguments representing the parameters to override in the new instance.
            These will be merged with the existing parameters, with the provided overrides taking precedence.

        Returns
        -------
        MGnifyDetail
            A new instance of the same class with the updated parameters.
        """
        merged_params = {**self.params, **param_overrides}
        # rm resource if acci passed
        merged_params.pop("resource", None)
        # Extract id from params for detail resources
        detail_id = merged_params.pop(self.id_param_key, None)

        new_qs = self.__class__(
            id=detail_id,
            config=self.config,
            params=merged_params,
        )
        new_qs.endpoint_module = self.endpoint_module

        return new_qs

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
            return self.get_list(
                resource=name,
                fetch=True,
                explain=False,
            )

        # if not a supported attr then raise error
        raise AttributeError(
            f"{self.__class__.__name__} object has no attribute {name!r}."
        )

    @property
    def downloads(self) -> list[dict[str, Any]]:
        """
        A list of download information dicts for the detail, extracted from the details results.

        Each dict is updated with the identifier of the detail.
        The identifier key is determined by the id_param_key of the detail class,
        e.g. "accession" for studies, samples, runs, analyses, genomes, assemblies;
        "biome_lineage" for biomes; "pubmed_id" for publications; "catalogue_id" for catalogues.
        """

        if not self.results:
            logging.debug(
                "No results found for detail; cannot extract downloads. Returning empty list."
            )
            return []

        if "downloads" not in self.to_df().columns:
            logging.debug(
                "Details DataFrame does not have 'downloads' column. Returning empty list."
            )
            return []

        logging.debug(
            f"Updating download info with identifier {self.identifier!r} to id_param_key {self.id_param_key!r}"
        )

        # updates the dicts with the id from the index, maybe pipeline_version if available
        for _, row in self.to_df().iterrows():
            # get downloads list from row
            downloads_list = row["downloads"]

            # get pipeline_version from row if avail, i.e., analysisdetail
            if "pipeline_version" in row and isinstance(row["pipeline_version"], str):
                pipe = row["pipeline_version"].strip("V")
            else:
                pipe = None

            # for each downlaod dict, add id and pipeline_version
            for each_download in downloads_list:
                # keep id
                each_download.update({self.id_param_key: self.identifier})

                # now pipe
                if pipe is None:
                    v_group = re.search(
                        r"\.v(\d+(?:\.\d+)?)",
                        each_download.get("download_group", ""),
                    ).group(1)
                    pipe = v_group

                if pipe is not None:
                    try:
                        pipe = PipelineVersions(float(pipe)).name
                    except Exception as e:
                        logging.debug(
                            f"Could not parse pipeline version from {pipe!r} for download {each_download!r}: {e}"
                        )

                each_download.update({"pipeline_version": pipe})

        return [
            item for sublist in self.to_df()["downloads"].values for item in sublist
        ]

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
        resource: ListResource,
        *,
        fetch: bool = True,
        explain: bool = False,
    ) -> "MGnifyList":
        """
        Get list proxy for a specific accession/pubmed_id/catalogue_id detail.

        Parameters
        ----------
        resource : str
            Valid child resource name e.g. in list_relationships(),
            such as "samples" for a study detail, or "analyses" for a run detail.
        fetch : bool
            Whether to immediately fetch the detail after creating the proxy.
        explain : bool
            Whether to print example URLs that would be called.
        Returns
        -------
        MGnifyList
            A proxy for the next resource.

        Examples
        -------
        samples = study.get_list("samples", fetch=False)
        """

        # get related MGnifyList class for the resource, e.g. Samples for "samples"
        logging.debug(
            f"Given resource: {resource}, {SupportedEndpoints.validate(resource)!r}"
        )
        proxy_cls = V2_ENDPOINT_LIST_PROXIES.get(SupportedEndpoints.validate(resource))(
            config=self.config
        )
        logging.debug(f"Getting proxy class {proxy_cls!r} for resource {resource!r}")

        logging.debug(
            f"Resolving id param for identifier {self.identifier!r} with id_param_key {self.id_param_key!r}"
        )
        # prep access param e.g. {"accession": "MGYS00001234"} or {"biome_lineage": "root"}
        id_param = self._resolve_id_param(self.identifier)
        logging.debug(f"Resolved access param for list proxy: {id_param}")

        # init list endpoint
        list_endpoint = proxy_cls.filter(**id_param)
        logging.debug(
            f"Set endpoint module for list proxy: {list_endpoint.endpoint_module} with params {list_endpoint.params!r}"
        )
        list_endpoint.endpoint_module = self._next_rel_module(resource)

        # extra auto
        if explain:
            list_endpoint.explain()
        if fetch:
            list_endpoint.bulk_fetch()
        return list_endpoint

    async def aget_list(
        self,
        resource: ListResource,
        *,
        fetch: bool = True,
        explain: bool = False,
    ) -> "MGnifyList":
        """
        Get list proxy for a specific accession/pubmed_id/catalogue_id detail.

        Parameters
        ----------
        resource : str
            Valid list resource name e.g. in list_relationships(), such as "samples" for a study detail, or "analyses" for a run detail.
        fetch : bool
            Whether to immediately fetch the detail after creating the proxy.
        explain : bool
            Whether to print example URLs that would be called.

        Returns
        -------
        MGnifyList
            A proxy for the next resource.

        Examples
        -------
        samples = await study.aget_list("samples", fetch=False)
        """

        proxy_cls = V2_ENDPOINT_LIST_PROXIES.get(SupportedEndpoints.validate(resource))
        logging.debug(f"Getting proxy class {proxy_cls} for resource {resource!r}")
        if not proxy_cls:
            raise ValueError(f"Unsupported resource: {resource}")

        custom_id_param_key = proxy_cls.id_param_key
        id_param = self._resolve_id_param(
            self.identifier, param_name=custom_id_param_key
        )
        logging.debug(f"Resolved access param for list proxy: {id_param}")
        list_endpoint = proxy_cls(config=self.config, **id_param)
        list_endpoint.endpoint_module = self._next_rel_module(resource)
        logging.debug(
            f"Set endpoint module for list proxy: {list_endpoint.endpoint_module} with params {list_endpoint.params!r}"
        )
        if explain:
            list_endpoint.explain()
        if fetch:
            await list_endpoint.abulk_fetch()
        return list_endpoint


# import concrete proxy classes from sibling modules. These imports occur
# after the base `MGnifyList`/`MGnifyDetail` classes are defined to avoid
# circular imports: concrete modules import the base classes from this
# package during their import.
from .analyses import Analyses, AnalysisDetail
from .assemblies import Assemblies, AssemblyDetail
from .biomes import BiomeDetail, Biomes
from .catalogues import CatalogueDetail, Catalogues
from .genomes import GenomeDetail, Genomes
from .publications import PublicationDetail, Publications
from .runs import RunDetail, Runs
from .samples import SampleDetail, Samples
from .studies import PrivateStudies, Studies, StudyDetail

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
