import asyncio
import inspect
import itertools
import logging
import os
import warnings
from copy import deepcopy
from math import ceil
from pathlib import Path
from typing import (
    Any,
    Callable,
    Literal,
    Optional,
)
from urllib.parse import urlencode

import pandas as pd
from tqdm import tqdm

from mgnipy._models.config import MgnipyConfig
from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy._shared_helpers.pydantic_help import validate_gt_int
from mgnipy.V2.mgni_py_v2 import Client
from mgnipy.V2.mgni_py_v2.api.analyses import (
    list_assemblies,
    list_mgnify_analyses,
)
from mgnipy.V2.mgni_py_v2.api.genomes import list_mgnify_genomes
from mgnipy.V2.mgni_py_v2.api.miscellaneous import list_mgnify_biomes
from mgnipy.V2.mgni_py_v2.api.samples import list_mgnify_samples
from mgnipy.V2.mgni_py_v2.api.studies import (
    list_mgnify_studies,
)

semaphore = get_semaphore()
BASE_URL = MgnipyConfig().base_url
CORE_MODULES = {
    SupportedEndpoints.BIOMES: list_mgnify_biomes,  # get all biomes, filtering option
    SupportedEndpoints.STUDIES: list_mgnify_studies,  # get all studies, filtering option
    SupportedEndpoints.SAMPLES: list_mgnify_samples,  # get all samples, filtering option or with study acc
    SupportedEndpoints.ANALYSES: list_mgnify_analyses,  # get all analyses, NO FILTERING OPTION, but with study or assem acc
    SupportedEndpoints.GENOMES: list_mgnify_genomes,  # listing all genomes, NO FILTERING OPTION but with assem acc
    # ^ list_genome_links_for_assembly,  # all genome links for given assembly
    SupportedEndpoints.ASSEMBLIES: list_assemblies,  # listing all assemblies, no filtering TODO more info?
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
    endpoint_module : Callable
        The function used to retrieve metadata for the selected resource.
    params : dict
        Parameters for the API call.
    count : int or None
        Total number of records available for the query.
    total_pages : int or None
        Total number of pages available for the query.
    results : list or None
        All results retrieved from the API.
    accessions : list or None
        List of accessions for the current resource, if available.
    """

    def __init__(
        self,
        *,
        resource: Optional[
            Literal["biomes", "studies", "samples", "genomes", "analyses", "assemblies"]
        ] = None,
        params: Optional[dict[str, Any]] = None,
        # checkpoint_dir: Optional[Path] = None,
        # checkpoint_freq: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize a Mgnifier instance for a specific MGnify resource.

        Parameters
        ----------
        resource : {"biomes", "studies", "samples", "genomes", "analyses", "assemblies"}, optional
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
        # if resource given, initiate endpoint module and supported params
        self._resource: Optional[SupportedEndpoints] = resource
        if self._resource:
            self._endpoint_module: Callable = CORE_MODULES[SupportedEndpoints(resource)]
            self._supported_kwargs: list[str] = self.list_parameters()
            self._pagination_status: bool = self._get_pagination_status()
        # otherwise initialize to None and require user to set resource or endpoint module before using
        else:
            self._endpoint_module = None
            self._supported_kwargs = None
            self._pagination_status = None

        # params as dict
        self._params: dict[str, Any] = params or {}
        # add kwargs to params if provided
        if kwargs:
            self._params.update(kwargs)

        # checkpointing
        # self._checkpoint_dir: Optional[Path] = checkpoint_dir
        # self._checkpoint_freq: int = checkpoint_freq or 3

        # results
        self._count: Optional[int] = None
        self._total_pages: Optional[int] = None
        self._cached_first_page: Optional[list] = None
        self._results: Optional[list[list[dict]]] = None

    def __iter__(self):
        """
        Allow iteration over the metadata records, yielding one record at a time.

        Returns
        -------
        Iterator[dict]
            An iterator that yields metadata records as dictionaries.
        """
        return self._unpageinate_results()

    def __getitem__(self, key) -> list[dict] | dict:
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
        results_list = list(self._unpageinate_results())
        # by index
        if isinstance(key, (int, slice)):
            return results_list[key]
        # by accession
        elif isinstance(key, str) and key in self.results_accessions:
            return [record for record in results_list if record["accession"] == key]
        # else raise error
        else:
            raise KeyError(
                f"Invalid key: {key}. "
                "Key must be an integer index, a slice, or a valid accession string."
            )

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
        elif name == "request_url":
            return self._build_url()
        elif name == "api_version":
            print("v2")
        else:
            try:
                return self.__dict__[f"_{name}"]
            except KeyError as e:
                raise KeyError(f"{name} is not a valid attribute of Mgnifier") from e

    def __str__(self):
        """
        Return a string representation of the Mgnifier instance, summarizing key configuration and state.

        Returns
        -------
        str
            Human-readable summary of the instance.
        """
        return (
            f"Mgnifier instance for resource: {self._resource}\n"
            f"----------------------------------------\n"
            f"Base URL: {self._base_url}\n"
            f"Parameters: {self._params}\n"
        )

    # decorators
    def require_endpoint_module(func):
        def wrapper(self, *args, **kwargs):
            if self.endpoint_module is None:
                raise RuntimeError(
                    "endpoint_module is not set: Please choose a valid `resource`"
                )
            return func(self, *args, **kwargs)

        return wrapper

    # setters
    @property
    def endpoint_module(self):
        return self._endpoint_module

    @endpoint_module.setter
    def endpoint_module(self, new_module):
        self._endpoint_module = new_module
        # update supported kwargs for new module
        self._supported_kwargs = self.list_parameters()
        # update pagination status for new module
        self._pagination_status = self._get_pagination_status()
        # autoupdate resource based on mgni_py_v2
        self._resource = os.path.basename(
            os.path.dirname(self.endpoint_module.__file__)
        )

    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, new_resource):
        if new_resource is None:
            self._resource = None
            self._endpoint_module = None
            self._supported_kwargs = None
            self._pagination_status = None
        elif SupportedEndpoints.is_valid(new_resource):
            # set resource name
            self._resource = new_resource
            self.endpoint_module: Callable = CORE_MODULES[
                SupportedEndpoints(new_resource)
            ]
        else:
            raise ValueError(
                f"Invalid resource: {new_resource}. "
                f"Resource must be one of {SupportedEndpoints.as_list()}."
            )

    @property
    def results_accessions(self) -> Optional[list[str]]:
        if self.to_pandas() is None:
            return None
        elif "accession" in self.to_pandas().columns:
            return self.to_pandas()["accession"].tolist()
        else:
            return None

    # methods
    @require_endpoint_module
    def list_parameters(self) -> list[str]:
        """
        Get the list of supported keyword arguments for the current resource's API function.

        Returns
        -------
        list of str
            List of supported keyword argument names.
        """
        """helper function to get supported kwargs for the current mpy module"""
        sig = inspect.signature(self.endpoint_module._get_kwargs)
        return list(sig.parameters.keys())

    def filter(
        self,
        **filters,
    ):
        """
        Update the parameters for the API call to filter results.

        Parameters
        ----------
        **filters
            Keyword arguments corresponding to the supported parameters for the current resource.
            These will be used to filter the results returned by the API.

        Returns
        -------
        Mgnifier
            A new Mgnifier instance with updated parameters for filtering results.
        """
        # make a copy of current instance
        new_mg = self._clone()
        # but with updates to params
        new_mg._params.update(filters)
        return new_mg

    @require_endpoint_module
    def dry_run(self) -> None:
        """
        Plan the API call by validating parameters and estimating the number of pages and records available.
        Prints the plan details for the user to review before executing the full data retrieval.
        This method can be called before get() to ensure that the parameters are valid and to understand the scope of the data retrieval.

        Returns
        -------
        None
        """
        # verbose
        print("Planning the API call with params:")
        # get the item count and total pages based on page_size if pagination, else set to 1
        self._get_counts()
        print(self._params)
        # verbose
        print(f"Total pages to retrieve: {self._total_pages}")
        print(f"Total records to retrieve: {self._count}")

    @require_endpoint_module
    def preview(self) -> pd.DataFrame:
        """
        Preview the first page of metadata for the current resource and parameters, without retrieving all pages. This allows the user to quickly check the structure and content of the data before deciding to retrieve everything.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the metadata from the first page of results.

        Raises
        ------
        RuntimeError
            If the API call fails or if no data is available to preview.
        """
        # plan if not already
        if (self._count is None) or (self._total_pages is None):
            # more verbose than _get_counts() alone
            self.dry_run()

        if self._pagination_status:
            # request first page and cache
            logging.info("Retrieving first page of results for preview...")
            tmp_params = self._tmp_param_update(page=1)
            response_dict = self._get_request(tmp_params)
            # dealing with response
            if response_dict is not None:
                self._cached_first_page = response_dict["items"]
                return self.to_pandas([self._cached_first_page])
        else:
            response_dict = self._get_request(self._params)
            if response_dict is not None:
                self._cached_first_page = [response_dict]
                return self.to_pandas([self._cached_first_page])
        raise RuntimeError("Failed to get response from MGnify API.")

    @require_endpoint_module
    def get(
        self,
        limit: Optional[int] = None,
        *,
        pages: Optional[list[int]] = None,
        strict: bool = False,
    ) -> pd.DataFrame:
        """ """
        if self._pagination_status:
            # async request all pages and store results in self._results
            with self._init_client() as client:
                self._collector(client, limit=limit, pages=pages, strict=strict)
        else:
            if (
                (self._total_pages is None)
                or (self._count is None)
                or (self._cached_first_page is None)
            ):
                _ = self.preview()
            # cache to result
            self._results = [self._cached_first_page]

        # return self.to_pandas(self._results)

    @require_endpoint_module
    async def aget(
        self,
        limit: Optional[int] = None,
        *,
        pages: Optional[list[int]] = None,
        strict: bool = False,
    ) -> pd.DataFrame:
        """handles pageinated (async) or not"""

        if self._pagination_status:
            # async request all pages and store results in self._results
            async with self._init_client() as client:
                await self._acollector(client, limit=limit, pages=pages, strict=strict)
        else:
            if (
                (self._total_pages is None)
                or (self._count is None)
                or (self._cached_first_page is None)
            ):
                _ = self.preview()
            # cache to result
            self._results = [self._cached_first_page]

        # return self.to_pandas(self._results)

    def to_pandas(self, data: Optional[list[dict]] = None, **kwargs) -> pd.DataFrame:
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
            logging.info("No data available to convert to DataFrame. Returning None.")
            return None

        combined_df = pd.concat(
            [self._df_expand_nested(pd.DataFrame(page)) for page in _data],
            ignore_index=True,
        )

        return pd.DataFrame(combined_df, **kwargs)

    def to_json(self, file_path: Optional[Path] = None) -> str:
        """
        Convert the current metadata to a JSON string or save it to a file.

        Parameters
        ----------
        file_path : Path, optional
            If provided, the JSON string will be saved to this file. If None, the JSON string is returned.

        Returns
        -------
        str or None
            The JSON string representation of the metadata, or None if saved to a file.

        Raises
        ------
        RuntimeError
            If no data is available to convert.
        """
        # TODO implement this method
        pass

    ## HIDDEN HELPER METHODS
    ## Help with requests
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

    def _clone(self):
        """
        Create a clone of the current Mgnifier instance for immutability :) but with no cache

        Returns
        -------
        Mgnifier
            A new Mgnifier instance with the same resource and parameters but no cached results.
        """
        new_mg = self.__class__(
            params=self._params,
        )
        # will also set resource
        new_mg.endpoint_module = self.endpoint_module

        return new_mg

    @require_endpoint_module
    def _get_request(self, given_params: dict) -> Optional[dict]:
        """
        Retrieve a single page of metadata using the synchronous API client.

        Parameters
        ----------
        given_params : dict
            Parameters for the API call.

        Returns
        -------
        dict or None
            Parsed response from the API, or None if the request failed.
        """
        with self._init_client() as client:
            response = self.endpoint_module.sync_detailed(
                client=client,
                **given_params,
            )
        logging.info(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            return response.parsed.to_dict()
        else:
            return None

    def _get_page(
        self, client: Client, params: Optional[dict[str, Any]] = None, **kwargs
    ) -> Optional[dict]:
        """
        Retrieve a single page of metadata using the synchronous API client.

        Parameters
        ----------
        client : Client
            MGnify API client instance.
        params : dict, optional
            Parameters for the API call.

        Returns
        -------
        dict or None
            Parsed response from the API, or None if the request failed.
        """
        return self.endpoint_module.sync_detailed(
            client=client,
            **(params or self._params),
            **kwargs,
        )

    def _collector(
        self,
        client: Client,
        limit: Optional[int] = None,
        pages: Optional[list[int]] = None,
        strict: bool = False,
    ):
        # not allow to run this without preview/plan first?
        if self._total_pages is None:
            if strict:
                raise AssertionError(
                    "Please run Mgnifier.dry_run() or .preview() before "
                    "deciding to collect metadata for params:\n"
                    f"{self._params}"
                )
            else:
                warnings.warn(
                    "Mgnifier.dry_run() not yet checked.", ResourceWarning, stacklevel=2
                )
                self.preview()

        # prep page nums
        if limit is not None:
            validate_gt_int(limit)
            # TODO exact limit when pageinated?
            max_page = ceil(limit / self._params["page_size"])
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
                    # else just skip invalid page numbers with warning
                    logging.warning(
                        f"Invalid page number {p} skipped as > than {self._total_pages}."
                    )
                    _pages.remove(p)
        elif pages is None:
            # init all pages if not provided
            _pages = list(range(1, self._total_pages + 1))
        else:
            raise TypeError("pages must be a list of integers or None")

        # append cached first page if avail
        if 1 in _pages and self._cached_first_page is not None:
            logging.info("Page 1 already cached from preview, skipping...")
            _pages.remove(1)
            self._results = [self._cached_first_page]
        else:
            self._results = []

        # gathering results as completed
        for page_num in tqdm(_pages, desc="Retrieving pages"):
            # awaiting each task as it completes and appending results
            page_result = self._get_page(
                client=client, params=self._params, page=page_num
            )
            self._results.append(page_result.parsed.to_dict()["items"])

    # @async_disk_lru_cache()
    async def _aget_page(
        self, client: Client, params: Optional[dict[str, Any]] = None, **kwargs
    ):
        """
        Asynchronously retrieve a single page of metadata.

        Parameters
        ----------
        client : Client
            MGnify API client instance.
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
            return await self.endpoint_module.asyncio_detailed(
                client=client,
                **(params or self._params),
                **kwargs,
            )

    async def _acollector(
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
            If True, raises an error if dry_run() or preview() has not been run.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If dry_run() or preview() has not been run and strict is True.
        ValueError
            If invalid page numbers are provided.
        TypeError
            If pages is not a list or None.
        """
        # not allow to run this without preview/plan first?
        if self._total_pages is None:
            if strict:
                raise AssertionError(
                    "Please run Mgnifier.dry_run() or .preview() before "
                    "deciding to collect metadata for params:\n"
                    f"{self._params}"
                )
            else:
                warnings.warn(
                    "Mgnifier.dry_run() not yet checked.", ResourceWarning, stacklevel=2
                )
                self.preview()

        # prep page nums
        if limit is not None:
            validate_gt_int(limit)
            # TODO exact limit when pageinated?
            max_page = ceil(limit / self._params["page_size"])
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
                    # else just skip invalid page numbers with warning
                    logging.warning(
                        f"Invalid page number {p} skipped as > than {self._total_pages}."
                    )
                    _pages.remove(p)
        elif pages is None:
            # init all pages if not provided
            _pages = list(range(1, self._total_pages + 1))
        else:
            raise TypeError("pages must be a list of integers or None")

        # append cached first page if avail
        if 1 in _pages and self._cached_first_page is not None:
            logging.info("Page 1 already cached from preview, skipping...")
            _pages.remove(1)
            self._results = [self._cached_first_page]
        else:
            self._results = []

        # creating async tasks
        async_tasks = [
            asyncio.create_task(
                self._aget_page(client=client, params=self._params, page=page_num)
            )
            for page_num in _pages
        ]

        # gathering results as completed
        for task in tqdm(asyncio.as_completed(async_tasks), total=len(async_tasks)):
            # awaiting each task as it completes and appending results
            page_result = await task
            self._results.append(page_result.parsed.to_dict()["items"])

    ## Help with workflow
    @require_endpoint_module
    def _get_counts(self):
        """
        Internal method to estimate the number of pages and records available for the current query.

        This method performs a minimal API call to set the total number of records and pages for the current resource and parameters.

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If the API call fails.
        """

        if self._pagination_status:
            # default if not given
            if "page_size" not in self._params:
                # check page_size > 0 if provided, default 25
                self._params["page_size"] = 25
                tmp_params = self._tmp_param_update(page_size=1)
            # check validity of given
            else:
                validate_gt_int(self._params["page_size"])
                tmp_params = self._tmp_param_update(page_size=1)

            # make tiny get request using mgni_py client
            response_dict = self._get_request(tmp_params)

            # dealing with response
            if response_dict is None:
                raise RuntimeError(
                    "Failed to get response from MGnify API:\n"
                    f"{self._build_url(params=tmp_params)}"
                )
            # otherwise set
            self._count = response_dict["count"]
            self._total_pages = ceil(self._count / self._params["page_size"])
        # not pagination
        else:
            self._count = 1
            self._total_pages = 1

    def _get_pagination_status(self) -> bool:
        """
        Check if the current resource requires pagination based on its supported keyword arguments.

        Returns
        -------
        bool
            True if pagination, False otherwise.
        """
        return (
            "page" in self._supported_kwargs and "page_size" in self._supported_kwargs
        )

    ## Help with data handling

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

    def _unpageinate_results(self) -> itertools.chain:
        """
        Unpaginate the results by flattening the list of pages into a single list of records.

        Returns
        -------
        itertools.chain
            An iterator that yields individual metadata records from all pages.
        """
        if self._results is None:
            raise RuntimeError(
                "No results available. Please run get() or aget() first."
            )
        return itertools.chain.from_iterable(self._results)

    ## Help with checks
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
            kwargy = self.endpoint_module._get_kwargs(**self._params)
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

    @require_endpoint_module
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
        print(encoded_params)
        if len(encoded_params) > 0:
            return f"{start_url}/?{encoded_params}"
        return start_url
