from __future__ import annotations

from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
)

import pandas as pd
import polars as pl

if TYPE_CHECKING:
    pass


class ResultsHandlerMixin:

    @property
    def data(self) -> dict[int, list[dict[str, Any]]]:
        """
        results based on the current resource.
        """
        return getattr(self, "_results", {}) or {}

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
