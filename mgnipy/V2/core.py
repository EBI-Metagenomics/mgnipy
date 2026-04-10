from __future__ import annotations

import inspect
import os
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Literal,
    Optional,
)
from urllib.parse import urlencode

import pandas as pd

from mgnipy._models.config import MgnipyConfig
from mgnipy._models.CONSTANTS import SupportedEndpoints
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

if TYPE_CHECKING:
    from mgnipy.V2.query_executor import QueryExecutor
    from mgnipy.V2.query_set import QuerySet

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
    State owner and facade for users. Holds current resource, params, and results. Provides user-facing methods for filtering, getting, and outputting data.
    """

    def __init__(
        self,
        *,
        resource: Optional[
            Literal[
                "biomes",
                "studies",
                "samples",
                "genomes",
                "analyses",
                "assemblies",
            ]
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
        self._resource = resource
        self._endpoint_module: Optional[Callable] = None
        self._supported_kwargs: Optional[list[str]] = None
        self._pagination_status: Optional[bool] = None
        # params as dict
        self._params: dict[str, Any] = params or {}
        # add kwargs to params if provided
        if kwargs:
            self._params.update(kwargs)
        # results
        self._count: Optional[int] = None
        self._total_pages: Optional[int] = None
        self._results: dict[int, list[dict]] = {}
        # set endpoint module and supported kwargs if resource provided
        if self._resource is not None:
            self._endpoint_module = CORE_MODULES[SupportedEndpoints(resource)]
            self._supported_kwargs = self.list_parameters()
            self._pagination_status = self._get_pagination_status()

        # query set and executor
        self._executor = QueryExecutor(self)
        self._qs = QuerySet(self)

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
            self.endpoint_module = CORE_MODULES[SupportedEndpoints(new_resource)]
        else:
            raise ValueError(
                f"Invalid resource: {new_resource}. "
                f"Resource must be one of {SupportedEndpoints.as_list()}."
            )

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
            self._qs.dry_run()

        if not (isinstance(page_num, int) and 0 < page_num <= self._total_pages):
            raise ValueError(
                f"Invalid page number: {page_num}. "
                "Pages must be positive integers "
                f"not exceeding total pages {self._total_pages}."
            )

        return page_num in self._results

    # get all pages (with option to filter which pages or how many records with limit)

    ## Helpers
    @require_endpoint_module
    def _build_url(
        self,
        params: Optional[dict[str, Any]] = None,
        exclude: list[str] = None,
    ) -> str:
        """
        Build a URL for the current resource and parameters (for logging/verbose output only).

        Parameters
        ----------
        params : dict, optional
            Parameters to include in the URL. If None, uses self._params.

        Returns
        -------
        str
            The constructed URL.
        """
        exclude = exclude or ["accession", "pubmed_id", "catalogue_id"]
        params = params or self._params
        # check params are valid for endpoint
        _kwargs: dict[str, Any] = self.endpoint_module._get_kwargs(**params)

        _end_url: str = _kwargs.get(
            "url", f"/metagenomics/api/v2/{self._resource}/"
        ).strip("/")

        incl_params = deepcopy(params)
        for k in exclude:
            incl_params.pop(k, None)
        start_url = os.path.join(self._base_url, _end_url)
        encoded_params = urlencode(incl_params, doseq=True)

        return f"{start_url}/?{encoded_params}" if encoded_params else start_url

    def _clone(self) -> "MGnifier":
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

    def _get_pagination_status(self) -> bool:
        """
        Check if the current resource requires pagination based on its supported keyword arguments.

        Returns
        -------
        bool
            True if pagination, False otherwise.
        """
        return (
            bool(self._supported_kwargs)
            and "page" in self._supported_kwargs
            and "page_size" in self._supported_kwargs
        )

    #### only preserve old mgnifier functionality
    def filter(self, **filters):
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
        return self._qs.filter(**filters).owner

    def page_size(self, n: int):
        """
        Set the page size for paginated API calls.

        Parameters
        ----------
        n : int

        Returns
        -------
        MGnifier
            A new MGnifier instance with the updated page size parameter.
        """
        return self._qs.page_size(n).owner

    def dry_run(self):
        """
        Plan the API call by validating parameters and estimating the number of pages and records available.
        Prints the plan details for the user to review before executing the full data retrieval.
        This method can be called before get() to ensure that the parameters are valid and to understand the scope of the data retrieval.

        Returns
        -------
        None
        """
        self._qs.dry_run()

    def explain(self, head: Optional[int] = None):
        """
        Print example URLs that would be called. Actual requests handled by client.
        """
        self._qs.explain(head=head)

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
        return self._qs.preview()

    def first(self) -> dict:
        """
        Alias for preview() to get the first item of first page of results.

        Returns
        -------
        dict
            The first item from the first page of results.
        """
        return self._qs.first()

    def get(
        self,
        limit: Optional[int] = None,
        *,
        pages: Optional[list[int]] = None,
        safety: bool = True,
        hide_progress: bool = False,
    ):
        """Getting all"""
        self._executor.get(
            limit=limit, pages=pages, safety=safety, hide_progress=hide_progress
        )

    async def aget(
        self,
        limit: Optional[int] = None,
        *,
        pages: Optional[list[int]] = None,
        safety: bool = True,
        hide_progress: bool = False,
    ):
        """Getting all asynchronously"""
        await self._executor.aget(
            limit=limit, pages=pages, safety=safety, hide_progress=hide_progress
        )

    @property
    def results_accessions(self) -> Optional[list[str]]:
        return self._qs.results_accessions

    def to_df(self, data: Optional[dict[int, list[dict]]] = None, **kwargs):
        return self._qs.to_df(data=data, **kwargs)

    def to_list(self, data: Optional[dict[int, list[dict]]] = None):
        return self._qs.to_list(data=data)

    def to_json(self, data: Optional[dict[int, list[dict]]] = None, **kwargs):
        return self._qs.to_json(data=data, **kwargs)

    def to_polars(self, data: Optional[dict[int, list[dict]]] = None, **kwargs):
        return self._qs.to_polars(data=data, **kwargs)

    def page(self, page_num: int, client: Optional[Client] = None):
        return self._executor.page(page_num, client=client)

    async def apage(self, page_num: int, client: Optional[Client] = None):
        return await self._executor.apage(page_num, client=client)
