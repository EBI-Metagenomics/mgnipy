from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

import httpx
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm_asyncio

from mgnipy._models.config import MGnipyConfig
from mgnipy._models.constants.CONSTANTS import SupportedEndpoints
from mgnipy._shared_helpers.ena import URL as ENA_URL
from mgnipy._shared_helpers.httpx_helpers import init_httpx_client
from mgnipy._shared_helpers.validators import validate_status_code
from mgnipy.V2.mgnifier.metadata import MGnifyMetadata
from mgnipy.V2.mixins import CheckpointMixin, ClientManagerMixin

logger = logging.getLogger(__name__)

ENA_HEADERS = {"Accept": "application/json"}
ENA_CONFIG_ADDONS = {"base_url": ENA_URL}


def _sample_query(sample_id: str) -> dict[str, str]:
    return {
        "result": "sample",
        "query": f'accession="{sample_id}" OR secondary_sample_accession="{sample_id}"',
        "fields": "all",
        "format": "json",
    }


def get_ena_sample_metadata(
    sample_id: str,
    client: httpx.Client | None = None,
) -> list[dict[str, Any]] | bool:
    """Fetch ENA sample records matching an accession or secondary accession."""
    request_client = client or httpx
    response = request_client.get(
        ENA_URL,
        headers=ENA_HEADERS,
        params=_sample_query(sample_id),
    )

    if not validate_status_code(
        response=response, acc=sample_id, logger=logger, db="ENA"
    ):
        return False

    try:
        payload = response.json()
    except ValueError:
        logger.error("Invalid JSON returned by ENA for sample %s", sample_id)
        return False

    if not isinstance(payload, list):
        logger.error("Unexpected ENA response for sample %s: %r", sample_id, payload)
        return False
    if not payload:
        logger.error("Empty ENA response for sample %s", sample_id)
        return False
    return payload


async def aget_ena_sample_metadata(
    sample_id: str,
    client: httpx.AsyncClient,
) -> list[dict[str, Any]] | bool:
    """Asynchronously fetch ENA sample records matching an accession."""
    response = await client.get(
        ENA_URL,
        headers=ENA_HEADERS,
        params=_sample_query(sample_id),
    )

    if not validate_status_code(
        response=response, acc=sample_id, logger=logger, db="ENA"
    ):
        return False

    try:
        payload = response.json()
    except ValueError:
        logger.error("Invalid JSON returned by ENA for sample %s", sample_id)
        return False

    if not isinstance(payload, list):
        logger.error("Unexpected ENA response for sample %s: %r", sample_id, payload)
        return False
    if not payload:
        logger.error("Empty ENA response for sample %s", sample_id)
        return False
    return payload


class ENASampler(CheckpointMixin, ClientManagerMixin):
    """Fetch ENA sample metadata for a list of sample accessions.

    Results are stored in an :class:`MGnifyMetadata` instance and can be
    checkpointed in the same way as other MGnipy collectors.
    """

    def __init__(
        self,
        sample_ids: list[str],
        config: MGnipyConfig = None,
        metadata: MGnifyMetadata = None,
    ):
        self._all_ids = sorted(sample_ids)
        self._metadata = metadata or MGnifyMetadata()
        self._results = self._metadata._results
        self.config = MGnipyConfig.model_validate(
            (config or MGnipyConfig()).model_dump() | ENA_CONFIG_ADDONS
        )
        self.client = init_httpx_client(self.config, headers=ENA_HEADERS)
        self._resource = SupportedEndpoints("_custom_endpoint")

    def __call__(
        self,
        sample_ids: list[str],
        metadata: MGnifyMetadata = None,
    ) -> "ENASampler":
        return ENASampler(
            sample_ids=sample_ids,
            config=self.config,
            metadata=metadata or self._metadata,
        )

    def __repr__(self) -> str:
        return f"ENASampler(len(sample_ids)={len(self._all_ids)}, metadata={self._metadata})"

    def __str__(self) -> str:
        return (
            f"ENASampler with {len(self._all_ids)} sample_ids.\n"
            f"Progress: {len(self._metadata)} ids.\n"
            f"Cache directory: {self.cache_path}\n"
        )

    @property
    def resource(self) -> str:
        return self._resource

    @property
    def metadata(self) -> MGnifyMetadata:
        return self._metadata

    @metadata.setter
    def metadata(self, value: MGnifyMetadata) -> None:
        if not isinstance(value, MGnifyMetadata):
            raise ValueError("metadata must be an instance of MGnifyMetadata.")
        self._metadata = value
        self._results = value._results

    @property
    def all_ids(self) -> list[str]:
        return self._all_ids

    @all_ids.setter
    def all_ids(self, value: list[str]) -> None:
        if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
            raise ValueError("all_ids must be a list of strings.")
        self._all_ids = sorted(value)

    @property
    def params(self) -> dict[str, Any]:
        return {
            "annotator": str(self.__class__),
            "resource": "ena_samples",
            "given_ids": self.all_ids,
        }

    def _iter_leftovers(self) -> list[str]:
        self.try_load_cache()
        self._metadata._sync_data()
        completed_ids = {
            identifier
            for record in self._metadata.data or []
            for identifier in (
                record.get("accession"),
                record.get("sample_accession"),
                record.get("secondary_sample_accession"),
            )
            if identifier is not None
        }
        return [
            sample_id for sample_id in self.all_ids if sample_id not in completed_ids
        ]

    def _append(self, sample_id: str, records: list[dict[str, Any]]) -> None:
        self._metadata.append_result(page_num=1, value=records)
        self.write_results(1, self._metadata.data)

    def enrich(
        self,
        limit: Optional[int] = 200,
        hide_progress: bool = False,
        skip_failed: bool = True,
    ) -> None:
        """Fetch and checkpoint ENA metadata for the configured sample IDs."""
        ids_todo = self._iter_leftovers()[:limit]
        client = self.client.get_httpx_client()
        for sample_id in tqdm_sync(
            ids_todo,
            total=len(self.all_ids),
            initial=len(self._metadata),
            desc="Enriching ENA samples",
            disable=hide_progress,
        ):
            try:
                records = get_ena_sample_metadata(sample_id, client=client)
            except RuntimeError:
                self.renew_client()
                records = get_ena_sample_metadata(
                    sample_id, client=self.client.get_httpx_client()
                )
            except Exception:
                logger.exception("Error enriching ENA sample %s", sample_id)
                records = False

            if records is not False:
                self._append(sample_id, records)
            elif not skip_failed:
                logger.error("Skipping failed ENA sample %s", sample_id)

    async def aenrich(
        self,
        limit: Optional[int] = 200,
        hide_progress: bool = False,
        skip_failed: bool = True,
    ) -> None:
        """Asynchronously fetch and checkpoint ENA metadata."""
        ids_todo = self._iter_leftovers()[:limit]
        client = self.client.get_async_httpx_client()

        async def fetch(sample_id: str) -> tuple[str, list[dict[str, Any]] | bool]:
            try:
                return sample_id, await aget_ena_sample_metadata(sample_id, client)
            except Exception:
                logger.exception("Error enriching ENA sample %s", sample_id)
                return sample_id, False

        tasks = [asyncio.create_task(fetch(sample_id)) for sample_id in ids_todo]
        for done in tqdm_asyncio.as_completed(
            tasks,
            total=len(self.all_ids),
            initial=len(self._metadata),
            desc="Enriching ENA samples",
            disable=hide_progress,
        ):
            sample_id, records = await done
            if records is not False:
                self._append(sample_id, records)
            elif not skip_failed:
                logger.error("Skipping failed ENA sample %s", sample_id)
