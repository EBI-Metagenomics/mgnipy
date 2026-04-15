from __future__ import annotations

import logging
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
)

import pandas as pd
import polars as pl

if TYPE_CHECKING:
    from mgnipy.V2.core import MGnifier
    from mgnipy.V2.query_executor import QueryExecutor


class QuerySet:
    def __init__(self, owner: MGnifier):
        self.owner: MGnifier = owner
        self.exec: QueryExecutor = owner._executor

    def _clone_owner(self) -> MGnifier:
        return self.owner._clone()

    # helpers
    def _df_expand_nested(
        self, df: pd.DataFrame, cols: list[str] = None
    ) -> pd.DataFrame:
        """
        Expand nested structures in the DataFrame into separate columns.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to expand.
        cols : list of str
            List of column names to expand.

        Returns
        -------
        pd.DataFrame
            The expanded DataFrame.
        """

        cols = cols or ["metadata"]

        new_df = df.copy()
        for c in cols:
            if c in new_df.columns:
                attr_df = pd.json_normalize(new_df[c])
                new_df = pd.concat([new_df.drop(columns=[c]), attr_df], axis=1)
        return new_df

    def _unpageinate_results(self, data: Optional[dict] = None) -> chain:
        """
        Unpaginate the results by flattening the dictionary of pages into a single list of records.

        Returns
        -------
        chain
            An iterator that yields individual metadata records from all pages.
        """
        _data = data or self.owner._results

        if _data == {} or _data is None:
            raise RuntimeError("No results available. Run preview/get/page first.")
        return chain.from_iterable(_data.values())

    # choose to filter request or not
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
        MGnifier
            A new MGnifier instance with updated parameters for filtering results.
        """
        # make a copy of current instance
        new_mg = self._clone_owner()
        # but with updates to params
        new_mg._params.update(filters)
        # update endpoint module based on new params
        new_mg.endpoint_module = new_mg._resolve_endpoint_module()
        return QuerySet(new_mg)

    # @require_pagination
    def page_size(self, n: int):
        """
        Set the page size for paginated API calls.

        Parameters
        ----------
        n : int

        Returns
        -------
        MGnifier
            A new MGnifier instance with the updated page size parameter.
        """
        if not isinstance(n, int) or n <= 0:
            raise ValueError("Page size must be a positive integer.")

        # make a copy of current instance
        new_mg = self._clone_owner()
        # but with updates to params
        new_mg._params.update({"page_size": n})
        return QuerySet(new_mg)

    # preview the request(s) prior to making them (option 1)
    def dry_run(self) -> None:
        """
        Plan the API call by validating parameters and estimating the number of pages and records available.
        Prints the plan details for the user to review before executing the full data retrieval.
        This method can be called before get() to ensure that the parameters are valid and to understand the scope of the data retrieval.

        Returns
        -------
        None
        """
        # verbose
        print("Planning the API call with params:")
        print(self.owner._params)

        if self.owner._count is not None and self.owner._total_pages is not None:
            logging.info("Already have count and total_pages from previous dry run")
        elif not self.owner._pagination_status:
            # if not pageinated only 1
            self.owner._count = 1
            self.owner._total_pages = 1
        else:
            # small get request to get count and calc total pages
            self.exec.get_pageinated_counts()

        print(f"Total pages to retrieve: {self.owner._total_pages}")
        print(f"Total records to retrieve: {self.owner._count}")

    # preview the request(s) prior to making them (option 2)
    def explain(self, head: Optional[int] = None) -> None:
        """
        Print example URLs that would be called. Actual requests handled by client.
        """
        # prep if not done already
        if self.owner._total_pages is None:
            self.dry_run()
        # if not paginated just print one url
        if not self.owner._get_pagination_status():
            print(self.owner._build_url())
        # Otherwise, print URLs for each page
        else:
            limit = (
                min(head, self.owner._total_pages) if head else self.owner._total_pages
            )
            for page in range(1, limit + 1):
                print(
                    self.owner._build_url(params={**self.owner._params, "page": page})
                )

    # preview the request(s) prior to making them (option 3)
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
        return self.to_df(first)

    # alternatively preview get first
    def first(self) -> dict:
        """
        Retrieve the first page of metadata for the current resource and parameters.
        Same as preview() but returns the raw dictionary instead of a DataFrame.
        """
        self.exec.get_any_first()
        return self.owner._results.get(1, [])

    # viewing the retrieved
    def to_df(
        self, data: Optional[dict[int, list[dict]]] = None, **kwargs
    ) -> pd.DataFrame:
        """
        Convert the current or provided metadata to a pandas DataFrame.

        Parameters
        ----------
        data : list of dict, optional
            List of records to convert. If None, uses self._results or self._previewed_page.
        **kwargs
            Additional keyword arguments passed to pd.DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the metadata.

        Raises
        ------
        RuntimeError
            If no data is available to convert.
        """

        _data = data or self.owner._results

        if _data == {} or _data is None:
            logging.info("No data available to convert to DataFrame. Returning None.")
            return None

        return pd.DataFrame(self._unpageinate_results(_data), **kwargs)

    def to_list(
        self, data: Optional[dict[int, list[dict]]] = None
    ) -> list[dict[str, Any]]:
        """
        Convert the current or provided metadata to a list of dictionaries.

        Parameters
        ----------
        data : dict of int to list of dict, optional
            The paginated data to convert. If None, uses self._results.

        Returns
        -------
        list of dict
            A list of metadata records as dictionaries.

        Raises
        ------
        RuntimeError
            If no data is available to convert.
        """
        _data = data or self.owner._results

        if _data == {} or _data is None:
            logging.info("No data available to convert to list. Returning empty list.")
            return []

        return list(self._unpageinate_results(_data))

    def to_json(
        self,
        data: Optional[dict[int, list[dict]]] = None,
        orient: str = "records",
        lines: bool = True,
        **json_kwargs,
    ) -> str:
        """
        Convert the current metadata to a JSON string or save it to a file.

        Parameters
        ----------
        data : dict of int to list of dict, optional
            The paginated data to convert. If None, uses self._results.
        **json_kwargs
            Additional keyword arguments passed to the JSON serialization function.

        Returns
        -------
        str or None
            The JSON string representation of the metadata, or None if no data is available.

        Raises
        ------
        RuntimeError
            If no data is available to convert.
        """
        return self.to_df(data).to_json(orient=orient, lines=lines, **json_kwargs)

    def to_polars(
        self, data: Optional[dict[int, list[dict]]] = None, **polars_kwargs
    ) -> pl.DataFrame:
        """
        Convert the current metadata to a Polars DataFrame.

        Parameters
        ----------
        data : dict of int to list of dict, optional
            The paginated data to convert. If None, uses self._results.
        **polars_kwargs
            Additional keyword arguments passed to pl.DataFrame.

        Returns
        -------
        pl.DataFrame
            A Polars DataFrame containing the metadata.

        Raises
        ------
        RuntimeError
            If no data is available to convert.
        """

        _data = data or self.owner._results

        if _data == {} or _data is None:
            logging.info(
                "No data available to convert to polars DataFrame. Returning None."
            )
            return None

        return pl.DataFrame(self._unpageinate_results(_data), **polars_kwargs)

    @property
    def results_accessions(self) -> Optional[list[str]]:
        """
        Get a list of accessions from the retrieved metadata results, if available.

        Returns
        -------
        list of str or None
            A list of accession strings if available, otherwise None.
        """
        if self.to_df() is None:
            return None
        elif "accession" in self.to_df().columns:
            return self.to_df()["accession"].tolist()
        else:
            return None

    @property
    def results_biome_lineages(self) -> Optional[list[str]]:
        """
        Get a list of biome lineages from the retrieved metadata results, if available.

        Returns
        -------
        list of str or None
            A list of biome lineage strings if available, otherwise None.
        """
        if self.to_df() is None:
            return None
        elif "lineage" in self.to_df().columns:
            return self.to_df()["lineage"].tolist()
        elif "biome_lineage" in self.to_df().columns:
            return self.to_df()["biome_lineage"].tolist()
        elif "biome" in self.to_df().columns:
            return self.to_df()["biome"].tolist()
        elif "biome_name" in self.to_df().columns:
            return self.to_df()["biome_name"].tolist()
        else:
            return None

    def _resolve_results_accession_params(self, accession: int | str) -> dict:
        if self.results_accessions is not None and isinstance(accession, int):
            return {"accession": self.results_accessions[accession]}

        if self.results_accessions is not None and accession in self.results_accessions:
            return {"accession": accession}

        if self.results_biome_lineages is not None and isinstance(accession, int):
            return {"biome_lineage": self.results_biome_lineages[accession]}

        if (
            self.results_biome_lineages is not None
            and accession in self.results_biome_lineages
        ):
            return {"biome_lineage": accession}

        raise KeyError(
            f"Invalid key: {accession}. "
            "Key must be an integer index, or a valid accession string. "
            "Accession must exist in`.results_accessions` or `.results_biome_lineages`."
        )
