import logging

logger = logging.getLogger(__name__)
from typing import Any, Literal, Optional

import pandas as pd

from mgnipy._models.config import MGnipyConfig, to_mgnipy_config
from mgnipy._models.constants.CONSTANTS import SupportedEndpoints
from mgnipy.V2.endpoints import ALL_SUPPORTED_RELATIONSHIPS
from mgnipy.V2.mixins import ResultsHandler
from mgnipy.V2.query_executor import QueryExecutor
from mgnipy.V2.query_set import QuerySet

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


class MGnifier(QuerySet, ResultsHandler):
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
            "publications",
            "publication",
            "catalogues",
            "catalogue",
        ],
        *,
        config: Optional[MGnipyConfig | dict] = None,
        params: Optional[dict[str, Any]] = None,
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
        QuerySet.__init__(
            self,
            resource=resource,
            config=to_mgnipy_config(config),
            params=params,
            **param_kwargs,
        )
        # init executor
        self.exec = QueryExecutor(self)

        # init result handler
        ResultsHandler.__init__(self)

    def __iter__(self):
        """Iterate over paginated results.

        Returns
        -------
        Iterator
            Iterator over result pages.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> for page in query:  # doctest: +SKIP
        ...     pass
        """
        return iter(self.exec)

    def __next__(self):
        """Fetch the next page of results.

        Returns
        -------
        dict
            The next page of results.
        """
        return next(self.exec)

    def __aiter__(self):
        """Return an async iterator for paginated results.

        Returns
        -------
        AsyncIterator
            Async iterator over result pages.
        """
        return self.exec.__aiter__()

    def __anext__(self):
        """Asynchronously fetch the next page of results.

        Returns
        -------
        dict
            The next page of results.
        """
        return self.exec.__anext__()

    def get(self):
        """Fetch all pages of results.

        Returns
        -------
        dict
            All result data.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> results = query.get()  # doctest: +SKIP
        """
        return self.exec.get()

    async def aget(self):
        """Asynchronously fetch all pages of results.

        Returns
        -------
        dict
            All result data.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> results = await query.aget()  # doctest: +SKIP
        """
        return await self.exec.aget()

    def page(self, *args, **kwargs):
        """Fetch a specific page or range of pages.

        Parameters
        ----------
        *args
            Positional arguments forwarded to executor.
        **kwargs
            Keyword arguments forwarded to executor.

        Returns
        -------
        dict
            The requested page(s) of results.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> page_data = query.page(1)  # doctest: +SKIP
        """
        return self.exec.page(*args, **kwargs)

    async def apage(self, *args, **kwargs):
        """Asynchronously fetch a specific page or range of pages.

        Parameters
        ----------
        *args
            Positional arguments forwarded to executor.
        **kwargs
            Keyword arguments forwarded to executor.

        Returns
        -------
        dict
            The requested page(s) of results.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> page_data = await query.apage(1)  # doctest: +SKIP
        """
        return await self.exec.apage(*args, **kwargs)

    def bulk_fetch(self, *args, **kwargs):
        """Fetch a large collection of results efficiently.

        Parameters
        ----------
        *args
            Positional arguments forwarded to executor.
        **kwargs
            Keyword arguments forwarded to executor.

        Returns
        -------
        dict
            All fetched results.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> results = query.bulk_fetch(limit=100)  # doctest: +SKIP
        """
        return self.exec.bulk_fetch(*args, **kwargs)

    async def abulk_fetch(self, *args, **kwargs):
        """Asynchronously fetch a large collection of results efficiently.

        Parameters
        ----------
        *args
            Positional arguments forwarded to executor.
        **kwargs
            Keyword arguments forwarded to executor.

        Returns
        -------
        dict
            All fetched results.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> results = await query.abulk_fetch(limit=100)  # doctest: +SKIP
        """
        return await self.exec.abulk_fetch(*args, **kwargs)

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

        self.exec.set_counts()

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

        self.exec.set_counts()
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
        return self.exec.first()

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
        return self.to_df(first)

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

    @property
    def id_param_key(self) -> str:
        """Get the parameter name used to identify this resource.

        Returns
        -------
        str
            The identifier parameter (e.g., "accession", "biome_lineage").

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> key = query.id_param_key  # doctest: +SKIP
        """
        try:
            return ID_PARAM[self.resource]
        except KeyError:
            raise AttributeError(
                f"Resource {self.resource} does not have a defined access identifier key."
            ) from None

    def _resolve_id_param(
        self, key: int | str, param_name: Optional[str] = None
    ) -> dict:
        """Resolve an identifier parameter by index or value.

        Parameters
        ----------
        key : int or str
            Integer position in the results, or a string identifier value
            (e.g., accession, biome lineage).

        Returns
        -------
        dict
            Dictionary with the identifier parameter key and its value.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.get()  # doctest: +SKIP
        >>> param_dict = query._resolve_id_param(0)  # doctest: +SKIP
        """

        if not param_name:
            param_name = self.id_param_key

        # allow index-based access
        if self.results_ids is not None and isinstance(key, int):
            return {param_name: self.results_ids[key]}
        # or by accession/biome_lineage/ids string directly
        if self.results_ids is not None and key in self.results_ids:
            return {param_name: key}

        raise KeyError(
            f"Invalid key: {key}. "
            "Key must be an integer index, or a valid id string. "
            f"Accession/id/biome_lineage must exist in`.results_ids`: {self.results_ids}"
        )

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

    @property
    def results_ids(self) -> Optional[list[str]]:
        """Get the list of identifiers from the current results.

        Returns
        -------
        list[str] or None
            List of identifiers (accessions, etc.), or ``None`` if no results.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.get()  # doctest: +SKIP
        >>> ids = query.results_ids  # doctest: +SKIP
        """
        if self.results is None:
            logger.warning(
                "No attempts for results to be retieved yet (e.g., .get(), .page()), so no accessions/ids available."
            )
            return None

        try:
            return [record[self.id_param_key] for record in self._unpageinate_results()]
        except KeyError as exc:
            raise KeyError(
                f"Identifier key '{self.id_param_key}' not found in results for resource '{self.resource}'. Cannot extract accessions/ids. Check .results"
            ) from exc

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

    def continue_iterator(self, *args, **kwargs):
        """
        Continue iteration from a specific page.
        THis is a facade of underlying QueryExecutor.continue_iterator,
        allowing users to resume iteration after an interruption or to jump to a specific page.

        Parameters
        ----------
        *args
            Positional arguments forwarded to executor.
        **kwargs
            Keyword arguments forwarded to executor.

        Returns
        -------
        None

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.continue_iterator(start_page=5)  # doctest: +SKIP
        """
        return self.exec.continue_iterator(*args, **kwargs)

    def resume(self):
        """
        Again facade of QueryExecutor.resume, allowing users to easily continue fetching results after an interruption.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.resume()  # doctest: +SKIP
        """
        return self.exec.resume()

    def reset_iterator(self):
        """Reset the pagination state to the beginning.

        Returns
        -------
        None

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.reset_iterator()  # doctest: +SKIP
        """
        return self.exec.reset_iterator()

    @property
    def progress(self):
        """
        Get the progress of the current query execution as a percentage.

        Returns
        -------
        str
            Progress percentage and counts (e.g., "75.00% (150/200 pages)").

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> print(query.progress)  # doctest: +SKIP
        """
        return self.exec.progress

    @property
    def last_successful_page(self) -> Optional[int]:
        """
        Get the last successfully retrieved page number.

        Returns
        -------
        int or None
            The last successful page number, or None if no pages have been retrieved yet.

        Examples
        --------
        >>> from mgnipy.V2.core import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.get()  # doctest: +SKIP
        >>> print(query.last_successful_page)  # doctest: +SKIP
        """
        return self.exec.last_successful_page
