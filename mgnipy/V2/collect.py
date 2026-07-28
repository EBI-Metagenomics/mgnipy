import logging

from mgnipy.V2.mixins import CheckpointMixin

logger = logging.getLogger(__name__)

import asyncio
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm_asyncio
from typing import (
    Any,
    Optional,
)

# from mgnipy.V2.proxies.analyses import AnalysisDetail
# from mgnipy.V2.proxies.studies import StudyDetail
# from mgnipy.V2.proxies.runs import RunDetail
# from mgnipy.V2.proxies.samples import SampleDetail
# from mgnipy.V2.proxies.assemblies import AssemblyDetail
from mgnipy._models.constants.CONSTANTS import SupportedEndpoints, DetailResourceStr
from mgnipy.V2.mgnifier.metadata import MGnifyMetadata
from mgnipy._shared_helpers.httpx_helpers import init_httpx_client
from mgnipy._models.config import MGnipyConfig
from mgnipy.emgapi_v2_client.client import AuthenticatedClient, Client
from mgnipy.V2.proxies import V2_ENDPOINT_DETAIL_PROXIES, MGnifyDetail


class EnrichMGnify(CheckpointMixin):

    def __init__(
        self,
        resource: DetailResourceStr,
        all_ids: list[str],
        config: MGnipyConfig = None,
        client: Optional[Client | AuthenticatedClient] = None,
        mgnify_metadata: MGnifyMetadata = None,
        detail_proxy: "MGnifyDetail" = None,
    ):

        if resource not in DetailResourceStr.__args__:
            raise ValueError(
                f"Invalid resource '{resource}'. Must be one of {DetailResourceStr.__args__}."
            )

        self._resource = SupportedEndpoints(resource)
        self.all_ids = sorted(all_ids)
        self.mgnify_metadata = mgnify_metadata or MGnifyMetadata([])
        self.config = config or MGnipyConfig()
        self.client = client or init_httpx_client(self.config)
        self.detail_proxy: MGnifyDetail = (
            detail_proxy or V2_ENDPOINT_DETAIL_PROXIES.get(self._resource)
        )

    @property
    def _results(self):
        return self.mgnify_metadata.data

    @_results.setter
    def _results(self, value):
        self.mgnify_metadata.data = value

    @property
    def resource(self) -> str:
        """for checkpointmixin"""
        return self._resource

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
        return [x for x in self.all_ids if x not in self.mgnify_metadata.ids]

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
            f"Enriching {len(ids_todo)} ids. Total runs: {len(self.all_ids)}. Already enriched: {len(self.mgnify_metadata)}."
        )

        for count, run in enumerate(
            tqdm_sync(
                ids_todo,
                total=len(self.all_ids),
                initial=len(self.mgnify_metadata),
                desc="Enriching metadata from MGnify",
                disable=hide_progress,
            )
        ):
            logger.debug(f"Enriching id {run}. Count: {count}")
            mg = None
            # get metadata
            try:
                mg = self.detail_proxy(
                    id=run, config=self.config, client=self.client
                ).get()
                logger.debug(f"{mg}")
            except Exception as e:
                logger.warning(f"Error occurred while enriching id {run}: {e}.")

            if mg is not None:
                self.mgnify_metadata.data.extend(mg)
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
            f"Enriching {len(ids_todo)} ids. Total runs: {len(self.all_ids)}. Already enriched: {len(self.mgnify_metadata)}."
        )

        async def _fetch(id: str) -> list[dict[str, Any]]:
            try:
                r = await self.detail_proxy(
                    id=id, config=self.config, client=self.client
                ).aget()
                return r
            except Exception as e:
                logger.error(f"Error occurred while enriching id {id}: {e}")
                return None

        tasks = [asyncio.create_task(_fetch(id)) for id in ids_todo]

        for done in tqdm_asyncio.as_completed(
            tasks,
            total=len(self.all_ids),
            initial=len(self.mgnify_metadata),
            desc="Enriching metadata from MGnify",
            disable=hide_progress,
        ):
            mg = await done
            if mg:
                self.mgnify_metadata.data.extend(mg)
