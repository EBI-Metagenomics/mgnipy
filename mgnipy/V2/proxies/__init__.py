from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
import re
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    ClassVar,
    Iterator,
    Optional,
)

import pandas as pd
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm_asyncio
from mgnipy._models.constants.CONSTANTS import (
    PipelineVersions,
    SupportedEndpoints,
    ListResourceStr,
    DetailResourceStr,
)
from mgnipy.V2.core import MGnifier
from mgnipy.V2.endpoints import (
    BETWEEN_RESOURCE_RELATIONSHIPS,
    PARENT_CHILD_RESOURCES,
    WITHIN_RESOURCE_RELATIONSHIPS,
    ID_PARAM,
)
from mgnipy.V2.metadata import MGnifyMetadata

if TYPE_CHECKING:
    from mgnipy.V2.query_set import QuerySet
    from mgnipy._models.config import MGnipyConfig


class MGnifyList(MGnifier):
    """
    A proxy for a list resource in the MGnify API, such as studies, samples, or analyses.

    This class provides methods to retrieve metadata, iterate over child details, and manage pagination and filtering for the list resource.
    """

    RESOURCE: ClassVar[Optional[ListResourceStr]] = None

    def __init__(
        self,
        *,
        config: Optional[MGnipyConfig | dict] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # Accept accidental "resource" in kwargs, but do not expose it in signature
        passed_resource: Optional[ListResourceStr] = kwargs.pop("resource", None)
        resolved_resource = self.RESOURCE or passed_resource

        if resolved_resource is None:
            raise TypeError(
                "Use a proxy e.g. proxies.studies.Studies or "
                "`resource` arg required: {ListResourceStr!r}"
            )

        logger.debug(
            f"Initializing MGnifyList with: {resolved_resource!r}, "
            f"params: {params}, config: {config}, also: {kwargs!r}"
        )
        super().__init__(
            resource=resolved_resource,
            config=config,
            params=params,
            **kwargs,
        )
        logger.debug(f"{self.resource!r} MGnifyList initialized.")

        self.child_resource: str = PARENT_CHILD_RESOURCES.get(self.resource, None)

        self._collected_details: dict[str, "MGnifyDetail"] = {}
        self._collected_details_metadata: dict[str, dict] = {}

    def __len__(self) -> int:
        """Return the number of child details based on results.

        Examples
        --------
        >>> from mgnipy.V2.proxies import Studies  # doctest: +SKIP
        >>> studies = Studies(config={})  # doctest: +SKIP
        >>> len(studies)  # doctest: +SKIP
        """
        return len(self.metadata.ids or [])

    def _reset_detail_iterator(self) -> None:
        """
        Initialize or reset the internal state for iterating over MGnifyDetails
        """
        # if refresh:
        #     try:
        #         self.exec.first()
        #     except Exception:
        #         pass
        self._detail_ids = list(self.metadata.ids or [])
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
        logger.debug(
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

    @property
    def _emgapi_detail_endpoint(self) -> Callable:
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
        >>> studies._emgapi_detail_endpoint
        <module 'mgnipy.emgapi_v2_client.api.studies.get_mgnify_study' from ...mgnipy/emgapi_v2_client/api/studies/get_mgnify_study.py'>
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
    def _detail_cls(self):
        """
        Get the detail class for the child resource.
        e.g. SampleDetail for "samples" list resource

        Returns
        -------
        MGnifyDetail subclass
        """
        detail_cls = V2_ENDPOINT_DETAIL_PROXIES.get(self.child_resource)
        if not detail_cls:
            raise ValueError(
                f"Unsupported child resource for detail: {self.child_resource}"
            )
        return detail_cls(
            config=self.config,
            client=self.client,
            resolve_auth=self.resolve_auth,
            interactive_auth=self.interactive_auth,
            semaphore=self.semaphore,
        )

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
        for acc in self.metadata.ids or []:
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
        for acc in self.metadata.ids or []:
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
            The identifier for the detail resource, or an integer index to look up the identifier from `.metadata.ids`.

        Returns
        -------
        MGnifyDetail
            A proxy for the child/detail for the given key

        Examples
        -------
        sample = samples._single_detail(id="MGYS00001234")})
        """

        # get the child detail class e.g. SampleDetail for "samples" list resource
        detail_cls = self._detail_cls
        # prep id param for given resource e.g. {"accession": "MGYS00001234"} or {"biome_lineage": "root"}
        custom_id_param_key = detail_cls._id_label
        id_param = self.metadata._resolve_id_param(key, param_name=custom_id_param_key)
        resolved_id = id_param[custom_id_param_key]
        logger.debug(f"Resolved id param for detail: {id_param}")

        # init detail proxy with id param
        child = detail_cls.filter(**id_param)
        logger.debug(f"Initialized detail proxy {child} with params {child.params!r}")
        # cache detail data mem
        self._collected_details_metadata[resolved_id] = child.page(1)
        self._collected_details[resolved_id] = child
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
            The identifier for the detail resource, or an integer index to look up the identifier from `.metadata.ids`.

        Examples
        -------
        sample = await samples._asingle_detail({"accession": "MGYS00001234"})
        """
        detail_cls = self._detail_cls
        custom_id_param_key = detail_cls._id_label
        logger.debug(f"Using custom ID param key: {custom_id_param_key}")
        id_param = self.metadata._resolve_id_param(key, param_name=custom_id_param_key)
        resolved_id = id_param[custom_id_param_key]
        logger.debug(f"Resolved id param for detail: {id_param}")
        child = detail_cls.filter(**id_param)

        # cache detail data mem
        self._collected_details_metadata[resolved_id] = await child.apage(1)
        self._collected_details[resolved_id] = child

        return child

    @property
    def mgnify_details(self) -> list[MGnifyDetail]:
        if len(self._collected_details) == 0:
            logger.warning(
                f"No {self.child_resource} details collected of total {len(self)}. Run `enrich_details()` first to populate details."
            )
        return self._collected_details

    @property
    def detailed_metadata(self) -> MGnifyMetadata:
        if len(self._collected_details_metadata) == 0:
            logger.warning(
                f"No {self.child_resource} details collected of total {len(self)}. Run `enrich_details()` first to populate details."
            )
        return MGnifyMetadata(
            results=self._collected_details_metadata,
            id_label=self._detail_cls._id_label,
        )

    @property
    def downloads(self) -> list[dict[str, Any]] | None:
        """
        Get a list of all download links from the detailed metadata.

        Returns
        -------
        list[dict[str, Any]] or None
            A list of dictionaries containing download information, or None if no details are available.
        """
        return [
            item
            for sublist in self.mgnify_details.values()
            for item in sublist.downloads
        ]

    def page_size(self, n: int) -> "MGnifyList":
        """
        Set the page size for paginated API calls.

        Parameters
        ----------
        n : int

        Returns
        -------
        MGnifyList
            A new MGnifyList instance with the updated page size parameter.
        """
        if not isinstance(n, int) or n <= 0:
            raise ValueError("Page size must be a positive integer.")

        # make a copy of current instance
        new_qs = self._clone(page_size=n)
        return new_qs

    def enrich_details(self, limit: Optional[int] = 200, hide_progress: bool = False):
        """
        Gets the details for each mgnify list item.
        Iterates through the accessions/ids (`.metadata.ids`) and retrieves their details using the corresponding detail proxy (e.g., `RunDetail` for `Runs`).

        Parameters
        ----------
        limit : Optional[int], default=200
            An optional integer to limit the number of runs to enrich. If not provided, it defaults to 200. If set to None, there will be no limit on the number of runs enriched.
        hide_progress : bool, default=False
            A boolean flag to control the display of the progress bar. If set to True, the progress bar will be hidden.

        Returns
        -------
        None
            This method does not return anything. It updates the internal state of the MGnifyList instance by populating the `.details` `.details_df` and `.detailed_metadata.results` with the details of each item.
        """

        logger.debug(
            f"Starting enrichment of {self.child_resource} details with limit {limit}."
        )

        if self.metadata.ids is None:
            logger.warning("No metadata.ids found to enrich details.")
            return

        details_todo: list[str] = [
            x for x in self.metadata.ids if x not in self._collected_details_metadata
        ][:limit]

        logger.debug(f"Number of details to enrich: {details_todo}")

        for count, detail_id in enumerate(
            tqdm_sync(
                details_todo,
                total=len(self.metadata.ids),
                initial=len(self._collected_details_metadata),
                desc=f"Enriching {self.child_resource} details",
                disable=hide_progress,
            )
        ):
            logger.info(f"Enriching detail {detail_id}. Count: {count}")
            # get detail
            self._single_detail(detail_id)

    async def aenrich_details(
        self, limit: Optional[int] = 200, hide_progress: bool = False
    ):
        """
        Async version of `enrich_details` that retrieves details for each item in the MGnifyList asynchronously.

        Parameters
        ----------
        limit : Optional[int], default=200
            An optional integer to limit the number of items to enrich. If not provided, it defaults to 200. If set to None, there will be no limit on the number of items enriched.
        hide_progress : bool, default=False
            A boolean flag to control the display of the progress bar. If set to True, the progress bar will be hidden.

        Returns
        -------
        None
            This method does not return anything. It updates the internal state of the MGnifyList instance by populating the `.details` `.details_df` and `.detailed_metadata.results` with the details of each item.
        """
        logger.debug(
            f"Starting async enrichment of {self.child_resource} details with limit {limit}."
        )

        details_todo: list[str] = [
            x for x in self.metadata.ids if x not in self._collected_details_metadata
        ][:limit]

        logging.debug(f"Number of details to enrich: {len(details_todo)}")

        logging.debug(
            f"Enriching details for {len(details_todo)} items asynchronously."
        )

        tasks = [self._asingle_detail(identifier) for identifier in details_todo]

        for done in tqdm_asyncio.as_completed(
            tasks,
            total=len(self.metadata.ids),
            initial=len(self._collected_details_metadata),
            desc=f"Enriching {self.child_resource} details",
            disable=hide_progress,
        ):
            await done

    def __getitem__(self, key: int | str) -> "MGnifyDetail":
        """
        Allow index or accession-based access to child details.
        Default is not lazy and will fetch immediately, but can be configured to return proxies without fetching.
        """
        return self._single_detail(key)


