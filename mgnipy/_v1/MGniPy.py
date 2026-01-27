
from pydantic import BaseModel, HttpUrl
from pathlib import Path
import requests
import pandas as pd
import os
import numpy as np
import json
import time
import anndata as ad
from mgnipy._pydantic_models.CONSTANTS import (
    SupportedApiVersions as SV, 
    SupportedEndpoints as SE
)
import mgni_py_v1

preview_module_V1 = {
    SE.ANALYSES: mgni_py_v1.api.analyses.analyses_list,
    SE.STUDIES: mgni_py_v1.api.studies.studies_list,
    SE.BIOMES: mgni_py_v1.api.biomes.biomes_list,
    None: mgni_py_v1.api.studies.studies_list,
}

preview_module_V2 = None

# init for each model
class Mgnifier:

    """
    TODO Class to interact with the Mgnify API.
    """

    def __init__(
        self,
        *,
        db: SE | None = None,
        params: dict | None = None,
        api_version: SV = SV.V1,
        base_url: HttpUrl = 'https://www.ebi.ac.uk/metagenomics/api/',
        cache_dir: Path = Path('tmp/mgnify_cache'),
        **kwargs,
    ):
        # url
        self._base_url = base_url
        self._api_version = api_version
        self._db = db
        self._cache_dir = cache_dir

        # params
        self._params = params or {}
        if kwargs:
            self._params.update(kwargs)
        if "page_size" not in self._params:
            self._params["page_size"] = 25

        # getting things started using the autoclient
        self._client = self._init_client()
        self.mgni_py_previewer = preview_module_V1[db]

        # cache
        self._total_pages = None
        self._cached_first_page = None
        self._checkpoint = None
        self._cached_the_rest = None


    def __getattr__(self, name: str):
        return self.__dict__[f"_{name}"]

    def __repr__(self):
        pass

    @property
    def planner(self):
        print("Planning the API call with params:")
        print(self._params)
        print(f"Acquiring meta for {self._params.get('page_size', 25)} {self._db} per page...")
        # make get request using mgni_py client
        resp_dict = self._get_request(self._params)
        # set
        self._total_pages = resp_dict['meta']['pagination']['pages']
        self._current_page = resp_dict['meta']['pagination']['page']
        self._count = resp_dict['meta']['pagination']['count']
        self._cached_first_page = resp_dict['data']

        print(f"Total pages to retrieve: {self._total_pages}")
        print(f"Total records to retrieve: {self._count}")


    @property
    def preview(self):
        if self._cached_first_page is None:
            print("MGnigier.planner not yet run. Running now...")
            self.planner
        
        print(f"Previewing Page 1 of {self._total_pages} pages ({self._count} records)...")

        return self.response_df(self._cached_first_page)

        
    # TODO pandera schema for data validation
    def response_df(data:dict)->pd.DataFrame:
        df = pd.DataFrame(data)
        attr_df = pd.json_normalize(df['attributes']) 
        df_extended = pd.concat([df.drop(columns=['attributes']), attr_df], axis=1)
        return df_extended
    
    # with async
    def download_metadata(self, pages):
        pass


    # helpers
    def _init_client(self):
        if self.api_version in [SV.V2, SV.LATEST]:
            from mgni_py_v2 import Client as ClientV2
            client = ClientV2(
                base_url=str(self.base_url),
            )
        elif self.api_version == SV.V1:
            from mgni_py_v1 import Client as ClientV1
            client = ClientV1(
                base_url=str(self.base_url),
            )
        else:
            raise ValueError(f"Unsupported API version: {self.api_version}")
        return client


    def _get_request(self, given_params: dict)-> dict:
        with self._client as client:
            response = self.mgni_py_previewer.sync(
                client=client,
                **given_params,
            )
        return response.to_dict()


    def _prep_coroutines(self):
        pass
    
    # basically get the path/method and matching datamodel
    # pass along params 
    # run
    # transform
    # cache as df? 

    def get_study_metadata(
        self,
    ) -> pd.DataFrame:
        pass

    def get_sample_metadata(
        self,
        study_accession:str,
    ) -> pd.DataFrame:
        pass

    def get_analysis_metadata(
        self,
        study_accession:str,
    ) -> pd.DataFrame:
        pass

    def _run(
        self, 
        params,

    ):
        pass

    def _find_download_url(
        self,
    ): 
        pass

    def _download_file(
        self,
    ):
        pass

    def open_taxa_file(
        self,
    ):
        pass

    