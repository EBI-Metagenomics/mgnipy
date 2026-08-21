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
# modified for Biosamples metadata and to fit MGnipy codebase
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
import asyncio
from typing import Any

import httpx
import pandas as pd
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm_asyncio

from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy._shared_helpers.ena import (
    aget_ena_metadata_from_run_acc,
    get_ena_metadata_from_run_acc,
)
from mgnipy._shared_helpers.validators import validate_status_code

URL = "https://www.ebi.ac.uk/biosamples/samples"
HEADERS = {"Accept": "application/json"}
SAMPLE_ID = "SampleID"
RUN_ID = "RunID"
GIVEN_ID = "GivenID"


def get_biosample_metadata(
    sample_acc: str,
    client: httpx.Client | None = None,
    incl_ena: bool = False,
) -> pd.DataFrame | bool:
    """
    Fetches BioSamples metadata for a given sample or run accession.

    This function retrieves curated metadata from the BioSamples database for the provided
    sample or run accession. It returns a DataFrame with the fields "SampleID", "name", "taxid", "SRA accession", and any other characteristics (not standardized) available for the sample. See BioSamples documentation for more details: https://read-docs-biosamples.readthedocs.io/en/latest/update/curation.html. If the sample or run accession is not found or if there is an error during retrieval, the function returns False.

    Parameters
    ----------
    sample_acc : str
        A string representing the sample or run accession for which the metadata needs to be retrieved.
        e.g. "SAMEA5180673"
    incl_ena : bool
        If True, the function will first attempt to retrieve metadata from ENA for the given run accession and include it in the BioSamples query parameters. This can help to retrieve more comprehensive metadata if the sample is linked to an ENA run. If False, the function will query BioSamples using only the provided sample accession.
    client: httpx.Client, optional
        An optional httpx.Client instance to use for making the API request. If not provided, just use httpx get

    Returns
    -------
    pd.DataFrame | bool
        A DataFrame containing the BioSamples metadata for the given sample or run accession, or False if the accession is not found or if there is an error during retrieval.

    Raises
    ------
    ValueError
        If the provided accession appears to be a project accession rather than a sample or run accession.
        i.e., if the accession starts with "ERP", "DRP", "SRP", or "PRJ"

    Notes
    -----
    - connection clean up is not handled in this function! If a client is passed, it is the caller's responsibility to manage its lifecycle (e.g., closing it after use).

    Examples
    --------
    >>> # Example usage of the function to retrieve BioSamples metadata for a given sample accession
    >>> biosample_metadata = get_biosample_metadata("SAMEA5180673", incl_ena=False) # doctest: +SKIP
    >>> # another example with ENA metadata
    >>> biosample_metadata_with_ena = get_biosample_metadata("SAMEA111547191", incl_ena=True) # doctest: +SKIP
    """
    # Query the BioSamples API for the given sample accession
    # https://read-docs-biosamples.readthedocs.io/en/latest/search/search-programmatically.html

    char_texts: dict[str, str] = {}

    if (
        sample_acc.startswith("ERP")
        or sample_acc.startswith("DRP")
        or sample_acc.startswith("SRP")
        or sample_acc.startswith("PRJ")
    ):
        raise ValueError(
            f"Provided accession {sample_acc} appears to be a project accession rather than a sample accession. Please provide a sample or runs accession to retrieve BioSamples metadata."
        )

    _given_id = sample_acc
    run_acc = None
    char_texts = {GIVEN_ID: _given_id}

    if incl_ena:
        logger.debug(f"Attempting to retrieve ENA metadata for sample {sample_acc}")
        ena_metadata = get_ena_metadata_from_run_acc(sample_acc, client=client)
        if ena_metadata is not False:
            # note saving over given sample_acc
            sample_acc = ena_metadata.loc[0, SAMPLE_ID]
            run_acc = ena_metadata.loc[0, RUN_ID]
            logger.debug(
                f"ENA metadata found for sample {sample_acc} and run {run_acc}, including in BioSamples query parameters."
            )
            # adding all ENA metadata fields to char_texts to be included in BioSamples results
            for col in ena_metadata.columns:
                logger.debug(f"Adding ENA metadta field {col}")
                char_texts[col] = ena_metadata.loc[0, col]

        else:
            logger.warning(
                f"No ENA metadata found for sample {sample_acc}, proceeding with BioSamples query without ENA parameters."
            )
            char_texts = {
                SAMPLE_ID: sample_acc,
                RUN_ID: run_acc,
            }
    else:
        logger.debug(
            f"incl_ena is set to False. Proceeding with BioSamples query for sample {sample_acc} without ENA metadata."
        )

    param = {"filter": f"acc:{sample_acc}"}

    if client:
        results: httpx.Response = client.get(URL, headers=HEADERS, params=param)
    else:
        results: httpx.Response = httpx.get(URL, headers=HEADERS, params=param)

    # checks
    logger.debug(f"Response status code: {results.status_code}")
    if not validate_status_code(
        response=results, acc=sample_acc, logger=logger, db="BioSamples"
    ):
        return False

    if "_embedded" not in results.json():
        logger.error(
            f"'_embedded' key not found in BioSamples response for sample {sample_acc}: {results.json()}"
        )
        return False

    try:
        # getting first sample record returned
        returned_samples: list[dict[str, Any]] = results.json()["_embedded"]["samples"]
    except (KeyError, TypeError):
        logger.error(f"Error parsing BioSamples response for sample {sample_acc}")
        return False

    if not returned_samples:
        logger.error(f"No BioSamples record found for sample {sample_acc}")
        return False
    elif len(returned_samples) > 1:
        logger.warning(
            f"Multiple BioSamples records found for sample {sample_acc}, using the first one returned. Total records found: {len(returned_samples)}"
        )
    biosample_record: dict[str, Any] = returned_samples[0]

    # metadta in characteristics field
    characteristics: dict[str, list[dict[str, Any]]] = biosample_record.get(
        "characteristics", {}
    )

    # function to get the first text value for a given characteristic, or "NA" if not available
    def first_text(name: str) -> str:
        values = characteristics.get(name, [])
        if not values:
            return "NA"
        text = values[0].get("text", "")
        return text if text else "NA"

    sample_acc = first_text("External Id")
    if char_texts.get(GIVEN_ID) != sample_acc and run_acc is None:
        # assuming given id is run if doesn't match sample id
        run_acc = char_texts.get(GIVEN_ID)

    # add sampleID, name, taxid, SRA accession,
    char_texts.update(
        {
            SAMPLE_ID: sample_acc,
            RUN_ID: run_acc,
            "SRA accession": biosample_record.get("sraAccession", "NA"),
            "name": biosample_record.get("name", "NA"),
            "taxid": biosample_record.get("taxId", "NA"),
        }
    )

    # now adding characteristics texts
    char_texts.update({key: first_text(key) for key in characteristics.keys()})

    # to pandas
    df = pd.DataFrame(char_texts, index=[0])
    return df


