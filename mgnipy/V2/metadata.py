import asyncio
import inspect
import os
from copy import deepcopy
from math import ceil
from pathlib import Path
from typing import (
    Any,
    List,
    Literal,
    Optional,
)
from urllib.parse import urlencode

import pandas as pd
from bigtree import (
    Tree,
)
from tqdm import tqdm

from mgnipy import BASE_URL
from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy._shared_helpers.pydantic_help import validate_gt_int
from mgnipy.V2._mgnipy_models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.mgni_py_v2 import Client
from mgnipy.V2.mgni_py_v2.api.genomes import list_mgnify_genomes
from mgnipy.V2.mgni_py_v2.api.miscellaneous import list_mgnify_biomes
from mgnipy.V2.mgni_py_v2.api.studies import (
    list_mgnify_studies,
    list_mgnify_study_analyses,
    list_mgnify_study_samples,
)

semaphore = get_semaphore()

METADATA_MODULES = {
    SupportedEndpoints.BIOMES: list_mgnify_biomes,  # what biomes
    SupportedEndpoints.STUDIES: list_mgnify_studies,  # search for study
    SupportedEndpoints.SAMPLES: list_mgnify_study_samples,  # all samples for given study
    SupportedEndpoints.ANALYSES: list_mgnify_study_analyses,  # all analyses for given study
    SupportedEndpoints.GENOMES: list_mgnify_genomes,
}


