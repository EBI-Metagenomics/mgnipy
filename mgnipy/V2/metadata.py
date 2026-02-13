from pathlib import Path
from typing import (
    Any,
    Literal,
    Optional,
)

import pandas as pd

# from mgnipy._pydantic_models.v2.adapters import validate_experiment_type
from mgnipy._shared_helpers import get_semaphore


# from .mgni_py_v2.api.analyses import analyses_list
# from mgni_py_v1.api.runs import runs_analyses_list
# from mgni_py_v1.api.samples import (
#     samples_list,
#     samples_runs_list,
# )

semaphore = get_semaphore()

# base class
# inheriting class for each endpoint 
# with methods for getting, planning etc. 

# a class to take all of these together 


class Mgnifier:

    def __init__(
        self,
        *,
        resource: Optional[
            Literal["studies", "samples", "genomes", "analyses"]
        ] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        pass


    def plan():
        pass

    def preview():
        pass

    async def get():
        # accessions
        pass

    def to_pandas():
        pass

    def to_parquet():
        pass

    def to_anndata():
        pass

    def to_polars():
        pass

    def export():
        pass

class StudyMgnifier(Mgnifier):

    def __init__(
        self,
        *,
        accessions: Optional[list[str]] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        pass


class AnalysisMgnifier(Mgnifier):
    def __init__(
        self,
        *,
        accessions: Optional[list[str]] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        pass

class SampleMgnifier(Mgnifier):
    def __init__(
        self,
        *,
        accessions: Optional[list[str]] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        pass

class GenomeMgnifier(Mgnifier):
    def __init__(
        self,
        *,
        accessions: Optional[list[str]] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        pass
