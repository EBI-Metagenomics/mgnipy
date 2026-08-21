#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2024-2025 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# original version downloaded from: https://github.com/EBI-Metagenomics/mgnify-pipelines-toolkit/blob/595e5bb04a08d6dab5b04e1f4c3afaca1c6a17b2/mgnify_pipelines_toolkit/analysis/shared/dwc_summary_generator.py#L267
# downloaded on: 22-May-2026
# modified to fit MGnipy codebase, reasoning: reduce dependencies, httpx client usage, and avoid logging issues
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import asyncio
from typing import List, Union

import httpx
import pandas as pd
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm_asyncio

from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy._shared_helpers.validators import validate_status_code

URL = "https://www.ebi.ac.uk/ena/portal/api/search"
HEADERS = {"Accept": "application/json"}
RUN_FIELDS_LIST = [
    "secondary_study_accession",
    "sample_accession",
    "instrument_model",
]
RUN_QUERY_ARGS = {
    "result": "read_run",
    "fields": ",".join(RUN_FIELDS_LIST),
    "limit": 10,
    "format": "json",
    "download": "false",
}
SAMPLE_FIELDS_LIST = [
    "lat",
    "lon",
    "collection_date",
    "depth",
    "center_name",
    "temperature",
    "salinity",
    "country",
]
SAMPLE_QUERY_ARGS = {
    "result": "sample",
    "fields": ",".join(SAMPLE_FIELDS_LIST),
    "limit": 10,
    "format": "json",
    "download": "false",
}


def _normalize_record(run_record: dict, sample_record: dict) -> pd.DataFrame:
    """
    Combine and normalize ENA run and sample records into a single DataFrame.
    """

    # combine dicts
    full_res_dict = run_record | sample_record

    # Turn empty values into NA
    full_res_dict = {
        field: "NA" if val == "" else val for field, val in full_res_dict.items()
    }

    if full_res_dict.get("collection_date", "") == "":
        full_res_dict["collectionDate"] = "NA"
    else:
        full_res_dict["collectionDate"] = full_res_dict["collection_date"]

    if "collection_date" in full_res_dict:
        del full_res_dict["collection_date"]

    res_df = pd.DataFrame(full_res_dict, index=[0])
    res_df = res_df.rename(
        columns={
            "run_accession": "RunID",
            "sample_accession": "SampleID",
            "secondary_study_accession": "StudyID",
            "lon": "decimalLongitude",
            "lat": "decimalLatitude",
            "instrument_model": "seq_meth",
        }
    )
    return res_df


def _fetch_run(
    run_acc: str,
    client: httpx.Client | None = None,
) -> dict | bool:
    """
    Fetch ENA run metadata for a given run accession. Returns the metadata as a dictionary if successful, or False if not found or an error occurs.

    Parameters
    ----------
    run_acc : str
        Accession identifier for the run to query from ENA.
    client : httpx.Client, optional
        An optional httpx.Client instance to use for making the request. If not provided, just use httpx.get.

    Notes
    -----
    - connection clean up is not handled in this function! If a client is passed, it is the caller's responsibility to manage its lifecycle (e.g., closing it after use).

    Examples
    --------
    #TODO: add doctests
    """
    run_query_args = RUN_QUERY_ARGS.copy()
    run_query_args["includeAccessions"] = run_acc

    logger.warning(
        f"Fetching ENA run metadata for run {run_acc} with params: {run_query_args}"
    )

    if client:
        results = client.get(URL, headers=HEADERS, params=run_query_args)
    else:
        results = httpx.get(URL, headers=HEADERS, params=run_query_args)

    if not validate_status_code(response=results, acc=run_acc, logger=logger, db="ENA"):
        logger.error(
            f"Failed to fetch ENA run metadata for run {run_acc}. Status code: {results.status_code}"
        )
        return False

    # check if response is empty
    run_payload = results.json()
    if not run_payload:
        logger.error(f"Empty ENA response for run {run_acc}")
        return False

    return run_payload[0]


def _fetch_sample(
    sample_acc: str,
    client: httpx.Client | None = None,
) -> dict | bool:
    """
    Fetch ENA sample metadata for a given sample accession. Returns the metadata as a dictionary if successful, or False if not found or an error occurs.

    Parameters
    ----------
    sample_acc : str
        Accession identifier for the sample to query from ENA.
    client : httpx.Client, optional
        An optional httpx.Client instance to use for making the request. If not provided, just use httpx.get.

    Notes
    -----
    - connection clean up is not handled in this function! If a client is passed, it is the caller's responsibility to manage its lifecycle (e.g., closing it after use).
    """
    sample_query_args = SAMPLE_QUERY_ARGS.copy()
    sample_query_args["includeAccessions"] = sample_acc

    if client:
        results = client.get(URL, headers=HEADERS, params=sample_query_args)
    else:
        results = httpx.get(URL, headers=HEADERS, params=sample_query_args)

    if not validate_status_code(
        response=results, acc=sample_acc, logger=logger, db="ENA"
    ):
        logger.error(
            f"Failed to fetch ENA sample metadata for sample {sample_acc}. Status code: {results.status_code}"
        )
        return False

    # check if response is empty
    payload = results.json()
    if not payload:
        logger.error(f"Empty ENA response for sample {sample_acc}")
        return False

    return payload[0]


