import asyncio
import json
import os
from pathlib import Path
from typing import (
    Any,
    Literal,
    Optional,
)
from urllib.parse import urlencode

import pandas as pd
from mgni_py_v1 import Client
from mgni_py_v1.api.analyses import analyses_list
from mgni_py_v1.api.biomes import biomes_studies_list
from mgni_py_v1.api.runs import runs_analyses_list
from mgni_py_v1.api.samples import samples_runs_list
from mgni_py_v1.api.studies import studies_samples_list
from mgni_py_v1.types import Response
from tqdm import tqdm

from mgnipy._pydantic_models.CONSTANTS import SupportedEndpoints
from mgnipy._pydantic_models.adapters import validate_experiment_type

# args
CONCURRENCY = 5
METADATA_MODULES = {
    SupportedEndpoints.BIOMES: biomes_studies_list,  # list studies per biome, search in biome
    SupportedEndpoints.STUDIES: studies_samples_list,  # list samples per study, search in study
    SupportedEndpoints.SAMPLES: samples_runs_list,  # list runs/assemply per sample, search in sample
    SupportedEndpoints.RUNS: runs_analyses_list,  # list analyses per run, search in a given run
    SupportedEndpoints.ANALYSES: analyses_list, # and results here, search in a given analyses
}

semaphore = asyncio.Semaphore(CONCURRENCY)


