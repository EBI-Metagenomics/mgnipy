import logging

logger = logging.getLogger(__name__)

from itertools import chain
from typing import Any, Optional

from mgnipy.V2.mgnifier.endpoints import ID_PARAM
import pandas as pd
import polars as pl


class ResultsHandler:
    """
    Mixin providing methods to handle and convert paginated results.
    This mixin provides methods to convert paginated results into various formats such as pandas DataFrames, lists of dictionaries, JSON strings, and Polars DataFrames.

    The mixin assumes the host class provides the following dependencies:
     - `data`: A property that returns an iterable of metadata records, typically a chain of dictionaries. This can be overridden by providing data directly to the conversion methods.
    """

    def __init__(self, data: Optional[list[dict[str, Any]]] = None):
        logger.debug("Initializing ResultsHandler")
        self._data = data

    def __add__(self, other: "ResultsHandler") -> "ResultsHandler":
        """
        Combine two ResultsHandler instances by concatenating their data.

        Parameters
        ----------
        other : ResultsHandler
            Another ResultsHandler instance to combine with this one.

        Returns
        -------
        ResultsHandler
            A new ResultsHandler instance containing the combined data from both instances.
        """
        # check
        logger.debug(f"Combining {self.__class__.__name__} instances")
        combined_data = chain(self.data, other.data)
        return self.__class__(combined_data)

    def __len__(self) -> int:
        """
        Get the number of records in the current instance.

        Returns
        -------
        int
            The number of records in the data.
        """
        return len(list(self.data or []))

    @property
    def data(self) -> list[dict[str, Any]]:
        """
        Get the data associated with the current instance.
        """

        return self._data

    @data.setter
    def data(self, value: list[dict[str, Any]]):
        self._data = list(value)

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

        cols = cols or [
            "metadata",
            "sample",
            "study",
            "biome",
            "run",
            "assembly",
            "read_run",
        ]

        new_df = df.copy()
        for c in cols:
            if c in new_df.columns:
                # expand the nested dict in column c into separate columns
                attr_df = pd.json_normalize(new_df[c])
                # rename the new columns to include the original column name as a prefix
                attr_df.columns = [f"{c}__{subcol}" for subcol in attr_df.columns]
                # drop c and concat new cols
                new_df = pd.concat([new_df.drop(columns=[c]), attr_df], axis=1)
        return new_df

    # viewing the retrieved
    def to_pandas(
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
            List of records to convert. If ``None``, uses :pyattr:`data`.
        expand_nested_dicts : list of str or bool, optional
            List of keys to expand into separate columns, or ``True`` to
            expand defaults.
        rename_columns : dict of str to str, optional
            A dictionary mapping old column names to new column names.
        **kwargs
            Additional keyword arguments passed to ``pd.DataFrame``.

        Returns
        -------
        pd.DataFrame or None
            DataFrame containing the metadata or ``None`` when no data is
            available.

        Examples
        --------
        >>> handler = ResultsHandler(data=[{"a": 1, "b": 2}])
        >>> df = handler.to_pandas()
        >>> list(df.columns)
        ['a', 'b']
        >>> df.iloc[0]['a']
        np.int64(1)
        """

        logger.debug(
            "Converting results to pandas DataFrame; expand_nested_dicts=%s",
            expand_nested_dicts,
        )

        _data = data or self.data
        if _data == [] or _data is None:
            logger.debug(
                "No data available for pandas DataFrame conversion, to_pandas returning None"
            )
            return None

        _rename_columns = rename_columns or {"lineage": "biome_lineage"}
        as_pandas = pd.DataFrame(_data, **kwargs).rename(columns=_rename_columns)

        if expand_nested_dicts is None or expand_nested_dicts is False:
            logger.debug("Returning pandas DataFrame without nested expansion")
            return as_pandas

        if isinstance(expand_nested_dicts, list):
            return self._df_expand_nested(
                as_pandas,
                cols=expand_nested_dicts,
            )
        if expand_nested_dicts is True:
            return self._df_expand_nested(as_pandas)

    def to_list(self, data: Optional[chain] = None) -> list[Any]:
        """
        Convert the current or provided metadata to a list of dictionaries.

        Parameters
        ----------
        data : optional
            The paginated data to convert. If ``None``, uses :pyattr:`data`.

        Returns
        -------
        list
            A list of metadata records as dictionaries, or ``None`` if no
            data is available.

        Examples
        --------
        >>> handler = ResultsHandler(data=[{"x": 10}])
        >>> handler.to_list()
        [{'x': 10}]
        """
        logger.debug("Converting results to list")
        _data = data or self.data

        if _data == [] or _data is None:
            logger.debug("No data available for list conversion")
            return None

        return list(_data)

    def to_json(
        self,
        data: Optional[chain] = None,
        orient: str = "records",
        lines: bool = True,
        **json_kwargs,
    ) -> str:
        """
        Convert the current metadata to a JSON string or save it to a file.

        Parameters
        ----------
        data : dict of int to list of dict, optional
            The paginated data to convert. If None, uses self.qs._results.
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
        logger.debug(
            "Converting results to JSON; orient=%s lines=%s",
            orient,
            lines,
        )
        return self.to_pandas(data, expand_nested_dicts=False).to_json(
            orient=orient, lines=lines, **json_kwargs
        )

    def to_polars(
        self,
        data: Optional[chain] = None,
        expand_nested_dicts: Optional[list[str] | bool] = False,
        rename_columns: Optional[dict[str, str]] = None,
        **polars_kwargs,
    ) -> pl.DataFrame:
        """
        Convert the current metadata to a Polars DataFrame.

        Parameters
        ----------
        data : dict of int to list of dict, optional
            The paginated data to convert. If None, uses self.qs._results.
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

        logger.debug("Converting results to Polars DataFrame")

        _data = data or self.data

        if _data == [] or _data is None:
            logger.debug("No data available for Polars DataFrame conversion")
            return None

        # first convert to pandas and then to polars to leverage the nested dict expansion and column renaming already implemented in to_pandas
        df_pd = self.to_pandas(
            data=_data,
            expand_nested_dicts=expand_nested_dicts,
            rename_columns=rename_columns,
        )

        return pl.from_pandas(df_pd, **polars_kwargs)

    def get_ids(self, label: Optional[str] = None) -> list[str]:
        """
        Get a list of IDs/accessions from the current metadata.

        Parameters
        ----------
        label : str, optional
            The key to extract IDs from. If None, uses the default key based on the resource type.

        Returns
        -------
        list of str
            A list of IDs extracted from the metadata.

        Raises
        ------
        ValueError
            If no data is available to extract IDs from.
        """
        _data = self.data

        if _data == [] or _data is None:
            return []

        logger.debug("Extracting IDs from results")
        # Determine the default label based on the resource type if not provided
        if label is None:
            resource_type = getattr(self, "resource", None)
            label = ID_PARAM.get(resource_type, "accession")

        if isinstance(_data, list):
            return [item.get(label) for item in _data if item.get(label) is not None]
        elif isinstance(_data, dict):
            return [
                item.get(label)
                for page in _data.values()
                for item in page
                if item.get(label) is not None
            ]


class MGnifyMetadata(ResultsHandler):

    def __init__(
        self,
        data: dict[int, list[dict]] | None = None,
        id_label: Optional[str] = None,
    ):

        self._res: dict[int, list[dict]] | None = data
        # init results
        if isinstance(data, dict):
            super().__init__(data=list(self.records))
        else:  # list or None
            super().__init__(data=self._res)
        self._id_label = id_label

    def __str__(self) -> str:
        """Return a human-readable summary of the metadata state.

        Returns
        -------
        str
            Summary including resource, URL, parameters, and endpoint info.

        Examples
        --------
        >>> from mgnipy.V2.mgnifier import MGnifyMetadata  # doctest: +SKIP
        >>> metadata = MGnifyMetadata("studies")  # doctest: +SKIP
        >>> print(metadata)  # doctest: +SKIP
        """

        return (
            f"MGnifyMetadata instance: Number of records: {len(self)!r}\n"
            f"Contains Pages/Request#/Details: {self.pages}\n"
        )

    @property
    def results(self) -> dict[int, list[dict]]:
        """
        Get the retrieved metadata results, if available.
        Results are stored in a dictionary with request number (e.g. page number) as keys.
        """
        return self._res

    def _unpageinate_results(self, data: Optional[dict] = None) -> chain:
        """
        Flattening the results into a single iterator of records.
        If paginated results are stored in a dictionary with page numbers as keys,
        this method will extract the records from all pages and combine them into a single iterable sequence.

        Returns
        -------
        chain
            An iterator that yields individual metadata records from all pages.
        """
        logger.debug("Flattening paginated results")
        _data = data or self._res

        def _page_to_records(page):
            if page is None:
                return []
            if isinstance(page, list):
                return page
            if isinstance(page, dict):
                return [page]
            return [page]

        if isinstance(_data, dict):
            return chain.from_iterable(_page_to_records(v) for v in _data.values())
        return chain.from_iterable(_page_to_records(v) for v in _data)

    @property
    def records(self) -> Optional[chain]:
        """
        Get an iterator of individual metadata records from the retrieved results, if available.
        This property provides a convenient way to access the metadata records without needing to handle pagination.

        Used by ResultsHandler mixin.

        Returns
        -------
        chain or None
            An iterator that yields individual metadata records if results are available, otherwise None.
        """
        if self._res is None:
            logger.warning(".data/.results is None. No record iterator available")
            return None
        return self._unpageinate_results()

    @property
    def ids(self) -> Optional[list[str]]:
        """Get the list of identifiers from the current results.

        Returns
        -------
        list[str] or None
            List of identifiers (accessions, etc.), or ``None`` if no results.

        Examples
        --------
        >>> from mgnipy.V2.mgnifier import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.get()  # doctest: +SKIP
        >>> ids = query.metadata.ids  # doctest: +SKIP
        """
        # if self.data is None:
        #     logger.warning(
        #         "No attempts for results to be retieved yet (e.g., .get(), .page()), so no accessions/ids available."
        #     )
        #     return None

        return self.get_ids(label=self._id_label)

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
        >>> from mgnipy.V2.mgnifier import MGnifier  # doctest: +SKIP
        >>> query = MGnifier("studies")  # doctest: +SKIP
        >>> query.get()  # doctest: +SKIP
        >>> param_dict = query._resolve_id_param(0)  # doctest: +SKIP
        """

        if not param_name:
            param_name = self._id_label

        # allow index-based access
        if self.ids is not None and isinstance(key, int):
            return {param_name: self.ids[key]}
        # or by accession/biome_lineage/ids string directly
        if self.ids is not None and key in self.ids:
            return {param_name: key}

        raise KeyError(
            f"Invalid key: {key}. "
            "Key must be an integer index, or a valid id string. "
            f"Accession/id/biome_lineage must exist in`.ids`: {self.ids}"
        )

    @property
    def pages(self) -> Optional[int]:
        """
        The pages available in the results, if any.
        This is determined by the keys of the results dictionary,
        which represent page numbers.

        Returns
        -------
        list[int]
            A list of page numbers available in the results.
        """
        if isinstance(self.results, dict):
            return list(self.results.keys())
        logger.debug("No pages available in results; returning empty list")
        return []

    @property
    def downloads(self) -> Optional[list[dict]]:
        """
        Get the downloads information from the current results, if available.
        This property extracts the 'downloads' key from each record in the results.

        Returns
        -------
        list[dict] or None
            A list of download information dictionaries, or None if no results are available.
        """
        if self.records is None:
            logger.warning("No records available to extract downloads information")
            return None

        downloads_list = []
        for record in self.records:
            downloads = record.get("downloads")
            if downloads is not None:
                downloads_list.append(downloads)

        return (
            [item for sublist in downloads_list for item in sublist]
            if downloads_list
            else None
        )
