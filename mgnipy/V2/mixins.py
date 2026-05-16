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
    Callable,
    Literal,
    Optional,
)

import pandas as pd
import polars as pl
from bigtree import (
    Tree,
)

from mgnipy._models.config import MGnipyConfig
from mgnipy._shared_helpers.writers import atomic_write_json

if TYPE_CHECKING:
    pass


class ResultsHandler:

    def __init__(self, data: Optional[chain[dict[str, Any]]] = None):
        logging.debug("Initializing ResultsHandler")
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

        logging.debug(
            "Converting results to pandas DataFrame; expand_nested_dicts=%s",
            expand_nested_dicts,
        )

        _data = data or self.data
        if _data == [] or _data is None:
            logging.debug("No data available for pandas DataFrame conversion")
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

        logging.debug("Returning pandas DataFrame without nested expansion")

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
        logging.debug("Converting results to list")
        _data = data or self.data

        if _data == [] or _data is None:
            logging.debug("No data available for list conversion")
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
        logging.debug(
            "Converting results to JSON; orient=%s lines=%s",
            orient,
            lines,
        )
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

        logging.debug("Converting results to Polars DataFrame")

        _data = data or self.data

        if _data == [] or _data is None:
            logging.debug("No data available for Polars DataFrame conversion")
            return None

        return pl.DataFrame(_data, **polars_kwargs)


