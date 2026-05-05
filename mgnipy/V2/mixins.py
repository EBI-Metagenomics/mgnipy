from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from itertools import chain
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
)

import pandas as pd
import polars as pl
from bigtree import (
    Tree,
)

from mgnipy._shared_helpers.writers import atomic_write_json

if TYPE_CHECKING:
    pass


class ResultsHandler:

    def __init__(self, data: Optional[chain[dict[str, Any]]] = None):
        self._data = data

    @property
    def data(self) -> chain[dict[str, Any]]:
        """
        results based on the current resource.
        """
        if self._data is None:
            return getattr(self, "records", []) or []
        return self._data

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
            List of records to convert. If None, uses self.qs._results or self._previewed_page.
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
        if _data == [] or _data is None:
            return None

        _rename_columns = rename_columns or {"lineage": "biome_lineage"}
        as_pandas = pd.DataFrame(_data, **kwargs).rename(columns=_rename_columns)

        if expand_nested_dicts is None or expand_nested_dicts is False:
            return as_pandas

        if isinstance(expand_nested_dicts, list):
            return self._df_expand_nested(
                as_pandas,
                cols=expand_nested_dicts,
            )
        if expand_nested_dicts is True:  # TODO
            return self._df_expand_nested(as_pandas)

    def to_list(self, data: Optional[chain] = None) -> list[Any]:
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

        if _data == [] or _data is None:
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
        return self.to_df(data, expand_nested_dicts=False).to_json(
            orient=orient, lines=lines, **json_kwargs
        )

    def to_polars(self, data: Optional[chain] = None, **polars_kwargs) -> pl.DataFrame:
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

        _data = data or self.data

        if _data == [] or _data is None:
            return None

        return pl.DataFrame(_data, **polars_kwargs)


class DiskCheckpointer:
    """
    Checkpoint manager for request-makers.
    """

    def __init__(
        self,
        params: dict,
        resource_str: str,
        config,
        results_store: Optional[dict] = None,
        count: Optional[int] = None,
        num_requests: Optional[int] = None,
    ):
        """Initialize with explicit dependencies."""
        self._params_dict = params
        self._resource_val = resource_str
        self.config = config
        self._results = results_store or {}
        self._total_records = count
        self._total_requests = num_requests

    @property
    def _cache_root(self) -> Path:
        return self.config.cache_dir or Path(".mgnipy_cache")

    @property
    def _cache_key(self) -> str:
        """Generate deterministic hash from resource + params."""
        params = self._params_dict.copy()
        serial = json.dumps(
            {"resource": self._resource_val, "params": params},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(serial.encode("utf-8")).hexdigest()

    @property
    def _cache_dir(self) -> Path:
        """Directory for this query's cached pages."""
        return self._cache_root / self._cache_key

    @property
    def _manifest_path(self) -> Path:
        """Path to manifest.json storing metadata."""
        return self._cache_dir / "manifest.json"

    def write_results(self, request_num: int, items: Any) -> None:
        """Auto atomic write to disk."""
        # ensure cache dir exists
        save_to = self._cache_dir
        save_to.mkdir(parents=True, exist_ok=True)

        # prep full filepath
        filepath = save_to / f"page_{request_num}.json"

        # and data for manifest
        manifest = {
            "resource": self._resource_val,
            "params": self._params_dict,
            "count": self._total_records,
            "total_pages": self._total_requests,
        }

        atomic_write_json(filepath, items)
        atomic_write_json(self._manifest_path, manifest)

    async def awrite_results(self, request_num: int, items: Any) -> None:
        """Async wrapper for write_results."""
        await asyncio.to_thread(self.write_results, request_num, items)

    def load_cache_results(self) -> list[int]:
        """Load cached pages into self._results. Returns count loaded."""
        load_from = self._cache_dir
        if not load_from.exists():
            return []

        pages_loaded = []
        for cache_file in sorted(load_from.glob("page_*.json")):
            try:
                # read in pg data
                with cache_file.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                # Extract page number from filename
                request_num = int(cache_file.stem.split("_", 1)[1])
                # load page if avail in cache
                self._results[request_num] = data
                # tracking
                pages_loaded.append(request_num)
            except Exception:
                logging.warning(f"Failed to load cache file: {cache_file}")

        return pages_loaded

    def load_cache_manifest(self) -> dict:
        # Load manifest if present
        mpath = self._manifest_path
        if mpath.exists():
            try:
                with mpath.open("r", encoding="utf-8") as fh:
                    manifest = json.load(fh)
                    self._total_records = manifest.get("count")
                    self._total_requests = manifest.get("total_pages")
            except Exception:
                logging.warning(f"Failed to load manifest file: {mpath}")
                manifest = {}
        else:
            manifest = {}
        return manifest

    def load_cache(self) -> int:
        pages_loaded = self.load_cache_results()
        self.load_cache_manifest()
        return pages_loaded

    async def aload_cache(self) -> int:
        """Async wrapper for load_cache."""
        return await asyncio.to_thread(self.load_cache)

    def clear_cache(self) -> None:
        """Remove all cached pages for this query."""
        load_from = self._cache_dir
        if load_from.exists():
            for cache_file in load_from.iterdir():
                try:
                    cache_file.unlink()
                except Exception:
                    logging.warning(f"Failed to delete cache file: {cache_file}")
            try:
                load_from.rmdir()
            except Exception:
                logging.warning(f"Failed to delete cache directory: {load_from}")


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
