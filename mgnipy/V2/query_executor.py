from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Any, Optional


from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy._shared_helpers.validators import validate_status_code

from mgnipy.emgapi_v2_client import AuthenticatedClient, Client

from mgnipy._shared_helpers.httpx_helpers import init_httpx_client

if TYPE_CHECKING:
    from mgnipy.emgapi_v2_client.types import Response as mpy_Response
    from mgnipy.V2.query_set import QuerySet


class QueryExecutor:
    """
    Responsible for executing the queries defined in a `QuerySet`, handling pagination, concurrency limits, and result caching.

    This class provides both synchronous and asynchronous methods to retrieve metadata pages from the MGnify API, with built-in support for concurrency control to protect the server. It also tracks successful page retrievals and allows for resuming or continuing iterations based on previously retrieved pages.

    The QueryExecutor is designed to work closely with a QuerySet, using its query definitions and caching mechanisms to efficiently retrieve and store results. It includes helper methods for initializing API clients, parsing responses, and managing iteration state.
    """

    def __init__(
        self,
        query_set: "QuerySet",
        httpx_client: Optional[Client | AuthenticatedClient] = None,
    ):
        self.qs: "QuerySet" = query_set
        self._endpoint_str: str = self.qs.emgapi_handler.endpoint_module.__name__.split(
            "."
        )[-1]

        # question: should this be shared across all instances of QueryExecutor or should each have their own?
        # i meant for this to be a concurrency limiter to protect the server -- did I get this right?
        self._semaphore = get_semaphore()

        self.httpx_client = httpx_client or init_httpx_client(self.qs.config)

    def query_setups(
        self, request_num: Optional[int] = None, **httpx_kwargs
    ) -> dict[dict[str, Any]]:
        if request_num is None:
            return self.qs.queries(**httpx_kwargs)
        return self.qs.queries(**httpx_kwargs).get(request_num, None)

    def _parse_response(self, response: mpy_Response) -> Optional[Any]:
        logger.info(f"Response status code: {response.status_code}")

        if not validate_status_code(
            response,
            logger=logger,
            db="MGnify",
            acc=getattr(self.qs, "identifier", ""),
            raise_error=False,
        ):
            logging.warning(
                f"Response validation failed for {self._endpoint_str} endpoint. Status code: {response.status_code}"
            )
            return None

        if isinstance(response.parsed, (bytes, bytearray)):
            return bytes(response.parsed)
        else:
            return response.parsed.to_dict()

    def _page_items(self, response: "mpy_Response") -> Optional[Any]:
        """Extract the 'items' from the API response.

        Example
        -------
        >>> # Parse items from response dict
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor._page_items({'items': [1,2,3]})  # doctest: +SKIP
        """
        if response is None:
            logger.warning("No response received from API.")
            return None

        if isinstance(response, (bytes, bytearray)):
            return bytes(response)

        if self.qs.emgapi_handler.is_list_endpoint:
            return response.get("items")
        else:
            logger.debug(
                "Endpoint is not a list endpoint, returning full response as items."
            )
            try:
                return response["items"]  # only because of biomes -_-
            except Exception:
                return response

    def _set_counts(self):
        """
        Helper method to set the count and num_requests attributes
        based on the current parameters and endpoint.

        Example
        -------
        >>> # Populate qs.count and qs.num_requests (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor._set_counts()  # doctest: +SKIP
        """
        if self.qs.count is not None and self.qs.num_requests is not None:
            logger.debug(
                f"Using cached count and num_requests vals: {self.qs.count}, {self.qs.num_requests}"
            )
        else:
            self.qs.count = self.qs.emgapi_handler.get_num_items(
                self._init_client(), params=self.qs.params
            )
            self.qs.num_requests = self.qs.emgapi_handler.get_num_pages(
                self.qs.count, page_size=self.qs.params.get("page_size", None)
            )
            logger.debug(
                f"Computed count and num_requests: {self.qs.count}, {self.qs.num_requests}"
            )

        # also init results dict if not already for tracking pages results
        if self.qs._results is None:
            self.qs._results = {}

    def _single_request(
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
        a_client = client or init_httpx_client(self.qs.config)
        # prep params
        request_params = {**(params or self.qs.params), **kwargs}
        # request
        response = self.qs.endpoint_module.sync_detailed(
            client=a_client,
            **request_params,
        )
        return self._parse_response(response)

    # getting specific page
    def request_page(
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

        Examples
        --------
        >>> # Fetch a single page (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor.page(1)  # doctest: +SKIP
        """

        self._set_counts()

        # check if alrady in results first
        if self.qs._is_in_results(page_num):
            logger.debug(f"Page {page_num} already retrieved.")
            return self.qs._results.get(page_num, None)

        # otherwise get page
        # init client if not provided
        a_client = client or self.httpx_client
        # getting params from qs
        params = self.query_setups(page_num).get("params", None)
        logger.info(f"Fetching request num {page_num} with params: {params}")
        response = self._single_request(
            client=a_client,
            params=params,
        )
        # get out items
        page_items = self._page_items(response)
        # add to results
        self.qs._results.update({page_num: page_items})
        return page_items

    async def _asingle_request(
        self,
        client: Optional[Client] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[dict]:
        """
        Retrieve a single get asynchronously using the asynchronous API client.

        Parameters
        ----------
        client : Client
            MGnify API client instance.
        params : dict, optional
            Parameters for the API call.
        **kwargs
            Additional keyword arguments for the API call.

        Returns
        -------
        dict or None
            Parsed response from the API, or None if the request failed.
        """
        # prep client
        a_client = client or self._init_client()
        # prep params
        request_params = {**(params or self.qs.params), **kwargs}
        # request
        async with self._semaphore:
            response = await self.qs.endpoint_module.asyncio_detailed(
                client=a_client,
                **request_params,
            )

        return self._parse_response(response)

    async def arequest_page(
        self,
        page_num: int,
        client: Optional[Client] = None,
    ) -> Optional[dict[int, list[dict]]]:
        """Async fetch for a single page.

        Example
        -------
        >>> import asyncio
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> asyncio.run(executor.apage(1))  # doctest: +SKIP
        """
        self._set_counts()
        if self.qs._is_in_results(page_num):
            logger.info(f"Page {page_num} already retrieved.")
            return self.qs._results.get(page_num, None)

        a_client = client or self._init_client()
        params = self.query_setups(page_num).get("params", None)
        logger.info(f"Fetching page {page_num} with params={params}")
        response = await self._asingle_request(client=a_client, params=params)
        page_items = self._page_items(response)
        self.qs._results.update({page_num: page_items})
        return page_items

    def __getattr__(self, name: str):
        if name == "httpx_client":
            return self._init_client().get_httpx_client()
        if name == "httpx_aclient":
            return self._init_client().get_async_httpx_client()
        if name == "api_version":
            print(self.config.api_version)
