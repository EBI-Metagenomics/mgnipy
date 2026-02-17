import asyncio
import os
from copy import deepcopy
from pathlib import Path
from typing import (
    Any,
    List,
    Literal,
    Optional,
)
from urllib.parse import urlencode

from tqdm import tqdm
from math import ceil
from mgnipy._shared_helpers.pydantic_help import validate_gt_int

from mgnipy.V2 import Client

import pandas as pd
import inspect
from mgnipy._shared_helpers import get_semaphore
from mgnipy.V2._mgnipy_models.CONSTANTS import SupportedEndpoints

from mgnipy.V2.biomes import list_mgnify_biomes
from mgnipy.V2.studies import (
    list_mgnify_studies,
    list_mgnify_study_samples,
    list_mgnify_study_analyses,
)
from mgnipy.V2.samples import list_mgnify_samples
from mgnipy.V2.analyses import get_mgnify_analysis
from mgnipy.V2.genomes import list_mgnify_genomes

semaphore = get_semaphore()

# constants
from mgnipy import (
    BASE_URL,
    #CACHE_DIR, TODO cache, paused for now
)

METADATA_MODULES = {
    SupportedEndpoints.BIOMES: list_mgnify_biomes,  # what biomes
    SupportedEndpoints.STUDIES: list_mgnify_studies,  # search for study
    SupportedEndpoints.SAMPLES: list_mgnify_study_samples,  # all samples for given study
    SupportedEndpoints.ANALYSES: list_mgnify_study_analyses,  # all analyses for given study
    SupportedEndpoints.GENOMES: list_mgnify_genomes, 
}

