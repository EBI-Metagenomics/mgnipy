import asyncio
import inspect
import logging
import os
import warnings
from copy import deepcopy
from itertools import chain
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
from mgnipy.V2.mgni_py_v2.types import Response as mpy_Response

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


class MGnifier:
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
        **kwargs,
    ):
        """
        Initialize a MGnifier instance for a specific MGnify resource.

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
        self._default_page_size: int = 25
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

        # results
        self._count: Optional[int] = None
        self._total_pages: Optional[int] = None
        self._previewed_page: Optional[list] = None
        # instead dict by page num, so can .page(<page_num>)
        self._results: dict[int, list[dict]] = {}

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
        if name == "httpx_client":
            return self._init_client().get_httpx_client()
        elif name == "httpx_aclient":
            return self._init_client().get_async_httpx_client()
        elif name == "request_url":
            return self._build_url()
        elif name == "api_version":
            print("v2")
        else:
            try:
                return self.__dict__[f"_{name}"]
            except KeyError as e:
                raise KeyError(f"{name} is not a valid attribute of MGnifier") from e

    def __str__(self):
        """
        Return a string representation of the MGnifier instance, summarizing key configuration and state.

        Returns
        -------
        str
            Human-readable summary of the instance.
        """
        return (
            f"MGnifier instance for resource: {self._resource}\n"
            f"----------------------------------------\n"
            f"Base URL: {self._base_url}\n"
            f"Parameters: {self._params}\n"
        )

    ## decorators
    def require_endpoint_module(func):
        def wrapper(self, *args, **kwargs):
            if self.endpoint_module is None:
                raise RuntimeError(
                    "endpoint_module is not set: Please choose a valid `resource`"
                )
            return func(self, *args, **kwargs)

        return wrapper

    def require_pagination(func):
        def wrapper(self, *args, **kwargs):
            if not self._pagination_status:
                raise RuntimeError(
                    f"Current endpoint does not support pagination: {self.endpoint_module}. "
                    "Please check the documentation for supported parameters."
                )
            return func(self, *args, **kwargs)

        return wrapper

    ## setters
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
        """
        Get a list of accessions from the retrieved metadata results, if available.

        Returns
        -------
        list of str or None
            A list of accession strings if available, otherwise None.
        """
        if self.to_pandas() is None:
            return None
        elif "accession" in self.to_pandas().columns:
            return self.to_pandas()["accession"].tolist()
        else:
            return None

    ## user-facing methods (in order of probable use)
    # help: what can filter by?
    @require_endpoint_module
    def list_parameters(self) -> list[str]:
        """
        Get the list of supported keyword arguments for the current resource's API function.

        Returns
        -------
        list of str
            List of supported keyword argument names.
        """
        sig = inspect.signature(self.endpoint_module._get_kwargs)
        return list(sig.parameters.keys())

    # choose to filter request or not
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
        MGnifier
            A new MGnifier instance with updated parameters for filtering results.
        """
        # make a copy of current instance
        new_mg = self._clone()
        # but with updates to params
        new_mg._params.update(filters)
        return new_mg

    # preview the request(s) prior to making them (option 1)
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
        print(self._params)

        if self._count is not None and self._total_pages is not None:
            logging.info("Already have count and total_pages from previous dry run")
        elif not self._pagination_status:
            # if not pageinated only 1
            self._count = 1
            self._total_pages = 1
        else:
            # small get request to get count and calc total pages
            response_dict = self._get_request(page_size=1)
            self._count = response_dict["count"]
            self._total_pages = ceil(
                self._count / self._params.get("page_size", self._default_page_size)
            )

        print(f"Total pages to retrieve: {self._total_pages}")
        print(f"Total records to retrieve: {self._count}")

    # preview the request(s) prior to making them (option 2)
    # TODO what request(s) with current params?
    @require_endpoint_module
    def explain(self):
        """
        Print URLs that would be called

        TODO: should actually print multiple urls? for each page
        """
        return self._build_url()

    # preview the request(s) prior to making them (option 3)
    @require_endpoint_module
    def preview(self) -> pd.DataFrame:
        """
        Preview the first page of metadata for the current resource and parameters, without retrieving all pages.
        This allows the user to quickly check the structure and content of the data before deciding to retrieve everything.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the metadata from the specified page of results.

        Raises
        ------
        RuntimeError
            If the API call fails or if no data is available to preview.
        """

        # already retrieved?
        if self._is_in_results(1):
            logging.info("Page 1 already retrieved, using cached results.")
            return self.to_pandas(data={1: self._results[1]})

        if not self._pagination_status:
            # then just get and add to results
            response_dict = self._get_request()
            self._results.update({1: response_dict})
            return self.to_pandas()

        # otherwise, get first page and return as df
        return self.to_pandas(data={1: self.page(1)})

    # now actually getting stuff!! (was lazy**/building queryies up to this point- just previewing and planning)
    # **however needed to make tiny requests to get counts, total pages, previews for paginated endpoints
    @require_endpoint_module
    @require_pagination
    def page(
        self, page_num: int, client: Optional[Client] = None
    ) -> Optional[dict[int, list[dict]]]:
        """
        Retrieve a specific page of metadata for the current resource and parameters.
        This method allows the user to retrieve metadata one page at a time,
        which can be useful for previewing data or for manual pagination control.

        Parameters
        ----------
        page_num : int
            The page number to retrieve (1-based index).
        client : Client, optional
            An optional MGnify API client instance to use for the request.
            If None, a new client will be initialized.
        Returns
        -------
        Optional[dict[int, list[dict]]]
            A dictionary containing the metadata from the specified page of results,
            or None if the page is not found.
        """

        # check if alrady in results first
        if self._is_in_results(page_num):
            logging.info(f"Page {page_num} already retrieved.")
            return self._results.get(page_num, None)

        # otherwise get page
        a_client = client or self._init_client()
        response = self._get_request(
            client=a_client,
            page=page_num,
        )
        # get out items
        page_items = self._page_items(response)
        # add to results
        self._results.update({page_num: page_items})
        return self._results.get(page_num, None)

    @require_endpoint_module
    def get(
        self,
        limit: Optional[int] = None,
        *,
        pages: Optional[list[int]] = None,
        safety: bool = True,
    ):
        """Getting all"""
        if not self._pagination_status:
            _ = self.preview()

        else:
            # async request all pages and store results in self._results
            with self._init_client() as client:
                self._pages_collector(client, limit=limit, pages=pages, safety=safety)
        # PICK UP HERE

    def to_pandas(
        self, data: Optional[dict[int, list[dict]]] = None, **kwargs
    ) -> pd.DataFrame:
        """
        Convert the current or provided metadata to a pandas DataFrame.

        Parameters
        ----------
        data : list of dict, optional
            List of records to convert. If None, uses self._results or self._previewed_page.
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

        _data = data or self._results

        if _data == {} or _data is None:
            logging.info("No data available to convert to DataFrame. Returning None.")
            return None

        return pd.DataFrame(self._unpageinate_results(_data), **kwargs)

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
                or (self._previewed_page is None)
            ):
                _ = self.preview()
            # cache to result
            self._results.update({1: self._previewed_page})

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
        Create a clone of the current MGnifier instance for immutability :) but with no cache

        Returns
        -------
        MGnifier
            A new MGnifier instance with the same resource and parameters but no cached results.
        """
        new_mg = self.__class__(
            params=self._params,
        )
        # will also set resource
        new_mg.endpoint_module = self.endpoint_module

        return new_mg

    def _get_request(
        self,
        client: Optional[Client] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[dict]:
        """
        Retrieve a single get using the synchronous API client.
        Handles pagination and not.

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
        # prep client
        a_client = client or self._init_client()
        # prep params
        request_params = {**(params or self._params), **kwargs}

        # make sure page_size if pageinated
        if self._pagination_status and "page_size" not in request_params:
            request_params["page_size"] = self._default_page_size

        response = self.endpoint_module.sync_detailed(
            client=a_client,
            **request_params,
        )
        logging.info(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            return response.parsed.to_dict()

    def _page_items(self, response: mpy_Response) -> Optional[dict]:
        """
        Extract the 'items' from the API response.
        """
        if response is None:
            logging.warning("No response received from API.")
            return None
        return response["items"]

    def _is_in_results(self, page_num: int) -> bool:
        """
        Check if results for a specific page number already exist in the results.

        Parameters
        ----------
        page_num : int
            The page number to check for existing results.

        Returns
        -------
        bool
            True if results for the specified page number exist, False otherwise.
        """
        # get number of pages if not already
        if (self._count is None) or (self._total_pages is None):
            self.dry_run()

        if not (isinstance(page_num, int) and 0 < page_num <= self._total_pages):
            raise ValueError(
                f"Invalid page number: {page_num}. "
                "Pages must be positive integers "
                f"not exceeding total pages {self._total_pages}."
            )

        return page_num in self._results

    @require_pagination
    def _pages_collector(
        self,
        client: Client,
        limit: Optional[int] = None,
        pages: Optional[list[int]] = None,
        safety: bool = True,
    ):
        """
        Collect metadata for all (or selected) pages and store results to self.results.

        Parameters
        ----------
        client : Client
            MGnify API client instance.
        limit : int, optional
            Maximum number of records to retrieve. If None, retrieves all records.
        pages : list of int, optional
            List of page numbers to retrieve. If None, retrieves all pages.
        safety : bool, default True
            If True, raises an error if dry_run() or preview()
            has not been run to check total pages and counts before collecting.
        """
        # not allow to run this without preview/plan first?
        if safety and self._total_pages is None:
            raise AssertionError(
                "Please run .dry_run() or .preview() before "
                "deciding to collect metadata for params:\n"
                f"{self._params}"
            )

        # prep page nums
        if isinstance(pages, list):
            _pages = deepcopy(pages)
        elif pages is None:
            # init all pages if not provided
            _pages = list(range(1, self._total_pages + 1))
        else:
            raise TypeError("pages must be a list of integers or None")

        if limit is not None:
            # limit to number of records/items
            # LIMITATION: since paginated cannot retrieve exact num sometimes
            # check if int and over zero
            validate_gt_int(limit)
            # get max number of pages based on limit and page size
            max_num_pages = ceil(
                limit / (self._params.get("page_size", self._default_page_size))
            )
            # filter out pages that are over the max
            _pages = [p for p in _pages if p <= max_num_pages]

        # get pages if not in results already
        a_client = client or self._init_client()
        for p in tqdm(_pages, desc="Retrieving pages"):
            # skip if page already retrieved
            if self._is_in_results(p):
                logging.info(f"Page {p} already retrieved, skipping...")
            else:
                self.page(p, client=a_client)

    # TODO
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

    # TODO
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
                    "Please run MGnifier.dry_run() or .preview() before "
                    "deciding to collect metadata for params:\n"
                    f"{self._params}"
                )
            else:
                warnings.warn(
                    "MGnifier.dry_run() not yet checked.", ResourceWarning, stacklevel=2
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
        if 1 in _pages and self._previewed_page is not None:
            logging.info("Page 1 already cached from preview, skipping...")
            _pages.remove(1)
            self._results = [self._previewed_page]
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

    def _unpageinate_results(self, data: Optional[dict] = None) -> chain:
        """
        Unpaginate the results by flattening the dictionary of pages into a single list of records.

        Returns
        -------
        chain
            An iterator that yields individual metadata records from all pages.
        """
        _data = data or self._results

        if _data == {} or _data is None:
            raise RuntimeError(
                "No results available. "
                "Please run preview(), get(), aget(), page() first."
            )
        return chain.from_iterable(_data.values())

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

        if len(encoded_params) > 0:
            return f"{start_url}/?{encoded_params}"
        return start_url
