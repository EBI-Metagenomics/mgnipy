import logging

logger = logging.getLogger(__name__)
from copy import deepcopy
from typing import Any, Callable, Optional

from mgnipy._models.config import MGnipyConfig, to_mgnipy_config
from mgnipy._models.constants.CONSTANTS import SupportedEndpoints, ResourceStr
from mgnipy._shared_helpers.validators import validate_gt_int
from mgnipy.V2.describe import DescribeEmgapiModule
from mgnipy.V2.endpoints import RESOURCES_ALL_ENDPOINTS
from mgnipy.V2.mixins import DiskCheckpointer


class QuerySet:
    """
    Query Builder and State Manager for MGnify API interactions.

    Builds a set of `.queries()` that represent the API calls to be made
    based on the current resource (API endpoint) and parameters.

    Stores the current state of the query set (including the resource type, parameters) and any `results`.

    Parameters
    ----------
    resource : str
        The type of resource to query (e.g., "studies", "samples", "runs", etc.).
    config : MGnipyConfig, optional
        Configuration object for MGnipy, including settings like base URL and authentication.
    params : dict, optional
        A dictionary of parameters to include in the API request. These will be used to filter results.
    **param_kwargs
        Additional keyword arguments that will be merged into the `params` dictionary. These provide a convenient way to specify parameters directly when initializing the QuerySet.

    Attributes
    ----------
    resource : SupportedEndpoints
        The type of resource being queried, represented as an instance of SupportedEndpoints.
    base_url : str
        The base URL for the API, derived from the configuration.
    config : MGnipyConfig
        The configuration for MGnipy, including settings like base URL and authentication.
    count : Optional[int]
        The total number of results for the query.
    num_requests : Optional[int]
        The number of API requests made for the query.
    results : dict[int, list[dict]]
        The results of the API requests, stored by page number.
    params : dict[str, Any]
        The parameters for the API request.
    emgapi_handler : DescribeEmgapiModule
        The handler for interacting with the EMGAPI module.

    Methods
    -------
    filter(**filters) -> QuerySet
        Return a new QuerySet instance with updated parameters for filtering results.
    list_urls() -> list[str]
        Generate and return a list of URLs for all the API requests that would be made to retrieve the data based on the current parameters.
    queries(**httpx_kwargs) -> list[dict[str, Any]]
        Generate a list of query parameter dictionaries for each API request that would be made based on the current parameters.
    """

    def __init__(
        self,
        resource: ResourceStr,
        *,
        config: Optional[MGnipyConfig] = None,
        params: Optional[dict[str, Any]] = None,
        **param_kwargs,
    ):

        logger.debug(f"Initializing QuerySet for resource {resource}")

        self.config: MGnipyConfig = to_mgnipy_config(config)

        # attribute initialization
        self._resource: SupportedEndpoints = SupportedEndpoints.validate(resource)
        self._count: Optional[int] = None
        self._num_requests: Optional[int] = None
        self._results: dict[int, list[dict]] = None
        self._params: dict[str, Any] = params or {}
        # add param_kwargs to params if provided, prioritizing param_kwargs
        if param_kwargs:
            self._params.update(param_kwargs)

        logger.debug(
            f"resource set to {self._resource} for QuerySet initialization and module {RESOURCES_ALL_ENDPOINTS[self._resource]} will be used"
        )

        # handlers
        # for emgapi_v2_client
        self.emgapi_handler: DescribeEmgapiModule = DescribeEmgapiModule(
            endpoint_module=RESOURCES_ALL_ENDPOINTS[self._resource]
        )
        self._id_label = self.emgapi_handler.id_param_key

    @property
    def count(self) -> Optional[int]:
        return self._count

    @count.setter
    def count(self, value: Optional[int]):
        if value is not None:
            validated_count = validate_gt_int(value, 0)
            self._count = validated_count
            logger.debug(f"Set count to {self._count} for {self.resource.value}")
        else:
            self._count = None
            logger.debug(f"Set count to None for {self.resource.value}")

    @property
    def num_requests(self) -> Optional[int]:
        return self._num_requests

    @num_requests.setter
    def num_requests(self, value: Optional[int]):
        if value is not None:
            validated_num = validate_gt_int(value, 0)
            self._num_requests = validated_num
            logger.debug(
                f"Set num_requests to {self._num_requests} for {self.resource.value}"
            )
        else:
            self._num_requests = None
            logger.debug(f"Set num_requests to None for {self.resource.value}")

    @property
    def endpoint_module(self) -> Callable:
        return self.emgapi_handler.endpoint_module

    @endpoint_module.setter
    def endpoint_module(self, value: Callable):
        """
        Default endpoint modules based on resource at initialization but can be re-assigned.
        When re-assigning, the QuerySet should be re-instantiated to update the urls and other info.

        """
        logger.info("Reassigning endpoint module for %s", self.resource.value)
        self.emgapi_handler = DescribeEmgapiModule(endpoint_module=value)
        self._count: Optional[int] = None
        self._num_requests: Optional[int] = None
        self._results: dict[int, list[dict]] = None
        # check that params are valid for new endpoint module
        # _ = self.emgapi_handler.validate_endpoint_kwargs(**self.params)
        # reset cache?

        # resource_str = (
        #     self.resource.value
        #     if hasattr(self, "resource")
        #     else self.__class__.__name__
        # )

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
        request_url = self._build_request_url()
        logger.debug(
            "Resolved request URL for %s: %s", self.resource.value, request_url
        )
        return request_url

    @property
    def params(self) -> dict[str, Any]:
        return self._params

    @params.setter
    def params(self, new_params: dict[str, Any]):
        logger.info("Updating params for %s", self.resource.value)
        self._params = new_params
        # check that params are valid for endpoint module
        _ = self.emgapi_handler.validate_endpoint_kwargs(**self._params)
        # reset cache?
        logger.debug(
            "Rebuilding cache handler after params update for %s",
            self.resource.value,
        )
        self.cache_handler = DiskCheckpointer(
            params_getter=lambda: self.params,
            resource_str=self.resource.value,
            config=self.config,
            results_store=self._results,
            count=self.count,
            num_requests=self.num_requests,
        )
        self._try_load_cache()

    @property
    def resource(self) -> SupportedEndpoints:
        return self._resource

    @resource.setter
    def resource(self, value: str):
        logger.info("Setting resource to %s", value)
        self._resource = SupportedEndpoints.validate(value)
        self.endpoint_module = RESOURCES_ALL_ENDPOINTS[self._resource]

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

        logger.debug(
            "Spawning QuerySet from %s to %s",
            self.resource.value,
            target_resource or self.resource,
        )

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
        logger.debug(
            "Cloning QuerySet for %s with overrides: %s",
            self.resource.value,
            sorted(param_overrides.keys()),
        )
        merged_params = {**self.params, **param_overrides}
        resource_override = merged_params.pop("resource", None)

        target_resource = (
            getattr(self, "RESOURCE", None) or resource_override or self.resource
        )

        new_qs = self.__class__(
            resource=target_resource,
            config=self.config,
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
        logger.info(
            "Filtering QuerySet for %s with keys: %s",
            self.resource.value,
            sorted(filters.keys()),
        )
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
        request_url = f"{str(self.base_url).rstrip('/')}/{path.lstrip('/')}"
        logger.debug("Built request URL for %s: %s", self.resource.value, request_url)
        return request_url

    def list_urls(self) -> list[str]:
        """
        Generate and return a list of URLs for all the API requests that would be made to retrieve the data based on the current parameters.
        This allows the user to see exactly which endpoints and query parameters will be used in the API calls before executing them.

        Returns
        -------
        list of str
            A list of URLs corresponding to each API request that would be made.
        """
        logger.info("Listing request URLs for %s", self.resource.value)

        if self.num_requests is None:
            logger.warning(
                "Number of requests is not set. Call planning helpers (e.g., .dry_run, explain) for accurate URL list"
            )
            total_pages = 0
        else:
            total_pages = self.num_requests

        if not self.emgapi_handler.is_list_endpoint:
            return [self._build_request_url()]

        # otherwise
        _parm = deepcopy(self.params)
        urls = []
        for pg in self.emgapi_handler.page_param_iter(total_pages):
            _parm.update(pg)
            urls.append(self._build_request_url(params=_parm))
        logger.debug("Generated %s URLs for %s", len(urls), self.resource.value)
        return urls

    def __call__(self, **kwargs):
        return self.filter(**kwargs)

    def queries(self, **httpx_kwargs) -> list[dict[str, Any]]:
        """
        Generate a list of query parameter dictionaries for each API request that would be made based on the current parameters.
        This allows the user to see the specific query parameters for each request before executing them.

        Returns
        -------
        list of dict
            A list of dictionaries, each containing the query parameters for a corresponding API request.
        """
        logger.debug(f"Building query plan for {self.resource.value}")

        if not self.emgapi_handler.is_list_endpoint:
            query_setup = {
                "url": self.emgapi_handler.sub_url(**self.params),
                "params": self.params,
            }
            logger.debug("Built single-query plan for %s", self.resource.value)
            return {1: query_setup}

        if self.num_requests is None:
            logger.warning(
                "Number of requests is not set. Call planning helpers (e.g., .dry_run, explain) for accurate URL list"
            )
            total_pages = 0
        else:
            total_pages = self.num_requests

        queries = {}
        for pg, pg_param in enumerate(
            self.emgapi_handler.page_param_iter(total_pages), start=1
        ):
            # prep numbereed params
            _parm = deepcopy(self.params)
            _parm.update(pg_param)
            # save set up
            query_setup = {
                "url": self.emgapi_handler.sub_url(**_parm),
                "params": _parm,
            }
            queries[pg] = query_setup
        logger.debug("Built %s query entries for %s", len(queries), self.resource.value)
        return queries

    @property
    def results(self) -> dict[int, list[dict]]:
        """
        Get the retrieved metadata results, if available.
        Results are stored in a dictionary with request number (e.g. page number) as keys.
        """
        if self._results is None:
            logger.warning(f"No results available for {self.resource.value}")
            print(
                "No results available. Please execute a query first e.g. .get(), .page()"
            )
        else:
            logger.debug(
                f"Returning results for {self.resource.value} with pages: {list(self._results.keys())}"
            )
        return self._results

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
        in_results = validated_int in (self._results or [])
        logger.debug(f"Result presence check: {in_results}")
        return in_results
