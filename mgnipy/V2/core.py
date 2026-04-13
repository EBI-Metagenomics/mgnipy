import inspect
import os
from copy import deepcopy
from typing import (
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
    get_mgnify_analysis,
    list_mgnify_analyses,
)
from mgnipy.V2.mgni_py_v2.api.assemblies import (
    get_assembly,
    list_analyses_for_assembly,
    list_assemblies,
    list_genome_links_for_assembly,
)
from mgnipy.V2.mgni_py_v2.api.genomes import (
    get_mgnify_genome,
    list_mgnify_genomes,
)
from mgnipy.V2.mgni_py_v2.api.miscellaneous import list_mgnify_biomes
from mgnipy.V2.mgni_py_v2.api.runs import (
    get_analysed_run,
    list_analysed_runs,
    list_runs_analyses,
)
from mgnipy.V2.mgni_py_v2.api.samples import (
    get_mgnify_sample,
    list_mgnify_samples,
    list_sample_runs,
)
from mgnipy.V2.mgni_py_v2.api.studies import (
    get_mgnify_study,
    list_mgnify_studies,
    list_mgnify_study_analyses,
    list_mgnify_study_samples,
)
from mgnipy.V2.query_executor import QueryExecutor
from mgnipy.V2.query_set import QuerySet

BASE_URL = MgnipyConfig().base_url
LIST_ENDPOINTS = {
    SupportedEndpoints.BIOMES: list_mgnify_biomes,  # get all biomes, filtering option
    SupportedEndpoints.STUDIES: list_mgnify_studies,  # get all studies, filtering option
    SupportedEndpoints.SAMPLES: list_mgnify_samples,  # get all samples, filtering option or with study acc
    SupportedEndpoints.RUNS: list_analysed_runs,  # get all runs, filtering option or with sample acc
    SupportedEndpoints.ANALYSES: list_mgnify_analyses,  # get all analyses, NO FILTERING OPTION, but with study or assem acc
    SupportedEndpoints.GENOMES: list_mgnify_genomes,  # listing all genomes, NO FILTERING OPTION but with assem acc
    # ^ list_genome_links_for_assembly,  # all genome links for given assembly
    SupportedEndpoints.ASSEMBLIES: list_assemblies,  # listing all assemblies, no filtering TODO more info?
}

ACC_DETAIL_ENDPOINTS = {
    SupportedEndpoints.BIOMES: list_mgnify_biomes,
    SupportedEndpoints.MISCELLANEOUS: list_mgnify_biomes,
    SupportedEndpoints.STUDIES: get_mgnify_study,
    SupportedEndpoints.SAMPLES: get_mgnify_sample,
    SupportedEndpoints.RUNS: get_analysed_run,
    SupportedEndpoints.ANALYSES: get_mgnify_analysis,
    SupportedEndpoints.GENOMES: get_mgnify_genome,
    SupportedEndpoints.ASSEMBLIES: get_assembly,
}

