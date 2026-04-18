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

from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy._shared_helpers.pydantic_help import validate_gt_int
from mgnipy.emgapi_v2_client import Client
from mgnipy.emgapi_v2_client.types import Response as mpy_Response

if TYPE_CHECKING:
    from mgnipy.V2.core import MGnifier


class QueryExecutor:
    def __init__(self, owner: "MGnifier"):
        self.owner = owner
        # question: should this be shared across all instances of QueryExecutor or should each have their own?
        # i meant for this to be a concurrency limiter to protect the server -- did I get this right?
        self._semaphore = get_semaphore()

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
            return await self.owner.endpoint_module.asyncio_detailed(
                client=client,
                **(request_params or self.owner._params),
            )

    async def map_with_concurrency(
        self,
        items,
        worker,
        *,
        concurrency: Optional[int] = None,
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
            concurrency=8,
        )
        """
        # get semaphore for concurrency
        semaphore = concurrency or self._semaphore

        # helper to run worker with semaphore
        async def _run_one(i, item):
            async with semaphore:
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

    def _init_client(self) -> Client:
        """
        Initialize and return a MGnify API client instance.

        Returns
        -------
        Client
            Configured MGnify API client.
        """
        return Client(
            base_url=str(self.owner._base_url),
            # TODO logs?
        )

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
        request_params = {**(params or self.owner._params), **kwargs}
        if self.owner._pagination_status and "page_size" not in request_params:
            request_params["page_size"] = self.owner._default_page_size
        return request_params

    def _parse_response(self, response: mpy_Response) -> Optional[dict[str, Any]]:
        logging.info(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            return response.parsed.to_dict()
        return None

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
        request_params = self._build_request_params(params, **kwargs)
        # request
        response = self.owner.endpoint_module.sync_detailed(
            client=a_client,
            **request_params,
        )
        return self._parse_response(response)

    async def _aget_request(
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
        request_params = self._build_request_params(params, **kwargs)
        # request
        response = await self._semaphore_guarded_request(
            client=a_client,
            **request_params,
        )
        return self._parse_response(response)

    def get_pageinated_counts(self):
        """
        Make a small get request with page_size=1 to determine if the endpoint is paginated and to get the total count of records.
        """

        # small get request to get count and calc total pages
        response_dict = self._get_request(page_size=1)
        self.owner._count = response_dict["count"]
        self.owner._total_pages = ceil(
            self.owner._count
            / self.owner._params.get("page_size", self.owner._default_page_size)
        )

    def get_any_first(self):
        """
        Retrieve the first page of metadata for the current resource and parameters.

        For unpaginated endpoints, this will retrieve all metadata which is just one. For paginated endpoints, this will retrieve just the first page of results.
        """

        # already retrieved?
        if self.owner._is_in_results(1):
            logging.info("First response already retrieved, using cached results.")
        # if not paginated
        elif not self.owner._pagination_status:
            # then just get and add to results
            response_dict = self._get_request()
            self.owner._results.update({1: response_dict})
        # otherwise, get first page
        else:
            self.page(1)

    async def aget_any_first(self):
        """
        Asynchronously retrieve the first page of metadata for the current resource and parameters.

        For unpaginated endpoints, this will retrieve all metadata which is just one. For paginated endpoints, this will retrieve just the first page of results.
        """

        if self.owner._is_in_results(1):
            logging.info("First response already retrieved, using cached results.")
        elif not self.owner._pagination_status:
            response_dict = await self._aget_request()
            self.owner._results.update({1: response_dict})
        else:
            await self.apage(1)

    def _page_items(self, response: mpy_Response) -> Optional[dict]:
        """
        Extract the 'items' from the API response.
        """
        if response is None:
            logging.warning("No response received from API.")
            return None
        return response.get("items", None)

    # getting specific page
    # @require_pagination
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
        if self.owner._is_in_results(page_num):
            logging.info(f"Page {page_num} already retrieved.")
            return self.owner._results.get(page_num, None)

        # otherwise get page
        a_client = client or self._init_client()
        response = self._get_request(
            client=a_client,
            page=page_num,
        )
        # get out items
        page_items = self._page_items(response)
        # add to results
        self.owner._results.update({page_num: page_items})
        return page_items

    # @require_pagination
    async def apage(
        self,
        page_num: int,
        client: Optional[Client] = None,
    ) -> Optional[dict[int, list[dict]]]:
        if self.owner._is_in_results(page_num):
            logging.info(f"Page {page_num} already retrieved.")
            return self.owner._results.get(page_num, None)

        a_client = client or self._init_client()
        response = await self._aget_request(client=a_client, page=page_num)
        page_items = self._page_items(response)
        self.owner._results.update({page_num: page_items})
        return page_items

    def _resolve_pages_to_collect(
        self,
        *,
        limit: Optional[int] = None,
        pages: Optional[list[int]] = None,
        safety: bool = True,
    ) -> list[int]:
        """
        Resolve the list of page numbers to collect based on the provided limit and pages parameters.

        Parameters
        ----------
        limit : int, optional
            Maximum number of records to retrieve. If None, retrieves all records.
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
        if safety and self.owner._total_pages is None:
            raise AssertionError(
                "Please run .dry_run() or .preview() or .explain()before deciding to collect metadata."
            )

        # prep page nums
        if isinstance(pages, list):
            resolved = deepcopy(pages)
        elif pages is None:
            # init all pages if not provided
            resolved = list(range(1, self.owner._total_pages + 1))
        else:
            raise TypeError("pages must be a list of integers or None")

        # keep only valid page numbers
        resolved = [
            p
            for p in resolved
            if isinstance(p, int) and 0 < p <= self.owner._total_pages
        ]

        if limit is not None:
            # limit to number of records/items
            # LIMITATION: since paginated cannot retrieve exact num sometimes
            # check if int and over zero
            validate_gt_int(limit)
            max_num_pages = ceil(
                limit
                / self.owner._params.get("page_size", self.owner._default_page_size)
            )
            # filter out pages that are over the max
            resolved = [p for p in resolved if p <= max_num_pages]

        return resolved

    # @require_pagination
    def _collect_pages(
        self,
        client: Client,
        limit: Optional[int] = None,
        pages: Optional[list[int]] = None,
        safety: bool = True,
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
            if self.owner._is_in_results(p):
                logging.info(f"Page {p} already retrieved, skipping...")
            else:
                self.page(p, client=a_client)

    # @require_pagination
    async def _acollect_pages(
        self,
        client: Client,
        limit: Optional[int] = None,
        pages: Optional[list[int]] = None,
        safety: bool = True,
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

        for task in tqdm(
            asyncio.as_completed(tasks),
            total=len(tasks),
            desc="Retrieving pages",
            disable=hide_progress,
        ):
            await task

    def get(
        self,
        limit: Optional[int] = None,
        *,
        pages: Optional[list[int]] = None,
        safety: bool = True,
        hide_progress: bool = False,
    ):
        """Getting all"""
        if not self.owner._pagination_status:
            self.get_any_first()
            return

        with self._init_client() as client:
            self._collect_pages(
                client,
                limit=limit,
                pages=pages,
                safety=safety,
                hide_progress=hide_progress,
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
        if not self.owner._pagination_status:
            await self.aget_any_first()
            return

        async with self._init_client() as client:
            await self._acollect_pages(
                client,
                limit=limit,
                pages=pages,
                safety=safety,
                hide_progress=hide_progress,
            )
