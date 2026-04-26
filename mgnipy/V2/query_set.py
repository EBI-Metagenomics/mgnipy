import inspect
import logging
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
from mgnipy.V2.endpoints import (
    ALL_ENDPOINTS,
    ALL_SUPPORTED_RELATIONSHIPS,
)
from mgnipy.V2.mixins import (
    ResultsHandlerMixin,
)
from mgnipy.V2.query_executor import QueryExecutor

ID_PARAM = {
    SupportedEndpoints.BIOMES: "biome_lineage",
    SupportedEndpoints.BIOME: "biome_lineage",
    SupportedEndpoints.STUDIES: "accession",
    SupportedEndpoints.SAMPLES: "accession",
    SupportedEndpoints.RUNS: "accession",
    SupportedEndpoints.ANALYSES: "accession",
    SupportedEndpoints.GENOMES: "accession",
    SupportedEndpoints.ASSEMBLIES: "accession",
    SupportedEndpoints.PUBLICATIONS: "pubmed_id",
    SupportedEndpoints.CATALOGUES: "catalogue_id",
    SupportedEndpoints.STUDY: "accession",
    SupportedEndpoints.SAMPLE: "accession",
    SupportedEndpoints.RUN: "accession",
    SupportedEndpoints.ANALYSIS: "accession",
    SupportedEndpoints.GENOME: "accession",
    SupportedEndpoints.ASSEMBLY: "accession",
    SupportedEndpoints.PUBLICATION: "pubmed_id",
    SupportedEndpoints.CATALOGUE: "catalogue_id",
}