class Mgnifier:
    """
    MGnify API v2 metadata retriever and manager.

    This class provides a unified interface for retrieving, previewing, and exporting metadata from the MGnify API v2 for various resources (biomes, studies, samples, analyses, genomes).

    Attributes
    ----------
    base_url : str
        The base URL for the MGnify API.
    resource : str
        The resource type (e.g., 'biomes', 'studies', 'samples', 'genomes', 'analyses').
    mpy_module : Callable
        The function used to retrieve metadata for the selected resource.
    params : dict
        Parameters for the API call.
    checkpoint_dir : Path or None
        Directory for checkpointing results.
    checkpoint_freq : int
        Frequency of checkpointing.
    count : int or None
        Total number of records available for the query.
    total_pages : int or None
        Total number of pages available for the query.
    cached_first_page : list or None
        Cached results from the first page.
    results : list or None
        All results retrieved from the API.
    accessions : list or None
        List of accessions for the current resource, if available.
    """

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
        """
        Initialize a Mgnifier instance for a specific MGnify resource.

        Parameters
        ----------
        resource : {"biomes", "studies", "samples", "genomes", "analyses"}, optional
            The resource type to query. Defaults to "biomes".
        params : dict, optional
            Dictionary of parameters for the API call.
        checkpoint_dir : Path, optional
            Directory to store checkpoints.
        checkpoint_freq : int, optional
            Frequency (in pages) to checkpoint results. Defaults to 3.
        **kwargs : dict
            Additional keyword arguments to include in the API parameters.
        """
        # for client
        self._base_url: str = BASE_URL
        self._resource: str = resource or "biomes"  # default
        self._mpy_module = METADATA_MODULES[SupportedEndpoints(self._resource)]

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

        # checkpointing
        self._checkpoint_dir: Optional[Path] = checkpoint_dir
        self._checkpoint_freq: int = checkpoint_freq or 3

        # results
        self._count: Optional[int] = None
        self._total_pages: Optional[int] = None
        self._cached_first_page: Optional[List] = None
        self._results: Optional[List[List[dict]]] = None
        self._accessions: Optional[List[str]] = None

    def __iter__(self):
        """
        Allow iteration over the metadata records, yielding one record at a time.

        Returns
        -------
        Iterator[dict]
            An iterator that yields metadata records as dictionaries. 
        """
        df = self.to_pandas() # TODO: work with the raw results instead of to df
        return (dict(row) for _, row in df.iterrows())

    def __getitem__(self, key) -> List[dict] | dict:
        """
        Allow indexing into the metadata records by integer index, accession, or lineage.

        Parameters
        ----------
        key : int, slice, or str
            The key to index by. Can be an integer index, a slice, 
            a valid accession string, or a valid lineage string.

        Returns
        -------
        list of dict or dict
            The metadata record(s) corresponding to the provided key.

        Raises
        ------
        KeyError
            If the key is not a valid index, accession, or lineage.
        """

        # TODO: work with the raw results instead of to df
        df = self.to_pandas()
        df_as_list = df.to_dict(orient="records")
        # by index
        if isinstance(key, (int, slice)):
            return df_as_list[key]
        # by accession
        elif (
            isinstance(key, str) 
            and self._accessions 
            and key in self._accessions
        ):
            return df.query(f"accession == '{key}'").to_dict(orient="records")
        # by lineage
        elif (
            isinstance(key, str) 
            and "lineage" in df.columns
        ):
            return df.query(f"lineage == '{key}'").to_dict(orient="records")
        # else raise error
        else:
            raise KeyError(
                f"Invalid key: {key}. "
                "Key must be an integer index, a slice, or a valid accession or lineage string."
            )


    @property
    def mpy_module(self):
        return self._mpy_module

    @mpy_module.setter
    def mpy_module(self, new_module):
        self._mpy_module = new_module

    def __getattr__(self, name: str):
        """
        Dynamically access attributes, including computed or helper properties.

        Parameters
        ----------
        name : str
            The attribute name to retrieve.

        Returns
        -------
        Any
            The value of the requested attribute or computed property.

        Raises
        ------
        AttributeError
            If the attribute does not exist.
        """
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
        """
        Return a string representation of the Mgnifier instance, summarizing key configuration and state.

        Returns
        -------
        str
            Human-readable summary of the instance.
        """
        return (
            f"Mgnifier instance for MGnify {self._resource} metadata\n"
            f"----------------------------------------\n"
            f"Base URL: {self._base_url}\n"
            f"Parameters: {self._params}\n"
            f"----------------------------------------\n"
            f"Checkpoint Directory: {self._checkpoint_dir}\n"
            f"Checkpoint Frequency: {self._checkpoint_freq}\n"
        )

    # methods
    def filter(
        self,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Update the parameters for the API call to filter results.

        Parameters
        ----------
        params : dict, optional
            Dictionary of parameters to update.
        **kwargs : dict
            Additional keyword arguments to include in the parameters.

        Returns
        -------
        None
        """

        if params:
            self._params.update(params)
        if kwargs:
            self._params.update(kwargs)
        # check new params are valid for endpoint
        self._check_kwargs()
        # reset results and metadata since params changed
        self._count = None
        self._total_pages = None
        self._cached_first_page = None
        self._results = None
        self._accessions = None

        return self

    def plan(self):
        """
        Estimate the number of pages and records available for the current query.

        This method performs a minimal API call to determine the total number of records and pages for the current resource and parameters.

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If the API call fails.
        """
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
        Preview the metadata of the first page of results as a DataFrame.

        If plan() has not been run, it will be called automatically.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the first page of results.

        Raises
        ------
        RuntimeError
            If the API call fails or no data is available.
        """
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
        limit: Optional[int] = None,
        *,
        pages: Optional[list[int]] = None,
        strict: bool = False,
    ) -> pd.DataFrame:
        """
        Retrieve all (or selected) pages of metadata asynchronously and return as a DataFrame.

        Parameters
        ----------
        limit : int, optional
            Maximum number of records to retrieve. If None, retrieves all records.
        pages : list of int, optional
            List of page numbers to retrieve. If None, retrieves all pages.
        strict : bool, default False
            If True, raises an error if plan() or preview() has not been run.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the concatenated results from all pages.

        Raises
        ------
        AssertionError
            If plan() or preview() has not been run and strict is True.
        RuntimeError
            If no data is available to convert to DataFrame.
        """

        # verbose
        print(self._build_url())

        # async request all pages and store results in self._results
        async with self._init_client() as client:
            await self._collector(client, limit=limit, pages=pages, strict=strict)

        # set accessions list for retrieved data if applicable
        self._set_accessions_list()

        return self.to_pandas(self._results)

    def to_pandas(self, data: Optional[List[dict]] = None, **kwargs) -> pd.DataFrame:
        """
        Convert the current or provided metadata to a pandas DataFrame.

        Parameters
        ----------
        data : list of dict, optional
            List of records to convert. If None, uses self._results or self._cached_first_page.
        **kwargs
            Additional keyword arguments passed to pd.DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the metadata.

        Raises
        ------
        RuntimeError
            If no data is available to convert.
        """

        _data = data or self._results or [self._cached_first_page]

        if _data == [None] or _data is None:
            print("No data available to convert to DataFrame. Returning None.")
            return None

        combined_df = pd.concat(
            [self._df_expand_nested(pd.DataFrame(page)) for page in _data],
            ignore_index=True,
        )

        return pd.DataFrame(combined_df, **kwargs)

    def to_parquet(self):
        """
        Convert the metadata to a parquet file.
        (Not yet implemented.)
        """
        pass

    def to_anndata(self):
        """
        Convert the metadata to an AnnData object.
        (Not yet implemented.)
        """
        pass

    def to_polars(self):
        """
        Convert the metadata to a polars DataFrame.
        (Not yet implemented.)
        """
        pass

    def export(self):
        """
        Export the metadata to a file or other format.
        (Not yet implemented.)
        """
        pass

    # hidden helper methods
    def _init_client(self):
        """
        Initialize and return a MGnify API client instance.

        Returns
        -------
        Client
            Configured MGnify API client.
        """
        client_v1 = Client(
            base_url=str(self._base_url),
            # TODO logs?
        )
        return client_v1

    def _get_page(self, given_params: dict) -> dict:
        """
        Retrieve a single page of metadata using the synchronous API client.

        Parameters
        ----------
        given_params : dict
            Parameters for the API call.

        Returns
        -------
        dict
            Parsed response from the API, or None if the request failed.
        """
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
        """
        Get the list of supported keyword arguments for the current resource's API function.

        Returns
        -------
        list of str
            List of supported keyword argument names.
        """
        """helper function to get supported kwargs for the current mpy module"""
        sig = inspect.signature(self._mpy_module._get_kwargs)
        return list(sig.parameters.keys())

    def _check_kwargs(self) -> str:
        """
        Validate the current parameters for the selected resource.

        Returns
        -------
        str
            Validated keyword arguments or raises an error if invalid.

        Raises
        ------
        ValueError
            If invalid parameters are provided.
        """
        try:
            kwargy = self._mpy_module._get_kwargs(**self._params)
        except ValueError as e:
            raise ValueError(f"Invalid parameters provided: {e}") from None
        return kwargy

    def _tmp_param_update(self, **kwargs) -> dict[str, Any]:
        """
        Return a copy of the current parameters, updated with any provided keyword arguments.

        Parameters
        ----------
        **kwargs
            Parameters to update or add.

        Returns
        -------
        dict
            Updated parameters dictionary.
        """
        temp_params = deepcopy(self._params)
        temp_params.update(kwargs)
        return temp_params

    def _build_url(
        self,
        params: Optional[dict[str, Any]] = None,
        exclude: list[str] = None,
    ) -> str:
        """
        Build a URL for the current resource and parameters (for logging/verbose output).

        Parameters
        ----------
        params : dict, optional
            Parameters to include in the URL. If None, uses self._params.

        Returns
        -------
        str
            The constructed URL.
        """
        """build url for logging/verbose only"""

        exclude = exclude or ["accession", "pubmed_id", "catalogue_id"]

        params = params or self._params

        # check params are valid for endpoint
        _kwargs: dict[str, Any] = self._check_kwargs()
        _end_url: str = _kwargs.get(
            "url", f"/metagenomics/api/v2/{self._resource}/"
        ).strip("/")
        incl_params = deepcopy(params)
        for k in exclude or []:
            incl_params.pop(k, None)
        start_url = os.path.join(self._base_url, _end_url)
        encoded_params = urlencode(incl_params, doseq=True)
        return f"{start_url}/?{encoded_params}"

    def _set_accessions_list(self) -> Optional[List[str]]:
        """
        Set the list of accessions for the current resource, if available.

        Returns
        -------
        list of str or None
            List of accessions, or None if not available for the resource.
        """
        """helper function to set accessions list for the current mpy module"""
        if self.to_pandas() is None:
            self._accessions = None
        elif self._mpy_module in [
            list_mgnify_studies, 
            list_mgnify_study_analyses,
            list_mgnify_study_samples,
            list_mgnify_genomes,
        ]:
            self._accessions = self.to_pandas()["accession"].tolist()
        else:
            self._accessions = None

    def _df_expand_nested(
        self, df: pd.DataFrame, cols: list[str] = None
    ) -> pd.DataFrame:
        """
        Expand nested structures in the DataFrame into separate columns.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to expand.
        cols : list of str
            List of column names to expand.

        Returns
        -------
        pd.DataFrame
            The expanded DataFrame.
        """

        cols = cols or ["metadata"]

        new_df = df.copy()
        for c in cols:
            if c in new_df.columns:
                attr_df = pd.json_normalize(new_df[c])
                new_df = pd.concat([new_df.drop(columns=[c]), attr_df], axis=1)
        return new_df

    # @async_disk_lru_cache()
    async def _get_page_async(
        self, client: Client, page_num: int, params: Optional[dict[str, Any]] = None
    ):
        """
        Asynchronously retrieve a single page of metadata.

        Parameters
        ----------
        client : Client
            MGnify API client instance.
        page_num : int
            Page number to retrieve.
        params : dict, optional
            Parameters for the API call.

        Returns
        -------
        Response
            The API response object for the requested page.
        """
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
        limit: Optional[int] = None,
        pages: Optional[list[int]] = None,
        strict: bool = False,
    ):
        """
        Asynchronously collect metadata for all (or selected) pages and store results.

        Parameters
        ----------
        client : Client
            MGnify API client instance.
        limit : int, optional
            Maximum number of records to retrieve. If None, retrieves all records.
        pages : list of int, optional
            List of page numbers to retrieve. If None, retrieves all pages.
        strict : bool, default False
            If True, raises an error if plan() or preview() has not been run.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If plan() or preview() has not been run and strict is True.
        ValueError
            If invalid page numbers are provided.
        TypeError
            If pages is not a list or None.
        """
        # not allow to run this without preview/plan first?
        if self._total_pages is None:
            if strict:
                raise AssertionError(
                    "Please run Mgnifier.plan() or .preview() before "
                    "deciding to collect metadata for params:\n"
                    f"{self._params}"
                )
            else:
                print("Mgnifier.plan() not yet checked. Running now...")
                self.plan()

        # prep page nums
        if limit is not None:
            if not (isinstance(limit, int) and limit > 0):
                raise ValueError("limit must be a positive integer.")
            # TODO for now undershooting limit 
            max_page = ceil(limit / self._params["page_size"])
            print(max_page)
            _pages = list(range(1, min(max_page, self._total_pages) + 1))
        elif isinstance(pages, list):
            _pages = deepcopy(pages)
            for p in pages:
                if not (isinstance(p, int) and 0 < p <= self._total_pages):
                    if strict:
                        raise ValueError(
                            f"Invalid page number: {p}. "
                            "Pages must be positive integers "
                            f"not exceeding total pages {self._total_pages}."
                        )
                    else:
                        print(
                            f"Warning: Invalid page number {p} skipped as > than {self._total_pages}."
                        )
                        _pages.remove(p)
        elif pages is None:
            # init all pages if not provided
            _pages = list(range(1, self._total_pages + 1))
        else:
            raise TypeError("pages must be a list of integers or None")

        # skip cached first page if avail
        if 1 in _pages and self._cached_first_page is not None:
            print("Page 1 already cached from preview, skipping...")
            _pages.remove(1)
            self._results = [self._cached_first_page]
        else:
            self._results = []

        # creating async tasks
        async_tasks = [
            asyncio.create_task(
                self._get_page_async(
                    client=client, page_num=page_num, params=self._params
                )
            )
            for page_num in _pages
        ]

        # gathering results as completed
        for task in tqdm(asyncio.as_completed(async_tasks), total=len(async_tasks)):
            # awaiting each task as it completes and appending results
            page_result = await task
            self._results.append(page_result.parsed.to_dict()["items"])