SUPPORTED_RELATIONSHIPS = {
    SupportedEndpoints.BIOMES: {SupportedEndpoints.STUDIES: list_mgnify_studies},
    SupportedEndpoints.MISCELLANEOUS: {SupportedEndpoints.STUDIES: list_mgnify_studies},
    SupportedEndpoints.STUDIES: {
        SupportedEndpoints.ANALYSES: list_mgnify_study_analyses,
        SupportedEndpoints.SAMPLES: list_mgnify_study_samples,
    },
    SupportedEndpoints.SAMPLES: {SupportedEndpoints.RUNS: list_sample_runs},
    SupportedEndpoints.RUNS: {SupportedEndpoints.ANALYSES: list_runs_analyses},
    SupportedEndpoints.ASSEMBLIES: {
        SupportedEndpoints.ANALYSES: list_analyses_for_assembly,
        SupportedEndpoints.GENOMES: list_genome_links_for_assembly,
    },
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
                "runs",
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
        resource : {"biomes", "studies", "samples", "runs", "genomes", "analyses", "assemblies"}, optional
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
        # params as dict
        self._params: dict[str, Any] = params or {}
        # add kwargs to params if provided
        if kwargs:
            self._params.update(kwargs)
        # results
        self._count: Optional[int] = None
        self._total_pages: Optional[int] = None
        self._results: dict[int, list[dict]] = {}
        self._endpoint_module: Optional[Callable] = None
        self._supported_kwargs: Optional[list[str]] = None
        self._pagination_status: Optional[bool] = None
        # set endpoint module and supported kwargs if resource provided
        self._resolve_resource_endpoint(resource)

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
        Get detail by accession or get a slice of results by index. If key is an integer index or slice, return the corresponding record(s) from the results. If key is a string and matches an accession in the results, return the record(s) with that accession.
        """
        acc_param = self._qs._resolve_results_accession_params(key)
        # if one
        return self.get_detail(acc_param)

    def get_detail(
        self,
        accession_param: dict[str, str],
    ) -> dict | pd.DataFrame:
        """
        Get detailed metadata for a specific accession by calling the appropriate endpoint module.

        Parameters
        ----------
        accession : str
            The accession identifier for which to retrieve detailed metadata.
        output_format : {"dict", "df"}, optional
            The format of the output. Defaults to "dict".

        Returns
        -------
        dict | pd.DataFrame
            A dictionary or DataFrame containing the detailed metadata for the specified accession.

        Raises
        ------
        RuntimeError
            If no endpoint module is set or if the API call fails.
        """
        new_mg = self.__class__(
            **accession_param,
        )

        new_mg.endpoint_module = ACC_DETAIL_ENDPOINTS[
            SupportedEndpoints(self._resource)
        ]

        print(new_mg._qs.first())
        return new_mg

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
        if name == "httpx_aclient":
            return self._init_client().get_async_httpx_client()
        if name == "request_url":
            return self._build_url()
        if name == "api_version":
            print("v2")
        if SupportedEndpoints.is_valid(name):
            if SupportedEndpoints(name) in SUPPORTED_RELATIONSHIPS.get(
                SupportedEndpoints(self._resource), []
            ):
                if self.accession:
                    acc_params = {"accession": self.accession}
                elif self.lineage:
                    acc_params = {"biome_lineage": self.lineage}
                mg = self._spawn(resource=name, **acc_params)
                mg.endpoint_module = SUPPORTED_RELATIONSHIPS[
                    SupportedEndpoints(self._resource)
                ][SupportedEndpoints(name)]
                return mg
            else:
                raise AttributeError(
                    f"{name} is not a valid related resource for {self._resource}. "
                    f"Supported related resources are: "
                    f"{[res.value for res in SUPPORTED_RELATIONSHIPS.get(SupportedEndpoints(self._resource), [])]}"
                )
        if name.startswith("__") and name.endswith("__"):
            return self.__dict__.get(name)
        try:
            return self.__dict__[f"_{name}"]
        except KeyError as e:
            raise KeyError(f"{name} is not a valid attribute of MGnifier") from e

    def __call__(self, **kwargs):
        return self.filter(**kwargs)

    @property
    def accession(self):
        return self._params.get("accession", None)

    @property
    def lineage(self):
        return self._params.get("biome_lineage", None)

    def __str__(self):
        """
        Return a string representation of the MGnifier instance, summarizing key configuration and state.

        Returns
        -------
        str
            Human-readable summary of the instance.
        """
        cls = type(self)
        class_path = f"{cls.__module__}.{cls.__qualname__}"
        return (
            f"MGnifier instance for resource: {self._resource}\n"
            f"I.e., {class_path}\n"
            f"----------------------------------------\n"
            f"Base URL: {self._base_url}\n"
            f"Parameters: {self._params}\n"
            f"Endpoint module: {self._endpoint_module.__name__ or 'None'}\n"
            f"Example request URL: {self.request_url}\n"
            f"Returns paginated results: {self._pagination_status}\n"
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
        self._resolve_resource_endpoint(new_resource)

    def _resolve_resource_endpoint(self, resource: str):
        if SupportedEndpoints.is_valid(resource):
            # set resource name
            self._resource = resource
            if "accession" in self._params:
                self._endpoint_module = ACC_DETAIL_ENDPOINTS[
                    SupportedEndpoints(resource)
                ]
            else:
                self.endpoint_module = LIST_ENDPOINTS[SupportedEndpoints(resource)]
        # reset all
        elif resource is None:
            self._resource = None
            self._endpoint_module = None
            self._supported_kwargs = None
            self._pagination_status = None
        else:
            raise ValueError(
                f"Invalid resource: {resource}. "
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

    def _spawn(self, *, resource: Optional[str] = None, **params) -> "MGnifier":
        return MGnifier(resource=resource or self._resource, **params)

    def _clone(self) -> "MGnifier":
        """
        Create a clone of the current MGnifier instance for immutability :) but with no cache

        Returns
        -------
        MGnifier
            A new MGnifier instance with the same resource and parameters but no cached results.
        """
        new_mg = self.__class__(
            # resource=self._resource,
            **deepcopy(self._params),
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

    @property
    def results_biome_lineages(self) -> Optional[list[str]]:
        return self._qs.results_biome_lineages

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
