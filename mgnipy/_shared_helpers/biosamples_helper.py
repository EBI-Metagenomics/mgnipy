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

import logging

logger = logging.getLogger(__name__)
from collections import defaultdict
from typing import Any, Dict, List, Union

import pandas as pd
import requests
from mgnify_pipelines_toolkit.analysis.shared.dwc_summary_generator import (
    get_ena_metadata_from_run_acc,
)

URL = "https://www.ebi.ac.uk/biosamples/samples"
HEADERS = {"Accept": "application/json"}


def get_biosample_metadata_from_acc(
    sample_acc: str,
    incl_ena: bool = True,
) -> Union[pd.DataFrame, bool]:
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

    Returns
    -------
    Union[pd.DataFrame, bool]
        A DataFrame containing the BioSamples metadata for the given sample or run accession, or False if the accession is not found or if there is an error during retrieval.

    Raises
    ------
    ValueError
        If the provided accession appears to be a project accession rather than a sample or run accession.
        i.e., if the accession starts with "ERP", "DRP", "SRP", or "PRJ"

    Examples
    --------
    >>> # Example usage of the function to retrieve BioSamples metadata for a given sample accession
    >>> biosample_metadata = get_biosample_metadata_from_acc("SAMEA5180673", incl_ena=False)
    >>> biosample_metadata.loc[0, "SampleID"]
    'SAMEA5180673'
    >>> str(biosample_metadata.loc[0, "taxid"])
    '408170'
    >>> biosample_metadata.loc[0, "StudyID"]
    Traceback (most recent call last):
    ...
    KeyError: 'StudyID'
    >>> # another example with ENA metadata
    >>> biosample_metadata_with_ena = get_biosample_metadata_from_acc("SAMEA111547191", incl_ena=True)
    >>> biosample_metadata_with_ena.loc[0, "StudyID"]
    'ERP142200'
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

    if incl_ena:
        ena_metadata = get_ena_metadata_from_run_acc(sample_acc)
        if ena_metadata is not False:
            # note saving over given sample_acc
            sample_acc = ena_metadata.loc[0, "SampleID"]

            logger.info(
                f"ENA metadata found for sample {sample_acc}, including in BioSamples query parameters."
            )

            for col in ena_metadata.columns:
                char_texts[col] = ena_metadata.loc[0, col]

        else:
            logger.info(
                f"No ENA metadata found for sample {sample_acc}, proceeding with BioSamples query without ENA parameters."
            )
            char_texts = {
                "SampleID": sample_acc,
            }

    results: requests.Response = requests.get(
        URL,
        headers=HEADERS,
        params={"filter": f"acc:{sample_acc}"},
    )

    # if not successful log and return false
    if results.status_code != 200:
        logger.error(f"BioSamples record not found for sample {sample_acc}")
        return False

    if "_embedded" not in results.json():
        logger.error(f"BioSamples record not found for sample {sample_acc}")
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

    # init row with sampleID, name, taxid, SRA accession,
    char_texts.update(
        {
            "SampleID": sample_acc,
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


def get_all_biosample_metadata_from_acc(
    samples: List[str],
) -> Dict[str, pd.DataFrame]:
    """
    Fetches BioSamples metadata for a list of sample accessions.

    This function retrieves metadata from Biosamples. For each valid sample accession, the
    metadata is parsed and stored in a dictionary, where the key is the sample
    accession and the value is a DataFrame containing the metadata.

    Parameters:
        samples (List[str]): A list of strings representing sample accessions for which
            the metadata needs to be retrieved.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary where keys are sample accessions and
        values are DataFrames containing the corresponding BioSamples metadata.
    """
    sample_metadata_dict = defaultdict(pd.DataFrame)

    for sample in samples:
        res_df = get_biosample_metadata_from_acc(sample)
        if res_df is not False:
            sample_metadata_dict[sample] = res_df

    return sample_metadata_dict
