import asyncio
import inspect
import json
import os
from copy import deepcopy
from pathlib import Path
from typing import (
    Any,
    Literal,
    Optional,
)
from urllib.parse import urlencode

import pandas as pd
from .mgni_py_v2 import Client
#from .mgni_py_v2.api.analyses import analyses_list
#from mgni_py_v1.api.runs import runs_analyses_list
# from mgni_py_v1.api.samples import (
#     samples_list,
#     samples_runs_list,
# )
from .mgni_py_v2.api.studies import list_mgnify_studies
from .mgni_py_v2.types import Response
from tqdm import tqdm

from mgnipy._shared_helpers import get_semaphore
# from mgnipy._pydantic_models.v2.adapters import validate_experiment_type
from mgnipy._pydantic_models.v2.CONSTANTS import SupportedEndpoints

semaphore = get_semaphore()


# init for each model
class Mgnifier:
    """
    The Mgnipy Mgnifier class is a user-friendly interface for exploring study, sample and analysis metadata from the MGnify API.

    """

    def __init__(
        self,
        *,
        root: Optional[
            Literal[
                "biomes", "super-studies", "publications", 
                "studies", "samples", "analyses", "annotations"
            ]
        ] = None,
        leaf: Optional[
            Literal["studies", "samples", "analyses"]
        ] = None,    
        depth: Optional[int] = None,

        checkpoint_dir: Optional[Path] = None,
        checkpoint_freq: Optional[int] = None,
        **kwargs,
    ):
        # url
        self._api_version = "v2" #TODO this and base url to env
        self._base_url = "https://www.ebi.ac.uk/" #TODO and this
        self._mpy_module = None

        self._all_biomes = None # to do biome helper
        self.param_validator = None # to do adapter to validate that kwargs are valid params for the endpoint



        # TODO checkpoints
        # prep checkpoint if
        self._checkpoint_dir = checkpoint_dir
        self._checkpoint_freq = checkpoint_freq or 3
        self._checkpoint_csv = None
        self._config_json = None
        if self._checkpoint_dir is not None:
            self._set_checkpoint_paths()

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

        # cache
        self._total_pages: Optional[int] = None
        self._cached_first_page: Optional[dict] = None

        self._results: Optional[list[pd.DataFrame]] = None