class DiskCheckpointer:
    """
    Checkpoint manager for request-makers.
    """

    def __init__(
        self,
        *,
        params_getter: Callable[[], dict],
        resource_str: str,
        config: MGnipyConfig,
        results_store: Optional[dict] = None,
        count: Optional[Callable[[], int]] = None,
        num_requests: Optional[Callable[[], int]] = None,
    ):
        """Initialize with explicit dependencies."""
        logging.debug("Initializing DiskCheckpointer for %s", resource_str)
        self._params_getter = params_getter
        self._resource_val = resource_str
        self.config = config
        self._results = results_store or {}
        self._total_records = count
        self._total_requests = num_requests

    @property
    def _cache_root(self) -> Optional[Path]:
        return self.config.cache_dir

    @property
    def _cache_key(self) -> str:
        """
        Generate deterministic hash from resource + params.

        Returns
        -------
        str
            A unique cache key for the current query parameters and resource.
            For a query to the 'samples' resource with parameters {'biome_lineage': 'root:Environmental:Terrestrial'},
            the cache key will be a SHA256 hash of the string representation of the resource and parameters,
            ensuring that identical queries will have the same cache key and thus access the same cached results.

        Example
        -------
        >>> # Imports
        >>> from mgnipy.V2.mixins import DiskCheckpointer
        >>> from mgnipy import MGnipyConfig
        >>> # Prepare parameters and config
        >>> params = {'lineage': 'root:Environmental:Terrestrial'}
        >>> resource = 'biome'
        >>> config = MGnipyConfig(cache_dir="/path/to/cache")
        >>> # Create DiskCheckpointer instance and compute cache key
        >>> cache_handler = DiskCheckpointer(params_getter=lambda: params, resource_str=resource, config=config)
        >>> cache_handler._cache_key
        '1eb56ddf5a2e7d60d8155c8bbe01f032f959a2519d43e99f31f533abffa3166f'
        """
        params = self._params_getter().copy()
        serial = json.dumps(
            {"resource": self._resource_val, "params": params},
            sort_keys=True,
            default=str,
        )
        cache_key = hashlib.sha256(serial.encode("utf-8")).hexdigest()
        logging.debug("Computed cache key for %s: %s", self._resource_val, cache_key)
        return cache_key

    @property
    def _cache_dir(self) -> Optional[Path]:
        """Directory for this query's cached pages."""
        root = self._cache_root
        if root is None:
            return None
        return root / self._cache_key

    @property
    def _manifest_path(self) -> Optional[Path]:
        """Path to mgnipy_manifest.json storing metadata."""
        cache_dir = self._cache_dir
        if cache_dir is None:
            return None
        return cache_dir / "mgnipy_manifest.json"

    def write_results(self, request_num: int, items: Any) -> None:
        """Auto atomic write to disk."""
        save_to = self._cache_dir
        if save_to is None:
            logging.debug(
                "Skipping cache write for %s page %s because cache is disabled",
                self._resource_val,
                request_num,
            )
            return

        logging.info("Writing cached results for page %s", request_num)
        save_to.mkdir(parents=True, exist_ok=True)

        filepath = save_to / f"mgnipy_page_{request_num}.json"
        manifest_path = self._manifest_path
        logging.info(
            f"Writing page {request_num} to {filepath} and manifest to {manifest_path}"
        )

        manifest = {
            "resource": self._resource_val,
            "params": self._params_getter(),
            "count": self._total_records,
            "total_pages": self._total_requests,
        }

        atomic_write_json(filepath, items)
        if manifest_path is not None:
            atomic_write_json(manifest_path, manifest)

    async def awrite_results(self, request_num: int, items: Any) -> None:
        """Async wrapper for write_results."""
        logging.debug("Asynchronously writing cached results for page %s", request_num)
        await asyncio.to_thread(self.write_results, request_num, items)

    def load_cache_results(self) -> list[int]:
        """Load cached pages into self._results. Returns count loaded."""
        load_from = self._cache_dir
        if load_from is None:
            logging.debug(
                "Skipping cache load for %s because cache is disabled",
                self._resource_val,
            )
            return []

        logging.info(f"Loading cached pages from {load_from}")
        if not load_from.exists():
            logging.info(f"No cache directory found at {load_from}")
            return []

        pages_loaded = []
        for cache_file in sorted(load_from.glob("mgnipy_page_*.json")):
            logging.info(f"Loading cached page from {cache_file}")
            try:
                # read in pg data
                with cache_file.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                # Extract page number from filename
                request_num = int(cache_file.stem.split("_")[-1])
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
        if mpath is None:
            return {}
        if mpath.exists():
            logging.info(f"Loading cache manifest from {mpath}")
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
        load_from = self._cache_dir
        if load_from is None:
            logging.debug(
                "Skipping cache load for %s because cache is disabled",
                self._resource_val,
            )
            return []

        logging.info(f"Loading cache for {self._resource_val} from {self._cache_dir}")
        pages_loaded = self.load_cache_results()
        self.load_cache_manifest()
        logging.info(f"Loaded {len(pages_loaded)} cached pages")
        return pages_loaded

    async def aload_cache(self) -> int:
        """Async wrapper for load_cache."""
        return await asyncio.to_thread(self.load_cache)

    def clear_cache(self) -> None:
        """Remove all cached pages for this query."""
        load_from = self._cache_dir
        if load_from is None:
            return
        if load_from.exists():
            logging.info("Clearing cache directory %s", load_from)
            for cache_file in load_from.iterdir():
                # extra check just in case
                if cache_file.name == "mgnipy_manifest.json" or (
                    cache_file.name.startswith("mgnipy_page_")
                    and cache_file.suffix == ".json"
                ):
                    try:
                        logging.debug("Deleting cache file %s", cache_file)
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
        logging.debug("Building tree from %s lineages", len(self.lineages))
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
        logging.info("Showing tree using method %s", method)
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

    @property
    def results(self) -> dict:
        """Get results and auto-normalize lineage field."""
        parent_results = super().results
        # Always normalize if results exist
        if parent_results:
            logging.debug("Normalizing lineage fields in results")
            self._normalise_lineage()
        return parent_results

    def _normalise_lineage(self):
        """
        Rename field "lineage" to "biome_lineage" for consistency with other resources.
        """
        if self._results:
            logging.debug("Renaming lineage fields to biome_lineage")
            for page_data in self._results.values():
                if isinstance(page_data, list):
                    for record in page_data:
                        if isinstance(record, dict) and "lineage" in record:
                            record["biome_lineage"] = record.pop("lineage")