# init for each model
class Mgnifier:
    """
    The Mgnipy Mgnifier class is a user-friendly interface for exploring study, sample and analysis metadata from the MGnify API.

    """

    def __init__(
        self,
        *,
        db: Optional[
            Literal["biomes", "studies", "samples", "runs", "analyses"]
        ] = None,
        params: Optional[dict[str, Any]] = None,
        checkpoint_dir: Optional[Path] = None,
        checkpoint_freq: Optional[int] = None,
        **kwargs,
    ):
        # url
        self._api_version = "v1"
        self._base_url = "https://www.ebi.ac.uk/metagenomics/api/"
        self._db = db
        self._mpy_module = METADATA_MODULES[SupportedEndpoints(db)]

        # TODO checkpoints
        # prep checkpoint if
        self._checkpoint_dir = checkpoint_dir
        self._checkpoint_freq = checkpoint_freq or 3
        self._checkpoint_csv = None
        self._checkpoint_json = None

        # params
        self._params = params or {}
        if kwargs:
            self._params.update(kwargs)
        if "page_size" not in self._params:
            self._params["page_size"] = 25
        if "experiment_type" in self._params:
            et_param = self._params["experiment_type"]
            # validate each exp type
            for et in et_param if isinstance(et_param, list) else [et_param]:
                validate_experiment_type(et)

        self._url = self._build_url()

        # cache
        self._total_pages = None
        self._cached_first_page = None
        self._cached_the_rest = None
        self._page_checkpoint = 0

        self._results = None

    @property
    def mpy_module(self):
        return self._mpy_module

    @mpy_module.setter
    def mpy_module(self, new_module):
        self._mpy_module = new_module
        if self._checkpoint_dir is not None:
            self._checkpoint_csv = os.path.join(
                self._checkpoint_dir, f"{self._mpy_module.__name__}.csv"
            )
            self._checkpoint_json = os.path.join(
                self._checkpoint_dir, f"{self._mpy_module.__name__}.json"
            )

    def __getattr__(self, name: str):
        if name == "mgni_py_client":
            return self._init_client()
        else:
            return self.__dict__[f"_{name}"]

    def __str__(self):
        return (
            f"Mgnifier instance for MGnify {self._db} metadata\n"
            f"----------------------------------------\n"
            f"Base URL: {self._base_url}\n"
            f"API Version: {self._api_version}\n"
            f"Parameters: {self._params}\n"
            f"Checkpoint Directory: {self._checkpoint_dir}\n"
            f"========================================\n"
            f"Request URL: {self._url}\n"
        )

    def plan(self):
        """
        Allows the user to see the numb er of pages/records to be retrieved
        before retrieving all data.
        """
        print("Planning the API call with params:")
        print(self._params)
        print(
            f"Acquiring meta for {self._params.get('page_size', 25)} {self._db} per page..."
        )
        print(f"Request URL: {self._url}")
        # make get request using mgni_py client
        resp_dict = self._get_request(self._params)
        if resp_dict is None:
            raise RuntimeError("Failed to get response from MGnify API.")
        # set
        self._total_pages = resp_dict["meta"]["pagination"]["pages"]
        self._current_page = resp_dict["meta"]["pagination"]["page"]
        self._count = resp_dict["meta"]["pagination"]["count"]
        self._cached_first_page = resp_dict["data"]
        self._page_checkpoint = 1

        print(f"Total pages to retrieve: {self._total_pages}")
        print(f"Total records to retrieve: {self._count}")

    def preview(self):
        """
        Previews the metadata of the first page of results as a DataFrame.
        """
        if self._cached_first_page is None:
            print("MGnigier.plan not yet checked. Running now...")
            self.plan()

        print(
            f"Previewing Page 1 of {self._total_pages} pages ({self._count} records)..."
        )

        return self.response_df(self._cached_first_page)

    async def collect(self, pages: Optional[list[int]] = None):

        print(self._url)

        async with self._init_client() as client:
            self._results = await self._collector(client, pages=pages)

        return pd.concat(self._results)

    async def continue_collect(self):
        print("Continuing collection from checkpoint...")
        if self._checkpoint_dir is None:
            raise ValueError("No checkpoint directory specified during initialization.")
        if not os.path.exists(self._checkpoint_json):
            raise FileNotFoundError(
                f"No checkpoint file found at {self._checkpoint_json}"
            )

        pass
        # TODO load checkpoint info

    # TODO pandera schema for data validation
    def response_df(self, data: dict) -> pd.DataFrame:
        """helper functinon to expand attributes column into separate columns"""
        df = pd.DataFrame(data)
        if "attributes" in df.columns:
            attr_df = pd.json_normalize(df["attributes"])
            df = pd.concat([df.drop(columns=["attributes"]), attr_df], axis=1)
        if "relationships" in df.columns:
            rel_df = pd.json_normalize(df["relationships"])
            df = pd.concat([df.drop(columns=["relationships"]), rel_df], axis=1)

        return df

    # helpers
    def _init_client(self):
        client_v1 = Client(
            base_url=str(self._base_url),
            # TODO logs?
        )
        return client_v1

    def _get_request(self, given_params: dict) -> dict:
        with self._init_client() as client:
            response = self._mpy_module.sync_detailed(
                client=client,
                **given_params,
            )
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            return response.parsed.to_dict()
        else: 
            return None

    def _build_url(self) -> str:
        """build url for logging/verbose"""
        start_url = os.path.join(self._base_url, self._api_version, self._db)
        encoded_params = urlencode(self._params)
        return f"{start_url}/?{encoded_params}"

    async def _get_page(self, client: Client, page_num: int) -> Response:
        """coroutine function to get coroutine for each page"""
        # limiting concurrency to protect server
        async with semaphore:
            return await self._mpy_module.asyncio_detailed(
                client=client,
                **self._params,
                page=page_num,
            )

    async def _collector(self, client: Client, pages: Optional[list[int]] = None):

        # not allow to run this without preview/plan first?
        if self._total_pages is None:
            raise AssertionError(
                "Please run Mgnifier.plan or .preview before"
                "deciding to collect metadata for params:\n"
                f"{self._params}"
            )

        if pages is None:
            print("No pages specified, collecting all...")
            pages = list(range(self._page_checkpoint + 1, self._total_pages + 1))

            # init TODO: dict?
            results = (
                [self.response_df(self._cached_first_page)]
                if self._cached_first_page
                else []
            )

        elif isinstance(pages, list):
            if not all(p <= self._total_pages for p in pages):
                raise ValueError(
                    f"One or more specified pages exceed total pages {self._total_pages}."
                    f"Specified pages: {pages}"
                )

            results = []
            print(f"Collecting specified pages: {pages}...")

        else:
            raise ValueError("pages must be a list of integers or None")

        # creating async tasks
        async_tasks = []
        for page_num in pages:
            task = asyncio.create_task(self._get_page(client, page_num))
            # label
            task.page = page_num
            async_tasks.append(task)

        # gathering results as completed
        for task in tqdm(asyncio.as_completed(async_tasks), total=len(async_tasks)):
            result = await task
            # page_num = getattr(task, "page", None) #FIXME why all none
            results.append(self.response_df(result.parsed.to_dict()["data"]))
            # checkpointing
            self._page_checkpoint += 1

            if (
                self._checkpoint_dir is not None
                and self._page_checkpoint % self._checkpoint_freq == 0
            ):
                print(f"Checkpointing at page {self._page_checkpoint}...")
                self._save_checkpoint(results)

        return results

    def _csv_checkpointer(self, results):
        pd.concat(results).to_csv(self._checkpoint_csv, delimiter=",", index=False)

        with open(self._checkpoint_json, "w") as f:
            json.dump(
                {
                    "page_checkpoint": self._page_checkpoint,
                    "params": self._params,
                    "db": self._db,
                    "checkpoint_freq": self._checkpoint_freq,
                },
                f,
                indent=2,
            )

