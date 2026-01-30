
import asyncio
from pydantic import BaseModel, HttpUrl
from pathlib import Path
import pandas as pd
import os

from tqdm import tqdm

from mgnipy._pydantic_models.CONSTANTS import (
    SupportedApiVersions as SV, 
    SupportedEndpoints as SE
)
from mgni_py_v1 import Client
from mgni_py_v1.api.analyses import analyses_list
from mgni_py_v1.api.studies import studies_list
from mgni_py_v1.api.biomes import biomes_list

from typing import Optional, Any

from mgni_py_v1.types import Response

from urllib.parse import urlencode


metadata_modules = {
    "analyses": analyses_list,
    "studies": studies_list,
    "biomes": biomes_list,
    None: studies_list,
}

CONCURRENCY = 5
semaphore = asyncio.Semaphore(CONCURRENCY)
CHECKPOINT_EVERY_N_PAGES = 3


# init for each model
class Mgnifier:

    """
    The Mgnipy Mgnifier class is a user-friendly interface for exploring study, sample and analysis metadata from the MGnify API.

    """

    def __init__(
        self,
        *,
        db: SE | None = None,
        params: dict | None = None,
        base_url: HttpUrl = 'https://www.ebi.ac.uk/metagenomics/api/',
        cache_dir: Path = Path('tmp/mgnify_cache'),
        **kwargs,
    ):
        # url
        self._api_version = "v1"
        self._base_url = base_url
        self._db = db
        self._cache_dir = cache_dir

        # params
        self._params = params or {}
        if kwargs:
            self._params.update(kwargs)
        if "page_size" not in self._params:
            self._params["page_size"] = 25

        self._url = self._build_url()

        # getting things started using the autoclient
        self._mpy_module = metadata_modules[db]

        # cache
        self._total_pages = None
        self._cached_first_page = None
        self._checkpoint = None
        self._cached_the_rest = None


    def __getattr__(self, name: str):
        if name == "mgni_py_client":
            return self._init_client()
        else:
            return self.__dict__[f"_{name}"]
    

    def plan(self):
        """
        Allows the user to see the numb er of pages/records to be retrieved before retrieving all data.
        """
        print("Planning the API call with params:")
        print(self._params)
        print(f"Acquiring meta for {self._params.get('page_size', 25)} {self._db} per page...")
        print(f"Request URL: {self._url}")
        # make get request using mgni_py client
        resp_dict = self._get_request(self._params)
        # set
        self._total_pages = resp_dict['meta']['pagination']['pages']
        self._current_page = resp_dict['meta']['pagination']['page']
        self._count = resp_dict['meta']['pagination']['count']
        self._cached_first_page = resp_dict['data']

        print(f"Total pages to retrieve: {self._total_pages}")
        print(f"Total records to retrieve: {self._count}")


    def preview(self):
        """
        Previews the metadata of the first page of results as a DataFrame.
        """
        if self._cached_first_page is None:
            print("MGnigier.plan not yet checked. Running now...")
            self.plan()
        
        print(f"Previewing Page 1 of {self._total_pages} pages ({self._count} records)...")

        return self.response_df(self._cached_first_page)


    # TODO pandera schema for data validation
    def response_df(self, data:dict)->pd.DataFrame:
        """helper functinon to expand attributes column into separate columns"""
        df = pd.DataFrame(data)
        attr_df = pd.json_normalize(df['attributes']) 
        df_extended = pd.concat([df.drop(columns=['attributes']), attr_df], axis=1)
        return df_extended


    # helpers
    def _init_client(self):
        client_v1 = Client(
            base_url=str(self._base_url),
            #TODO logs?
        )
        return client_v1


    def _get_request(self, given_params: dict) -> dict:
        with self._init_client() as client:
            response = self._mpy_module.sync_detailed(
                client=client,
                **given_params,
            )
        print(f"Response status code: {response.status_code}")
        return response.parsed.to_dict()
    

    def _build_url(self) -> str:
        """build url for logging/verbose"""
        start_url = os.path.join(
            self._base_url, 
            self._api_version,
            self._db
        )
        encoded_params = urlencode(self._params)
        return f"{start_url}/?{encoded_params}"


    async def _get_page(self, client, page_num:int):
        """coroutine function to get coroutine for each page"""
        # limiting concurrency to protect server 
        async with semaphore:
            return await self._mpy_module.asyncio_detailed(
                client=client,
                **self._params,
                page=page_num,
            )


    async def _collector(self, client, pages:Optional[list[int]]=None):

        
        # not allow to run this without preview/plan first?
        if self._total_pages is None:
            raise AssertionError(
                "Please run Mgnifier.plan or .preview before" 
                "deciding to collect metadata for params:\n"
                f"{self._params}"
            )

        if pages is None: 
            print(f"No pages specified, collecting all...")
            pages = list(range(1, self._total_pages + 1))
        

        elif isinstance(pages, list):
            if not all(p<=self._total_pages for p in pages):
                raise ValueError(
                    f"One or more specified pages exceed total pages {self._total_pages}."
                    f"Specified pages: {pages}"
                )
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
        results = {}
        for task in tqdm(asyncio.as_completed(async_tasks), total=len(async_tasks)):
            result = await task
            page_num = getattr(task, "page", None) #FIXME why all none 
            results[page_num] = result
        
        return results
    
    async def collect(self, pages:Optional[list[int]]=None):

        print(self._url)

        async with self._init_client() as client:
            results = await self._collector(client, pages=pages)

        # process results
        # TODOa
        return results