def get_all_biosample_metadata(
    samples: list[str],
    incl_ena: bool = False,
) -> pd.DataFrame:
    """
    Fetches BioSamples metadata for a list of sample accessions.

    This function retrieves metadata from Biosamples. For each valid sample accession, the
    metadata is parsed and stored in a dictionary, where the key is the sample
    accession and the value is a DataFrame containing the metadata.

    Parameters
    ----------
    samples : list[str]
        A list of strings representing sample accessions for which the metadata needs to be retrieved.
    incl_ena : bool
        If True, the function will first attempt to retrieve metadata from ENA for the given run

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the BioSamples metadata for all requested samples.
    """
    sample_metadata = []

    with httpx.Client(headers=HEADERS) as client:
        for sample in tqdm_sync(
            samples, desc="Retrieving BioSamples metadata for samples"
        ):
            res_df = get_biosample_metadata(sample, incl_ena=incl_ena, client=client)
            if res_df is not False:
                sample_metadata.append(res_df)

    return pd.concat(sample_metadata, ignore_index=True)


async def aget_biosample_metadata(
    sample_acc: str,
    client: httpx.AsyncClient,
    incl_ena: bool = False,
) -> pd.DataFrame | bool:
    """
    Fetches BioSamples metadata for a given sample or run accession.

    This function retrieves curated metadata from the BioSamples database for the provided
    sample or run accession. It returns a DataFrame with the fields "SampleID", "name", "taxid", "SRA accession", and any other characteristics (not standardized) available for the sample. See BioSamples documentation for more details: https://read-docs-biosamples.readthedocs.io/en/latest/update/curation.html. If the sample or run accession is not found or if there is an error during retrieval, the function returns False.

    Parameters
    ----------
    sample_acc : str
        A string representing the sample or run accession for which the metadata needs to be retrieved.
        e.g. "SAMEA5180673"
    incl_ena : bool
        If True, the function will first attempt to retrieve metadata from ENA for the given run accession and include it in the BioSamples query parameters. This can help to retrieve more comprehensive metadata if the sample is linked to an ENA run. If False, the function will query BioSamples using only the provided sample accession.
    client: httpx.AsyncClient
        An httpx.AsyncClient instance to use for making the API request.

    Returns
    -------
    pd.DataFrame | bool
        A DataFrame containing the BioSamples metadata for the given sample or run accession, or False if the accession is not found or if there is an error during retrieval.

    Raises
    ------
    ValueError
        If the provided accession appears to be a project accession rather than a sample or run accession.
        i.e., if the accession starts with "ERP", "DRP", "SRP", or "PRJ"

    Notes
    -----
    - connection clean up is not handled in this function! If a client is passed, it is the caller's responsibility to manage its lifecycle (e.g., closing it after use).

    Examples
    --------
    >>> # Example usage of the function to retrieve BioSamples metadata for a given sample accession
    >>> biosample_metadata = get_biosample_metadata("SAMEA5180673", incl_ena=False) # doctest: +SKIP
    >>> # another example with ENA metadata
    >>> biosample_metadata_with_ena = get_biosample_metadata("SAMEA111547191", incl_ena=True) # doctest: +SKIP
    """
    # Query the BioSamples API for the given sample accession
    # https://read-docs-biosamples.readthedocs.io/en/latest/search/search-programmatically.html

    char_texts: dict[str, str] = {}

    if (
        sample_acc.startswith("ERP")
        or sample_acc.startswith("DRP")
        or sample_acc.startswith("SRP")
        or sample_acc.startswith("PRJ")
    ):
        raise ValueError(
            f"Provided accession {sample_acc} appears to be a project accession rather than a sample accession. Please provide a sample or runs accession to retrieve BioSamples metadata."
        )

    _given_id = sample_acc
    run_acc = None
    char_texts = {GIVEN_ID: _given_id}

    if incl_ena:
        logger.debug(f"Attempting to retrieve ENA metadata for sample {sample_acc}")
        ena_metadata = await aget_ena_metadata_from_run_acc(sample_acc, client=client)
        if ena_metadata is not False:
            # note saving over given sample_acc
            sample_acc = ena_metadata.loc[0, SAMPLE_ID]
            run_acc = ena_metadata.loc[0, RUN_ID]
            logger.debug(
                f"ENA metadata found for sample {sample_acc} and run {run_acc}, including in BioSamples query parameters."
            )
            # adding all ENA metadata fields to char_texts to be included in BioSamples results
            for col in ena_metadata.columns:
                logger.debug(f"Adding ENA metadta field {col}")
                char_texts[col] = ena_metadata.loc[0, col]

        else:
            logger.warning(
                f"No ENA metadata found for sample {sample_acc}, proceeding with BioSamples query without ENA parameters."
            )
            char_texts = {
                SAMPLE_ID: sample_acc,
                RUN_ID: run_acc,
            }
    else:
        logger.debug(
            f"incl_ena is set to False. Proceeding with BioSamples query for sample {sample_acc} without ENA metadata."
        )

    logger.debug(f"client: {client}")
    results: httpx.Response = await client.get(
        URL, headers=HEADERS, params={"filter": f"acc:{sample_acc}"}
    )

    # checks
    logger.debug(f"Response status code: {results.status_code}")
    if not validate_status_code(
        response=results, acc=sample_acc, logger=logger, db="BioSamples"
    ):
        return False

    if "_embedded" not in results.json():
        logger.error(
            f"'_embedded' key not found in BioSamples response for sample {sample_acc}: {results.json()}"
        )
        return False

    try:
        # getting first sample record returned
        returned_samples: list[dict[str, Any]] = results.json()["_embedded"]["samples"]
    except (KeyError, TypeError):
        logger.error(f"Error parsing BioSamples response for sample {sample_acc}")
        return False

    if not returned_samples:
        logger.error(f"No BioSamples record found for sample {sample_acc}")
        return False
    elif len(returned_samples) > 1:
        logger.warning(
            f"Multiple BioSamples records found for sample {sample_acc}, using the first one returned. Total records found: {len(returned_samples)}"
        )
    biosample_record: dict[str, Any] = returned_samples[0]

    # metadta in characteristics field
    characteristics: dict[str, list[dict[str, Any]]] = biosample_record.get(
        "characteristics", {}
    )

    # function to get the first text value for a given characteristic, or "NA" if not available
    async def first_text(name: str) -> str:
        values = characteristics.get(name, [])
        if not values:
            return "NA"
        text = values[0].get("text", "")
        return text if text else "NA"

    sample_acc = await first_text("External Id")
    if char_texts.get(GIVEN_ID) != sample_acc and run_acc is None:
        # assuming given id is run if doesn't match sample id
        run_acc = char_texts.get(GIVEN_ID)

    # add sampleID, name, taxid, SRA accession,
    char_texts.update(
        {
            SAMPLE_ID: sample_acc,
            RUN_ID: run_acc,
            "SRA accession": biosample_record.get("sraAccession", "NA"),
            "name": biosample_record.get("name", "NA"),
            "taxid": biosample_record.get("taxId", "NA"),
        }
    )

    # now adding characteristics texts
    char_texts.update({key: await first_text(key) for key in characteristics.keys()})

    # to pandas
    df = pd.DataFrame(char_texts, index=[0])
    return df


