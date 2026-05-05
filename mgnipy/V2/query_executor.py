from __future__ import annotations

import asyncio
import logging
from copy import deepcopy
from math import ceil
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
)

from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from mgnipy._shared_helpers.async_helpers import (
    get_semaphore,
)
from mgnipy._shared_helpers.validators import validate_gt_int
from mgnipy.emgapi_v2_client import (
    AuthenticatedClient,
    Client,
)

if TYPE_CHECKING:
    from mgnipy.emgapi_v2_client.types import Response as mpy_Response
    from mgnipy.V2.query_set import QuerySet

PAGES_LIMIT = 100
ITEMS_LIMIT = PAGES_LIMIT * 25


class QueryExecutor:
    def __init__(self, query_set: "QuerySet"):
        self.qs = query_set

        # question: should this be shared across all instances of QueryExecutor or should each have their own?
        # i meant for this to be a concurrency limiter to protect the server -- did I get this right?
        self._semaphore = get_semaphore()

    def query_setups(
        self, request_num: Optional[int], **httpx_kwargs
    ) -> dict[dict[str, Any]]:
        if request_num is None:
            return self.qs.queries(**httpx_kwargs)
        return self.qs.queries(**httpx_kwargs).get(request_num, None)

    def __iter__(self):
        for q in self.query_setups():
            yield self.page(q)

    async def __aiter__(self):
        for q in self.query_setups():
            yield await self.apage(q)

    def _init_client(
        self,
        auth_token: Optional[str] = None,
        **httpx_kwargs,
    ) -> Client:
        """
        Initialize and return a MGnify API client instance.

        Returns
        -------
        Client
            Configured MGnify API client.
        """

        _auth = auth_token or self.qs.config.auth_token

        if _auth:
            logging.info("Initializing client with provided auth token.")
            return AuthenticatedClient(
                base_url=str(self.qs.base_url),
                token=_auth,
                **httpx_kwargs,
            )

        return Client(
            base_url=str(self.qs.base_url),
            **httpx_kwargs,
        )

    def set_counts(self):
        """
        Helper method to set the count and num_requests attributes
        based on the current parameters and endpoint.
        """
        if self.qs.count is not None and self.qs.num_requests is not None:
            logging.debug("Already have count and num_requests from previous dry runs")
        else:
            self.qs.count = self.qs.emgapi_handler.get_num_items(
                self._init_client(), params=self.qs.params
            )
            self.qs.num_requests = self.qs.emgapi_handler.get_num_pages(
                self.qs.count, page_size=self.qs.params.get("page_size", None)
            )

    def first(self) -> dict:
        """
        Retrieve the first page of metadata for the current resource and parameters.
        Same as preview() but returns the raw dictionary instead of a DataFrame.
        """

        if self.qs._is_in_results(1):
            logging.info("First response already retrieved, using cached results.")
        elif not self.qs.emgapi_handler._is_list_endpoint:
            response_dict = self.exec.get()
            self.qs._results[1] = response_dict

        return self.qs._results.get(1, [])

    async def afirst(self) -> dict:
        """
        Asynchronously retrieve the first page of metadata for the current resource and parameters.
        Same as preview() but returns the raw dictionary instead of a DataFrame.
        """
        if self.qs._is_in_results(1):
            logging.info("First response already retrieved, using cached results.")
        elif not self.qs.emgapi_handler._is_list_endpoint:
            response_dict = await self.exec.aget()
            self.qs._results[1] = response_dict

        return self.qs._results.get(1, [])

    async def _semaphore_guarded_request(
        self,
        client: Client,
        **request_params,
    ):
        """
        Make an API request while respecting the concurrency
        limits of the server using a semaphore.

        Parameters
        ----------
        client : Client
            MGnify API client instance.
        **request_params
            Parameters for the API call.

        Returns
        -------
        dict or None
            Parsed response from the API, or None if the request failed.
        """
        # limiting concurrency to protect server
        async with self._semaphore:
            return await self.qs.endpoint_module.asyncio_detailed(
                client=client,
                **(request_params or self.qs.params),
            )

    async def map_with_concurrency(
        self,
        items,
        worker,
        hide_progress: bool = False,
    ):
        """
        Map a worker function over a list of items with controlled concurrency.
        In plain English, it is a “process these things in parallel, but not too many at once” helper.

        Example
        -------
        results = await self.map_with_concurrency(
            items=pages,
            worker=lambda p: self.apage(p, client),
        )
        """

        # helper to run worker with semaphore
        async def _run_one(i, item):
            async with self._semaphore:
                return i, await worker(item)

        # create tasks for all items
        tasks = [asyncio.create_task(_run_one(i, item)) for i, item in enumerate(items)]
        # collect results as they complete, preserving order
        ordered = [None] * len(tasks)
        # tqdm for progress bar
        for task in tqdm(
            asyncio.as_completed(tasks),
            total=len(tasks),
            desc="Processing",
            disable=hide_progress,
        ):
            i, value = await task
            ordered[i] = value
        return ordered

    def _parse_response(self, response: mpy_Response) -> Optional[dict[str, Any]]:
        logging.info(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            return response.parsed.to_dict()
        if response.status_code == 403:
            raise PermissionError(
                "Access forbidden: You do not have permission to access this resource. "
                "Please check your authentication token and permissions."
            )
        if response.status_code == 404:
            raise FileNotFoundError(
                "Resource not found: The requested resource does not exist. "
                "Please check the endpoint and parameters."
            )
        return None

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
        a_client = client or self._init_client()
        # prep params
        request_params = {**(params or self.qs.params), **kwargs}
        # request
        response = self.qs.endpoint_module.sync_detailed(
            client=a_client,
            **request_params,
        )
        return self._parse_response(response)

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
        response = await self._semaphore_guarded_request(
            client=a_client,
            **request_params,
        )
        return self._parse_response(response)

    def _page_items(self, response: "mpy_Response") -> Optional[dict]:
        """
        Extract the 'items' from the API response.
        """
        if response is None:
            logging.warning("No response received from API.")
            return None
        return response.get("items", None)

    # getting specific page
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

        self.set_counts()

        # check if alrady in results first
        if self.qs._is_in_results(page_num):
            logging.info(f"Page {page_num} already retrieved.")
            return self.qs._results.get(page_num, None)

        # otherwise get page
        # init client if not provided
        a_client = client or self._init_client()
        # getting params from qs
        params = self.query_setups(page_num)
        response = self._single_request(
            client=a_client,
            params=params,
        )
        # get out items
        page_items = self._page_items(response)
        # add to results
        self.qs._results.update({page_num: page_items})
        # checkpoint each page
        try:
            self.qs.cache_handler.write_results(page_num, page_items)
        except Exception:
            logging.exception(f"Failed to checkpoint page {page_num}")
        return page_items

    async def apage(
        self,
        page_num: int,
        client: Optional[Client] = None,
    ) -> Optional[dict[int, list[dict]]]:
        self.set_counts()
        if self.qs._is_in_results(page_num):
            logging.info(f"Page {page_num} already retrieved.")
            return self.qs._results.get(page_num, None)

        a_client = client or self._init_client()
        params = self.query_setups(page_num)
        response = await self._asingle_request(client=a_client, params=params)
        page_items = self._page_items(response)
        self.qs._results.update({page_num: page_items})
        # checkpoint
        try:
            await self.qs.cache_handler.awrite_results(page_num, page_items)
        except Exception:
            logging.exception(f"Failed to checkpoint page {page_num}")
        return page_items

    def _resolve_pages_to_collect(
        self,
        *,
        limit: Optional[int] = None,
        pages: Optional[list[int]] = None,
        safety: bool = False,
    ) -> list[int]:
        """
        Resolve the list of page numbers to collect based on the provided limit and pages parameters.

        Parameters
        ----------
        limit : int, optional
            Maximum number of items to retrieve.
        pages : list of int, optional
            List of page numbers to retrieve. If None, retrieves all pages.
        safety : bool, default True
            If True, raises an error if dry_run() or preview() has not been run to check total pages and counts before collecting.

        Returns
        -------
        list of int
            A list of page numbers to collect based on the provided parameters.
        """

        # not allow to run this without preview/plan first?
        if self.qs.count is None:
            if safety:
                raise AssertionError(
                    "Total items is unknown. Please run .dry_run() or .preview() or .explain() before collecting metadata."
                )
            else:
                logging.debug(
                    "Total items is unknown (no dry run) running set_counts() to retrieve count."
                )
                self.set_counts()

        _upper_limits = min(
            ITEMS_LIMIT,
            self.qs.count,
        )

        if limit is not None:
            # check if int and over zero
            validate_gt_int(limit)
            # cap limit to upper limits
            limit = min(limit, _upper_limits)

        logging.debug(
            f"Resolved limit for collection: {limit} (upper limits: {PAGES_LIMIT} pages or {ITEMS_LIMIT} items)"
        )

        # prep page nums
        if isinstance(pages, list):
            resolved = deepcopy(pages)
        elif pages is None:
            # init all pages if not provided
            resolved = list(range(1, self.qs.num_requests + 1))
        else:
            raise TypeError("pages must be a list of integers or None")

        # keep only valid page numbers
        resolved = [
            p for p in resolved if isinstance(p, int) and 0 < p <= self.qs.num_requests
        ]

        # limits
        max_num_pages = ceil(
            limit
            / self.qs.params.get("page_size", self.qs.emgapi_handler.default_page_size)
        )
        max_num_pages = min(max_num_pages, PAGES_LIMIT, self.qs.num_requests)
        logging.debug(
            f"Calculated max number of pages to collect based on limit: {max_num_pages}"
        )
        # filter out pages that are over the max
        resolved = [p for p in resolved if p <= max_num_pages]

        return resolved

    def _collect_pages(
        self,
        client: Client,
        limit: Optional[int] = None,
        pages: Optional[list[int]] = None,
        safety: bool = False,
        hide_progress: bool = False,
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

        collect_pages = self._resolve_pages_to_collect(
            limit=limit, pages=pages, safety=safety
        )

        # get pages if not in results already
        a_client = client or self._init_client()
        for p in tqdm(collect_pages, desc="Retrieving pages", disable=hide_progress):
            # skip if page already retrieved
            if self.qs._is_in_results(p):
                logging.info(f"Page {p} already retrieved, skipping...")
            else:
                self.page(p, client=a_client)

    async def _acollect_pages(
        self,
        client: Client,
        limit: Optional[int] = None,
        pages: Optional[list[int]] = None,
        safety: bool = False,
        hide_progress: bool = False,
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
        safety : bool, default True
            If True, raises an error if dry_run() or preview() has not been run.
        """

        collect_pages = self._resolve_pages_to_collect(
            limit=limit, pages=pages, safety=safety
        )

        # creating async tasks
        tasks = [asyncio.create_task(self.apage(p, client)) for p in collect_pages]

        for done in tqdm_asyncio.as_completed(tasks):
            await done

    def bulk_fetch(
        self,
        limit: Optional[int] = None,
        *,
        pages: Optional[list[int]] = None,
        safety: bool = False,
        hide_progress: bool = False,
    ):
        """Getting all to an extent"""
        with self._init_client() as client:
            self._collect_pages(
                client,
                limit=limit,
                pages=pages,
                safety=safety,
                hide_progress=hide_progress,
            )

    async def abulk_fetch(
        self,
        limit: Optional[int] = None,
        *,
        pages: Optional[list[int]] = None,
        safety: bool = False,
        hide_progress: bool = False,
    ):
        """Getting all-ish asynchronously"""
        async with self._init_client() as client:
            await self._acollect_pages(
                client,
                limit=limit,
                pages=pages,
                safety=safety,
                hide_progress=hide_progress,
            )

    def __getattr__(self, name: str):
        if name == "httpx_client":
            return self._init_client().get_httpx_client()
        if name == "httpx_aclient":
            return self._init_client().get_async_httpx_client()
        if name == "api_version":
            print(self.config.api_version)
