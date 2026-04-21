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

from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.endpoints import ACC_DETAIL_ENDPOINTS

if TYPE_CHECKING:
    from mgnipy.V2.query_set import QuerySet


class ResultHandlerMixin:

    @property
    def data(self) -> dict[int, list[dict[str, Any]]]:
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

        if _data == {} or _data is None:
            return None

        as_pandas = pd.DataFrame(self._unpageinate_results(_data), **kwargs)

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


class DetailNavigationMixin:

    def _detail_resource(self) -> SupportedEndpoints:
        # Map list resources to singular detail resources.
        mapping = {
            SupportedEndpoints.STUDIES: SupportedEndpoints.STUDY,
            SupportedEndpoints.SAMPLES: SupportedEndpoints.SAMPLE,
            SupportedEndpoints.RUNS: SupportedEndpoints.RUN,
            SupportedEndpoints.ANALYSES: SupportedEndpoints.ANALYSIS,
            SupportedEndpoints.GENOMES: SupportedEndpoints.GENOME,
            SupportedEndpoints.ASSEMBLIES: SupportedEndpoints.ASSEMBLY,
        }
        r = SupportedEndpoints.validate(self.resource)
        return mapping.get(r, r)

    def iter_details(self) -> Iterator["QuerySet"]:
        """
        Lazily iterate over child detail proxies.

        Example
        -------
        for sample in samples.iter_details():
            sample.get()
        """
        for acc in self.results_accessions or []:
            yield self.get_detail(self._resolve_results_accession_params(acc))

    def collect_details(
        self,
        *,
        fetch: bool = False,
        by_accession: bool = False,
    ) -> list["QuerySet"] | dict[str, "QuerySet"]:
        items: list["QuerySet"] = []
        for item in self.iter_details():
            if fetch:
                item.get()
            items.append(item)

        if by_accession:
            return {x.accession: x for x in items if x.accession is not None}
        return items

    async def __aiter__(self) -> AsyncIterator["QuerySet"]:
        async for item in self.aiter_details():
            yield item

    async def aiter_details(self) -> AsyncIterator["QuerySet"]:
        for acc in self.results_accessions or []:
            yield await self.aget_detail(self._resolve_results_accession_params(acc))

    async def acollect_details(
        self,
        *,
        fetch: bool = False,
        by_accession: bool = False,
        concurrency: Optional[int] = None,
        hide_progress: bool = False,
    ) -> list["QuerySet"] | dict[str, "QuerySet"]:
        acc_params = [
            self._resolve_results_accession_params(acc)
            for acc in (self.results_accessions or [])
        ]

        async def _worker(accession_param):
            child = await self.aget_detail(accession_param)
            if fetch:
                await child.aget()
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

    def __getitem__(self, key):
        return self.get_detail(self._resolve_results_accession_params(key))

    def get_detail(self, accession_param: dict[str, str]) -> "QuerySet":
        detail_resource = self._detail_resource()
        child = self._spawn(resource=detail_resource.value, **accession_param)
        child.endpoint_module = ACC_DETAIL_ENDPOINTS[detail_resource]
        return child

    async def aget_detail(self, accession_param: dict[str, str]) -> "QuerySet":
        # Same behavior as sync variant; caller can await child.aget() later.
        return self.get_detail(accession_param)