class MGnifyDetail(MGnifier):
    RESOURCE: ClassVar[Optional[DetailResourceStr]] = None

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
                f"or pass as a resource param: {DetailResourceStr!r}"
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
        logger.debug(
            f"Resolved id param key for {resolved_resource!r}: {id_param_key!r}"
        )

        # init MGnifier without id first
        super().__init__(
            resource=resolved_resource,
            config=config,
            **kwargs,
            **{id_param_key: id},
        )

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
        detail_id = merged_params.pop(self._id_label, None)

        new_qs = self.__class__(
            id=detail_id,
            config=self.config,
            params=merged_params,
            client=self.client,
            resolve_auth=self.resolve_auth,
            interactive_auth=self.interactive_auth,
            semaphore=self.semaphore,
        )
        new_qs.endpoint_module = self.endpoint_module

        return new_qs

    def _next_rel_module(self, name: str) -> SupportedEndpoints:
        """
        Get the next resource name based on the relationship name
        e.g. for a study detail, "samples" -> "sample" detail endpoint module.

        Parameters
        ----------
        name : str
            The name of the relationship, e.g. "samples" for a study detail.

        Returns
        -------
        SupportedEndpoints
            The corresponding endpoint module for the related resource.
        """
        if name in self.list_relationships():
            return BETWEEN_RESOURCE_RELATIONSHIPS[self.resource][
                SupportedEndpoints.validate(name)
            ]

        raise AttributeError(f"{self.resource} does not have linked resource: {name!r}")

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
            return self.params[self._id_label]
        except KeyError:
            raise AttributeError(
                f"Identifier key '{self._id_label}' not found in parameters for resource '{self.resource}'."
            ) from None

    def get_list(
        self,
        resource: ListResourceStr,
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
        logger.debug(
            f"Given resource: {resource}, {SupportedEndpoints.validate(resource)!r}"
        )
        proxy_cls = V2_ENDPOINT_LIST_PROXIES.get(SupportedEndpoints.validate(resource))(
            config=self.config,
            client=self.client,
            resolve_auth=self.resolve_auth,
            interactive_auth=self.interactive_auth,
        )
        logger.debug(f"Getting proxy class {proxy_cls!r} for resource {resource!r}")

        logger.debug(
            f"Resolving id param for identifier {self.identifier!r} with id_param_key {self._id_label!r}"
        )
        # prep access param e.g. {"accession": "MGYS00001234"} or {"biome_lineage": "root"}
        id_param = self.metadata._resolve_id_param(self.identifier)
        logger.debug(f"Resolved access param for list proxy: {id_param}")

        # init list endpoint
        list_endpoint = proxy_cls.filter(**id_param)
        logger.debug(
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
        resource: ListResourceStr,
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

        logger.debug(
            f"Given resource: {resource}, {SupportedEndpoints.validate(resource)!r}"
        )
        proxy_cls = V2_ENDPOINT_LIST_PROXIES.get(SupportedEndpoints.validate(resource))(
            config=self.config,
            client=self.client,
            resolve_auth=self.resolve_auth,
            interactive_auth=self.interactive_auth,
        )
        logger.debug(f"Getting proxy class {proxy_cls!r} for resource {resource!r}")

        logger.debug(
            f"Resolving id param for identifier {self.identifier!r} with id_param_key {self._id_label!r}"
        )
        id_param = self.metadata._resolve_id_param(self.identifier)
        logger.debug(f"Resolved access param for list proxy: {id_param}")

        # init list endpoint
        list_endpoint = proxy_cls.filter(**id_param)
        logger.debug(
            f"Set endpoint module for list proxy: {list_endpoint.endpoint_module} with params {list_endpoint.params!r}"
        )
        list_endpoint.endpoint_module = self._next_rel_module(resource)

        if explain:
            list_endpoint.explain()
        if fetch:
            await list_endpoint.abulk_fetch()
        return list_endpoint

    @property
    def downloads(self) -> list[dict[str, Any]]:
        """
        Get the list of downloads for this detail.
        """

        # no results, no downloads
        if len(self.metadata) == 0:
            return []

        # checking column names
        df = self.metadata.to_pandas()
        logger.debug(f"Metadata columns: {df.columns.tolist()}")

        if "downloads" not in df.columns:
            logger.debug("No 'downloads' field. Returning empty list.")
            return []

        # combine all downloads lists into one list
        _downloads = [item for sublist in df["downloads"] for item in sublist]

        if not _downloads:
            logger.debug("No downloads found in metadata. Returning empty list.")
            return []

        downloads_cols: list[str] = pd.DataFrame(_downloads).columns
        logger.debug(f"downloads columns: {downloads_cols}")
        if self._id_label not in downloads_cols:
            logger.debug(
                f"No '{self._id_label}' field in downloads. "
                f"Attempting to add identifier info with id_param_key {self._id_label!r} and identifier {self.identifier!r}."
            )
            self._add_id_param_field(self.identifier)

        if "pipeline_version" not in downloads_cols:
            logger.debug(
                "No 'pipeline_version' field in downloads. "
                "Attempting to add pipeline version info."
            )
            self._add_pipeline_version_field()

        return _downloads

    def downloads_df(self, **pd_kwargs) -> Optional[pd.DataFrame]:
        """
        Looking for a "downloads" field in the metadata results and return as a DataFrame if found.
        """
        return pd.DataFrame(self.downloads, **pd_kwargs)

    def _add_pipeline_version_field(self):
        for item_dict in self.metadata.records:

            # get pipeline_version from row if avail, i.e., analysisdetail
            if "pipeline_version" in item_dict and isinstance(
                item_dict["pipeline_version"], str
            ):
                a_pipe = item_dict["pipeline_version"].lower().strip("v")
            else:
                a_pipe = None

            for each_download in item_dict.get("downloads", []):

                # if pipeline in download_group, use that instead
                v_group = re.search(
                    r"\.v(\d+(?:\.\d+)?)",
                    each_download.get("download_group", ""),
                    re.IGNORECASE,
                ).group(1)
                # priority to ver in download_group
                pipe = v_group or a_pipe

                if pipe is not None:
                    try:
                        pipe = PipelineVersions(float(pipe)).name
                    except Exception as e:
                        logger.error(
                            f"Could not parse pipeline version from {pipe!r} for download {each_download!r}: {e}"
                        )

                each_download.update({"pipeline_version": pipe})

    def _add_id_param_field(self, given_id: str):

        for item_dict in self.metadata.records:
            logger.debug(f"{item_dict.keys()}")
            for each_download in item_dict.get("downloads", []):
                # keep id
                each_download.update({self._id_label: given_id})

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
}
