import asyncio
import io
import logging
import warnings
import webbrowser
import zlib
from pathlib import Path
from typing import (
    Callable,
    Generator,
    Literal,
    Optional,
)

import aiofiles
import httpx
import ijson
import pandas as pd
from pydantic import (
    DirectoryPath,
    HttpUrl,
)
from requests.exceptions import HTTPError
from skbio.io import read
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm as tqdm_async

from mgnipy._models.config import MgnipyConfig
from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy.emgapi_v2_client.api.analyses import (
    analysis_get_mgnify_analysis_with_annotations,
)
from mgnipy.emgapi_v2_client.models.m_gnify_analysis_with_annotations import (
    MGnifyAnalysisWithAnnotations,
)
from mgnipy.V2.core import MGnifier

semaphore = get_semaphore()
BASE_URL = MgnipyConfig().base_url


class MGazine(MGnifyAnalysisWithAnnotations):
    """More so an extended data class"""

    def __init__(self, accession: str):
        # mgnifier TODO handing private data
        self._mgnifier_helper = MGnifier(accession=accession)
        # set endpoint
        self._mgnifier_helper.endpoint_module = (
            analysis_get_mgnify_analysis_with_annotations
        )
        # get the data
        self._mgnifier_helper.get()
        # init with the data
        super().__init__(**self._mgnifier_helper.results[0][0])

    @property
    def url_dict(self) -> dict[str, dict]:
        """returns a dict of alias: url for all downloads"""
        return {f["alias"]: f.get("url", None) for f in self.downloads}

    @property
    def downloads_df(self) -> pd.DataFrame:
        """returns a dataframe of all downloads with columns alias, url, file_type"""
        return pd.DataFrame(self.downloads)

    @property
    def url_list(self):
        """returns a list of all download urls"""
        return [f.get("url", None) for f in self.downloads]

    def _get_url_by_alias(
        self, alias: str, df: Optional[pd.DataFrame] = None
    ) -> Optional[str]:
        """
        Gets the download url for a given alias

        Parameters
        ----------
        alias : str
            The alias of the download.
        df : Optional[pd.DataFrame], optional
            The dataframe to query. If None, uses the downloads_df property.

        Returns
        -------
        Optional[str]
            The download url for the given alias, or None if not found.
        """
        df = df or self.downloads_df
        try:
            return df.query(f"alias == '{alias}'")["url"].values[0]
        except RuntimeError as err:
            raise KeyError(f"Issue getting download url for alias: {alias}") from err

    def _get_alias_by_url(
        self, url: HttpUrl, df: Optional[pd.DataFrame] = None
    ) -> Optional[str]:
        """
        Gets the alias for a given download url

        Parameters
        ----------
        url : HttpUrl
            The url of the download.
        df : Optional[pd.DataFrame], optional
            The dataframe to query. If None, uses the downloads_df property.

        Returns
        -------
        Optional[str]
            The alias for the given url, or None if not found.
        """
        df = df or self.downloads_df
        try:
            return df.query(f"url == '{url}'")["alias"].values[0]
        except RuntimeError as err:
            raise KeyError(f"Issue getting alias for url: {url}") from err

    def _get_type_by_alias(
        self, alias: str, df: Optional[pd.DataFrame] = None
    ) -> Optional[str]:
        """
        Gets the file type for a given alias

        Parameters
        ----------
        alias : str
            The alias of the download.
        df : Optional[pd.DataFrame], optional
            The dataframe to query. If None, uses the downloads_df property.

        Returns
        -------
        Optional[str]
            The file type for the given alias, or None if not found.
        """
        df = df or self.downloads_df
        try:
            return df.query(f"alias == '{alias}'")["file_type"].values[0]
        except RuntimeError as err:
            raise KeyError(f"Issue getting file type for alias: {alias}") from err

    def _prioritize_alias(
        self,
        alias: Optional[str],
        url: Optional[HttpUrl],
        required: bool = False,
    ) -> tuple[str, HttpUrl]:
        """
        Prioritizes alias over url. If both are provided, alias is used and url is ignored with a warning.

        Parameters
        ----------
        alias : Optional[str]
            The alias of the download.
        url : Optional[HttpUrl]
            The url of the download.
        required : bool, optional
            If required is True, raises an error if neither alias nor url is provided.

        Returns
        -------
        tuple[str, HttpUrl]
            A tuple of (alias, url) where alias is the prioritized alias and url is the corresponding url.
        """
        if alias and url:
            warnings.warn(
                "Both `alias` and `url` provided, ignoring `url`.", stacklevel=2
            )
            url = self._get_url_by_alias(alias)
        elif alias and not url:
            url = self._get_url_by_alias(alias)
        elif url and not alias:
            try:
                alias = self._get_alias_by_url(url)
            except KeyError:
                # to reuse download/adownload for other urls
                alias = None

        if required and not alias and not url:
            raise ValueError("Either `alias` or `url` must be provided.")

        return alias, url

    def stream_tsv(
        self,
        url: str,
        sep: str = "\t",
        chunksize: Optional[int] = None,
        max_skip: int = 5,
        **pd_kwargs,
    ) -> pd.DataFrame | pd.io.parsers.readers.TextFileReader:
        """
        Reads a tsv file from a url and returns an iterator of pandas dataframes.
        Handles potential issues with extra header rows (causing pd.errors.ParserError)
        by trying to read the file with increasing skiprows until it succeeds or reaches max_skip.

        Parameters
        ----------
        url : str
            The url of the tsv file to stream.
        sep : str, optional
            The separator used in the tsv file. Default is tab.
        chunksize : int, optional
            The number of rows to include in each chunk. Default is None.
        max_skip : int, optional
            The maximum number of rows to skip before raising an error. Default is 5.
        pd_kwargs : dict, optional
            Additional keyword arguments to pass to pandas read_csv.

        Returns
        -------
        pd.DataFrame | pd.io.parsers.readers.TextFileReader
            An iterator of pandas dataframes.
        """

        for skip in range(max_skip + 1):
            try:
                return pd.read_csv(
                    url,
                    sep=sep,
                    chunksize=chunksize,
                    skiprows=skip if skip > 0 else None,
                    **pd_kwargs,
                )
            except pd.errors.ParserError:
                continue  # Try next skiprows value
            except Exception as err:
                raise RuntimeError(
                    f"Error reading TSV from {url} with skiprows={skip}"
                ) from err
        raise pd.errors.ParserError(
            f"Failed to parse {url} after skipping up to {max_skip} rows."
        )

    def stream_html(self, url: str, **web_kwargs) -> bool:
        """
        Streams an html file from a url and opens it in the default web browser.

        Parameters
        ----------
        url : str
            The url of the html file to stream.
        web_kwargs : dict, optional
            Additional keyword arguments to pass to webbrowser.open.

        Returns
        -------
        bool
            True if the url was opened successfully, False otherwise.
        """
        return webbrowser.open(url, **web_kwargs)

    def stream_txt(
        self,
        url: str,
        chunksize: Optional[int] = None,
        httpx_client: Optional[httpx.Client] = None,
        **httpx_kwargs,
    ) -> Generator:
        """
        Streams a txt file from a url and returns an iterator of strings.

        Parameters
        ----------
        url : str
            The url of the txt file to stream.
        chunksize : Optional[int], optional
            The number of characters to include in each chunk. Default is None.
        httpx_kwargs : dict, optional
            Additional keyword arguments to pass to the httpx client.

        Returns
        -------
        Generator[str, None, None]
            An iterator of strings.
        """

        client = httpx_client or self._mgnifier_helper.httpx_client

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
        Streams a fasta file from a url and returns an iterator of tuples (header, sequence).

        Parameters
        ----------
        url : str
            The url of the fasta file to stream.
        skbio_kwargs : dict, optional
            Additional keyword arguments to pass to the skbio parsers.
            https://scikit.bio/docs/latest/generated/skbio.io.format.fasta.html

        Returns
        -------
        Generator[tuple[str, str], None, None]
            An iterator of tuples (header, sequence).
        """
        return read(url, format="fasta", **skbio_kwargs)

    def stream_gff(self, url: str, **skbio_kwargs) -> Generator:
        """
        Streams a gff file from a url and returns an iterator of parsed gff records.

        Parameters
        ----------
        url : str
            The url of the gff file to stream.
        skbio_kwargs : dict, optional
            Additional keyword arguments to pass to the skbio parser.
            https://scikit.bio/docs/latest/generated/skbio.io.format.gff3.html

        Returns
        -------
        Generator[skbio.io._gff3.GFF3Record, None, None]
            "generator of tuple (seq_id of str type, skbio.metadata.IntervalMetadata)"
        """
        return read(url, format="gff3", **skbio_kwargs)

    def stream_biom(self, url: str, **skbio_kwargs) -> Generator:
        """
        Streams a biom file from a url and returns an iterator of parsed biom records.

        Parameters
        ----------
        url : str
            The url of the biom file to stream.
        skbio_kwargs : dict, optional
            Additional keyword arguments to pass to the skbio parser.
        Returns
        -------
        Generator[dict, None, None]
            An iterator of parsed biom records as dictionaries.
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
        """
        Streams a gzipped file from a url and returns a file-like object that can be read in chunks.
        Written using GPT-5.3-Codex.
        Uses httpx for streaming and zlib for decompression.

        Parameters
        ----------
        url : str
            The url of the gzipped file to stream.
        chunksize : int, optional
            The size of each chunk to read from the stream.
        httpx_client : httpx.Client, optional
            The httpx client to use for streaming.
        decode : bool, default False
            Whether to decode the decompressed bytes to a string.
        encoding : str, default "utf-8"
            The encoding to use for decoding bytes to a string.
        errors : str, default "replace"
            The error handling strategy for decoding bytes to a string.
        **httpx_kwargs : dict
            Additional keyword arguments to pass to the httpx client.

        Returns
        -------
        bytes | str | io.BufferedReader | io.TextIOWrapper
            A file-like object that can be read in chunks.
            If `chunksize` is None, returns the full decompressed content as bytes,
            or string based on `decode`.
        """

        # Pick caller-provided client, or fallback to the shared MGnifier client.
        client = httpx_client or self._mgnifier_helper.httpx_client
        logging.debug(
            "stream_gzipped called url=%s chunksize=%s decode=%s",
            url,
            chunksize,
            decode,
        )

        # Backward-compatible mode: no chunksize means full download into memory.
        if chunksize is None:
            logging.debug("Using full-download mode (chunksize=None)")
            # Perform a normal blocking GET.
            r = client.get(url, timeout=None, **httpx_kwargs)
            # Raise if HTTP status is not 2xx.
            r.raise_for_status()
            # Create gzip-compatible streaming decompressor (16 + MAX_WBITS enables gzip header).
            decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
            # Decompress full payload bytes and flush remaining tail bytes.
            data = decompressor.decompress(r.content) + decompressor.flush()
            logging.debug(
                "Full-download mode complete: compressed=%d decompressed=%d",
                len(r.content),
                len(data),
            )
            # Return text if decode=True, else raw bytes.
            return data.decode(encoding, errors=errors) if decode else data

        # Validate chunksize for streaming mode.
        if not isinstance(chunksize, int) or chunksize <= 0:
            raise ValueError("`chunksize` must be a positive integer or None.")

        # Custom raw stream that adapts httpx streamed gzip bytes to a readable file-like object.
        class _HTTPGzipRaw(io.RawIOBase):
            def __init__(self):
                # Open streaming HTTP response context.
                self._cm = client.stream("GET", url, timeout=None, **httpx_kwargs)
                # Enter context manually so this object controls lifecycle.
                self._resp = self._cm.__enter__()
                # Fail fast on non-2xx.
                self._resp.raise_for_status()
                # Iterate compressed bytes in fixed-size network chunks.
                self._iter = self._resp.iter_raw(chunk_size=chunksize)
                # Incremental gzip decompressor.
                self._decomp = zlib.decompressobj(16 + zlib.MAX_WBITS)
                # Internal decompressed byte buffer.
                self._buf = bytearray()
                # End-of-stream marker.
                self._eof = False
                # Track whether decompressor.flush() has been called.
                self._flushed = False
                logging.debug("Streaming HTTP/gzip reader initialized")

            def readable(self) -> bool:
                # Required by BufferedReader to know this raw stream supports reading.
                return True

            def _fill(self, need: int) -> None:
                # Keep buffering until we have enough bytes or we hit EOF.
                while len(self._buf) < need and not self._eof:
                    try:
                        # Pull next compressed network chunk.
                        chunk = next(self._iter)
                    except StopIteration:
                        # Network stream finished; flush remaining decompressor tail once.
                        if not self._flushed:
                            tail = self._decomp.flush()
                            if tail:
                                self._buf.extend(tail)
                            self._flushed = True
                        # Mark EOF so future reads stop pulling.
                        self._eof = True
                        logging.debug("Reached end of HTTP stream")
                        break

                    # If chunk is non-empty, incrementally decompress and append output.
                    if chunk:
                        out = self._decomp.decompress(chunk)
                        if out:
                            self._buf.extend(out)

            def readinto(self, b) -> int:
                # If already closed, signal EOF.
                if self.closed:
                    return 0
                # Create writable view into caller-provided buffer.
                mv = memoryview(b)
                # Ensure internal buffer has enough data for requested read.
                self._fill(len(mv))
                # Compute how many bytes we can actually return.
                n = min(len(mv), len(self._buf))
                # No bytes available means EOF.
                if n <= 0:
                    return 0
                # Copy decompressed bytes into caller buffer.
                mv[:n] = self._buf[:n]
                # Remove consumed bytes from internal buffer.
                del self._buf[:n]
                # Return byte count copied.
                return n

            def close(self) -> None:
                # Close HTTP stream context exactly once.
                if not self.closed:
                    try:
                        self._cm.__exit__(None, None, None)
                    finally:
                        super().close()
                        logging.debug("Streaming HTTP/gzip reader closed")

        # Wrap raw stream in BufferedReader for efficient file-like reads.
        raw = _HTTPGzipRaw()
        buffered = io.BufferedReader(raw, buffer_size=chunksize)

        # If decode requested, wrap bytes stream as text stream.
        if decode:
            return io.TextIOWrapper(buffered, encoding=encoding, errors=errors)

        # Default return: binary buffered reader (works with ijson.kvitems).
        return buffered

    def stream_jsonl(
        self,
        url: str,
        orient: Optional[
            Literal["records", "split", "index", "columns", "values", "table"]
        ] = None,
        chunksize: Optional[int] = None,
        **pd_kwargs,
    ) -> dict:
        """
        Streams a jsonl file from a url and returns the parsed json as a dictionary.

        Parameters
        ----------
        url : str
            The url of the json file to stream.
        sep : str, optional
            The separator to use when parsing the json file. Default is "\t".
        chunksize : Optional[int], optional
            The size of the chunks to read from the stream. Default is None.
        max_skip : int, optional
            The maximum number of rows to skip before raising an error. Default is 5.
        **pd_kwargs : dict
            Additional keyword arguments to pass to the pandas parser.
        Returns
        -------
        dict
            The parsed json as a dictionary.
        """

        return pd.read_json(
            url, orient=orient, lines=True, chunksize=chunksize, **pd_kwargs
        )

    def stream_json(
        self,
        url: str,
        chunksize: Optional[int] = None,
        httpx_client: Optional[httpx.Client] = None,
        **httpx_kwargs,
    ) -> dict | Generator:
        """
        Streams a json file from a url and returns the parsed json as a dictionary or an iterator of dictionaries if chunksize is specified.

        Parameters
        ----------
        url : str
            The url of the json file to stream.
        chunksize : Optional[int], optional
            The size of the chunks to read from the stream. Default is None.
        **httpx_kwargs : dict
            Additional keyword arguments to pass to the httpx client.
        Returns
        -------
        dict | Generator
            The parsed json as a dictionary, or an iterator of dictionaries if chunksize is specified.
        """

        client = httpx_client or self._mgnifier_helper.httpx_client

        # normal full get and json parse
        if chunksize is None and not (url.endswith(".gz") or url.endswith(".gzip")):
            # If no chunksize and not gzipped, do a normal full GET and parse as JSON.
            with client.get(url, **httpx_kwargs) as response:
                response.raise_for_status()
                return response.json()
        # streaming json, not zipped
        elif chunksize is not None and not (
            url.endswith(".gz") or url.endswith(".gzip")
        ):
            # If chunksize specified and not gzipped, stream text and parse JSON objects one by one.
            with client.stream("GET", url, **httpx_kwargs) as response:
                response.raise_for_status()
                for entry in ijson.kvitems(response.iter_text(), ""):
                    yield entry
        # gzipped json (with or without chunksize)
        elif url.endswith(".gz") or url.endswith(".gzip"):
            # If gzipped, use the stream_gzipped method to get a file-like object and parse JSON objects one by one.
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

    def stream_tree(self, url: str, **skbio_kwargs) -> Generator:
        """
        Streams a tree file from a url and returns an iterator of parsed tree records.

        Parameters
        ----------
        url : str
            The url of the tree file to stream.
        skbio_kwargs : dict, optional
            Additional keyword arguments to pass to the skbio parser.
        Returns
        -------
        Generator[dict, None, None]
            An iterator of parsed tree records as dictionaries.
        """
        return read(url, format="newick", **skbio_kwargs)

    def _fix_inconsistent_cols(
        self, fields: list[str], pad_to: int = 15
    ) -> list[str] | None:
        """
        Fixes inconsistent columns in a list of strings.

        Parameters
        ----------
        fields : list[str]
            The list of strings to fix.
        pad_to : int, optional
            The number of columns to pad or truncate to. Default is 15.

        Returns
        -------
        list[str] | None
            The fixed list of strings, or None if the fields are invalid.
        """
        # pad to
        if len(fields) < pad_to:
            return fields + [""] * (pad_to - len(fields))
        # truncate
        if len(fields) > pad_to:
            return fields[:pad_to]
        return fields

    def _get_streamer(
        self,
        alias: Optional[str] = None,
        url: Optional[HttpUrl] = None,
        chunksize: int = 1000,
        httpx_client: Optional[httpx.Client] = None,
        max_skip: int = 5,
        **kwargs,
    ):
        """
        Gets the appropriate streamer function based on the file type of the download.

        Parameters
        ----------
        alias : Optional[str]
            The alias of the download to stream.
        url : Optional[HttpUrl]
            The url of the download to stream.
        chunksize : int, optional
            The size of the chunks to read from the stream. Default is 1000.
        httpx_client : Optional[httpx.Client], optional
            The httpx client to use for making requests. Default is None.
        max_skip : int, optional
            The maximum number of rows to skip before raising an error. Default is 5.
        kwargs : dict
            Additional keyword arguments to pass to the streamer function.

        Returns
        -------
        Callable
            A function that can be called to stream the download.
        """

        client = httpx_client or self._mgnifier_helper.httpx_client

        # get alias/url
        _alias, _url = self._prioritize_alias(alias, url, required=True)
        # return stream based on file type
        file_type = self._get_type_by_alias(_alias)
        if file_type == "tsv":
            if _url.endswith(".gz") or _url.endswith(".gzip"):
                logging.debug(f"tsv file type ends with .gz: {_url}")
                try:
                    return self.stream_tsv(
                        _url,
                        chunksize=chunksize,
                        max_skip=max_skip,
                        compression="gzip",
                        **kwargs,
                    )
                except pd.errors.ParserError as e:
                    logging.error(f"ParserError: {e}")
                    return self.stream_tsv(
                        _url,
                        chunksize=chunksize,
                        max_skip=max_skip,
                        compression="gzip",
                        engine="python",
                        on_bad_lines=self._fix_inconsistent_cols,
                        **kwargs,
                    )
            elif _url.endswith(".txt") or _url.endswith(".tsv"):
                return self.stream_tsv(
                    _url, chunksize=chunksize, max_skip=max_skip, **kwargs
                )
        elif file_type == "csv":
            return self.stream_tsv(
                _url, sep=",", chunksize=chunksize, max_skip=max_skip, **kwargs
            )
        elif file_type == "html":
            return lambda: self.stream_html(_url, **kwargs)
        elif file_type == "txt":  # TODO: to constants
            return self.stream_txt(
                _url, chunksize=chunksize, httpx_client=client, **kwargs
            )
        elif file_type == "gff":
            return self.stream_gff(_url, **kwargs)
        elif file_type == "biom":
            return self.stream_biom(_url, **kwargs)
        elif file_type == "fasta":
            return self.stream_fasta(_url, **kwargs)
        elif file_type == "tree":
            return self.stream_tree(_url, **kwargs)
        elif file_type == "json":
            return self.stream_jsonl(
                _url, orient="records", chunksize=chunksize, **kwargs
            )
        elif file_type == "other" and ".json" in _url:
            if _url.endswith("json.gz") or _url.endswith("json.gzip"):
                return self.stream_json(
                    _url, chunksize=chunksize, httpx_client=client, **kwargs
                )

            logging.info(
                f"{_alias} is only available for download "
                f"(e.g., `.download({_alias}))`"
            )
            # more info
            logging.debug(
                f"Alias: {_alias}\nURL: {_url}\nFile type: {file_type}. "
                "Only '.json' files can be streamed under 'other' type, "
                "otherwise this download is only available for download."
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
    ) -> dict[str, Callable]:
        """
        Streams a download based on its alias or url. If neither alias nor url is provided, streams all downloads.
        (if chunksize is specified, it's kinda lazy loading)

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
        dict[str, Callable]
            A dictionary of alias: streamer_function for the requested downloads.
        """
        # get alias/url
        _alias, _url = self._prioritize_alias(alias, url)
        # if neither alias nor url provided, stream all downloads
        if not _alias and not _url:
            aliases = self.downloads_df["alias"].tolist()
        else:
            aliases = [_alias]
        # return dict of alias: streamer_function
        client = self._mgnifier_helper.httpx_client

        # TODO: skip404 client error for now
        streams = {}
        for a in aliases:
            try:
                logging.info(f"Setting up stream for alias: {a}")
                streams[a] = self._get_streamer(
                    alias=a,
                    chunksize=chunksize,
                    httpx_client=client,
                    max_skip=max_skip,
                    **kwargs,
                )
            except HTTPError as err:
                logging.error(f"HTTP error for alias {a} and url {_url}: {err}")
                continue  # skip this stream but continue with others

        return streams

    def download(
        self,
        to_dir: DirectoryPath,
        alias: Optional[str] = None,
        *,
        url: Optional[str] = None,
        filename: Optional[str] = None,
        httpx_client: Optional[httpx.Client] = None,
        hide_progress: bool = False,
    ):
        """
        Downloads a file from a url or alias to a specified directory.

        Parameters
        ----------
        to_dir : DirectoryPath
            The directory to download the file to.
        alias : Optional[str], optional
            The alias of the file to download. If not provided, `url` must be provided. Default is None.
        url : Optional[str], optional
            The url of the file to download. If not provided, `alias` must be provided. Default is None.
        filename : Optional[str], optional
            The name to save the file as. If not provided, the alias will be used as the filename. Default is None.


        Raises
        ------
        ValueError
            If neither `alias` nor `url` is provided, or if `url` is provided without a corresponding `alias` in the downloads.
        """
        # get alias/url
        _alias, _url = self._prioritize_alias(alias, url, required=True)

        # if no alias then need filename
        if not _alias and not filename:
            raise ValueError(
                "If `url` not from downloads, `filename` must be provided since no alias available."
            )

        # make dir if not exists
        to_dir = Path(to_dir)
        to_dir.mkdir(parents=True, exist_ok=True)

        # prep full path
        filepath = to_dir / filename if filename else to_dir / _alias

        # reuse httpx client if provided, otherwise init new client using mgnifier
        with httpx_client or self._mgnifier_helper.httpx_client as client:
            with client.stream("GET", _url) as response:
                response.raise_for_status()
                total = int(response.headers.get("content-length", 0))
                with (
                    open(filepath, "wb") as f,
                    tqdm_sync(
                        total=total,
                        unit="B",
                        unit_scale=True,
                        desc=f"Downloading {filename or _alias}",
                        ascii=" >=",
                        disable=hide_progress,
                    ) as pbar,
                ):
                    for chunk in response.iter_bytes():
                        f.write(chunk)
                        pbar.update(len(chunk))

    async def adownload(
        self,
        to_dir: DirectoryPath,
        alias: Optional[str] = None,
        *,
        url: Optional[str] = None,
        filename: Optional[str] = None,
        httpx_aclient: Optional[httpx.AsyncClient] = None,
        hide_progress: bool = False,
    ):
        """
        Asynchronously downloads a file from a url or alias to a specified directory.

        Parameters
        ----------
        to_dir : DirectoryPath
            The directory to download the file to.
        alias : Optional[str], optional
            The alias of the file to download. If not provided, `url` must be provided. Default is None.
        url : Optional[str], optional
            The url of the file to download. If not provided, `alias` must be provided. Default is None.
        filename : Optional[str], optional
            The name to save the file as. If not provided, the alias will be used as the filename. Default is None.
            Note that if `url` is provided without a corresponding `alias` in the downloads,
            `filename` must be provided since there is no alias to use as the filename.
        httpx_aclient : Optional[httpx.AsyncClient], optional
            An optional httpx.AsyncClient to use for the download.
            If not provided, a new client will be created using the mgnifier helper. Default is None.
        """
        # get alias/url
        _alias, _url = self._prioritize_alias(alias, url, required=True)

        # if no alias then need filename
        if not _alias and not filename:
            raise ValueError(
                "If `url` not from downloads, `filename` must be provided since no alias available."
            )

        # make dir if not exists
        to_dir = Path(to_dir)
        to_dir.mkdir(parents=True, exist_ok=True)

        # prep full path
        filepath = to_dir / filename if filename else to_dir / _alias

        # arg TODO mixins
        # semaphore to limit concurrent downloads, can be adjusted in config
        async with semaphore:
            if httpx_aclient is not None:
                client = httpx_aclient
                # Do NOT use 'async with' here, just use the client directly
                async with client.stream("GET", _url) as response:
                    response.raise_for_status()
                    total = int(response.headers.get("content-length", 0))
                    with tqdm_sync(
                        total=total,
                        unit="B",
                        unit_scale=True,
                        desc=f"Downloading {filename or _alias}",
                        ascii="░▒█",
                        disable=hide_progress,
                    ) as pbar:
                        async with aiofiles.open(filepath, "wb") as f:
                            async for chunk in response.aiter_bytes():
                                await f.write(chunk)
                                pbar.update(len(chunk))
            else:
                async with self._mgnifier_helper.httpx_aclient as client:
                    async with client.stream("GET", _url) as response:
                        response.raise_for_status()
                        total = int(response.headers.get("content-length", 0))
                        with tqdm_sync(
                            total=total,
                            unit="B",
                            unit_scale=True,
                            desc=f"Downloading {filename or _alias}",
                            ascii="░▒█",
                            disable=hide_progress,
                        ) as pbar:
                            async with aiofiles.open(filepath, "wb") as f:
                                async for chunk in response.aiter_bytes():
                                    await f.write(chunk)
                                    pbar.update(len(chunk))

    async def adownload_all(
        self,
        to_dir: DirectoryPath,
        hide_progress: bool = False,
    ):
        """
        Asynchronously downloads all files in the downloads to a specified directory.

        Parameters
        ----------
        to_dir : DirectoryPath
            The directory to download the files to.
        hide_progress : bool, optional
            Whether to hide the progress bars. Default is False.

        Note
        ----
        This method will use the `adownload` method for each file,
        so it will respect the same parameters and behavior for handling aliases, urls, filenames, and httpx clients.
        If you want to customize those parameters for each file,
        you can call `adownload` directly for each file instead of using this method.
        """

        logging.debug("Initializing async client once for all downloads")
        async with self._mgnifier_helper.httpx_aclient as client:

            # create tasks for each download
            tasks = [
                self.adownload(
                    to_dir=to_dir,
                    alias=a,
                    httpx_aclient=client,
                    hide_progress=hide_progress,
                )
                for a in self.url_dict
            ]
            # Overall progress bar
            for f in tqdm_async(
                asyncio.as_completed(tasks),
                total=len(tasks),
                desc="Overall Progress",
                ascii=" >=",
                disable=hide_progress,
            ):
                try:
                    await f
                except httpx.ConnectError as ce:
                    # flag and continue with downloads
                    logging.error(
                        f"Connection error occurred while downloading {f}: {ce}"
                    )
                except Exception as e:
                    # flag and continue with downloads ..
                    logging.error(f"Error occurred while downloading {f}: {e}")

    def download_all(
        self,
        to_dir: DirectoryPath,
        hide_progress: bool = False,
    ):
        """
        TODO fix
        Downloads all files in the downloads to a specified directory.

        Parameters
        ----------
        to_dir : DirectoryPath
            The directory to download the files to.
        hide_progress : bool, optional
            Whether to hide the progress bars. Default is False.

        Note
        ----
        This method will use the `download` method for each file,
        so it will respect the same parameters and behavior for handling aliases, urls, filenames, and httpx clients.
        If you want to customize those parameters for each file,
        you can call `download` directly for each file instead of using this method.
        """

        logging.debug("Initializing client once for all downloads")
        with self._mgnifier_helper.httpx_client as client:
            aliases = list(self.url_dict.keys())

            for alias in tqdm_sync(
                aliases,
                total=len(aliases),
                desc="Overall Progress",
                ascii=" >=",
                disable=hide_progress,
            ):
                try:
                    self.download(
                        to_dir=to_dir,
                        alias=alias,
                        httpx_client=client,
                        hide_progress=hide_progress,
                    )
                except httpx.ConnectError as ce:
                    logging.error(
                        "Connection error occurred while downloading %s: %s",
                        alias,
                        ce,
                    )
                except Exception as e:
                    logging.error(
                        "Error occurred while downloading %s: %s",
                        alias,
                        e,
                    )


class MGazineCurator:

    def __init__(
        self,
        *mgazines,
    ):

        if mgazines and all(isinstance(m, MGazine) for m in mgazines):
            self.mgazines = mgazines
        elif mgazines and all(isinstance(m, str) for m in mgazines):
            self.mgazines = [MGazine(m) for m in mgazines]
        else:
            raise ValueError(
                "Invalid input: all inputs must be either MGazine instances or accession strings."
            )

    def go_terms(self):
        pass


# class DatasetBuilder(MGnifier):

#     def __init__(
#         self,
#         accession: str,
#     ):
#         super().__init__(
#             accession=accession,
#         )
#         self.mpy_module = analysis_get_mgnify_analysis_with_annotations

#     def __getitem__(self, key):
#         pass

#     def __getattr__(self, name):
#         if name == "annotations":
#             return self
#         else:
#             raise KeyError(f"DatasetBuilder object has no attribute {name}")

#     def export(self):
#         pass


# should there be different dataset builders?
# and they can be added to dataset builder as attributes?
