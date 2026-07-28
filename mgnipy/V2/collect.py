import logging

from mgnipy.V2.mixins import CheckpointMixin
from mgnipy._shared_helpers.biosamples_helper import get_biosample_metadata

logger = logging.getLogger(__name__)

import asyncio
import pandas as pd
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm_asyncio
from typing import (
    Any,
    Optional,
)

from mgnipy._models.constants.CONSTANTS import SupportedEndpoints, DetailResourceStr
from mgnipy.V2.mgnifier.metadata import MGnifyMetadata, ResultsHandler
from mgnipy._shared_helpers.httpx_helpers import init_httpx_client
from mgnipy._models.config import MGnipyConfig
from mgnipy.emgapi_v2_client.client import AuthenticatedClient, Client
from mgnipy.V2.proxies import V2_ENDPOINT_DETAIL_PROXIES, MGnifyDetail


class MGnetizer(CheckpointMixin):

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
            self._resource = SupportedEndpoints(resource)
            self.detail_proxy: MGnifyDetail = (
                detail_proxy or V2_ENDPOINT_DETAIL_PROXIES.get(self._resource)
            )
        else:
            self._resource = None
            self.detail_proxy: MGnifyDetail = detail_proxy
        self._all_ids = sorted(all_ids)
        self._mgnify_metadata = mgnify_metadata or MGnifyMetadata([])
        self.config = config or MGnipyConfig()
        self.client = client or init_httpx_client(self.config)

    def __call__(
        self,
        resource: DetailResourceStr,
        all_ids: list[str],
        mgnify_metadata: MGnifyMetadata = None,
        detail_proxy: "MGnifyDetail" = None,
    ) -> "MGnetizer":
        """
        Creates a new instance of MGnetizer with the specified resource, all_ids, mgnify_metadata, and detail_proxy. This allows for creating a new MGnetizer instance with different parameters without modifying the existing instance.
        """
        return MGnetizer(
            resource=resource,
            all_ids=all_ids,
            config=self.config,
            client=self.client,
            mgnify_metadata=mgnify_metadata or self._mgnify_metadata,
            detail_proxy=detail_proxy or self.detail_proxy,
        )

    @property
    def mgnify_metadata(self) -> MGnifyMetadata:
        return self._mgnify_metadata

    @mgnify_metadata.setter
    def mgnify_metadata(self, value: MGnifyMetadata):
        if not isinstance(value, MGnifyMetadata):
            raise ValueError("mgnify_metadata must be an instance of MGnifyMetadata.")
        self._mgnify_metadata = value

    @property
    def _results(self):
        return self._mgnify_metadata.data

    @_results.setter
    def _results(self, value):
        self._mgnify_metadata.data = value

    @property
    def resource(self) -> str:
        """for checkpointmixin"""
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
        return self._all_ids

    @all_ids.setter
    def all_ids(self, value: list[str]):
        if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
            raise ValueError("all_ids must be a list of strings.")
        self._all_ids = sorted(value)

    @property
    def params(self) -> dict[str, Any]:
        """for checkpointmixin"""
        return {
            "annotator": str(self.__class__),
            "resource": self.resource.value,
            "given_ids": self.all_ids,
        }

    def _iter_leftovers(self) -> list[str]:
        """
        Identify and return the list of run accessions that have not yet been enriched.

        Parameters
        ----------
        all_ids : list of str
            The complete list of run accessions.
        enriched_ids : list of str
            The list of run accessions that have already been enriched.

        Returns
        -------
        list of str
            A list of run accessions that are present in `all_ids` but not in `enriched_ids`.
        """
        self.try_load_cache()
        return [x for x in self.all_ids if x not in self._mgnify_metadata.ids]

    def enrich(self, limit: Optional[int] = 200, hide_progress: bool = False) -> None:
        """
        Enriches the metadata for the given ids by iterating through the ids and retrieving their details using the corresponding MGnifyDetail proxy. The results are cached using the CheckpointMixin to avoid redundant API calls in future runs.

        Parameters
        ----------
        limit : Optional[int], default=200
            An optional integer to limit the number of ids to enrich. If not provided, it defaults to 200.
            If set to None, there will be no limit on the number of ids enriched.
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
                self._mgnify_metadata.data.extend(mg)
                logger.debug(f"{self._mgnify_metadata.data}")
                self.write_results(1, self._results)

    async def aenrich(
        self, limit: Optional[int] = 200, hide_progress: bool = False
    ) -> None:
        """
        Asynchronously enriches the metadata for the given ids by iterating through the ids and retrieving their details using the corresponding MGnifyDetail proxy. The results are cached using the CheckpointMixin to avoid redundant API calls in future runs.

        Parameters
        ----------
        limit : Optional[int], default=200
            An optional integer to limit the number of ids to enrich. If not provided, it defaults to 200.
            If set to None, there will be no limit on the number of ids enriched.
        hide_progress : bool, default=False
            Whether to hide the progress bar during enrichment.
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
                self._mgnify_metadata.data.extend(mg)
                self.write_results(1, self._results)

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


