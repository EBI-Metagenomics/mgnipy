from __future__ import annotations

import asyncio
import hashlib
import io
import json
import logging

logger = logging.getLogger(__name__)
import webbrowser
import zlib
from http.client import IncompleteRead
from itertools import chain
from pathlib import Path
from typing import Any, Callable, Generator, Literal, Optional

import httpx
import ijson
import pandas as pd
import polars as pl
from bigtree import Tree
from pydantic import HttpUrl
from skbio.io import read

from mgnipy._models.config import MGnipyConfig
from mgnipy._shared_helpers.biosamples_helper import (
    get_biosample_metadata_from_acc,
)
from mgnipy._shared_helpers.writers import atomic_write_bytes, atomic_write_json


class ResultsHandler:

    def __init__(self, data: Optional[chain[dict[str, Any]]] = None):
        logger.debug("Initializing ResultsHandler")
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

        cols = cols or [
            "metadata",
            "sample",
            "study",
            "biome",
            "run",
            "assembly",
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
        >>> df = handler.to_df()
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
            logger.debug("No data available for pandas DataFrame conversion")
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

        logger.debug("Returning pandas DataFrame without nested expansion")

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
        return self.to_df(data, expand_nested_dicts=False).to_json(
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

        # first convert to pandas and then to polars to leverage the nested dict expansion and column renaming already implemented in to_df
        df_pd = self.to_df(
            data=_data,
            expand_nested_dicts=expand_nested_dicts,
            rename_columns=rename_columns,
        )

        return pl.from_pandas(df_pd, **polars_kwargs)


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
        logger.debug("Initializing DiskCheckpointer for %s", resource_str)
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
        logger.debug("Computed cache key for %s: %s", self._resource_val, cache_key)
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
            logger.debug(
                "Skipping cache write for %s page %s because cache is disabled",
                self._resource_val,
                request_num,
            )
            return

        logger.info("Writing cached results for page %s", request_num)
        save_to.mkdir(parents=True, exist_ok=True)

        filepath = save_to / f"mgnipy_page_{request_num}.json"
        manifest_path = self._manifest_path
        logger.info(
            f"Writing page {request_num} to {filepath} and manifest to {manifest_path}"
        )
        manifest = {
            "resource": self._resource_val,
            "params": self._params_getter(),
            "count": self._total_records,
            "total_pages": self._total_requests,
        }

        # Write bytes (binary downloads) using atomic_write_bytes, otherwise JSON
        try:
            if isinstance(items, (bytes, bytearray)):
                bin_path = filepath.with_suffix(".bin")
                atomic_write_bytes(bin_path, bytes(items))
            else:
                atomic_write_json(filepath, items)
        except Exception:
            logger.warning(f"Failed to write cache file for page {request_num}")
        if manifest_path is not None:
            atomic_write_json(manifest_path, manifest)

    async def awrite_results(self, request_num: int, items: Any) -> None:
        """Async wrapper for write_results."""
        logger.debug("Asynchronously writing cached results for page %s", request_num)
        await asyncio.to_thread(self.write_results, request_num, items)

    def load_cache_results(self) -> list[int]:
        """Load cached pages into self._results. Returns count loaded."""
        load_from = self._cache_dir
        if load_from is None:
            logger.debug(
                "Skipping cache load for %s because cache is disabled",
                self._resource_val,
            )
            return []

        logger.info(f"Loading cached pages from {load_from}")
        if not load_from.exists():
            logger.info(f"No cache directory found at {load_from}")
            return []

        pages_loaded = []
        for cache_file in sorted(load_from.glob("mgnipy_page_*.*")):
            if cache_file.suffix not in {".json", ".bin"}:
                continue
            logger.info(f"Loading cached page from {cache_file}")
            try:
                if cache_file.suffix == ".bin":
                    with cache_file.open("rb") as fh:
                        data = fh.read()
                else:
                    with cache_file.open("r", encoding="utf-8") as fh:
                        data = json.load(fh)
                # Extract page number from filename
                request_num = int(cache_file.stem.split("_")[-1])
                # load page if avail in cache
                self._results[request_num] = data
                # tracking
                pages_loaded.append(request_num)
            except Exception:
                logger.warning(f"Failed to load cache file: {cache_file}")

        return pages_loaded

    def load_cache_manifest(self) -> dict:
        # Load manifest if present
        mpath = self._manifest_path
        if mpath is None:
            return {}
        if mpath.exists():
            logger.info(f"Loading cache manifest from {mpath}")
            try:
                with mpath.open("r", encoding="utf-8") as fh:
                    manifest = json.load(fh)
                    self._total_records = manifest.get("count")
                    self._total_requests = manifest.get("total_pages")
            except Exception:
                logger.warning(f"Failed to load manifest file: {mpath}")
                manifest = {}
        else:
            manifest = {}
        return manifest

    def load_cache(self) -> int:
        load_from = self._cache_dir
        if load_from is None:
            logger.debug(
                "Skipping cache load for %s because cache is disabled",
                self._resource_val,
            )
            return []

        logger.info(f"Loading cache for {self._resource_val} from {self._cache_dir}")
        pages_loaded = self.load_cache_results()
        self.load_cache_manifest()
        logger.info(f"Loaded {len(pages_loaded)} cached pages")
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
            logger.info("Clearing cache directory %s", load_from)
            for cache_file in load_from.iterdir():
                # extra check just in case
                if cache_file.name == "mgnipy_manifest.json" or (
                    cache_file.name.startswith("mgnipy_page_")
                    and cache_file.suffix in {".json", ".bin"}
                ):
                    try:
                        logger.debug("Deleting cache file %s", cache_file)
                        cache_file.unlink()
                    except Exception:
                        logger.warning(f"Failed to delete cache file: {cache_file}")
            try:
                load_from.rmdir()
            except Exception:
                logger.warning(f"Failed to delete cache directory: {load_from}")


class StreamMixin:
    """
    Mixin providing streaming helpers for downloads.

    # TODO remove below dependencies on mgnifier
    This mixin assumes the host class provides the following helpers/properties:
    - `_mgnifier_helper(url, cache_dir=None)` returning an object with
      `.exec.httpx_client` and `.exec.httpx_aclient` attributes
    - `_get_type_by_alias(alias)` to resolve file types
    - `downloads_df` when needed for examples/tests

    The implementation mirrors the streaming helpers previously defined
    on :class:`MGazine` so they can be reused by other classes.
    """

    def __init__(self, mgnifier_helper=None):
        self._mgnifier_helper = mgnifier_helper or getattr(
            self, "_mgnifier_helper", None
        )

    def _handle_incomplete_read(self, url: str):
        # self._download_helper = DownloadMixin(self._mgnifier_helper)
        # TODO
        logger.warning(
            f"You can also download the file {url} using the 'download' method instead of streaming and then read it into memory from disk, which may be more reliable for unstable connections."
        )
        raise IncompleteRead(
            f"Incomplete read error encountered when streaming {url}. This may be due to a network issue or server timeout. Consider retrying the request or checking your connection."
        ) from None

    def stream_pandas(
        self,
        url: str,
        sep: str = "\t",
        chunksize: Optional[int] = None,
        max_skip: int = 5,
        low_memory: bool = False,
        **pd_kwargs,
    ) -> pd.DataFrame | pd.io.parsers.readers.TextFileReader:
        """
        Read a TSV from a URL or local file with resilient header handling.

        The helper will retry with increasing ``skiprows`` when ``pandas``
        raises a ``ParserError`` (useful for files with extra header lines).
        When ``chunksize`` is provided an iterator is returned.

        Parameters
        ----------
        url : str
            The URL or local file path to read the TSV from.
        sep : str
            The delimiter to use (default is tab).
        chunksize : int or None
            If an integer is provided, returns an iterator that yields DataFrames
            of that many rows. If None, returns a single DataFrame.
        max_skip : int
            The maximum number of lines to skip when trying to parse the TSV.
        **pd_kwargs
            Additional keyword arguments passed to ``pd.read_csv``.

        Returns
        -------
        pd.DataFrame or TextFileReader
            A DataFrame containing the TSV data, or an iterator yielding DataFrames
            if ``chunksize`` is specified.

        Raises
        ------
        ValueError
            If ``chunksize`` is not a positive integer or None.
        RuntimeError
            If the TSV cannot be parsed after skipping up to ``max_skip`` lines.
        Pandas ParserError
            If the TSV cannot be parsed due to a format error (after retries).
        """

        for skip in range(max_skip + 1):
            try:
                return pd.read_csv(
                    url,
                    sep=sep,
                    chunksize=chunksize,
                    skiprows=skip if skip > 0 else None,
                    low_memory=low_memory,
                    **pd_kwargs,
                )
            except pd.errors.ParserError:
                continue  # Try next skiprows value
            except IncompleteRead:
                self._handle_incomplete_read(url)
            except Exception as err:
                raise RuntimeError(
                    f"Error reading file from {url} with skiprows={skip}"
                ) from err
        raise pd.errors.ParserError(
            f"Failed to parse {url} after skipping up to {max_skip} rows."
        )

    def stream_polars(
        self,
        url: str,
        sep: str = "\t",
        chunksize: Optional[int] = None,
        max_skip: int = 5,
        low_memory: bool = False,
        **pl_kwargs,
    ):
        """
        Read a TSV from a URL or local file into a Polars DataFrame with resilient header handling.

        The helper will retry with increasing ``skip_rows`` when Polars raises an error
        (useful for files with extra header lines). When ``chunksize`` is provided an iterator is returned.

        Parameters
        ----------
        url : str
            The URL or local file path to read the TSV from.
        sep : str
            The delimiter to use (default is tab).
        chunksize : int or None
            If an integer is provided, returns an iterator that yields DataFrames
            of that many rows. If None, returns a single DataFrame.
        max_skip : int
            The maximum number of lines to skip when trying to parse the TSV.
        **pl_kwargs
            Additional keyword arguments passed to ``pl.read_csv``.

        Returns
        -------
        pl.DataFrame or Iterator[pl.DataFrame]
            A Polars DataFrame containing the TSV data, or an iterator yielding DataFrames
            if ``chunksize`` is specified.

        Raises
        ------
        ValueError
            If ``chunksize`` is not a positive integer or None.
        RuntimeError
            If the TSV cannot be parsed after skipping up to ``max_skip`` lines.
        Polars Error
            If the TSV cannot be parsed due to a format error (after retries).
        """

        if chunksize is None:
            the_chosen = pl.read_csv
        else:
            the_chosen = pl.scan_csv

        for skip in range(max_skip + 1):
            try:
                return the_chosen(
                    url,
                    separator=sep,
                    skip_rows_after_header=skip,
                    truncate_ragged_lines=True,
                    infer_schema_length=10000,
                    low_memory=low_memory,
                    **pl_kwargs,
                )
            except pl.exceptions.PolarsError:
                continue  # Try next skip_rows value
            except IncompleteRead:
                self._handle_incomplete_read(url)
            except Exception as err:
                raise RuntimeError(
                    f"Error reading file from {url} with skip_rows_after_header={skip}"
                ) from err
        raise pl.exceptions.PolarsError(
            f"Failed to parse {url} after skipping up to {max_skip} rows."
        )

    def stream_html(self, url: str, **web_kwargs) -> bool:
        """
        Open an HTML URL in the default web browser.

        Parameters
        ----------
        url : str
            The URL to open in the web browser.
        **web_kwargs
            Additional keyword arguments passed to `webbrowser.open()`, such as `new` and `autoraise`.

        Returns
        -------
        bool
            True if the URL was opened successfully, False otherwise.
        """

        return webbrowser.open(url, **web_kwargs)

    def stream_txt(
        self,
        url: str,
        chunksize: Optional[int] = None,
        httpx_client: Optional[httpx.Client] = None,
        **httpx_kwargs,
    ) -> str | Generator:
        """
        Stream a plain-text resource.
        When ``chunksize`` is ``None`` the full text is returned as a string.
        When ``chunksize`` is an integer the function yields lists of lines.

        Parameters
        ----------
        url : str
            The URL to stream the text from.
        chunksize : int or None
            If an integer is provided, yields lists of lines of that size. If None, yields the entire text as a single string.
        httpx_client : httpx.Client, optional
            An optional httpx.Client to use for the request. If None, a new client will be created for the request.
        **httpx_kwargs
            Additional keyword arguments passed to the httpx.Client.request() method

        Returns
        -------
        str or Generator
            The full text as a string if chunksize is None, or a generator yielding lists of lines if chunksize is an integer.
        """

        client = httpx_client or self._mgnifier_helper().exec.httpx_client

        if chunksize is None:
            # load as whole
            with client.get(url, **httpx_kwargs) as response:
                response.raise_for_status()
                return response.text
        elif isinstance(chunksize, int) and chunksize > 0:
            # load in chunks
            with client.stream("GET", url, **httpx_kwargs) as response:
                response.raise_for_status()
                chunk = []
                for line in response.iter_text():
                    chunk.append(line)
                    if len(chunk) == chunksize:
                        yield chunk
                        chunk = []
                if chunk:
                    yield chunk
        else:
            raise ValueError("`chunksize` must be a positive integer or None.")

    def stream_fasta(self, url: str, **skbio_kwargs) -> Generator:
        """
        Stream a FASTA file from a URL using scikit-bio's read function. Refer there for more info.

        Parameters
        ----------
        url : str
            The URL to the FASTA file to stream.
        **skbio_kwargs
            Additional keyword arguments passed to `skbio.io.read()`, such as `into` and `verify`.

        Returns
        -------
        Generator
            A generator yielding scikit-bio Sequence objects parsed from the FASTA file.
        """
        return read(url, format="fasta", **skbio_kwargs)

    def stream_gff(self, url: str, **skbio_kwargs) -> Generator:
        """
        Stream a GFF file from a URL using scikit-bio's read function. Refer there for more info.

        Parameters
        ----------
        url : str
            The URL to the GFF file to stream.
        **skbio_kwargs
            Additional keyword arguments passed to `skbio.io.read()`, such as `into` and `verify`.

        Returns
        -------
        Generator
            A generator yielding scikit-bio Sequence objects parsed from the GFF file.
        """
        return read(url, format="gff3", **skbio_kwargs)

    def stream_biom(self, url: str, **skbio_kwargs) -> Generator:
        """
        Stream a biom file from a URL using scikit-bio's read function. Refer there for more info.

        Parameters
        ----------
        url : str
            The URL to the biom file to stream.
        **skbio_kwargs
            Additional keyword arguments passed to `skbio.io.read()`, such as `into` and `verify`.

        Returns
        -------
        Generator
            A generator yielding scikit-bio Sequence objects parsed from the biom file.
        """
        return read(url, format="biom", **skbio_kwargs)

    def stream_gzipped(
        self,
        url: str,
        chunksize: Optional[int] = None,
        httpx_client: Optional[httpx.Client] = None,
        decode: bool = False,
        encoding: str = "utf-8",
        errors: str = "replace",
        **httpx_kwargs,
    ) -> bytes | str | io.BufferedReader | io.TextIOWrapper:
        """Stream a gzipped HTTP resource and present a file-like interface.

        When ``chunksize`` is None the entire compressed payload is fetched
        and decompressed into memory. When ``chunksize`` is provided a
        streaming file-like object is returned.
        """

        client = httpx_client or self._mgnifier_helper().exec.httpx_client
        logger.debug(
            "stream_gzipped called url=%s chunksize=%s decode=%s",
            url,
            chunksize,
            decode,
        )

        if chunksize is None:
            logger.debug("Using full-download mode (chunksize=None)")
            r = client.get(url, timeout=None, **httpx_kwargs)
            r.raise_for_status()
            decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
            data = decompressor.decompress(r.content) + decompressor.flush()
            logger.debug(
                "Full-download mode complete: compressed=%d decompressed=%d",
                len(r.content),
                len(data),
            )
            return data.decode(encoding, errors=errors) if decode else data

        if not isinstance(chunksize, int) or chunksize <= 0:
            raise ValueError("`chunksize` must be a positive integer or None.")

        class _HTTPGzipRaw(io.RawIOBase):
            def __init__(self):
                self._cm = client.stream("GET", url, timeout=None, **httpx_kwargs)
                self._resp = self._cm.__enter__()
                self._resp.raise_for_status()
                self._iter = self._resp.iter_raw(chunk_size=chunksize)
                self._decomp = zlib.decompressobj(16 + zlib.MAX_WBITS)
                self._buf = bytearray()
                self._eof = False
                self._flushed = False
                logger.debug("Streaming HTTP/gzip reader initialized")

            def readable(self) -> bool:
                return True

            def _fill(self, need: int) -> None:
                while len(self._buf) < need and not self._eof:
                    try:
                        chunk = next(self._iter)
                    except StopIteration:
                        if not self._flushed:
                            tail = self._decomp.flush()
                            if tail:
                                self._buf.extend(tail)
                            self._flushed = True
                        self._eof = True
                        logger.debug("Reached end of HTTP stream")
                        break

                    if chunk:
                        out = self._decomp.decompress(chunk)
                        if out:
                            self._buf.extend(out)

            def readinto(self, b) -> int:
                if self.closed:
                    return 0
                mv = memoryview(b)
                self._fill(len(mv))
                n = min(len(mv), len(self._buf))
                if n <= 0:
                    return 0
                mv[:n] = self._buf[:n]
                del self._buf[:n]
                return n

            def close(self) -> None:
                if not self.closed:
                    try:
                        self._cm.__exit__(None, None, None)
                    finally:
                        super().close()
                        logger.debug("Streaming HTTP/gzip reader closed")

        raw = _HTTPGzipRaw()
        buffered = io.BufferedReader(raw, buffer_size=chunksize)

        if decode:
            return io.TextIOWrapper(buffered, encoding=encoding, errors=errors)

        return buffered

    def stream_jsonl(
        self,
        url: str,
        orient: Optional[
            Literal["records", "split", "index", "columns", "values", "table"]
        ] = None,
        chunksize: Optional[int] = None,
        dataframe_engine: Optional[Literal["pandas", "polars"]] = "pandas",
        **df_kwargs,
    ) -> dict:
        if dataframe_engine == "pandas":
            return pd.read_json(
                url, orient=orient, lines=True, chunksize=chunksize, **df_kwargs
            )
        elif dataframe_engine == "polars":
            if chunksize is None:
                return pl.read_ndjson(url, infer_schema_length=10000, **df_kwargs)
            else:
                return pl.scan_ndjson(url, infer_schema_length=10000, **df_kwargs)

    def stream_json(
        self,
        url: str,
        chunksize: Optional[int] = None,
        httpx_client: Optional[httpx.Client] = None,
        **httpx_kwargs,
    ) -> dict | Generator:
        client = httpx_client or self._mgnifier_helper().exec.httpx_client

        if chunksize is None and not (url.endswith(".gz") or url.endswith(".gzip")):
            with client.get(url, **httpx_kwargs) as response:
                response.raise_for_status()
                return response.json()
        elif chunksize is not None and not (
            url.endswith(".gz") or url.endswith(".gzip")
        ):
            with client.stream("GET", url, **httpx_kwargs) as response:
                response.raise_for_status()
                for entry in ijson.kvitems(response.iter_text(), ""):
                    yield entry
        elif url.endswith(".gz") or url.endswith(".gzip"):
            with self.stream_gzipped(
                url,
                chunksize=chunksize,
                httpx_client=client,
                decode=True,
                **httpx_kwargs,
            ) as gzipped_stream:
                for entry in ijson.kvitems(gzipped_stream, ""):
                    yield entry
        else:
            raise ValueError(f"Unsupported file type for URL: {url}")

    def _fix_inconsistent_cols(
        self, fields: list[str], pad_to: int = 15
    ) -> list[str] | None:
        """Pad or truncate list of fields to ``pad_to`` length.

        Parameters
        ----------
        fields : list of str
            List of column names to adjust.
        pad_to : int, optional
            Desired length of the returned list. Defaults to 15.

        Returns
        -------
        list of str or None
            The adjusted list of fields or ``None`` when ``pad_to`` is 0.
        """

        if len(fields) < pad_to:
            return fields + [""] * (pad_to - len(fields))
        if len(fields) > pad_to:
            return fields[:pad_to]
        return fields

    def stream_tree(self, url: str, **skbio_kwargs) -> Generator:
        return read(url, format="newick", **skbio_kwargs)

    def _get_streamer(
        self,
        alias: Optional[str] = None,
        url: Optional[HttpUrl] = None,
        chunksize: int = 1000,
        httpx_client: Optional[httpx.Client] = None,
        max_skip: int = 5,
        dataframe_engine: Optional[Literal["pandas", "polars"]] = "pandas",
        low_memory: bool = False,
        **kwargs,
    ):
        client = httpx_client or self._mgnifier_helper().exec.httpx_client

        _alias, _url = self._prioritize_alias(alias, url, required=True)
        file_type = self._get_type_by_alias(_alias)

        if dataframe_engine == "polars" and file_type == "tsv":
            return self.stream_polars(
                _url,
                sep="\t",
                chunksize=chunksize,
                max_skip=max_skip,
                low_memory=low_memory,
                **kwargs,
            )

        if dataframe_engine == "polars" and file_type == "csv":
            return self.stream_polars(
                _url,
                sep=",",
                chunksize=chunksize,
                max_skip=max_skip,
                low_memory=low_memory,
                **kwargs,
            )

        if file_type == "tsv":
            if _url.endswith(".gz") or _url.endswith(".gzip"):
                logger.debug(f"tsv file type ends with .gz: {_url}")
                try:
                    return self.stream_pandas(
                        _url,
                        chunksize=chunksize,
                        max_skip=max_skip,
                        compression="gzip",
                        **kwargs,
                    )
                except pd.errors.ParserError as e:
                    logger.error(f"ParserError: {e}")
                    return self.stream_pandas(
                        _url,
                        chunksize=chunksize,
                        max_skip=max_skip,
                        compression="gzip",
                        engine="python",
                        on_bad_lines=self._fix_inconsistent_cols,
                        **kwargs,
                    )
            elif _url.endswith(".txt") or _url.endswith(".tsv"):
                return self.stream_pandas(
                    _url,
                    chunksize=chunksize,
                    max_skip=max_skip,
                    low_memory=low_memory,
                    **kwargs,
                )

        if file_type == "csv":
            return self.stream_pandas(
                _url,
                sep=",",
                chunksize=chunksize,
                max_skip=max_skip,
                low_memory=low_memory,
                **kwargs,
            )

        if file_type == "html":
            return lambda: self.stream_html(_url, **kwargs)

        if file_type == "txt":
            return self.stream_txt(
                _url, chunksize=chunksize, httpx_client=client, **kwargs
            )

        if file_type == "gff":
            return self.stream_gff(_url, **kwargs)
        if file_type == "biom":
            return self.stream_biom(_url, **kwargs)
        if file_type == "fasta":
            return self.stream_fasta(_url, **kwargs)
        if file_type == "tree":
            return self.stream_tree(_url, **kwargs)
        if file_type == "json":
            return self.stream_jsonl(
                _url,
                orient="records",
                chunksize=chunksize,
                dataframe_engine=dataframe_engine,
                low_memory=low_memory,
                **kwargs,
            )
        if file_type == "other" and ".json" in _url:
            if _url.endswith("json.gz") or _url.endswith("json.gzip"):
                return self.stream_json(
                    _url, chunksize=chunksize, httpx_client=client, **kwargs
                )

            logger.info(
                f"{_alias} is only available for download (e.g., `.download({_alias}))`"
            )
            logger.debug(
                f"Alias: {_alias}\nURL: {_url}\nFile type: {file_type}. Only '.json' files can be streamed under 'other' type, otherwise this download is only available for download."
            )
        else:
            raise ValueError(f"Unsupported file type for streaming: {file_type}")

    def stream(
        self,
        *,
        alias: Optional[str] = None,
        url: Optional[HttpUrl] = None,
        chunksize: Optional[int] = None,
        max_skip: int = 5,
        **kwargs,
    ) -> Any:
        """
        Streams a single download based on its alias or url.

        If ``chunksize`` is specified then iterators of dataframes or strings
        will be returned; otherwise the full data will be returned as a single
        object.

        Supported formats and their handlers
        ------------------------------------
        - tsv: handled by :meth:`stream_pandas` (pandas) or :meth:`stream_polars` (polars).
          Gzipped TSVs are supported via the gzip/compression options.
        - csv: handled by :meth:`stream_pandas` / :meth:`stream_polars` (sep=",").
        - txt: handled by :meth:`stream_txt` (returns full text or yields line chunks).
        - html: handled by :meth:`stream_html` (opens URL in browser).
        - fasta: handled by :meth:`stream_fasta` (scikit-bio generator).
        - gff: handled by :meth:`stream_gff` (scikit-bio generator).
        - biom: handled by :meth:`stream_biom` (scikit-bio generator).
        - gzipped HTTP resources: use :meth:`stream_gzipped` for a file-like object,
          or :meth:`stream_json` for gzipped JSON content.
        - jsonl / ndjson: handled by :meth:`stream_jsonl` (pandas or polars modes).
        - json: handled by :meth:`stream_json` (returns full JSON or streams via ijson).
        - tree/newick: handled by :meth:`stream_tree` (scikit-bio newick reader).
        - other: if the URL ends with ``.json`` it's streamed via :meth:`stream_json`;
          otherwise use the download helper for unsupported binary formats.

        Parameters
        ----------
        alias : Optional[str]
            The alias of the download to stream.
        url : Optional[HttpUrl]
            The url of the download to stream.
        chunksize : Optional[int]
            The size of the chunks to read from the stream.
        max_skip : int, optional
            The maximum number of rows to skip before raising an error. Default is 5.
        **kwargs
            Additional keyword arguments to pass to the streamer function.

        Returns
        -------
        Any
            The streamer result for the resolved alias or url.
        """
        # resolve a single alias/url target
        _alias, _url = self._prioritize_alias(alias, url, required=True)

        # return a single streamer result, not a dict of all streams
        client = self._mgnifier_helper().exec.httpx_client
        logger.info("Setting up stream for alias=%s url=%s", _alias, _url)

        try:
            return self._get_streamer(
                alias=_alias,
                url=_url,
                chunksize=chunksize,
                httpx_client=client,
                max_skip=max_skip,
                **kwargs,
            )
        except httpx.HTTPError as err:
            logger.error("HTTP error for alias=%s url=%s: %s", _alias, _url, err)
            raise


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
        logger.debug("Building tree from %s lineages", len(self.lineages))
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
        logger.info("Showing tree using method %s", method)
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
            logger.debug("Normalizing lineage fields in results")
            self._normalise_lineage()
        return parent_results

    def _normalise_lineage(self):
        """
        Rename field "lineage" to "biome_lineage" for consistency with other resources.
        """
        if self._results:
            logger.debug("Renaming lineage fields to biome_lineage")
            for page_data in self._results.values():
                if isinstance(page_data, list):
                    for record in page_data:
                        if isinstance(record, dict) and "lineage" in record:
                            record["biome_lineage"] = record.pop("lineage")


class BioSamplesMetadataMixin:

    def __init__(self):
        self._cache_biosamples_w_ena: pd.DataFrame | None = None
        self._cache_biosamples_no_ena: pd.DataFrame | None = None
        self._cache_biosamples_details_w_ena: pd.DataFrame | None = None
        self._cache_biosamples_details_no_ena: pd.DataFrame | None = None

    def details_biosamples_metadata(
        self, incl_ena: bool = True, overwrite: bool = False
    ) -> pd.DataFrame:
        """
        A pandas DataFrame containing the concatenated BioSamples metadata for all samples in the list.
        Each row corresponds to a sample, and columns include 'SampleID', 'SRA accession', 'taxid', and any characteristics available for the samples.

        Parameters
        ----------
        incl_ena : bool, optional
            Whether to include ENA-specific metadata fields in the resulting DataFrame. Defaults to True.
        overwrite : bool, optional
            Whether to overwrite the cached DataFrame if it already exists. Defaults to False.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the BioSamples metadata for all samples in the list.

        Notes
        -----
        - This property relies on the `biosample_metadata` property of each `SampleDetail` instance, which retrieves the BioSamples metadata for each sample accession.
        - The resulting DataFrame is constructed by concatenating the individual DataFrames for each sample, and if each sample has different characteristics, the resulting DataFrame will have columns for all unique characteristics across the samples, with missing values filled as NaN.
        """

        if (
            incl_ena
            and self._cache_biosamples_details_w_ena is not None
            and not overwrite
        ):
            logger.debug("Using cached BioSamples metadata with ENA fields for details")
            return self._cache_biosamples_details_w_ena

        if (
            not incl_ena
            and self._cache_biosamples_details_no_ena is not None
            and not overwrite
        ):
            logger.debug(
                "Using cached BioSamples metadata without ENA fields for details"
            )
            return self._cache_biosamples_details_no_ena

        if incl_ena:
            logger.debug("Fetching BioSamples metadata with ENA fields for details")
            self._cache_biosamples_details_w_ena = pd.concat(
                [
                    detail.biosamples_metadata(incl_ena=incl_ena, overwrite=overwrite)
                    for detail in self.details
                ],
                ignore_index=True,
            )
            return self._cache_biosamples_details_w_ena
        else:
            logger.debug("Fetching BioSamples metadata without ENA fields for details")
            self._cache_biosamples_details_no_ena = pd.concat(
                [
                    detail.biosamples_metadata(incl_ena=incl_ena, overwrite=overwrite)
                    for detail in self.details
                ],
                ignore_index=True,
            )
            return self._cache_biosamples_details_no_ena

    def biosamples_metadata(
        self, incl_ena: bool = True, overwrite: bool = False
    ) -> pd.DataFrame:
        """
        A pandas DataFrame containing the BioSamples metadata for the sample associated with this `SampleDetail` instance, based on its accession. The DataFrame includes columns such as 'SampleID', 'SRA accession', 'taxid', and any characteristics available for the sample.

        Parameters
        ----------
        incl_ena : bool, optional
            Whether to include ENA-specific metadata fields in the resulting DataFrame. Defaults to True.
        overwrite : bool, optional
            Whether to overwrite the cached DataFrame if it already exists. Defaults to False.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the BioSamples metadata for the sample associated with this `SampleDetail` instance.

        Notes
        -----
        - This property retrieves the BioSamples metadata for the sample accession using the `get_biosample_metadata_from_acc` function, which queries the BioSamples API and constructs a DataFrame with the relevant metadata fields.
        - The resulting DataFrame will have a single row corresponding to the sample accession, and columns for 'SampleID', 'SRA accession', 'taxid', and any characteristics available for the sample, with missing values filled as 'NA'.
        """

        if incl_ena and self._cache_biosamples_w_ena is not None and not overwrite:
            logger.debug(
                f"Using cached BioSamples metadata with ENA fields for {self.identifier}"
            )
            return self._cache_biosamples_w_ena

        if not incl_ena and self._cache_biosamples_no_ena is not None and not overwrite:
            logger.debug(
                f"Using cached BioSamples metadata without ENA fields for {self.identifier}"
            )
            return self._cache_biosamples_no_ena

        if incl_ena:
            logger.debug(
                f"Fetching BioSamples metadata with ENA fields for {self.identifier}"
            )
            self._cache_biosamples_w_ena = get_biosample_metadata_from_acc(
                self.identifier, incl_ena=incl_ena, overwrite=overwrite
            )
            return self._cache_biosamples_w_ena
        else:
            logger.debug(
                f"Fetching BioSamples metadata without ENA fields for {self.identifier}"
            )
            self._cache_biosamples_no_ena = get_biosample_metadata_from_acc(
                self.identifier, incl_ena=incl_ena, overwrite=overwrite
            )
            return self._cache_biosamples_no_ena