class BiomesMgnifier(Mgnifier):

    def __init__(self, **kwargs):
        self._tree = None
        super().__init__(resource="biomes", **kwargs)

    # biome-specific methods
    def to_bigtree(self) -> Tree:
        """
        Convert the biomes metadata to a tree structure for visualization or analysis.

        Returns
        -------
        Tree
            A tree representation of the biomes and their relationships.
        """
        if self._results is None:
            raise RuntimeError(
                "No data available to convert to tree. "
                "Please run preview() or get() first."
            )
        # convert to pandas and then to tree
        df = self.to_pandas()
        # TODO generate nodes first
        self._tree = Tree.from_list(df["lineage"], sep=":")
        return self._tree

    def show_tree(
        self,
        method: Literal[
            "compact",
            "show",
            "print",
            "horizontal",
            "hshow",
            "h",
            "hprint",
            "vertical",
            "vshow",
            "v",
            "vprint",
        ] = "compact",
    ):
        if self._tree is None:
            # create tree if not already
            self.to_bigtree()

        if method in ["compact", "show", "print"]:
            # TODO print_tree(self._tree)
            self._tree.show()
        elif method in ["horizontal", "hshow", "h", "hprint"]:
            self._tree.hshow()
        elif method in ["vertical", "vshow", "v", "vprint"]:
            self._tree.vshow()
        else:
            raise ValueError(
                f"Invalid method: {method}. "
                "Supported methods: 'compact', 'show', 'print', "
                "'horizontal', 'hshow', 'h', 'hprint', "
                "'vertical', 'vshow', 'v', 'vprint'."
            )


class StudiesMgnifier(Mgnifier):

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(resource="studies", params=params, **kwargs)


class AnalysesMgnifier(Mgnifier):
    def __init__(
        self,
        study_accession: str,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(
            resource="analyses", params=params, accession=study_accession, **kwargs
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
            resource="samples", accession=study_accession, params=params, **kwargs
        )


class GenomesMgnifier(Mgnifier):
    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # TODO
        super().__init__(resource="genomes", params=params, **kwargs)
