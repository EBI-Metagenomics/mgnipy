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
        # tracking
        self._last_successful_page = None
        self.reset_iterator()

    def query_setups(
        self, request_num: Optional[int] = None, **httpx_kwargs
    ) -> dict[dict[str, Any]]:
        if request_num is None:
            return self.qs.queries(**httpx_kwargs)
        return self.qs.queries(**httpx_kwargs).get(request_num, None)

    def _init_iter_state(self, asyncio: bool = False) -> None:
        """
        Setup internal state for iteration or async iteration.

        Examples
        --------
        >>> # Initialize iterator state for sync iteration
        >>> executor._init_iter_state(asyncio=False)  # doctest: +SKIP
        >>> # Initialize for async iteration
        >>> executor._init_iter_state(asyncio=True)  # doctest: +SKIP
        """
        self.set_counts()
        limited_pages = self._resolve_pages_to_collect(limit=ITEMS_LIMIT, safety=False)
        if asyncio:
            self._aiter_page_nums = limited_pages
            self._aiter_index = 0
        else:
            self._iter_page_nums = limited_pages
            self._iter_index = 0

    def __iter__(self):
        """Initialize and return a synchronous iterator over pages.

        Example
        -------
        >>> # Iterate pages synchronously (network calls skipped in doctest)
        >>> for page in QueryExecutor(qs):  # doctest: +SKIP
        ...     pass
        """
        self._init_iter_state(asyncio=False)
        return self

    def __next__(self):
        """
        Retrieve the next page of results in synchronous iteration.

        Example
        -------
        >>> # Get next page via iterator
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> next(executor)  # doctest: +SKIP
        """
        if not self._iter_page_nums:
            self._init_iter_state(asyncio=False)
        if self._iter_index >= len(self._iter_page_nums):
            raise StopIteration
        page_num = self._iter_page_nums[self._iter_index]
        self._iter_index += 1
        try:
            result = self.page(page_num)
            # mark success
            self._last_successful_page = page_num
            return result
        except Exception as e:
            logging.error(f"Error fetching page {page_num}: {e}")
            raise

    def get(self):
        """Alternative to getting the next page of results.

        Returns
        -------
        The next page dict or ``None`` when iteration is complete.

        Example
        -------
        >>> # Fetch next page via helper (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor.get()  # doctest: +SKIP
        """
        try:
            return next(self)
        except StopIteration:
            return None

    def __aiter__(self):
        """Initialize and return an asynchronous iterator over pages.

        Example
        -------
        >>> # Async iteration pattern (doctest skipped)
        >>> async for page in QueryExecutor(qs):  # doctest: +SKIP
        ...     pass
        """
        self._init_iter_state(asyncio=True)
        return self

    async def __anext__(self):
        """
        Retrieve the next page of results in asynchronous iteration.

        Example
        -------
        >>> # Get next page via async iterator
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> asyncio.run(executor.__anext__())  # doctest: +SKIP
        """
        if not self._aiter_page_nums:
            self._init_iter_state(asyncio=True)
        if self._aiter_index >= len(self._aiter_page_nums):
            raise StopAsyncIteration
        p = self._aiter_page_nums[self._aiter_index]
        self._aiter_index += 1
        try:
            result = await self.apage(p)
            self._last_successful_page = p
            return result
        except Exception as e:
            logging.error(f"Error fetching page {p}: {e}")
            raise

    async def aget(self):
        """Async alternative to fetch the next page.

        Returns
        -------
        The next page dict or ``None`` when iteration is complete.

        Example
        -------
        >>> # Async fetch via helper (doctest skipped)
        >>> import asyncio
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> asyncio.run(executor.aget())  # doctest: +SKIP
        """
        try:
            return await self.__anext__()
        except StopAsyncIteration:
            return None

    def reset_iterator(self):
        """Reset the iterator to start from the beginning.

        Example
        -------
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor.reset_iterator()  # doctest: +SKIP
        """
        self._iter_page_nums = []
        self._iter_index = 0
        self._aiter_page_nums = []
        self._aiter_index = 0

    def continue_iterator(self, start_page: Optional[int] = None):
        """
        - Continue iterating from a given page or next batch after pages_limit
        - For resuming after hitting the page limit

        Parameters
        ----------
        start_page : int, optional
            The page number to start from.
            If None, starts from the next page after the current limit.

        Returns
        -------
        self
            Returns self for method chaining.

        Examples
        --------
        >>> # Continue from a specific page
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor.continue_iterator(start_page=50)  # doctest: +SKIP
        >>> # Continue from next batch after previous pages
        >>> executor.continue_iterator()  # doctest: +SKIP
        """
        # how many items and pages
        self.set_counts()
        # list pages
        all_page_nums = list(self.query_setups().keys())

        if start_page is None:
            # then cont from last batch
            start_page = max(self._iter_page_nums) + 1 if self._iter_page_nums else 1

        # Get remaining pages from start_page onwards
        remaining_pages = [p for p in all_page_nums if p >= start_page]

        # still limits to next batch
        limited_pages = self._resolve_pages_to_collect(
            limit=ITEMS_LIMIT, pages=remaining_pages, safety=False
        )

        # set
        self._iter_page_nums = limited_pages
        self._iter_index = 0
        logging.info(
            f"Continuing iteration from page {start_page}, "
            f"loaded {len(self._iter_page_nums)} pages"
        )
        return self

    def resume(self):
        """Resume iteration from the page after the last successful one.

        Example
        -------
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor.resume()  # doctest: +SKIP
        """
        if self._last_successful_page is None:
            logging.warning("No successful pages yet, so resuming from start")
            self.reset_iterator()
            return self

        # continuing from successful page
        next_page = self._last_successful_page + 1
        logging.info(f"Resuming from page {next_page}")
        return self.continue_iterator(start_page=next_page)

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

        Example
        -------
        >>> # Initialize an http client (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor._init_client()  # doctest: +SKIP
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

        Example
        -------
        >>> # Populate qs.count and qs.num_requests (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor.set_counts()  # doctest: +SKIP
        """
        if self.qs.count is not None and self.qs.num_requests is not None:
            logging.debug(
                f"Using cached count and num_requests vals: {self.qs.count}, {self.qs.num_requests}"
            )
        else:
            self.qs.count = self.qs.emgapi_handler.get_num_items(
                self._init_client(), params=self.qs.params
            )
            self.qs.num_requests = self.qs.emgapi_handler.get_num_pages(
                self.qs.count, page_size=self.qs.params.get("page_size", None)
            )

        if self.qs._results is None:
            self.qs._results = {}

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

        """Return the first page (cached or fetched).

        Example
        -------
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor.first()  # doctest: +SKIP
        """
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

        """Async variant returning the first page.

        Example
        -------
        >>> import asyncio
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> asyncio.run(executor.afirst())  # doctest: +SKIP
        """
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
        >>> # Map worker over pages with concurrency (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> pages = [1,2,3]  # doctest: +SKIP
        >>> results = await executor.map_with_concurrency(
        ...     items=pages,
        ...     worker=lambda p: executor.apage(p),
        ... )  # doctest: +SKIP
        """

        # Define a helper coroutine that wraps the worker with semaphore protection.
        # This ensures that at most `semaphore.value` workers run concurrently.
        # The index `i` is captured and returned so we can reconstruct order later.
        async def _run_one(i, item):
            # Acquire semaphore slot; block if all slots are taken.
            # This throttles concurrency to protect the server.
            async with self._semaphore:
                # Run the worker and return both the index and the result value.
                # The index is crucial for preserving order.
                return i, await worker(item)

        # Create all async tasks upfront (one per item).
        # enumerate() pairs each item with its original index (0, 1, 2, ...).
        # asyncio.create_task() schedules the coroutine; it starts running soon
        # but may not complete immediately (depends on semaphore availability).
        tasks = [asyncio.create_task(_run_one(i, item)) for i, item in enumerate(items)]

        # Preallocate a list to hold results in their original order.
        # Initialize with None so we can place results by index without knowing
        # which task will finish first. This is key to preserving order.
        ordered = [None] * len(tasks)

        # as_completed(tasks) yields tasks in completion order, NOT original order.
        # So tasks that finish fast are yielded first, regardless of their original index.
        # tqdm_asyncio wraps this to show a progress bar.
        for task in tqdm_asyncio.as_completed(
            tasks, disable=hide_progress, desc="Retrieving pages"
        ):
            # Unpack the tuple (i, value) returned by the completed task.
            # i = original index of this item
            # value = result from worker(item)
            i, value = await task

            # Place the result into its original position using the index.
            # Example: if item[5] finishes first, its result goes to ordered[5],
            # even though it's the first to complete.
            # This is why we get back results in original order despite as_completed().
            ordered[i] = value

        # Return results in their original order (same as input items order).
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
        """Extract the 'items' from the API response.

        Example
        -------
        >>> # Parse items from response dict
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor._page_items({'items': [1,2,3]})  # doctest: +SKIP
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

        Examples
        --------
        >>> # Fetch a single page (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor.page(1)  # doctest: +SKIP
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
        params = self.query_setups(page_num).get("params", None)
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
        """Async fetch for a single page.

        Example
        -------
        >>> import asyncio
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> asyncio.run(executor.apage(1))  # doctest: +SKIP
        """
        self.set_counts()
        if self.qs._is_in_results(page_num):
            logging.info(f"Page {page_num} already retrieved.")
            return self.qs._results.get(page_num, None)

        a_client = client or self._init_client()
        params = self.query_setups(page_num).get("params", None)
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

        Example
        -------
        >>> # Resolve pages to collect (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor._resolve_pages_to_collect(limit=10)  # doctest: +SKIP
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
        else:  # if no limit provided, just use upper limits
            limit = _upper_limits

        logging.debug(
            f"Resolved limit for collection: {limit} items (upper limits: {PAGES_LIMIT} pages or {ITEMS_LIMIT} items)"
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

        Example
        -------
        >>> # Collect pages (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> with executor._init_client() as client:  # doctest: +SKIP
        ...     executor._collect_pages(client, limit=10)  # doctest: +SKIP
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

        Example
        -------
        >>> # Async collect pages (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> async with executor._init_client() as client:  # doctest: +SKIP
        ...     await executor._acollect_pages(client, limit=10)  # doctest: +SKIP
        """

        collect_pages = self._resolve_pages_to_collect(
            limit=limit, pages=pages, safety=safety
        )

        # creating async tasks
        tasks = [asyncio.create_task(self.apage(p, client)) for p in collect_pages]

        for done in tqdm_asyncio.as_completed(
            tasks, disable=hide_progress, desc="Retrieving pages"
        ):
            await done

    def bulk_fetch(
        self,
        limit: Optional[int] = None,
        *,
        pages: Optional[list[int]] = None,
        safety: bool = False,
        hide_progress: bool = False,
    ):
        """Fetch pages in bulk synchronously.

        Example
        -------
        >>> # Bulk fetch usage (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor.bulk_fetch(limit=50)  # doctest: +SKIP
        """
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
        """Fetch pages in bulk asynchronously.

        Example
        -------
        >>> # Async bulk fetch (doctest skipped)
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> import asyncio
        >>> asyncio.run(executor.abulk_fetch(limit=50))  # doctest: +SKIP
        """
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