class BioSampler(CheckpointMixin):

    def __init__(
        self,
        run_ids: list[str],
        config: MGnipyConfig = None,
        client: Optional[Client | AuthenticatedClient] = None,
        metadata: ResultsHandler = None,
    ):

        self._all_ids = sorted(run_ids)
        self._metadata = metadata or ResultsHandler([])
        self.config = config or MGnipyConfig()
        self.client = client or init_httpx_client(self.config)
        self._resource = SupportedEndpoints("_custom_endpoint")

    def __call__(
        self,
        run_ids: list[str],
        metadata: ResultsHandler = None,
    ) -> "MGnetizer":
        """
        Creates a new instance of MGnetizer with the specified resource, all_ids, mgnify_metadata, and detail_proxy. This allows for creating a new MGnetizer instance with different parameters without modifying the existing instance.
        """
        return BioSampler(
            run_ids=run_ids,
            config=self.config,
            client=self.client,
            metadata=metadata or self._metadata,
        )

    @property
    def resource(self) -> str:
        """for checkpointmixin"""
        return self._resource

    @property
    def metadata(self) -> ResultsHandler:
        """Returns the enriched metadata as a ResultsHandler instance."""
        return self._metadata

    @metadata.setter
    def metadata(self, value: ResultsHandler):
        if not isinstance(value, ResultsHandler):
            raise ValueError("metadata must be an instance of ResultsHandler.")
        self._metadata = value

    @property
    def _results(self):
        return self._metadata.data

    @_results.setter
    def _results(self, value):
        self._metadata.data = value

    @property
    def all_ids(self) -> list[str]:
        return self._all_ids

    @all_ids.setter
    def all_ids(self, value: list[str]):
        if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
            raise ValueError("all_ids must be a list of strings.")
        self._all_ids = sorted(value)

    @property
    def params(self) -> dict[str, Any]:
        """for checkpointmixin"""
        return {
            "annotator": str(self.__class__),
            "resource": "biosamples",
            "given_ids": self.all_ids,
        }

    def _iter_leftovers(self) -> list[str]:
        """
        Identify and return the list of run accessions that have not yet been enriched.

        Parameters
        ----------
        all_ids : list of str
            The complete list of run accessions.
        enriched_ids : list of str
            The list of run accessions that have already been enriched.

        Returns
        -------
        list of str
            A list of run accessions that are present in `all_ids` but not in `enriched_ids`.
        """
        self.try_load_cache()
        return [x for x in self.all_ids if x not in self._metadata.get_ids("SampleID")]

    def enrich(
        self,
        limit: Optional[int] = 200,
        hide_progress: bool = False,
        incl_ena: bool = True,
        skip_failed: bool = True,
    ):
        """
        Enriches the biosample metadata for the biosamples in the taxonomic dataset by iterating through the biosample accessions and retrieving their details using the BiosampleDetail proxy. The results are cached using the CheckpointMixin to avoid redundant API calls in future runs.

        Parameters
        ----------
        limit : Optional[int], default=200
            An optional integer to limit the number of biosamples to enrich. If not provided, it defaults to 200. This is useful for testing or when dealing with large datasets to avoid long runtimes during development. If set to None, there will be no limit on the number of biosamples enriched.

        Returns
        -------
        None
            The function does not return anything. It updates the `run_results` attribute of the TaxaMGazine instance with the enriched run metadata.

        """

        logger.debug(
            f"Starting enrichment of biosample meta for short description with limit {limit}."
        )

        runs_todo: list[str] = self._iter_leftovers()[:limit]
        # logger.warning(
        #     f"Enriching {len(runs_todo)} biosamples. Total samples (with runs enriched): {len(self.runs_to_samples)}. Already enriched: {len(self.biosamples_metadata)}."
        # )

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
                bm = get_biosample_metadata(run, incl_ena=incl_ena)
            except Exception as e:
                logger.error(f"Error occurred while enriching run {run}: {e}")
                bm = False

            if isinstance(bm, pd.DataFrame) and not bm.empty:
                self._metadata.data.extend([bm.iloc[0].to_dict()])
                self.write_results(1, self._results)
                continue

            if not skip_failed:
                continue
            else:
                logger.error(
                    f"Enrichment for biosample {run} did not return a valid DataFrame. Appending placeholder with GivenID only."
                )
                self._metadata.data.extend([{"GivenID": run}])
                self.write_results(1, self._results)

    async def aenrich(
        self,
        limit: Optional[int] = 200,
        hide_progress: bool = False,
        incl_ena: bool = True,
        skip_failed: bool = True,
    ) -> None:
        """
        Asynchronously enriches the metadata for the given ids by iterating through the ids and retrieving their details using the corresponding MGnifyDetail proxy. The results are cached using the CheckpointMixin to avoid redundant API calls in future runs.

        Parameters
        ----------
        limit : Optional[int], default=200
            An optional integer to limit the number of ids to enrich. If not provided, it defaults to 200.
            If set to None, there will be no limit on the number of ids enriched.
        hide_progress : bool, default=False
            Whether to hide the progress bar during enrichment.
        """
        # TODO
        logger.error(
            "Asynchronous enrichment of biosample metadata is not yet implemented."
        )

        # ids_todo: list[str] = self._iter_leftovers()[:limit]

        # logger.warning(
        #     f"Enriching {len(ids_todo)} ids. Total runs: {len(self.all_ids)}. Already enriched: {len(self._metadata)}."
        # )

        # async def _fetch(run: str) -> list[dict[str, Any]]:
        #     try:
        #         r = await aget_biosample_metadata(run, incl_ena=incl_ena)
        #         return r
        #     except Exception as e:
        #         logger.error(f"Error occurred while enriching run {run}: {e}")
        #         return False

        # tasks = [asyncio.create_task(_fetch(run)) for run in ids_todo]

        # for done in tqdm_asyncio.as_completed(
        #     tasks,
        #     total=len(self.all_ids),
        #     initial=len(self._metadata),
        #     desc="Enriching biosamples",
        #     disable=hide_progress,
        # ):
        #     bm = await done
        #     logger.debug(f"Enriched biosample metadata: {bm}")
        #     if isinstance(bm, pd.DataFrame) and not bm.empty:
        #         self._metadata.data.extend([bm.iloc[0].to_dict()])
        #         self.write_results(1, self._results)
        #         continue

        #     if not skip_failed:
        #         continue
        #     else:
        #         logger.error(
        #             f"Enrichment for biosample {run} did not return a valid DataFrame. Appending placeholder with GivenID only."
        #         )
        #         self._metadata.data.extend([{"GivenID": run}])
        #         self.write_results(1, self._results)