async def _afetch_run(run_acc: str, client: httpx.AsyncClient) -> dict | bool:
    """
    Fetch ENA run metadata for a given run accession. Returns the metadata as a dictionary if successful, or False if not found or an error occurs.

    Parameters
    ----------
    run_acc : str
        Accession identifier for the run to query from ENA.
    client : httpx.AsyncClient
        An httpx.AsyncClient instance to use for making the request.

    Notes
    -----
    - connection clean up is not handled in this function! If a client is passed, it is the caller's responsibility to manage its lifecycle (e.g., closing it after use).
    """

    # prep params
    run_query_args = RUN_QUERY_ARGS.copy()
    run_query_args["includeAccessions"] = run_acc

    # fetch data
    logger.debug(f"afetch_run client: {client}")
    results = await client.get(URL, headers=HEADERS, params=run_query_args)

    # checks
    if not validate_status_code(response=results, acc=run_acc, logger=logger, db="ENA"):
        logger.error(
            f"Failed to fetch ENA run metadata for run {run_acc}. Status code: {results.status_code}"
        )
        return False
    # check if response is empty
    run_payload = results.json()
    if not run_payload:
        logger.error(f"Empty ENA response for run {run_acc}")
        return False

    return run_payload[0]


async def _afetch_sample(sample_acc: str, client: httpx.AsyncClient) -> dict | bool:
    """
    Fetch ENA sample metadata for a given sample accession. Returns the metadata as a dictionary if successful, or False if not found or an error occurs.

    Parameters
    ----------
    sample_acc : str
        Accession identifier for the sample to query from ENA.
    client : httpx.AsyncClient
        An httpx.AsyncClient instance to use for making the request.

    Notes
    -----
    - connection clean up is not handled in this function! If a client is passed, it is the caller's responsibility to manage its lifecycle (e.g., closing it after use).
    """

    # prep params
    sample_query_args = SAMPLE_QUERY_ARGS.copy()
    sample_query_args["includeAccessions"] = sample_acc

    # fetch data
    results = await client.get(URL, headers=HEADERS, params=sample_query_args)

    # checks
    if not validate_status_code(
        response=results, acc=sample_acc, logger=logger, db="ENA"
    ):
        logger.error(
            f"Failed to fetch ENA sample metadata for sample {sample_acc}. Status code: {results.status_code}"
        )
        return False
    # check if response is empty
    sample_payload = results.json()
    if not sample_payload:
        logger.error(f"Empty ENA response for sample {sample_acc}")
        return False

    return sample_payload[0]


def get_ena_metadata_from_run_acc(
    run_acc: str, client: httpx.Client | None = None
) -> Union[pd.DataFrame, bool]:
    """
    Fetches and processes metadata from ENA using the provided run accession.
    This function queries the European Nucleotide Archive (ENA) API to retrieve
    metadata related to the specified run accession. Once the metadata is
    retrieved, it performs cleaning and formatting to return the data in a
    structured pandas DataFrame.

    Parameters
    ----------
    run_acc : str
        Accession identifier for the run to query from ENA.
    client : httpx.Client, optional
        An optional httpx.Client instance to use for making the request. If not provided, just use httpx.get.

    Returns
    -------
    Union[pd.DataFrame, bool]
        A pandas DataFrame containing the retrieved and processed metadata
        if the query is successful, or False if the data for the given run
        accession is not found.

    Examples
    --------
    >>> run_acc = "ERR1234567"  # example run accession
    >>> metadata_df = get_ena_metadata_from_run_acc(run_acc) # doctest: +SKIP

    Notes
    -----
    - connection clean up is not handled in this function! If a client is passed, it is the caller's responsibility to manage its lifecycle (e.g., closing it after use).
    """
    run_record: dict | bool = _fetch_run(run_acc, client=client)
    logger.debug(f"Fetched run record for {run_acc}")
    if run_record is False:
        return False

    sample_acc = run_record["sample_accession"]

    sample_record: dict | bool = _fetch_sample(sample_acc, client=client)
    logger.debug(f"Fetched sample record for {sample_acc}")
    if sample_record is False:
        return False

    return _normalize_record(run_record, sample_record)


async def aget_ena_metadata_from_run_acc(
    run_acc: str, client: httpx.AsyncClient | None = None
) -> Union[pd.DataFrame, bool]:
    """
    Async version of get_ena_metadata_from_run_acc.
    """
    run_record: dict | bool = await _afetch_run(run_acc, client=client)
    logger.debug(f"Fetched run record for {run_acc}")
    if run_record is False:
        return False

    sample_acc = run_record["sample_accession"]
    sample_record: dict | bool = await _afetch_sample(sample_acc, client=client)
    logger.debug(f"Fetched sample record for {sample_acc}")
    if sample_record is False:
        return False

    return _normalize_record(run_record, sample_record)


def get_all_ena_metadata_from_run_acc(
    run_accs: List[str],
) -> pd.DataFrame:

    # init for pd concat later
    results: list[pd.DataFrame] = []

    # for safely closing client
    with httpx.Client(headers=HEADERS) as client:
        # progress bar
        for run_acc in tqdm_sync(run_accs, desc="Fetching ENA metadata for runs"):
            logger.debug(f"Fetching ENA metadata for run {run_acc}")
            res_df = get_ena_metadata_from_run_acc(run_acc, client=client)
            if res_df is not False:
                results.append(res_df)

    return pd.concat(results, ignore_index=True)


async def aget_all_ena_metadata_from_run_acc(
    run_accs: list[str],
) -> pd.DataFrame:
    """
    Async version of get_all_ena_metadata_from_run_acc.
    """
    results: list[pd.DataFrame] = []

    semaphore = get_semaphore(10)

    async with semaphore:
        async with httpx.AsyncClient(headers=HEADERS) as client:
            tasks = [
                asyncio.create_task(
                    aget_ena_metadata_from_run_acc(run_acc, client=client)
                )
                for run_acc in run_accs
            ]

            for done in tqdm_asyncio.as_completed(
                tasks,
                total=len(tasks),
                desc="(async) Retrieving ENA metadata",
            ):
                res_df = await done
                if res_df is not False:
                    results.append(res_df)

    return pd.concat(results, ignore_index=True)
