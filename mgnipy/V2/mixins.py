from __future__ import annotations

import inspect
import os
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
)
from urllib.parse import urlencode

import pandas as pd
import polars as pl
from bigtree import (
    Tree,
)

from mgnipy._shared_helpers.docstring_parser import (
    get_docstring,
    parse_docstring,
)

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


class BiomesTreeMixin:

    @property
    def lineages(self) -> list[str]:
        return getattr(self, "results_ids", []) or []

    @property
    def tree(self) -> Tree:
        """
        Convert the biomes metadata to a tree structure for visualization or analysis.

        Returns
        -------
        Tree
            A tree representation of the biomes and their relationships.
        """
        # TODO generate nodes first
        return Tree.from_list(self.lineages, sep=":")

    def show_tree(
        self,
        method: Literal[
            "compact",
            "show",
            "print",
            "horizontal",
            "hshow",
            "h",
            "hprint",
            "vertical",
            "vshow",
            "v",
            "vprint",
        ] = "compact",
    ):
        if method in ["compact", "show", "print"]:
            # TODO print_tree(self._tree)
            self.tree.show()
        elif method in ["horizontal", "hshow", "h", "hprint"]:
            self.tree.hshow()
        elif method in ["vertical", "vshow", "v", "vprint"]:
            self.tree.vshow()
        else:
            raise ValueError(
                f"Invalid method: {method}. "
                "Supported methods: 'compact', 'show', 'print', "
                "'horizontal', 'hshow', 'h', 'hprint', "
                "'vertical', 'vshow', 'v', 'vprint'."
            )


class DescribeEmgapiMixin:

    def endpoint_module(self):
        return getattr(self, "endpoint_module", None)

    def list_supported_params(self) -> list[str]:
        """
        Lists supported keyword arguments for the endpoint module.

        Returns
        -------
        list of str
            List of supported keyword argument names.
        """
        sig = inspect.signature(self.endpoint_module._get_kwargs)
        return list(sig.parameters.keys())

    def validate_endpoint_kwargs(self, **kwargs) -> dict[str, Any]:
        """
        Validates the provided keyword arguments against the supported parameters of the endpoint module.

        Parameters
        ----------
        **kwargs
            Keyword arguments to validate.

        Returns
        -------
        dict of str to Any
            The validated keyword arguments.

        Raises
        ------
        ValueError
            If any provided keyword argument is not supported by the endpoint module.
        """
        return self.endpoint_module._get_kwargs(**kwargs)

    @property
    def emgapi_resource(self) -> Optional[str]:
        """
        Retrieves the name of the endpoint resource based on the endpoint module.

        Returns
        -------
        str or None
            The name of the endpoint resource, or None if the endpoint module is not set.
        """
        return os.path.basename(os.path.dirname(self.endpoint_module.__file__))

    def sub_url(self, **kwargs) -> Optional[str]:
        """
        Constructs the sub-URL for the endpoint based on the current parameters.

        Returns
        -------
        str or None
            The constructed sub-URL, or None if the endpoint module is not set.
        """
        _kwargs = self.validate_endpoint_kwargs(**kwargs)
        _end_url: str = _kwargs.get(
            "url", f"/metagenomics/api/v2/{self.emgapi_resource}/"
        ).strip("/")

        return _end_url

    def resolve_query_string(self, **kwargs) -> str:
        """
        Resolves the query string for the endpoint based on the current parameters.

        Parameters
        ----------
        **kwargs
            Keyword arguments to validate and include in the query string.

        Returns
        -------
        str
            The resolved query string.
        """
        _kwargs = self.validate_endpoint_kwargs(**kwargs)

        # get validated params if any
        params = _kwargs.get("params", {})

        # encode params for url
        return urlencode(params, doseq=True)

    def url_path(self, **kwargs) -> str:
        """
        Constructs the full URL path for the endpoint based on the current parameters.

        Parameters
        ----------
        **kwargs
            Keyword arguments to validate and include in the URL construction.

        Returns
        -------
        str
            The constructed URL path.
        """
        _end_url = self.sub_url(**kwargs)
        query_string = self.resolve_query_string(**kwargs)

        return f"{_end_url}?{query_string}" if query_string else _end_url

    @property
    def emgapi_docs(self) -> str:
        return get_docstring(self.endpoint_module, "sync")

    def describe_endpoint(self, as_dict: bool = False) -> dict[str, str] | None:
        return parse_docstring(self.emgapi_docs, as_dict=as_dict)
