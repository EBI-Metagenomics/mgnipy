from __future__ import annotations

from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Iterator,
    Optional,
)

import pandas as pd
import polars as pl

if TYPE_CHECKING:
    from mgnipy.V2.query_set import QuerySet


class ResultHandlerMixin:

    @property
    def data(self) -> dict[int, list[dict[str, Any]]]:
        """
        results based on the current resource.
        """
        return getattr(self, "_results", {}) or {}

    # @property
    # def id_param_key(self) -> str:
    #     """
    #     Get the key for the ID parameter based on the current resource.

    #     Returns
    #     -------
    #     str
    #         The key for the ID parameter.
    #     """
    #     return self.id_param_key

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
        _data = data or self.data

        def _page_to_records(page):
            if page is None:
                return []
            if isinstance(page, list):
                return page
            if isinstance(page, dict):
                return [page]
            return [page]

        return chain.from_iterable(_page_to_records(v) for v in _data.values())

    # viewing the retrieved
    def to_df(
        self,
        data: Optional[dict[int, list[dict]]] = None,
        expand_nested_dicts: Optional[list[str] | bool] = False,
        rename_columns: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Convert the current or provided metadata to a pandas DataFrame.

        Parameters
        ----------
        data : list of dict, optional
            List of records to convert. If None, uses self._results or self._previewed_page.
        expand_nested_dicts : list of str, optional
            List of keys to expand into separate columns.
        rename_columns : dict of str to str, optional
            A dictionary mapping old column names to new column names.
        **kwargs
            Additional keyword arguments passed to pd.DataFrame.

        Returns
        -------
        pd.DataFrame | None
            DataFrame containing the metadata.

        Raises
        ------
        RuntimeError
            If no data is available to convert.
        """

        _data = data or self.data

        _rename_columns = rename_columns or {"lineage": "biome_lineage"}

        if _data == {} or _data is None:
            return None

        as_pandas = pd.DataFrame(self._unpageinate_results(_data), **kwargs).rename(
            columns=_rename_columns
        )

        if expand_nested_dicts is None or expand_nested_dicts is False:
            return as_pandas

        if isinstance(expand_nested_dicts, list):
            return self._df_expand_nested(
                as_pandas,
                cols=expand_nested_dicts,
            )
        if expand_nested_dicts is True:  # TODO
            return self._df_expand_nested(as_pandas)

    def to_list(
        self, data: Optional[dict[int, list[dict]]] = None
    ) -> list[dict[str, Any]]:
        """
        Convert the current or provided metadata to a list of dictionaries.

        Parameters
        ----------
        data : dict of int to list of dict, optional
            The paginated data to convert. If None, uses self.data.

        Returns
        -------
        list of dict | None
            A list of metadata records as dictionaries, or None if no data is available .

        Raises
        ------
        RuntimeError
            If no data is available to convert.
        """
        _data = data or self.data

        if _data == {} or _data is None:
            return None

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
        return self.to_df(data, expand_nested_dicts=False).to_json(
            orient=orient, lines=lines, **json_kwargs
        )

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

        _data = data or self.data

        if _data == {} or _data is None:
            return None

        return pl.DataFrame(self._unpageinate_results(_data), **polars_kwargs)

    @property
    def results_ids(self) -> Optional[list[str]]:
        """
        Get a list of accessions from the retrieved metadata results, if available.

        Returns
        -------
        list of str or None
            A list of accession strings if available, otherwise None.
        """
        if self.to_df() is None:
            return None
        elif self.id_param_key in self.to_df().columns:
            return self.to_df()[self.id_param_key].tolist()
        else:
            return None


class DetailNavigationMixin:

    def iter_details(self, fetch: bool = False) -> Iterator["QuerySet"]:
        """
        Lazily iterate over child detail proxies.

        Parameters
        ----------
        fetch : bool
            Whether to immediately fetch each detail after creating the proxy.

        Returns
        -------
        Iterator of QuerySet
            An iterator that yields child detail proxies.

        Example
        -------
        for sample in samples.iter_details():
            sample.get()
        """
        for acc in self.results_accessions or []:
            yield self.get_next(self._resolve_access_param(acc), fetch=fetch)

    def collect_details(
        self,
        *,
        fetch: bool = False,
        by_accession: bool = False,
    ) -> list["QuerySet"] | dict[str, "QuerySet"]:
        """
        Collect child detail proxies into a list or dict.

        Parameters
        ----------
        fetch : bool
            Whether to immediately fetch the details after creating the proxies.
        by_accession : bool
            Whether to return a dict keyed by accession instead of a list.

        Returns
        -------
        list of QuerySet or dict of str to QuerySet
            A list or dict of child detail proxies.

        Example
        -------
        samples.collect_details(fetch=True, by_accession=True)


        """

        items: list["QuerySet"] = []
        for item in self.iter_details(fetch=fetch):
            items.append(item)

        if by_accession:
            return {x.accession: x for x in items if x.accession is not None}
        return items

    def __iter__(self) -> Iterator["QuerySet"]:
        return self.iter_details()

    async def __aiter__(self) -> AsyncIterator["QuerySet"]:
        async for item in self.aiter_details():
            yield item

    async def aiter_details(self, fetch: bool = False) -> AsyncIterator["QuerySet"]:
        for acc in self.results_accessions or []:
            yield await self.aget_next(self._resolve_access_param(acc), fetch=fetch)

    async def acollect_details(
        self,
        *,
        fetch: bool = False,
        by_accession: bool = False,
        concurrency: Optional[int] = None,
        hide_progress: bool = False,
    ) -> list["QuerySet"] | dict[str, "QuerySet"]:
        acc_params = [
            self._resolve_access_param(acc) for acc in (self.results_accessions or [])
        ]

        async def _worker(access_param):
            child = await self.aget_next(access_param, fetch=fetch)
            return child

        items = await self.exec.map_with_concurrency(
            items=acc_params,
            worker=_worker,
            concurrency=concurrency,
            hide_progress=hide_progress,
        )

        if by_accession:
            return {
                x.accession: x
                for x in items
                if x is not None and x.accession is not None
            }
        return items

    def __getitem__(self, key: int | str) -> "QuerySet":
        """
        Allow index or accession-based access to child details.
        Default is not lazy and will fetch immediately, but can be configured to return proxies without fetching.
        """
        return self.get_next(
            self._resolve_access_param(key),
            fetch=True,
        )


class RelatedNavigationMixin:

    @property
    def identifier(self) -> Optional[list[str]]:
        """
        identifier from parent, could be accessions, biome_lineages, or catalogue_ids depending on resource type.
        """
        return self.results_ids

    def __getattr__(self, name: str):
        # if is a supported relationship
        if name in self.list_relationships():
            return self.get_next(
                self._resolve_access_param(self.identifier),
                resource_name=name,
                fetch=False,
            )
