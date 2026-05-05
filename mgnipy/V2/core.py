import logging
from typing import (
    Any,
    Literal,
    Optional,
)

import pandas as pd

from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.endpoints import (
    ALL_SUPPORTED_RELATIONSHIPS,
)
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
    Orchestrates between query building, execution, and results handling to provide a user-friendly interface for retrieving and working with MGnify metadata.
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
        config: Optional[dict] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):

        # init query set
        QuerySet.__init__(
            self,
            resource=resource,
            config=config,
            params=params,
            **kwargs,
        )
        # init executor
        self.exec = QueryExecutor(self)

        # init result handler
        ResultsHandler.__init__(self)

    def __iter__(self):
        return iter(self.exec)

    def __next__(self):
        return next(self.exec)

    def __aiter__(self):
        return self.exec.__aiter__()

    def __anext__(self):
        return self.exec.__anext__()

    def reset_iterator(self):
        return self.exec.reset_iterator()

    def continue_iterator(self, start_page: Optional[int] = None):
        return self.exec.continue_iterator(start_page=start_page)

    def get(self):
        return self.exec.get()

    async def aget(self):
        return await self.exec.aget()

    def page(self, *args, **kwargs):
        return self.exec.page(*args, **kwargs)

    async def apage(self, *args, **kwargs):
        return await self.exec.apage(*args, **kwargs)

    def bulk_fetch(self, *args, **kwargs):
        return self.exec.bulk_fetch(*args, **kwargs)

    async def abulk_fetch(self, *args, **kwargs):
        return await self.exec.abulk_fetch(*args, **kwargs)

    # preview the request(s) prior to making them
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

        self.exec.set_counts()

        print(f"Total requests to make: {self.num_requests}")
        print(f"Total records to retrieve: {self.count}")

    def explain(self, head: Optional[int] = None) -> None:
        """
        Print example URLs that would be called. Actual requests handled by client.
        """

        self.exec.set_counts()

        limit = head or self.num_requests

        for url in self.list_urls()[:limit]:
            print(url)

    def first(self) -> Optional[dict]:
        """
        Retrieve the first record from the results of the current query.
        This method executes the query and returns the first record from the results, if available.

        Returns
        -------
        dict or None
            The first record from the results as a dictionary, or None if no results are available.
        """
        return self.exec.first()

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

    # forward from emgapi handler
    def list_supported_params(self) -> list[str]:
        return self.emgapi_handler.list_supported_params()

    def describe_endpoint(self, **kwargs) -> dict[str, str] | None:
        return self.emgapi_handler.describe_endpoint(**kwargs)

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
            f"Returns paginated results: {self.emgapi_handler.is_list_endpoint}\n"
        )
