import asyncio
import logging
from pathlib import Path

from mgnipy.V2.metadata import MGnifyMetadata
from mgnipy._shared_helpers.httpx_helpers import init_httpx_client
from mgnipy.emgapi_v2_client.client import AuthenticatedClient, Client

logger = logging.getLogger(__name__)
from typing import Any, Optional

import pandas as pd

from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from mgnipy._models.config import MGnipyConfig, to_mgnipy_config
from mgnipy._models.constants.CONSTANTS import ResourceStr
from mgnipy.V2.endpoints import ALL_SUPPORTED_RELATIONSHIPS
from mgnipy.V2.mixins import DiskCheckpointer
from mgnipy.V2.query_executor import QueryExecutor
from mgnipy.V2.query_set import QuerySet


class MGnifier(QuerySet):
    """
    MGnifier is a class that provides an interface for querying the MGnify API.
    It allows users to specify a resource and query parameters, and then fetch results in a paginated manner.
    The class also includes methods for fetching specific pages, performing bulk fetches, and planning API calls with a dry run.

    Parameters
    ----------
    resource : str
        The MGnify resource to query (e.g., "studies", "samples").
    config : MGnipyConfig or dict, optional
        Configuration for MGnipy, either as an MGnipyConfig instance or a dictionary of configuration parameters (default is None).
    params : dict, optional
        Query filter parameters (default is None).
    **param_kwargs
        Additional parameters treated as query filters.

    Attributes
    ----------
    TODO
    """

    def __init__(
        self,
        resource: ResourceStr,
        *,
        config: Optional[MGnipyConfig | dict] = None,
        params: Optional[dict[str, Any]] = None,
        httpx_client: Optional[Client | AuthenticatedClient] = None,
        interactive_auth: bool = False,
        **param_kwargs,
    ) -> None:
        """Initialize a query for a given MGnify resource.

        Parameters
        ----------
        resource : str
            Name of the MGnify resource to query (e.g., "studies", "samples").
        config : dict, optional
            Configuration dictionary for authentication and base URL.
        params : dict, optional
            Query filter parameters.
        **param_kwargs
            Additional parameters treated as query filters.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier
        >>> query = MGnifier("studies")
        """

        # init query set
        super().__init__(
            resource=resource,
            config=to_mgnipy_config(config),
            params=params,
            **param_kwargs,
        )

        self.httpx_client = httpx_client or init_httpx_client(self.config)

        # init executor with client
        self.exec = QueryExecutor(self, self.httpx_client)

        # and iter
        self.reset_iterator()

        # configuration and auth init
        self.config: MGnipyConfig = to_mgnipy_config(config)
        # PICK UP HERE
        self.config.resolve_auth_token(interactive=interactive_auth)

        # cache handler
        logger.debug(f"Creating cache handler for {self._resource.value}")
        self.cache_handler = DiskCheckpointer(
            params_getter=lambda: self.params,
            resource_str=self.resource.value,
            config=self.config,
            results_store=self._results,
        )
        # load cache
        # self.load_cache()

    @QuerySet.count.setter
    def count(self, value: int):
        self._count = value
        logger.debug(f"Set count to {value}")
        # to the disk too
        self.cache_handler._total_records = self._count

    @QuerySet.num_requests.setter
    def num_requests(self, value: int):
        self._num_requests = value
        logger.debug(f"Set num_requests to {value}")
        # to the disk too
        self.cache_handler._total_requests = self._num_requests

    @property
    def progress(self):
        completed = len(self.metadata.pages)
        total = len(self.queries().keys())
        percent = completed / total if total > 0 else 0
        # dummy bar for fun
        bar_length = 20
        filled = int(bar_length * percent)
        bar = "█" * filled + "░" * (bar_length - filled)

        progress_str = f"Retrieved pages: {percent:.0%}|{bar}| {completed}/{total}"
        print(progress_str)

    @property
    def metadata(self) -> MGnifyMetadata:
        """Get the retrieved metadata results, if available.

        Returns
        -------
        MGnifyMetadata
            An object containing the retrieved metadata results and related methods.
        """
        return MGnifyMetadata(results=self._results, id_label=self._id_label)

    @property
    def cache_dir(self) -> Optional[Path]:
        return self.cache_handler._cache_dir

    def load_cache(self):
        # try to load from cache
        try:
            # results
            self._pages_from_cache = self.cache_handler.load_cache_results()
            logger.info(
                f"Loaded pages {self._pages_from_cache} from cache for resource {self.resource.value}"
            )
            # if cache results loaded, update
            if self._pages_from_cache:
                self._results = self.cache_handler._results
            # manifest
            self._cached_manifest = self.cache_handler.load_cache_manifest()
            # update
            self.count = self._cached_manifest.get("count", None)
            self.num_requests = self._cached_manifest.get("total_pages", None)
        except Exception as e:
            logger.warning(f"Failed to load from cache: {e}")
            self._pages_from_cache = []
            self._cached_manifest = {}

    def clear_cache(self):
        """
        Clear the cached results for the current resource and parameters.
        This will delete any cached files associated with the current query parameters.
        """
        logger.warning(f"Clearing cache for {self.resource.value} at {self.cache_dir}")
        self.cache_handler.clear_cache()
        # reset loaded cache state
        self._pages_from_cache = []
        self._cached_manifest = {}

    def _leftover_pages(self) -> list[int]:

        # ensure counts/pages are known
        self.exec._set_counts()
        # compute pages we still need to fetch
        return [x for x in self.queries() if x not in self.metadata.pages]

    def _init_iter_state(self):
        # stable order + iterator state
        self._iter_page_nums = list(
            self.queries().keys()
        )  # sorted(self._leftover_pages())
        self._iter_index = 0

    def __iter__(self):
        """
        Initialize and return a synchronous iterator over pages.
        """
        self._init_iter_state()
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
        # if no pages loaded, load with limits to next batch
        if not self._iter_page_nums:
            self._init_iter_state()
            logger.debug(
                f"No pages loaded yet, initialized iterator with pages: {self._iter_page_nums}"
            )
        # check if we have exhausted the loaded pages
        if self._iter_index >= len(self._iter_page_nums):
            raise StopIteration
        # get next page num and advance index
        page_num = self._iter_page_nums[self._iter_index]
        logger.debug(f"Advancing to request num {page_num}")
        self._iter_index += 1
        try:
            result = self.page(page_num)
            return result
        except Exception as e:
            logger.error(f"Error fetching request num {page_num}: {e}")
            raise

    def __aiter__(self):
        """Initialize and return an asynchronous iterator over pages.

        Example
        -------
        >>> # Async iteration pattern (doctest skipped)
        >>> async for page in QueryExecutor(qs):  # doctest: +SKIP
        ...     pass
        """
        self._init_iter_state()
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
        if not self._iter_page_nums:
            self._init_iter_state()
        if self._iter_index >= len(self._iter_page_nums):
            raise StopAsyncIteration
        p = self._iter_page_nums[self._iter_index]
        logger.debug(f"Advancing to request num {p} (async)")
        self._iter_index += 1
        try:
            result = await self.apage(p)
            return result
        except Exception as e:
            logger.error(f"Error fetching request num {p}: {e}")
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

    def page(self, page_num: int, client: Optional[Client] = None):
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
        >>> from mgnipy import MGnifier  # doctest: +SKIP
        >>> studies = MGnifier("studies")  # doctest: +SKIP
        >>> page_data = studies.page(1)  # doctest: +SKIP
        """

        logger.debug(f"Fetching page {page_num} for resource {self.resource.value}")
        page_items = self.exec.request_page(
            page_num=page_num,
            client=client,
        )
        logger.debug(f"page_items type {type(page_items)}")

        # checkpoint each page
        try:
            self.cache_handler.write_results(page_num, page_items)
        except Exception:
            logger.exception(f"Failed to checkpoint page {page_num}")
        return page_items

    async def apage(
        self,
        page_num: int,
        client: Optional[Client] = None,
    ) -> Optional[dict[int, list[dict]]]:
        """
        Asynchronously fetch a specific page or range of pages.

        Parameters
        ----------
        page_num : int
            The page number to retrieve (1-based index).
        client : Client, optional
            An optional MGnify API client instance to use for the request.
            If None, a new client will be initialized.

        Returns
        -------
        dict
            The requested page(s) of results.

        Examples
        --------
        >>> from mgnipy import MGnifier  # doctest: +SKIP
        >>> studies = MGnifier("studies")  # doctest: +SKIP
        >>> import asyncio  # doctest: +SKIP
        >>> page_data = asyncio.run(studies.apage(1))  # doctest: +SKIP
        """

        logger.info(
            f"Asynchronously fetching page {page_num} for resource {self.resource.value}"
        )

        page_items = await self.exec.arequest_page(
            page_num=page_num,
            client=client,
        )

        # checkpoint
        try:
            await self.cache_handler.awrite_results(page_num, page_items)
        except Exception:
            logger.exception(f"Failed to checkpoint page {page_num}")
        return page_items

    def bulk_fetch(
        self,
        limit: Optional[int] = 200,
        *,
        pages: Optional[list[int]] = None,
        client: Optional[Client] = None,
        hide_progress: bool = False,
    ):
        """
        Collect metadata for all (or selected) pages and store results to self.results.

        Parameters
        ----------
        client : Client
            MGnify API client instance.
        limit : int, optional
            Maximum number of pages to retrieve. If None, retrieves all pages (default is 200).
        pages : list of int, optional
            List of page numbers to retrieve. If None, retrieves all pages.
        safety : bool, default True
            If True, raises an error if dry_run() or preview()
            has not been run to check total pages and counts before collecting.
        from_page : int, default 0
            The page number to start collecting from.
        """

        if pages is None:
            pages = self._leftover_pages()

        # get pages if not in results already
        a_client = client or self.exec._init_client()
        for p in tqdm(
            pages[:limit],
            total=len(self.queries()),
            initial=len(self.metadata.pages),
            desc=f"Retrieving {self.resource} pages",
            disable=hide_progress,
        ):
            logger.debug(f"Advancing to request num {p}")
            self.page(p, client=a_client)
        return self

    async def abulk_fetch(
        self,
        limit: Optional[int] = 200,
        *,
        pages: Optional[list[int]] = None,
        client: Optional[Client] = None,
        hide_progress: bool = False,
    ):
        """
        Asynchronously collect metadata for all (or selected) pages and store results to self.results.

        Parameters
        ----------
        client : Client
            MGnify API client instance.
        limit : int, optional
            Maximum number of pages to retrieve. If None, retrieves all pages (default is 200).
        pages : list of int, optional
            List of page numbers to retrieve. If None, retrieves all pages.

        """
        if pages is None:
            pages = self._leftover_pages()

        # create tasks
        a_client = client or self.exec._init_client()

        tasks = [asyncio.create_task(self.apage(p, a_client)) for p in pages[:limit]]

        # run with progress bar
        for done in tqdm_asyncio.as_completed(
            tasks,
            total=len(self.queries()),
            initial=len(self.metadata.pages),
            desc=f"(async)Retrieving {self.resource} pages",
            disable=hide_progress,
        ):
            await done
        return self

    def dry_run(self) -> None:
        """
        Plan the API call by validating parameters and estimating the number of pages and records available.
        Prints the plan details for the user to review before executing the full data retrieval.
        This method can be called before get() to ensure that the parameters are valid and to understand the scope of the data retrieval.

        Returns
        -------
        None

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies", params={"search": "gut"})  # doctest: +SKIP
        >>> query.dry_run()  # doctest: +SKIP
        """
        print("Planning the API call with params:")
        print(self.params)

        self.exec._set_counts()

        print(f"Total requests to make: {self.num_requests}")
        print(f"Total records to retrieve: {self.count}")

    def explain(self, head: Optional[int] = None) -> None:
        """Print example API URLs that would be called.

        Parameters
        ----------
        head : int, optional
            Maximum number of URLs to print. If ``None``, prints all.

        Returns
        -------
        None

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.explain(head=3)  # doctest: +SKIP
        """

        self.exec._set_counts()
        if self.num_requests is None or self.count is None:
            raise RuntimeError(
                "Cannot explain API calls because the number of requests could not be determined. Ensure that the endpoint is valid and that the count of items can be retrieved."
            )

        limit = head or self.num_requests

        for url in self.list_urls()[:limit]:
            print(url)

    def first(self) -> Optional[dict]:
        """Get the first record from the query results.

        Executes the query and returns the first metadata record.

        Returns
        -------
        dict or None
            The first record as a dictionary, or ``None`` if unavailable.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> first_record = query.first()  # doctest: +SKIP
        """
        if self._is_in_results(1):
            logger.debug("First page already in results, using cached results")
        else:
            logger.debug("First page not in results, fetching from API")
            _ = self.page(1)

        return self._results.get(1, [])

    def preview(self) -> pd.DataFrame:
        """Get a DataFrame preview of the first page of results.

        Quickly check the structure and content of the data without
        retrieving all pages.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the first page of metadata.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> df = query.preview()  # doctest: +SKIP
        """

        first = self.first()
        return self.metadata.to_pandas(first)

    def list_supported_params(self) -> list[str]:
        """Get the valid query filter parameters for this resource.

        Returns
        -------
        list[str]
            Supported parameter names.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> params = query.list_supported_params()  # doctest: +SKIP
        """
        return self.emgapi_handler.list_supported_params()

    def describe_endpoint(self, **kwargs) -> dict[str, str] | None:
        """Retrieve documentation about the endpoint.

        Returns
        -------
        dict[str, str] or None
            Endpoint documentation, or ``None`` if unavailable.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> docs = query.describe_endpoint()  # doctest: +SKIP
        """
        return self.emgapi_handler.describe_endpoint(**kwargs)

    def list_relationships(self) -> list[str]:
        """Get the names of related resources available from this resource.

        Returns
        -------
        list[str]
            Names of related resource types (e.g., ["samples", "analyses"]).

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> relationships = query.list_relationships()  # doctest: +SKIP
        """
        if self.resource in ALL_SUPPORTED_RELATIONSHIPS:
            return [
                endpoint.value
                for endpoint in ALL_SUPPORTED_RELATIONSHIPS[self.resource]
            ]
        else:
            return []

    def describe_relationships(self):
        """Describe the related resources and their relationships.

        Returns
        -------
        None

        Note
        ----
        This method is not yet implemented.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.describe_relationships()  # doctest: +SKIP
        """
        pass  # TODO

    def __str__(self) -> str:
        """Return a human-readable summary of the query state.

        Returns
        -------
        str
            Summary including resource, URL, parameters, and endpoint info.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> print(query)  # doctest: +SKIP
        """
        cls = type(self)
        class_path = f"{cls.__module__}.{cls.__qualname__}"
        return (
            f"MGnifier instance for resource: {self.resource}\n"
            f"I.e., {class_path}\n"
            f"----------------------------------------\n"
            f"Base URL: {self.base_url}\n"
            f"Parameters: {self.params}\n"
            f"Example request URL: {self._build_request_url()}\n"
            f"Endpoint module: {self.endpoint_module.__name__ or 'None'}\n"
            f"Is list endpoint (returns paginated results): {self.emgapi_handler.is_list_endpoint}\n"
            f"Cache directory: {self.cache_dir}\n"
        )

    def reset_iterator(self):
        """Reset the iterator to start from the beginning.

        Example
        -------
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor.reset_iterator()  # doctest: +SKIP
        """
        self._iter_page_nums = []
        self._iter_index = 0
