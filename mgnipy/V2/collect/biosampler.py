from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import asyncio
from typing import (
    Any,
    Optional,
)

import pandas as pd
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm_asyncio

from mgnipy._models.config import MGnipyConfig
from mgnipy._models.constants.CONSTANTS import SupportedEndpoints
from mgnipy._shared_helpers.biosamples_helper import (
    GIVEN_ID as BIOSAMPLES_GIVEN_ID,
    HEADERS as BIOSAMPLES_HEADERS,
    SAMPLE_ID as BIOSAMPLES_SAMPLE_ID,
    URL as BIOSAMPLES_URL,
    aget_biosample_metadata,
    get_biosample_metadata,
)
from mgnipy._shared_helpers.httpx_helpers import init_httpx_client
from mgnipy.emgapi_v2_client.client import AuthenticatedClient, Client
from mgnipy.V2.mgnifier.metadata import MGnifyMetadata
from mgnipy.V2.mixins import CheckpointMixin, ClientManagerMixin

BIOSAMPLES_CONFIG_ADDONS = {"base_url": BIOSAMPLES_URL}


class BioSampler(CheckpointMixin, ClientManagerMixin):
    """Fetches BioSamples metadata for a given list of ENA run or sample accessions.

    BioSampler is designed to retrieve the rich sample metadata from `BioSamples`_ for a list of Run or Sample `ENA`_ accessions.

    It uses the :func:`~.biosamples_helper.get_biosample_metadata` or :func:`~.biosamples_helper.aget_biosample_metadata` (TODO) function to fetch the metadata for each accession with option to cache the results using the :class:`.CheckpointMixin` to avoid redundant API calls in future runs.

    Parameters
    ----------
    sample_ids : list of str
        A list of ENA run or sample accessions for which to fetch the BioSamples metadata. If a run accession then :meth:`~BioSampler.enrich(incl_ena=True)` is required so that the sample accession can be retrieved from ENA first and then passed to a BioSamples API request.
    config : MGnipyConfig, optional
        An optional configuration object for MGnipy. If not provided, a default configuration will be used.
    client : Client or AuthenticatedClient, optional
        An optional HTTP client for making requests. If not provided, a default client will be initialized using the provided or default configuration.
    metadata : ResultsHandler, optional
        An optional :class:`.ResultsHandler` instance to store the enriched metadata. If not provided, a new :class:`~.ResultsHandler` will be created to hold the results.

    Attributes
    ----------
    all_ids : list of str
        The complete list of ENA run or sample accessions provided during initialization.
    metadata : ResultsHandler
        The enriched metadata as a :class:`~.ResultsHandler` instance.

    Notes
    -----
    - The :meth:`enrich` method iterates through the list of accessions and fetches their metadata, storing the results in a :class:`~ResultsHandler` instance.
    - By default there is the option to include ENA metadata in the enrichment process, which can be controlled via the `incl_ena` parameter. If `incl_ena` is False, then only sample accessions will return BioSamples metadata!
    - The :meth:`aenrich` method is intended to provide an asynchronous version of the enrichment process, but it is currently not implemented. Future updates will include asynchronous fetching of metadata to improve performance for large datasets.
    - The class is designed to be flexible, allowing users to specify a limit on the number of accessions to enrich in a single run, which is useful for testing or when dealing with large datasets to avoid long runtimes during development. If the limit is set to None, there will be no limit on the number of accessions enriched.
    - It uses the CheckpointMixin to cache results and avoid redundant API calls.

    .. _BioSamples: https://www.ebi.ac.uk/biosamples/
    .. _ENA: https://www.ebi.ac.uk/ena/browser/home
    """

    def __init__(
        self,
        sample_ids: list[str],
        config: MGnipyConfig = None,
        metadata: MGnifyMetadata = None,
    ):

        self._all_ids: list[str] = sorted(sample_ids)
        self._metadata: MGnifyMetadata = metadata or MGnifyMetadata()
        self._results = self._metadata._results  # For CheckpointMixin
        if config:
            # replace with BIOSAMPLES_URL and BIOSAMPLES_HEADERS
            self.config: MGnipyConfig = MGnipyConfig.model_validate(
                config.model_dump() | BIOSAMPLES_CONFIG_ADDONS
            )
        else:
            self.config = MGnipyConfig(**BIOSAMPLES_CONFIG_ADDONS)

        self.client: Client | AuthenticatedClient = init_httpx_client(
            self.config, headers=BIOSAMPLES_HEADERS
        )

        self._resource: SupportedEndpoints = SupportedEndpoints("_custom_endpoint")

    def __call__(
        self,
        sample_ids: list[str],
        metadata: MGnifyMetadata = None,
    ) -> "BioSampler":
        """
        Creates a new instance of BioSampler with the specified resource, all_ids, mgnify_metadata, and detail_proxy. This allows for creating a new BioSampler instance with different parameters without modifying the existing instance.
        """
        return BioSampler(
            sample_ids=sample_ids,
            config=self.config,
            metadata=metadata or self._metadata,
        )

    def __repr__(self):
        return (
            f"BioSampler(len(sample_ids)={len(self._all_ids)}, "
            f"metadata={self._metadata})"
        )

    def __str__(self):
        return (
            f"BioSampler with {len(self._all_ids)} sample_ids. \n"
            f"Progress: {len(self._metadata)} ids. \n"
            f"Cache directory: {self.cache_path} \n"
        )

    @property
    def resource(self) -> str:
        """For :class:`.CheckpointMixin`"""
        return self._resource

    @property
    def metadata(self) -> MGnifyMetadata:
        """The enriched metadata as a MGnifyMetadata instance."""
        return self._metadata

    @metadata.setter
    def metadata(self, value: MGnifyMetadata):
        if not isinstance(value, MGnifyMetadata):
            raise ValueError("metadata must be an instance of MGnifyMetadata.")
        self._metadata = value

    @property
    def all_ids(self) -> list[str]:
        """The list of ENA run or sample accessions set during initialization."""
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
            "resource": "biosamples",
            "given_ids": self.all_ids,
        }

    def _iter_leftovers(self) -> list[str]:
        """Identify and return the list of run accessions that have not yet been enriched.

        Returns
        -------
        list of str
            A list of run accessions that are present in :attr:`all_ids` but not in :meth:`.ResultsHandler.get_ids`.
        """
        self.try_load_cache()
        self._metadata._sync_data()
        return [
            x
            for x in self.all_ids
            if x not in self._metadata.get_ids(BIOSAMPLES_SAMPLE_ID)
        ]

    def enrich(
        self,
        limit: Optional[int] = 200,
        hide_progress: bool = False,
        incl_ena: bool = False,
        skip_failed: bool = True,
    ):
        """Fetches BioSample metadata for the given run/sample accessions.

        This method iterates through the list of ENA run or sample accessions provided during initialization and retrieves their corresponding BioSample metadata. The results are stored in the :class:`.ResultsHandler` instance associated with this class. This does not return anything.

        Parameters
        ----------
        limit : Optional[int], default=200
            An optional integer to limit the number of biosamples to enrich. If set to None, there will be no limit on the number of biosamples enriched.
        hide_progress : bool, default=False
            Whether to hide the progress bar during enrichment.
        incl_ena : bool, default=False
            Whether to include an API call to ENA prior to the BioSamples requeßst. If set to False, only sample accessions will return BioSamples metadata.
        skip_failed : bool, default=True
            Whether to skip failed enrichments. If set to True, failed enrichments will be logged and skipped, and a placeholder with the GivenID will be appended to the results (appear as completed in :meth:`.ResultsHandler.get_ids`). If set to False, any failed enrichments will not be appended to the results (appear as still left to do).
        """

        logger.debug(
            f"Starting enrichment of biosample meta for short description with limit {limit}."
        )

        runs_todo: list[str] = self._iter_leftovers()[:limit]
        logger.warning(
            f"Enriching {len(runs_todo)} biosamples. Total samples (with runs enriched): {len(self._metadata.get_ids(BIOSAMPLES_SAMPLE_ID))}. Already enriched: {len(self._metadata)}."
        )

        for count, run in enumerate(
            tqdm_sync(
                runs_todo,
                total=len(self.all_ids),
                initial=len(self._metadata),
                desc="Enriching biosamples",
                disable=hide_progress,
            )
        ):
            logger.info(f"Enriching biosample {run}. Count: {count}")

            # get metadata
            try:
                bm = get_biosample_metadata(
                    run, client=self.client.get_httpx_client(), incl_ena=incl_ena
                )
            except RuntimeError:
                self.renew_client()
                bm = get_biosample_metadata(
                    run, client=self.client.get_httpx_client(), incl_ena=incl_ena
                )
            except Exception as e:
                logger.error(f"Error occurred while enriching run {run}: {e}")
                bm = False

            if isinstance(bm, pd.DataFrame) and not bm.empty:
                logger.debug(
                    "Enriched biosample metadata is non-empty DataFrame. Appending to results."
                )
                self._metadata.append_result(page_num=1, value=[bm.iloc[0].to_dict()])
                self.write_results(1, self._metadata.data)
                continue

            if not skip_failed:
                continue
            else:
                logger.error(
                    f"Enrichment for biosample {run} did not return a valid DataFrame. Appending placeholder with GivenID only."
                )
                self._metadata.append_result(
                    page_num=1, value=[{BIOSAMPLES_GIVEN_ID: run}]
                )
                self.write_results(1, self._metadata.data)

    async def aenrich(
        self,
        limit: Optional[int] = 200,
        hide_progress: bool = False,
        incl_ena: bool = False,
        skip_failed: bool = False,
    ) -> None:
        """Async version of :meth:`enrich`.

        See :meth:`enrich` for details on parameters and behavior.

        This is a placeholder and not yet implemented.
        """
        ids_todo: list[str] = self._iter_leftovers()[:limit]

        logger.warning(
            f"Enriching {len(ids_todo)} ids. "
            f"Total runs: {len(self.all_ids)}. "
            f"Already enriched: {len(self._metadata)}."
        )

        async def _fetch(run: str) -> list[dict[str, Any]]:
            """Fetches the biosample metadata for a given run accession asynchronously."""
            try:
                logger.debug(f"client: {self.client}")
                r = await aget_biosample_metadata(
                    run, client=self.client.get_async_httpx_client(), incl_ena=incl_ena
                )
                return r
            except RuntimeError:
                self.renew_client()
                r = await aget_biosample_metadata(
                    run, client=self.client.get_async_httpx_client(), incl_ena=incl_ena
                )
                return r
            except Exception as e:
                logger.error(f"Error occurred while enriching run {run}: {e}")
                return False

        # to coroutines
        tasks = [asyncio.create_task(_fetch(run)) for run in ids_todo]

        for done in tqdm_asyncio.as_completed(
            tasks,
            total=len(self.all_ids),
            initial=len(self._metadata),
            desc="Enriching biosamples",
            disable=hide_progress,
        ):
            bm = await done
            if isinstance(bm, pd.DataFrame) and not bm.empty:
                logger.debug(
                    "(Async) Enriched biosample metadata is non-empty DataFrame. Appending to results."
                )
                self._metadata.append_result(page_num=1, value=[bm.iloc[0].to_dict()])
                self.write_results(1, self._metadata.data)
                continue

            if not skip_failed:
                continue
            else:
                logger.error("`skip_failed` is not yet implemented for async.")
                continue