class QuerySet(ResultsHandlerMixin):
    """
    Plans, builds, validates and previews queries based on endpoint_module and params of the MGnifier owner.
    Stores the request urls.
    if mgnifier owner changes then the QuerySet should be re-instantiated to update the urls and other info.
    """

    def __init__(
        self,
        resource: Literal[
            "biomes",
            "biome",
            "studies",
            "study",
            "samples",
            "sample",
            "runs",
            "run",
            "genomes",
            "genome",
            "analyses",
            "analysis",
            "assemblies",
            "assembly",
        ],
        *,
        config: Optional[MgnipyConfig] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):

        self.config = MgnipyConfig(**config) if config else MgnipyConfig()

        self._base_url: str = str(self.config.base_url)
        self._resource = SupportedEndpoints.validate(resource)
        # params as dict
        self._params: dict[str, Any] = params or {}
        # add kwargs to params if provided, prioritizing kwargs
        if kwargs:
            self._params.update(kwargs)

        # default endpoint modules based on resource, can be overridden by owner
        self._endpoint_module: Callable = ALL_ENDPOINTS[self._resource]

        # check that params are valid for endpoint module
        # check params are valid for endpoint
        # self._endpoint_module._get_kwargs(**self._params)

        self.exec: QueryExecutor = QueryExecutor(self)

        self.count: Optional[int] = None
        self.total_pages: Optional[int] = None
        self.default_page_size: int = 25

        # request_urls
        self.request_urls: Optional[list[str]] = None

        # results
        self._results: dict[int, list[dict]] = {}

    @property
    def request_url(self) -> str:
        """
        Get the URL for the API request based on the current resource and parameters.
        This is a single URL that represents the request for the current page of results.

        Returns
        -------
        str
            The constructed URL for the API request.
        """
        return self._build_request_url()

    @property
    def endpoint_module(self) -> Callable:
        return self._endpoint_module

    @endpoint_module.setter
    def endpoint_module(self, value: Callable):
        # clone the current instance but with updated endpoint module
        self._endpoint_module = value
        # check params are valid for new endpoint module
        # self._endpoint_module._get_kwargs(**self._params)
        # reset results and urls since endpoint module changed
        self._results = {}
        self.request_urls = None

    @property
    def params(self) -> dict[str, Any]:
        return self._params

    @params.setter
    def params(self, new_params: dict[str, Any]):
        self._params = new_params
        # check that params are valid for endpoint module
        self.endpoint_module._get_kwargs(**self._params)

    @property
    def results(self) -> dict[int, list[dict]]:
        return self._results

    @property
    def results_ids(self) -> Optional[list[str]]:
        """
        Get a list of accessions from the retrieved metadata results, if available.

        Returns
        -------
        list of str or None
            A list of accession strings if available, otherwise None.
        """
        if self.to_df() is None:
            return None
        elif self.id_param_key in self.to_df().columns:
            return self.to_df()[self.id_param_key].tolist()
        else:
            return None

    @property
    def resource(self) -> SupportedEndpoints:
        return self._resource

    @resource.setter
    def resource(self, value: str):
        self._resource = SupportedEndpoints.validate(value)
        self.endpoint_module = ALL_ENDPOINTS[self._resource]
        # check that params are valid for new endpoint module
        self.endpoint_module._get_kwargs(**self._params)
        # reset results and urls since resource changed
        self._results = {}
        self.request_urls = None

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
        if (self.count is None) or (self.total_pages is None):
            self.dry_run()

        if not (isinstance(page_num, int) and 0 < page_num <= self.total_pages):
            raise ValueError(
                f"Invalid page number: {page_num}. "
                "Pages must be positive integers "
                f"not exceeding total pages {self.total_pages}."
            )

        return page_num in self._results

    # PARAM HANDLING
    def _spawn(
        self,
        *,
        target_resource: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> "QuerySet":
        """
        Spawn a new QuerySet instance for a related resource with given parameters.

        Returns
        -------
        QuerySet
            A new QuerySet instance with other resource and parameters.

        """

        merged_params = {**(params or {}), **kwargs}
        resource_override = merged_params.pop("resource", None)

        return QuerySet(
            resource=target_resource or resource_override or self.resource,
            config=self.config,
            params=merged_params,
        )

    def _clone(self, **param_overrides):
        """
        'polymorphism-aware, immutable-style clone helper' to create a new instance of the same class with updated parameters.
        This method is used internally to create new QuerySet instances with updated parameters while preserving the original instance's state.

        Parameters
        ----------
        **param_overrides
            Keyword arguments representing the parameters to override in the new instance.
            These will be merged with the existing parameters, with the provided overrides taking precedence.

        Returns
        -------
        QuerySet
            A new instance of the same class with the updated parameters.
        """
        merged_params = {**self.params, **param_overrides}
        resource_override = merged_params.pop("resource", None)

        target_resource = (
            getattr(self, "RESOURCE", None) or resource_override or self.resource
        )

        new_qs = self.__class__(
            resource=target_resource,
            config=self.config.model_dump(mode="json"),
            params=merged_params,
        )
        new_qs.endpoint_module = self.endpoint_module

        return new_qs

    def filter(
        self,
        **filters,
    ) -> "QuerySet":
        """
        Update the parameters for the API call to filter results.

        Parameters
        ----------
        **filters
            Keyword arguments corresponding to the supported parameters for the current resource.
            These will be used to filter the results returned by the API.

        Returns
        -------
        QuerySet
            A new QuerySet instance with updated parameters for filtering results.
        """
        # make a copy of current instance but with updated params
        new_qs = self._clone(**filters)
        return new_qs

    def page_size(self, n: int) -> "QuerySet":
        """
        Set the page size for paginated API calls.

        Parameters
        ----------
        n : int

        Returns
        -------
        QuerySet
            A new QuerySet instance with the updated page size parameter.
        """
        if not isinstance(n, int) or n <= 0:
            raise ValueError("Page size must be a positive integer.")

        # make a copy of current instance
        new_qs = self._clone(page_size=n)
        return new_qs

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def pagination_status(self) -> bool:
        """
        Check if the current resource requires pagination based on its supported keyword arguments.

        Returns
        -------
        bool
            True if pagination, False otherwise.
        """
        return (
            "page" in self.list_supported_params()
            and "page_size" in self.list_supported_params()
        )

    def list_supported_params(self) -> list[str]:
        """
        Lists supported keyword arguments for the endpoint module.

        Returns
        -------
        list of str
            List of supported keyword argument names.
        """
        sig = inspect.signature(self.endpoint_module._get_kwargs)
        return list(sig.parameters.keys())

    def _build_request_params(
        self, params: Optional[dict[str, Any]] = None, **kwargs
    ) -> dict[str, Any]:
        """
        Build the parameters for the API request by combining the current parameters with
        any additional parameters provided.

        Parameters
        ----------
        params : dict, optional
            Additional parameters to include in the API request.
        **kwargs
            Additional keyword arguments to include in the API request.

        Returns
        -------
        dict
            The combined parameters for the API request.
        """
        # combine params with kwargs, with kwargs taking precedence
        request_params = {**(params or self.params), **kwargs}
        # if pagination and no page size set, add default page size
        if self.pagination_status and "page_size" not in request_params:
            request_params["page_size"] = self.default_page_size
        return request_params

    def _build_request_url(
        self,
        params: Optional[dict[str, Any]] = None,
        exclude: list[str] = None,
    ) -> str:
        """
        Build a URL for the current resource and parameters using
        the endpoint module's URL template and the provided parameters.
        (currently for logging/verbose output only).

        Parameters
        ----------
        params : dict, optional
            Parameters to include in the URL. If None, uses self.params.
        exclude : list of str, optional
            List of parameter names to exclude from the URL query string.
            These are typically parameters that are not used for filtering in the API call,
            such as 'accession' or 'pubmed_id'.

        Returns
        -------
        str
            The constructed URL.
        """
        # specific to api design, exclude params not used for filtering
        exclude = exclude or ["accession", "pubmed_id", "catalogue_id"]
        _params = deepcopy(params or self.params)
        # check params are valid for endpoint
        _kwargs: dict[str, Any] = self.endpoint_module._get_kwargs(**_params)
        # resource based on emgapi_v2_client
        emgapi_resource = os.path.basename(
            os.path.dirname(self.endpoint_module.__file__)
        )

        _end_url: str = _kwargs.get(
            "url", f"/metagenomics/api/v2/{emgapi_resource}/"
        ).strip("/")

        url = os.path.join(self._base_url, _end_url)

        # exclude params not for filtering from encoding
        incl_params = deepcopy(_params)
        for k in exclude:
            incl_params.pop(k, None)
        # encode params for url
        encoded_params = urlencode(incl_params, doseq=True)

        return f"{url}/?{encoded_params}" if encoded_params else url

    # preview the request(s) prior to making them (option 1)
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
        print(self.params)

        if self.count is not None and self.total_pages is not None:
            logging.info("Already have count and total_pages from previous dry run")
        elif not self.pagination_status:
            # if not pageinated only 1
            self.count = 1
            self.total_pages = 1
        else:
            # small get request to get count and calc total pages
            self.exec.get_pageinated_counts()

        print(f"Total pages to retrieve: {self.total_pages}")
        print(f"Total records to retrieve: {self.count}")

    # preview the request(s) prior to making them (option 2)
    def list_urls(self) -> list[str]:
        """
        Generate and return a list of URLs for all the API requests that would be made to retrieve the data based on the current parameters.
        This allows the user to see exactly which endpoints and query parameters will be used in the API calls before executing them.

        Returns
        -------
        list of str
            A list of URLs corresponding to each API request that would be made.
        """
        if self.request_urls is not None:
            return self.request_urls
        if not self.pagination_status:
            self.request_urls = [self._build_request_url()]
        else:
            # ensure we have total_pages calculated
            if self.total_pages is None:
                self.dry_run()

            self.request_urls = []
            for page in range(1, self.total_pages + 1):
                _parm = deepcopy(self.params)
                _parm.update({"page": page})
                self.request_urls.append(self._build_request_url(params=_parm))

        return self.request_urls

    def explain(self, head: Optional[int] = None) -> None:
        """
        Print example URLs that would be called. Actual requests handled by client.
        """
        _ = self.list_urls()  # ensure urls are generated
        limit = min(head, self.total_pages) if head else self.total_pages

        for url in self.list_urls()[:limit]:
            print(url)

    # preview the request(s) prior to making them (option 3)
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

        first = self.first()
        return self.to_df({1: first})

    # alternatively preview get first
    def first(self) -> dict:
        """
        Retrieve the first page of metadata for the current resource and parameters.
        Same as preview() but returns the raw dictionary instead of a DataFrame.
        """
        self.exec.get_any_first()
        return self._results.get(1, [])

    async def afirst(self) -> dict:
        """
        Asynchronously retrieve the first page of metadata for the current resource and parameters.
        Same as preview() but returns the raw dictionary instead of a DataFrame.
        """
        await self.exec.aget_any_first()
        return self._results.get(1, [])

    # dunder methods
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
            f"MGnifier instance for resource: {self.resource}\n"
            f"I.e., {class_path}\n"
            f"----------------------------------------\n"
            f"Base URL: {self._base_url}\n"
            f"Parameters: {self.params}\n"
            f"Endpoint module: {self.endpoint_module.__name__ or 'None'}\n"
            f"Example request URL: {self._build_request_url()}\n"
            f"Returns paginated results: {self.pagination_status}\n"
        )

    def __call__(self, **kwargs):
        return self.filter(**kwargs)

    @property
    def id_param_key(self) -> str:
        try:
            return ID_PARAM[self.resource]
        except KeyError:
            raise AttributeError(
                f"Resource {self.resource} does not have a defined access identifier key."
            ) from None

    @property
    def identifier(self) -> Optional[str]:
        """
        Get the identifier value from the parameters based on the resource type.
        This is used for constructing URLs for related resources.

        Returns
        -------
        str or None
            The identifier value corresponding to the resource type, or None if not available.
        """
        try:
            return self.params[self.id_param_key]
        except KeyError:
            raise AttributeError(
                f"Identifier key '{self.id_param_key}' not found in parameters for resource '{self.resource}'."
            ) from None

    def _resolve_id_param(self, key: int | str) -> dict:
        """
        Resolve the identifier parameter for a related resource based on the provided key,
        which can be either an index or a string identifier.
        This method checks if the key is a valid index in the results or a valid identifier string,
        and returns the corresponding parameter dictionary for accessing the related resource.

        Parameters
        ----------
        key : int or str
            An integer index referring to the position in the results, or a string identifier (such as
            an accession or biome lineage) that exists in the results.

        Returns
        -------
        dict
            A dictionary containing the identifier parameter key and its corresponding value,
            which can be used to access the related resource.
            For example, {"accession": "MGYS00001234"} or {"biome_lineage": "root"}.
        """
        # allow index-based access
        if self.results_ids is not None and isinstance(key, int):
            return {self.id_param_key: self.results_ids[key]}
        # or by accession/biome_lineage/ids string directly
        if self.results_ids is not None and key in self.results_ids:
            return {self.id_param_key: key}

        raise KeyError(
            f"Invalid key: {key}. "
            "Key must be an integer index, or a valid id string. "
            f"Accession/id/biome_lineage must exist in`.results_ids`: {self.results_ids}"
        )

    # RELATIONSHIP HANDLING
    def list_relationships(self) -> list[str]:
        if self.resource in ALL_SUPPORTED_RELATIONSHIPS:
            return [
                endpoint.value
                for endpoint in ALL_SUPPORTED_RELATIONSHIPS[self.resource]
            ]
        else:
            return []

    def describe_relationships(self):
        pass  # TODO
