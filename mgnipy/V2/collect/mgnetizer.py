from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from typing import Any, Optional
import asyncio

from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm_asyncio

from mgnipy._models.config import MGnipyConfig
from mgnipy._models.constants.CONSTANTS import DetailResourceStr, SupportedEndpoints
from mgnipy._shared_helpers.biosamples_helper import URL as BIOSAMPLES_URL
from mgnipy._shared_helpers.httpx_helpers import init_httpx_client
from mgnipy.emgapi_v2_client import AuthenticatedClient, Client
from mgnipy.V2.datasets import MGazine
from mgnipy.V2.mgnifier.endpoints import PARENT_CHILD_RESOURCES
from mgnipy.V2.mgnifier.metadata import MGnifyMetadata
from mgnipy.V2.mixins import CheckpointMixin, ClientManagerMixin
from mgnipy.V2.proxies import V2_ENDPOINT_DETAIL_PROXIES, MGnifyDetail

BIOSAMPLES_CONFIG_ADDONS = {"base_url": BIOSAMPLES_URL}


class MGnetizer(CheckpointMixin, ClientManagerMixin):
    """Fetch detailed metadata for a given list of MGnify accessions.

    MGnetizer is designed to retrieve the rich metadata from `MGnify`_ for a list of accessions/ids.

    Unlike :class:`MGnifier` or the :mod:`mgnipy.V2.proxies` module, which are designed to search for MGnify lists OR fetch detailed metadata for a single accession at a time, MGnetizer allows for batch processing of multiple accessions. It uses the :class:`.MGnifyDetail` proxy to fetch detailed metadata for each accession and stores the results in a :class:`.MGnifyMetadata` instance.

    Parameters
    ----------
    resource : DetailResourceStr
        The type of resource to fetch metadata for. Must be one of the supported :class:`MGnifyDetail` resource types (e.g., "study", "sample", "run", etc.).
    all_ids : list of str
        A list of MGnify accessions/ids for which to fetch detailed metadata.
    config : MGnipyConfig, optional
        An optional configuration object for MGnipy. If not provided, a default configuration will be used.
    client : Client or AuthenticatedClient, optional
        An optional HTTP client for making requests. If not provided, a default client will be initialized using the provided or default configuration.
    mgnify_metadata : MGnifyMetadata, optional
        An optional :class:`.MGnifyMetadata` instance to store the enriched metadata.
    detail_proxy : MGnifyDetail, optional
        An optional :class:`.MGnifyDetail` proxy instance to use for fetching detailed metadata. If not provided, the appropriate proxy will be selected based on the specified resource.

    Attributes
    ----------
    resource : DetailResourceStr
        The type of resource being processed.
    all_ids : list of str
        The complete list of MGnify accessions/ids provided during initialization.
    mgnify_metadata : MGnifyMetadata
        The enriched metadata as a :class:`.MGnifyMetadata` instance.
    metadata : MGnifyMetadata
        Alias for :attr:`mgnify_metadata`.
    params : dict
        A dictionary of parameters used for checkpointing, including the resource type and a sorted list of accessions/ids. Used for caching and resuming enrichment processes.
    """

    def __init__(
        self,
        resource: DetailResourceStr,
        all_ids: list[str],
        config: MGnipyConfig = None,
        client: Optional[Client | AuthenticatedClient] = None,
        mgnify_metadata: MGnifyMetadata = None,
        detail_proxy: "MGnifyDetail" = None,
    ):

        if resource:
            # Validate and set the resource type
            self._resource = SupportedEndpoints(resource)
            # Set the appropriate detail proxy based on the resource type, if not provided
            self.detail_proxy: MGnifyDetail = (
                detail_proxy
                or V2_ENDPOINT_DETAIL_PROXIES.get(self._resource)
                or V2_ENDPOINT_DETAIL_PROXIES.get(
                    PARENT_CHILD_RESOURCES.get(self._resource)
                )  # e.g. if plural 'runs' get 'run'
            )
        else:
            # If no resource is provided, set to None
            self._resource = None
            # keep the detail_proxy as provided (can be None)
            self.detail_proxy: MGnifyDetail = detail_proxy

        self._all_ids = sorted(all_ids)
        self._mgnify_metadata = mgnify_metadata or MGnifyMetadata()
        self.config = config or MGnipyConfig()
        self.client = client or init_httpx_client(self.config)
        self._results = self._mgnify_metadata._results  # For CheckpointMixi

    def __call__(
        self,
        resource: DetailResourceStr,
        all_ids: list[str],
        mgnify_metadata: MGnifyMetadata = None,
        detail_proxy: "MGnifyDetail" = None,
    ) -> "MGnetizer":
        """
        Creates a new instance of MGnetizer with the specified resource, :meth:`all_ids`, :meth:`mgnify_metadata`, and detail_proxy. This allows for creating a new MGnetizer instance with different parameters without modifying the existing instance.
        """
        return MGnetizer(
            resource=resource,
            all_ids=all_ids,
            config=self.config,
            client=self.client,
            mgnify_metadata=mgnify_metadata or self._mgnify_metadata,
            detail_proxy=detail_proxy or self.detail_proxy,
        )

    def __repr__(self):
        return (
            f"MGnetizer(resource={self._resource}, len(all_ids)={len(self._all_ids)}, "
            f"mgnify_metadata={self._mgnify_metadata}, detail_proxy={self.detail_proxy})"
        )

    def __str__(self):
        return (
            f"MGnetizer for resource '{self._resource}' with {len(self._all_ids)} ids. \n"
            f"Progress: {len(self._mgnify_metadata)} ids. \n"
            f"Detail proxy: {self.detail_proxy.__name__ if self.detail_proxy else None} \n"
            f"Cache directory: {self.cache_path} \n"
        )

    def explain(self):
        for i in self.all_ids:
            self.detail_proxy(id=i, config=self.config).explain()

    @property
    def mgnify_metadata(self) -> MGnifyMetadata:
        """The enriched metadata as an MGnifyMetadata instance."""
        return self._mgnify_metadata

    @mgnify_metadata.setter
    def mgnify_metadata(self, value: MGnifyMetadata):
        if not isinstance(value, MGnifyMetadata):
            raise ValueError("mgnify_metadata must be an instance of MGnifyMetadata.")
        self._mgnify_metadata = value

    @property
    def resource(self) -> str:
        """For :class:`.CheckpointMixin`"""
        return self._resource

    @resource.setter
    def resource(self, value: str):
        if value not in DetailResourceStr.__args__:
            raise ValueError(
                f"Invalid resource '{value}'. Must be one of {DetailResourceStr.__args__}."
            )
        self._resource = SupportedEndpoints(value)

        if self.detail_proxy is None:
            self.detail_proxy = V2_ENDPOINT_DETAIL_PROXIES.get(self._resource)

    @property
    def all_ids(self) -> list[str]:
        """The list of MGnify accessions/ids set during initialization."""
        return self._all_ids

    @all_ids.setter
    def all_ids(self, value: list[str]):
        if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
            raise ValueError("all_ids must be a list of strings.")
        self._all_ids = sorted(value)

    @property
    def params(self) -> dict[str, Any]:
        """For :class:`.CheckpointMixin`"""
        return {
            "annotator": str(self.__class__),
            "resource": str(self.resource),
            "given_ids": self.all_ids,
        }

    def _iter_leftovers(self) -> list[str]:
        """Identify and return the list of accessions that have not yet been enriched.

        Returns
        -------
        list of str
            A list of accessions that are present in :attr:`all_ids` but not in :meth:`.MGnifyMetadata.ids`.
        """

        self.try_load_cache()
        self._mgnify_metadata._sync_data()
        logger.debug(f"Num ids in cache: {len(self._mgnify_metadata.ids)}")
        return [x for x in self.all_ids if x not in self._mgnify_metadata.ids]

    def enrich(self, limit: Optional[int] = 200, hide_progress: bool = False) -> None:
        """Fetches MGnify metadata for the given accessions.

        This method iterates through the list of MGnify or ENA run accessions provided during initialization and retrieves their corresponding MGnify detail metadata. The results are stored in the :class:`.MGnifyMetadata` instance associated with this class. This does not return anything.

        Parameters
        ----------
        limit : Optional[int], default=200
            An optional integer to limit the number of detaile metadata to retrieve. If set to None, there will be no limit on the number of accessions enriched.
        hide_progress : bool, default=False
            Whether to hide the progress bar during enrichment.
        """
        ids_todo: list[str] = self._iter_leftovers()[:limit]

        logger.warning(
            f"Enriching {len(ids_todo)} ids. Total runs: {len(self.all_ids)}. Already enriched: {len(self._mgnify_metadata)}."
        )

        for count, run in enumerate(
            tqdm_sync(
                ids_todo,
                total=len(self.all_ids),
                initial=len(self._mgnify_metadata),
                desc="Enriching metadata from MGnify",
                disable=hide_progress,
            )
        ):
            logger.debug(f"Enriching id {run}. Count: {count}")
            mg = None
            # get metadata
            try:
                mg = self.detail_proxy(
                    id=run, config=self._deactivated_cache_config, client=self.client
                ).get()
            except Exception as e:
                logger.warning(f"Error occurred while enriching id {run}: {e}.")

            if mg is not None:
                # save over page 1
                self._mgnify_metadata.append_result(page_num=1, value=mg)
                self.write_results(1, self._mgnify_metadata.data)

    async def aenrich(
        self, limit: Optional[int] = 200, hide_progress: bool = False
    ) -> None:
        """Async version of :meth:`enrich`.

        See :meth:`enrich` for details on parameters and behavior.
        """
        ids_todo: list[str] = self._iter_leftovers()[:limit]

        logger.warning(
            f"Enriching {len(ids_todo)} ids. Total runs: {len(self.all_ids)}. Already enriched: {len(self._mgnify_metadata)}."
        )

        async def _fetch(id: str) -> list[dict[str, Any]]:
            try:
                r = await self.detail_proxy(
                    id=id, config=self._deactivated_cache_config, client=self.client
                ).aget()
                return r
            except Exception as e:
                logger.error(f"Error occurred while enriching id {id}: {e}")
                return None

        tasks = [asyncio.create_task(_fetch(id)) for id in ids_todo]

        for done in tqdm_asyncio.as_completed(
            tasks,
            total=len(self.all_ids),
            initial=len(self._mgnify_metadata),
            desc="Enriching metadata from MGnify",
            disable=hide_progress,
        ):
            mg = await done
            if mg:
                self._mgnify_metadata.append_result(page_num=1, value=mg)
                self.write_results(1, self._mgnify_metadata.data)

    @property
    def metadata(self) -> MGnifyMetadata:
        """Returns the enriched metadata as an MGnifyMetadata instance."""
        return self._mgnify_metadata

    @property
    def _deactivated_cache_config(self) -> MGnipyConfig:
        """
        Deactivates the caching mechanism by setting the cache directory to None.
        This is useful when you want to ensure that no caching occurs during certain operations.
        """
        return MGnipyConfig.model_validate(
            self.config.model_dump() | {"cache_dir": None}
        )

    @property
    def downloads(self) -> list[str]:
        """Returns the list of downloads from the enriched metadata."""
        return self._mgnify_metadata.downloads

    @property
    def datasets(self) -> "MGazine":
        """Returns a MGazine instance containing the enriched datasets."""

        if str(self.resource) != "study":
            raise ValueError(
                f"MGnetizer.datasets is only available for resource 'study', not '{self.resource}'."
            )
        return MGazine(
            downloads=self.downloads,
            config=self.config,
            client=self.client,
            mgnify_studies=self._mgnify_metadata.to_list(),
        )
