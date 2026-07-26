"""MGnifier: A class for querying the MGnify API with support for caching, pagination, and metadata retrieval."""

import asyncio
import logging
from pathlib import Path

from mgnipy.V2.mgnifier.metadata import MGnifyMetadata
from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy._shared_helpers.httpx_helpers import init_httpx_client
from mgnipy.emgapi_v2_client.client import AuthenticatedClient, Client

logger = logging.getLogger(__name__)
from typing import Any, Optional

import pandas as pd

from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from mgnipy._models.config import MGnipyConfig, to_mgnipy_config
from mgnipy._models.constants.CONSTANTS import ResourceStr
from mgnipy.V2.mgnifier.endpoints import ALL_SUPPORTED_RELATIONSHIPS
from mgnipy.V2.mixins import CheckpointMixin, ClientManagerMixin
from mgnipy.V2.mgnifier.query_executor import QueryExecutor
from mgnipy.V2.mgnifier.query_set import QuerySet


class MGnifier(QuerySet, CheckpointMixin, ClientManagerMixin):
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
    client : Client or AuthenticatedClient, optional
        An optional MGnify API client instance to use for requests (default is None).
    resolve_auth : bool, optional
        Whether to resolve authentication using the provided config (default is True).
    interactive_auth : bool, optional
        Whether to prompt for authentication interactively if needed (default is False).
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
        client: Optional[Client | AuthenticatedClient] = None,
        resolve_auth: bool = True,
        interactive_auth: bool = False,
        semaphore: Optional[asyncio.Semaphore] = None,
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
        client : Client or AuthenticatedClient, optional
            An optional MGnify API client instance to use for requests (default is None).
        resolve_auth : bool, optional
            Whether to resolve authentication using the provided config (default is True).
        interactive_auth : bool, optional
            Whether to prompt for authentication interactively if needed (default is False).
        **param_kwargs
            Additional parameters treated as query filters.

        Examples
        --------
        >>> from mgnipy.V2.mgnifier import MGnifier
        >>> query = MGnifier("studies")
        """

        # init query set
        super().__init__(
            resource=resource,
            config=to_mgnipy_config(config),
            params=params,
            **param_kwargs,
        )
        # and iter
        self.reset_iterator()

        # configuration and auth (overwrites from queryset)
        self.config: MGnipyConfig = to_mgnipy_config(config)
        self.resolve_auth = resolve_auth
        self.interactive_auth = interactive_auth

        if self.resolve_auth:
            self.config.resolve_auth_token(interactive=self.interactive_auth)

        # init executor
        if client is None:
            # create our own client and mark ownership
            self.client = init_httpx_client(self.config)
            self._owns_client = True
        else:
            # client was provided (e.g., from MGnipy); default to borrowed
            self.client = client
            self._owns_client = False
            logger.info(f"client from mgnipy:{self._owns_client}")

        self.semaphore = semaphore or get_semaphore()
        # init executor with client
        self.exec = QueryExecutor(self, self.client)

    def _clone(self, **param_overrides):
        """
        Provides a way to create a new instance of MGnifier with the same configuration and parameters, but with the ability to override specific parameters. Overwrites QuerySet._clone().

        Parameters
        ----------
        **param_overrides
            Keyword arguments representing the parameters to override in the new instance.
            These will be merged with the existing parameters, with the provided overrides taking precedence.

        Returns
        -------
        MGnifier
            A new instance of the same class with the updated parameters.
        """
        logger.info(
            f"Cloning MGnifier with overrides: {sorted(param_overrides.keys())}",
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
            client=self.client,
            resolve_auth=self.resolve_auth,
            interactive_auth=self.interactive_auth,
            semaphore=self.semaphore,
        )
        new_qs.endpoint_module = self.endpoint_module

        return new_qs

    @property
    def progress(self) -> None:
        """
        Display the progress of the current query set.
        """
        self.try_load_cache()

        completed: int = len(self.metadata.pages)
        total: int = len(self.build_queries().keys())
        percent: float = completed / total if total > 0 else 0
        # dummy bar for fun
        bar_length: int = 20
        filled: int = int(bar_length * percent)
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
        self.try_load_cache()
        return MGnifyMetadata(results=self._results, id_label=self._id_label)

    @property
    def cache_dir(self) -> Optional[Path]:
        return self.cache_path

    def get(self):
        """Alternative to getting the next page of results.

        Returns
        -------
        The next page dict or ``None`` when iteration is complete.

        Example
        -------
        mg = MGnifier("studies")  # doctest: +SKIP
        next_page = mg.get()  # doctest: +SKIP
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
        mg = MGnifier("studies")  # doctest: +SKIP
        next_page = await mg.aget()  # doctest: +SKIP
        """
        try:
            return await self.__anext__()
        except StopAsyncIteration:
            return None

    def __next__(self):
        """
        Retrieve the next page of results in synchronous iteration.

        Example
        -------
        # Get next page
        mg = MGnifier("studies")  # doctest: +SKIP
        next_page = next(mg)  # doctest: +SKIP
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

        # otherwise, get next page num and advance index
        page_num = self._iter_page_nums[self._iter_index]
        logger.debug(f"Advancing to request num {page_num}")
        self._iter_index += 1
        try:
            result = self.page(page_num)
            return result
        except Exception as e:
            logger.error(f"Error fetching request num {page_num}: {e}")
            raise

    async def __anext__(self):
        """
        Retrieve the next page of results in asynchronous iteration.

        Example
        -------
        # Get next page
        mg = MGnifier("studies")  # doctest: +SKIP
        next_page = await next(mg)  # doctest: +SKIP
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

    def page(self, page_num: int):
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
        mg = MGnifier("studies")  # doctest: +SKIP
        page_data = mg.page(1)  # doctest: +SKIP
        """
        self.try_load_cache()
        logger.debug(f"Fetching page {page_num}")
        page_items = self.exec.request_page(page_num=page_num)

        # checkpoint each page
        try:
            self.write_results(page_num, page_items)
        except Exception:
            logger.exception(f"Failed to checkpoint page {page_num}")
        return page_items

    async def apage(self, page_num: int) -> Optional[dict[int, list[dict]]]:
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
        mg = MGnifier("studies")  # doctest: +SKIP
        page_data = asyncio.run(mg.apage(1))  # doctest: +SKIP
        """
        self.try_load_cache()
        logger.info(f"Asynchronously fetching page {page_num}")

        async with self.semaphore:
            page_items = await self.exec.arequest_page(page_num=page_num)

        # checkpoint
        try:
            await self.awrite_results(page_num, page_items)
        except Exception:
            logger.exception(f"Failed to checkpoint page {page_num}")
        return page_items

    def reset_iterator(self):
        """Reset the iterator to start from the beginning.

        Example
        -------
        >>> executor = QueryExecutor(qs)  # doctest: +SKIP
        >>> executor.reset_iterator()  # doctest: +SKIP
        """
        self._iter_page_nums = []
        self._iter_index = 0

    def __iter__(self):
        """
        Initialize and return a synchronous iterator over pages.
        """
        self._init_iter_state()
        return self

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

    def _init_iter_state(self):
        """
        Initialize the iterator state for synchronous and asynchronous iteration.
        This method sets up the list of page numbers to iterate over and resets the index for iteration
        to the beginning. It is called at the start of both synchronous and asynchronous iteration.
        """
        # stable order + iterator state
        self._iter_page_nums = list(
            self.build_queries().keys()
        )  # sorted(self._leftover_pages())
        self._iter_index = 0

    def _leftover_pages(self) -> list[int]:
        """Compute the list of pages that have not yet been retrieved."""
        # ensure counts/pages are known
        self.try_load_cache()
        self.exec._set_counts()
        # compute pages we still need to fetch
        return [x for x in self.build_queries() if x not in self.metadata.pages]

    def bulk_fetch(
        self,
        limit: Optional[int] = 200,
        *,
        pages: Optional[list[int]] = None,
        hide_progress: bool = False,
    ):
        """
        Collect metadata for all (or selected) pages and store results to self.results.

        Parameters
        ----------
        limit : int, optional
            Maximum number of pages to retrieve. If None, retrieves all pages (default is 200).
        pages : list of int, optional
            List of page numbers to retrieve. If None, retrieves all pages.
        hide_progress : bool, optional
            Whether to hide the progress bar during retrieval (default is False).
        """

        if pages is None:
            pages = self._leftover_pages()

        # get pages if not in results already w/progressbar
        for p in tqdm(
            iterable=pages[:limit],
            total=len(self.build_queries()),
            initial=len(self.metadata.pages),
            desc=f"Retrieving {self.resource} pages",
            disable=hide_progress,
        ):
            logger.debug(f"Advancing to request num {p}")
            # fetch page and store
            self.page(p)

        return self

    async def abulk_fetch(
        self,
        limit: Optional[int] = 200,
        *,
        pages: Optional[list[int]] = None,
        hide_progress: bool = False,
    ):
        """
        Asynchronously collect metadata for all (or selected) pages and store results to self.results.

        Parameters
        ----------
        limit : int, optional
            Maximum number of pages to retrieve. If None, retrieves all pages (default is 200).
        pages : list of int, optional
            List of page numbers to retrieve. If None, retrieves all pages.
        hide_progress : bool, optional
            Whether to hide the progress bar during retrieval (default is False).

        """
        if pages is None:
            pages = self._leftover_pages()

        # create tasks
        tasks = [asyncio.create_task(self.apage(p)) for p in pages[:limit]]

        # run with progress bar
        for done in tqdm_asyncio.as_completed(
            tasks,
            total=len(self.build_queries()),
            initial=len(self.metadata.pages),
            desc=f"(async)Retrieving {self.resource} pages",
            disable=hide_progress,
        ):
            logger.debug(f"Page retrieval completed: {done}")
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
        >>> from mgnipy.V2.mgnifier import MGnifier  # doctest: +SKIP
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
        >>> from mgnipy.V2.mgnifier import MGnifier  # doctest: +SKIP
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
        >>> from mgnipy.V2.mgnifier import MGnifier  # doctest: +SKIP
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
        >>> from mgnipy.V2.mgnifier import MGnifier  # doctest: +SKIP
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
        >>> from mgnipy.V2.mgnifier import MGnifier  # doctest: +SKIP
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
        >>> from mgnipy.V2.mgnifier import MGnifier  # doctest: +SKIP
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
        >>> from mgnipy.V2.mgnifier import MGnifier  # doctest: +SKIP
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
        >>> from mgnipy.V2.mgnifier import MGnifier  # doctest: +SKIP
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
        >>> from mgnipy.V2.mgnifier import MGnifier  # doctest: +SKIP
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