async def aget_all_biosample_metadata(
    samples: list[str],
    incl_ena: bool = False,
) -> pd.DataFrame:
    """
    Fetches BioSamples metadata for a list of sample accessions.

    This function retrieves metadata from Biosamples. For each valid sample accession, the
    metadata is parsed and stored in a dictionary, where the key is the sample
    accession and the value is a DataFrame containing the metadata.

    Parameters
    ----------
    samples (list[str])
        A list of strings representing sample accessions for which the metadata needs to be retrieved.

    Returns
    -------
    dict[str, pd.DataFrame]
        A dictionary where keys are sample accessions and values are DataFrames containing the corresponding BioSamples metadata.

    Notes
    -----
    - connection clean up is not handled in this function! If a client is passed, it is the caller's responsibility to manage its lifecycle (e.g., closing it after use).
    """
    sample_metadata = []

    semaphore = get_semaphore(10)

    # protect api
    async with semaphore:
        async with httpx.AsyncClient(headers=HEADERS) as client:
            tasks = {
                asyncio.create_task(
                    aget_biosample_metadata(acc, client=client, incl_ena=incl_ena)
                ): acc
                for acc in samples
            }

            for done in tqdm_asyncio.as_completed(
                tasks, desc="(async) Retrieving BioSamples metadata for samples"
            ):
                res_df = await done
                if res_df is not False:
                    sample_metadata.append(res_df)

    return pd.concat(sample_metadata, ignore_index=True)
