import logging
import os
from copy import deepcopy
from itertools import chain
from typing import (
    Any,
    Callable,
    Literal,
    Optional,
)

import pandas as pd

from mgnipy._models.config import AuthMGnipyConfig
from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.describe import DescribeEmgapiModule
from mgnipy.V2.endpoints import (
    ALL_ENDPOINTS,
    ALL_SUPPORTED_RELATIONSHIPS,
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


class QuerySet:
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
        config: Optional[dict] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):

        # attribute initialization
        self._resource: SupportedEndpoints = SupportedEndpoints.validate(resource)
        self.count: Optional[int] = None
        self.num_requests: Optional[int] = None
        self.default_page_size: int = 25
        self.request_urls: Optional[list[str]] = None
        self._results: dict[int, list[dict]] = None
        self._params: dict[str, Any] = params or {}
        # add kwargs to params if provided, prioritizing kwargs
        if kwargs:
            self._params.update(kwargs)

        # handlers
        # for emgapi_v2_client
        self.emgapi_handler: DescribeEmgapiModule = DescribeEmgapiModule(
            endpoint_module=ALL_ENDPOINTS[self._resource]
        )
        # for executing requests
        self.exec: QueryExecutor = QueryExecutor(self)
        # configuration and auth init
        self.config: AuthMGnipyConfig = (
            AuthMGnipyConfig(**config) if config else AuthMGnipyConfig()
        )
        # interactive auth?
        if os.getenv("MGNIPY_AUTHENTICATION_OFF") == "1":
            logging.debug(
                "Authentication disabled e.g. for docs build. Set MGNIPY_AUTHENTICATION_OFF=0 to enable authentication."
            )
        elif self.emgapi_handler.is_private:
            logging.debug(
                f"Endpoint module {self.emgapi_handler.endpoint_module.__name__} corresponds to a private endpoint. Authentication will be required."
            )
            self.config.resolve_auth_token(interactive=True)
        else:  # silently attemp to resolve but no pop up
            self.config.resolve_auth_token(interactive=False)

    @property
    def endpoint_module(self) -> Callable:
        return self.emgapi_handler.endpoint_module

    @endpoint_module.setter
    def endpoint_module(self, value: Callable):
        """
        Default endpoint modules based on resource at initialization but can be re-assigned.
        When re-assigning, the QuerySet should be re-instantiated to update the urls and other info.

        """
        self.emgapi_handler = DescribeEmgapiModule(endpoint_module=value)
        self.count: Optional[int] = None
        self.num_requests: Optional[int] = None
        self.request_urls: Optional[list[str]] = None
        self._results: dict[int, list[dict]] = None
        # check that params are valid for new endpoint module
        _ = self.emgapi_handler.validate_endpoint_kwargs(**self._params)

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
    def params(self) -> dict[str, Any]:
        return self._params

    @params.setter
    def params(self, new_params: dict[str, Any]):
        self._params = new_params
        # check that params are valid for endpoint module
        _ = self.emgapi_handler.validate_endpoint_kwargs(**self._params)

    @property
    def results(self) -> dict[int, list[dict]]:
        """
        Get the retrieved metadata results, if available.
        Results are stored in a dictionary with request number (e.g. page number) as keys.
        """
        if self._results is None:
            print(
                "No results available. Please execute a query first e.g. .get(), .page()"
            )
        return self._results

    def _unpageinate_results(self, data: Optional[dict] = None) -> chain:
        """
        Flattening the results into a single iterator of records.
        If paginated results are stored in a dictionary with page numbers as keys,
        this method will extract the records from all pages and combine them into a single iterable sequence.

        Returns
        -------
        chain
            An iterator that yields individual metadata records from all pages.
        """
        _data = data or self.results

        def _page_to_records(page):
            if page is None:
                return []
            if isinstance(page, list):
                return page
            if isinstance(page, dict):
                return [page]
            return [page]

        return chain.from_iterable(_page_to_records(v) for v in _data.values())

    @property
    def records(self) -> Optional[chain]:
        """
        Get an iterator of individual metadata records from the retrieved results, if available.
        This property provides a convenient way to access the metadata records without needing to handle pagination.

        Returns
        -------
        chain or None
            An iterator that yields individual metadata records if results are available, otherwise None.
        """
        if self.results is None:
            return None
        return self._unpageinate_results()

    @property
    def results_ids(self) -> Optional[list[str]]:
        """
        Get a list of accessions from the retrieved metadata results, if available.

        Returns
        -------
        list of str or None
            A list of accession strings if available, otherwise None.
        """
        if self.results is None:
            logging.warning(
                "No attempts for results to be retieved yet (e.g., .get(), .page()), so no accessions/ids available."
            )
            return None

        try:
            return [record[self.id_param_key] for record in self._unpageinate_results()]
        except KeyError as exc:
            raise KeyError(
                f"Identifier key '{self.id_param_key}' not found in results for resource '{self.resource}'. Cannot extract accessions/ids. Check .results"
            ) from exc

    @property
    def resource(self) -> SupportedEndpoints:
        return self._resource

    @resource.setter
    def resource(self, value: str):
        self._resource = SupportedEndpoints.validate(value)
        self.endpoint_module = ALL_ENDPOINTS[self._resource]

    def _is_in_results(self, request_num: int) -> bool:
        """
        Check if results for a specific request number already exist in the results.

        Parameters
        ----------
        request_num : int
            The request number (e.g., page number) to check for existing results.

        Returns
        -------
        bool
            True if results for the specified request number exist, False otherwise.
        """
        # get number of pages if not already
        self.set_counts()

        if not (isinstance(request_num, int) and 0 < request_num <= self.num_requests):
            raise ValueError(
                f"Invalid request number: {request_num}. "
                "Request numbers (e.g., page number) must be positive integers "
                f"not exceeding total pages/number of requests {self.num_requests}."
            )

        return request_num in self._results

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

    @property
    def base_url(self) -> str:
        return self.config.base_url

    def _build_request_url(
        self,
        params: Optional[dict[str, Any]] = None,
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
        # accept given params or use self.params
        _params = deepcopy(params or self.params)
        # combine sub_url and encoded query params
        path = self.url_path(**_params)
        # return full url with base url+sub_url+encoded params
        return os.path.join(self.base_url, path)

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
        print("Planning the API call with params:")
        print(self.params)

        self.set_counts()

        print(f"Total requests to make: {self.num_requests}")
        print(f"Total records to retrieve: {self.count}")

    def set_counts(self):
        """
        Helper method to set the count and num_requests attributes
        based on the current parameters and endpoint.
        """
        if self.count is not None and self.num_requests is not None:
            logging.debug("Already have count and num_requests from previous dry runs")
        else:
            self.count = self.emgapi_handler.get_num_items(
                self.exec._init_client(), params=self.params
            )
            self.num_requests = self.emgapi_handler.get_num_pages(
                self.count, page_size=self.params.get("page_size", None)
            )

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
        self.set_counts()
        # cached?
        if self.request_urls is not None:
            return self.request_urls

        if not self.emgapi_handler.is_list_endpoint:
            self.request_urls = [self._build_request_url()]
        else:
            self.request_urls = []
            for page in range(1, self.num_requests + 1):
                _parm = deepcopy(self.params)
                _parm.update({"page": page})
                self.request_urls.append(self._build_request_url(params=_parm))

        return self.request_urls

    def explain(self, head: Optional[int] = None) -> None:
        """
        Print example URLs that would be called. Actual requests handled by client.
        """
        _ = self.list_urls()  # ensure urls are generated
        limit = (
            min(
                head,
                self.num_requests,
            )
            if head
            else self.num_requests
        )

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
        # PICK UP HERE: so no mixin but intead resultshandler

    # alternatively preview get first
    def first(self) -> dict:
        """
        Retrieve the first page of metadata for the current resource and parameters.
        Same as preview() but returns the raw dictionary instead of a DataFrame.
        """

        if self._is_in_results(1):
            logging.info("First response already retrieved, using cached results.")
        elif not self._is_list_endpoint:
            response_dict = self.exec.get()
            self._results[1] = response_dict

        return self._results.get(1, [])

    async def afirst(self) -> dict:
        """
        Asynchronously retrieve the first page of metadata for the current resource and parameters.
        Same as preview() but returns the raw dictionary instead of a DataFrame.
        """
        if self._is_in_results(1):
            logging.info("First response already retrieved, using cached results.")
        elif not self._is_list_endpoint:
            response_dict = await self.exec.aget()
            self._results[1] = response_dict

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
            f"Base URL: {self.base_url}\n"
            f"Parameters: {self.params}\n"
            f"Endpoint module: {self.endpoint_module.__name__ or 'None'}\n"
            f"Example request URL: {self._build_request_url()}\n"
            f"Returns paginated results: {self._is_list_endpoint}\n"
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
