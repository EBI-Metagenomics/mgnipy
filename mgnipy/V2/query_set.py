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

from mgnipy._models.config import AuthMGnipyConfig
from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy._shared_helpers.pydantic_help import validate_gt_int
from mgnipy.V2.describe import DescribeEmgapiModule
from mgnipy.V2.endpoints import (
    ALL_ENDPOINTS,
)
from mgnipy.V2.mixins import DiskCheckpointMixin


class QuerySet(DiskCheckpointMixin):
    """
    Builds and stores the current state of a query, including the resource type, parameters, and results.
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

        # load any existing cached pages for this exact query
        try:
            loaded = self.load_cache_from_disk()
            if loaded:
                logging.info(f"Loaded {loaded} cached page(s) for {self._resource}")
        except Exception:
            logging.exception("Failed to load query cache")

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

        # validate num is positive int
        validated_int = validate_gt_int(request_num, 0)

        return validated_int in self._results

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
        path = self.emgapi_handler.url_path(**_params)
        # return full url with base url+sub_url+encoded params
        return f"{str(self.base_url).rstrip('/')}/{path.lstrip('/')}"

    def list_urls(self) -> list[str]:
        """
        Generate and return a list of URLs for all the API requests that would be made to retrieve the data based on the current parameters.
        This allows the user to see exactly which endpoints and query parameters will be used in the API calls before executing them.

        Returns
        -------
        list of str
            A list of URLs corresponding to each API request that would be made.
        """

        if self.num_requests is None:
            logging.warning(
                "Number of requests is not set. Call planning helpers (e.g., .dry_run, explain) for accurate URL list"
            )
            total_pages = 0
        else:
            total_pages = self.num_requests

        if not self.emgapi_handler.is_list_endpoint:
            return [self._build_request_url()]

        # otherwise
        _parm = deepcopy(self.params)
        return [
            self._build_request_url(params=_parm.update(pg_param))
            for pg_param in self.emgapi_handler.page_param_iter(total_pages)
        ]

    def __call__(self, **kwargs):
        return self.filter(**kwargs)