class Mgnifier:

    def __init__(
        self,
        *,
        resource: Optional[
            Literal["biomes", "studies", "samples", "genomes", "analyses"]
        ] = None,
        params: Optional[dict[str, Any]] = None,
        checkpoint_dir: Optional[Path] = None,
        checkpoint_freq: Optional[int] = None,
        **kwargs,
    ):
        # for client
        self._base_url: str = BASE_URL
        self._resource: str = resource or "biomes"  # default
        self._mpy_module = METADATA_MODULES[
            SupportedEndpoints(self._resource)
        ]

        # params as dict
        self._params: dict[str, Any] = params or {}
        # add kwargs to params if provided
        if kwargs:
            self._params.update(kwargs)
        # check page_size > 0 if provided, default 25
        if "page_size" not in self._params:
            self._params["page_size"] = 25
        else: 
            validate_gt_int(self._params["page_size"])
        # check params are valid for endpoint
        self._kwargs: dict[str, Any] = self._check_kwargs()
        self._end_url: str = self._kwargs.get(
            "url", 
            f"/metagenomics/api/v2/{self._resource}/"
        ).strip("/")

        # checkpointing
        self._checkpoint_dir: Optional[Path] = checkpoint_dir
        self._checkpoint_freq: int = checkpoint_freq or 3

        # results 
        self._count: Optional[int] = None
        self._total_pages: Optional[int] = None
        self._cached_first_page: Optional[List] = None
        self._results: Optional[List[List[dict]]] = None
        self._accessions: Optional[List[str]] = None


    @property
    def mpy_module(self):
        return self._mpy_module

    @mpy_module.setter
    def mpy_module(self, new_module):
        self._mpy_module = new_module

    def __getattr__(self, name: str):
        if name == "mgnipy_client":
            return self._init_client()
        elif name == "supported_kwargs":
            return self._get_supported_kwargs()
        elif name == "request_url":
            return self._build_url()
        elif name == "api_version":
            print("v2")
        elif name == "accessions":
            self._set_accessions_list()
            return self._accessions
        else:
            return self.__dict__[f"_{name}"]


    def __str__(self):
        return (
            f"Mgnifier instance for MGnify {self._resource} metadata\n"
            f"----------------------------------------\n"
            f"Base URL: {self._base_url}\n"
            f"Parameters: {self._params}\n"
            f"==========================================\n"
            f"Request URL: {self._build_url()}\n"
            f"----------------------------------------\n"
            f"Checkpoint Directory: {self._checkpoint_dir}\n"
            f"Checkpoint Frequency: {self._checkpoint_freq}\n"
        )


    # methods
    def plan(self):
        """
        View number of pages/records to be retrieved before retrieving all data.
        """
        print("Planning the API call with params:")
        print(self._params)
        print(
            f"Acquiring meta for {self._params['page_size']} {self._resource} per page..."
        )

        # make tiny get request using mgni_py client
        tmp_params = self._tmp_param_update(page_size=1)
        response_dict = self._get_page(tmp_params)
        if response_dict is None:
            raise RuntimeError("Failed to get response from MGnify API.")
        
        # set
        self._count = response_dict["count"]
        self._total_pages = ceil(self._count / self._params["page_size"])

        # verbose
        print(f"Total pages to retrieve: {self._total_pages}")
        print(f"Total records to retrieve: {self._count}")


    def preview(self):
        """
        Previews the metadata of the first page of results as a DataFrame.
        """
        # plan if not already
        if (self._count is None) or (self._total_pages is None):
            print("Mgnifier.plan() not yet checked. Running now...")
            self.plan()
        # request first page and cache
        print("Retrieving first page of results for preview...")
        tmp_params = self._tmp_param_update(page=1)
        response_dict = self._get_page(tmp_params)
        if response_dict is None:
            raise RuntimeError("Failed to get response from MGnify API.")
        self._cached_first_page = response_dict["items"]
        # verbose
        print(
            f"Previewing page 1 of {self._total_pages} pages of {self._count} records:"
        )
        return self.to_pandas([self._cached_first_page])


    async def get(
        self, 
        pages: Optional[list[int]] = None,
        strict: bool = False,
    ) -> pd.DataFrame:

        # verbose
        print(self._build_url())

        # async request all pages and store results in self._results
        async with self._init_client() as client:
            await self._collector(client, pages=pages, strict=strict)

        # set accessions list for retrieved data if applicable
        self._set_accessions_list()

        return self.to_pandas(self._results)


    def to_pandas(
        self, 
        data: Optional[List[dict]] = None,
        **kwargs
    ) -> pd.DataFrame:
        
        _data = data or self._results or [self._cached_first_page]

        if _data==[None] or _data is None:
            raise RuntimeError(
                "No data available to convert to DataFrame. "
                "Please run preview() or get() first."
            )
        
        combined_df = pd.concat(
            [pd.DataFrame(page) for page in _data],
            ignore_index=True
        )

        return pd.DataFrame(combined_df, **kwargs)


    def to_parquet(self):
        pass


    def to_anndata(self):
        pass


    def to_polars(self):
        pass


    def export(self):
        pass


    # hidden helper methods 
    def _init_client(self):
        client_v1 = Client(
            base_url=str(self._base_url),
            # TODO logs?
        )
        return client_v1

    def _get_page(self, given_params: dict) -> dict:
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

    def _get_supported_kwargs(self) -> list[str]:
        """helper function to get supported kwargs for the current mpy module"""
        sig = inspect.signature(self._mpy_module._get_kwargs)
        return list(sig.parameters.keys())

    def _check_kwargs(self) -> str: 
        try: 
            kwargy = self._mpy_module._get_kwargs(**self._params)
        except ValueError as e:
            raise ValueError(f"Invalid parameters provided: {e}")
        return kwargy

    def _tmp_param_update(self, **kwargs) -> dict[str, Any]:
        temp_params = deepcopy(self._params)
        temp_params.update(kwargs)
        return temp_params

    def _build_url(self, params: Optional[dict[str, Any]] = None) -> str:
        """build url for logging/verbose only"""
        params = params or self._params
        start_url = os.path.join(self._base_url, self._end_url)
        encoded_params = urlencode(params, doseq=True)
        return f"{start_url}/?{encoded_params}"
    
    def _set_accessions_list(self) -> Optional[List[str]]:
        """helper function to set accessions list for the current mpy module"""

        if self._mpy_module == list_mgnify_studies:
            self._accessions = self.to_pandas()['accession'].tolist()
        elif self._mpy_module == list_mgnify_study_analyses:
            self._accessions = self.to_pandas()['accession'].tolist()
        elif self._mpy_module == list_mgnify_study_samples:
            self._accessions = self.to_pandas()['accession'].tolist()
        elif self._mpy_module == list_mgnify_genomes:
            self._accessions = self.to_pandas()['accession'].tolist()
        else:
            self._accessions = None

    # @async_disk_lru_cache()
    async def _get_page_async(
        self, 
        client: Client, 
        page_num: int, 
        params: Optional[dict[str, Any]] = None
    ):
        """coroutine function to get coroutine for each page"""
        # limiting concurrency to protect server
        async with semaphore:
            return await self._mpy_module.asyncio_detailed(
                client=client,
                **(params or self._params),
                page=page_num,
            )    

    async def _collector(
        self,
        client: Client,
        pages: Optional[list[int]] = None,
        strict: bool = False,
    ):
        # not allow to run this without preview/plan first?
        if self._total_pages is None:
            if strict: 
                raise AssertionError(
                    "Please run Mgnifier.plan() or .preview() before "
                    "deciding to collect metadata for params:\n"
                    f"{self._params}"
                )
            else:
                print(
                    "Mgnifier.plan() not yet checked. Running now..."
                )
                self.plan()
        
        # prep page nums
        if isinstance(pages, list):
            for p in pages:
                if not (isinstance(p, int) and 0 < p <= self._total_pages):
                    raise ValueError(
                        f"Invalid page number: {p}. " 
                        "Pages must be positive integers "
                        f"not exceeding total pages {self._total_pages}."
                    )
        elif pages is None: 
            # init all pages if not provided
            pages = list(range(1, self._total_pages + 1))
        else: 
            raise TypeError("pages must be a list of integers or None")
        
        # skip cached first page if avail
        if 1 in pages and self._cached_first_page is not None:
            print("Page 1 already cached from preview, skipping...")
            _pages = deepcopy(pages)
            _pages.remove(1)
            self._results = [self._cached_first_page]
        else:
            _pages = deepcopy(pages)
            self._results = []

        # creating async tasks
        async_tasks = [
            asyncio.create_task(
                self._get_page_async(
                    client=client, 
                    page_num=page_num, 
                    params=self._params
                )
            )  for page_num in _pages
        ]

        # gathering results as completed
        for task in tqdm(
            asyncio.as_completed(async_tasks), 
            total=len(async_tasks)
        ):
            # awaiting each task as it completes and appending results
            page_result = await task
            self._results.append(page_result.parsed.to_dict()["items"])


class BiomesMgnifier(Mgnifier):

    def __init__(
        self, 
        *,
        leaves: Optional[
            Literal["studies", "samples", "analyses"]
        ] = None,
        **kwargs
    ):
        super().__init__(resource="biomes", **kwargs)

    # biome-specific methods



class StudiesMgnifier(Mgnifier):

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource='studies', params=params, **kwargs)


class AnalysesMgnifier(Mgnifier):
    def __init__(
        self,
        study_accession: str,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(
            resource='analyses',
            params=params, 
            accession=study_accession, 
            **kwargs
        )


class SamplesMgnifier(Mgnifier):
    def __init__(
        self,
        study_accession: str,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(
            resource='samples',
            accession=study_accession, 
            params=params, 
            **kwargs
        )


class GenomesMgnifier(Mgnifier):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # TODO 
        super().__init__(
            resource="genomes",
            params=params, 
            **kwargs
        )
    
