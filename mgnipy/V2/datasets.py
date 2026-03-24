import asyncio
import warnings
import webbrowser
from pathlib import Path
from typing import (
    Callable,
    Generator,
    Optional,
)

import aiofiles
import httpx
import pandas as pd
from pydantic import (
    DirectoryPath,
    HttpUrl,
)
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm as tqdm_async

from mgnipy._models.config import MgnipyConfig
from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy.V2.core import MGnifier
from mgnipy.V2.mgni_py_v2.models.m_gnify_analysis_with_annotations import (
    MGnifyAnalysisWithAnnotations,
)

from mgnipy.V2.mgni_py_v2.api.analyses import (  # isort:skip
    analysis_get_mgnify_analysis_with_annotations_661c2d6a as get_analysis_annotations,
)

semaphore = get_semaphore()
BASE_URL = MgnipyConfig().base_url


class MGazine(MGnifyAnalysisWithAnnotations):
    """More so an extended data class"""

    def __init__(self, accession: str):
        # mgnifier TODO handing private data
        self._mgnifier_helper = MGnifier(accession=accession)
        # set endpoint
        self._mgnifier_helper.endpoint_module = get_analysis_annotations
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
        self, alias: Optional[str], url: Optional[HttpUrl], required: bool = False
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
            except Exception:
                raise  # Re-raise any other error
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
            return self.stream_tsv(
                _url, chunksize=chunksize, max_skip=max_skip, **kwargs
            )
        elif file_type == "csv":
            return self.stream_tsv(
                _url, sep=",", chunksize=chunksize, max_skip=max_skip, **kwargs
            )
        elif file_type == "html":
            return lambda: self.stream_html(_url, **kwargs)
        elif file_type in ["txt", "fasta", "fastq"]:
            return self.stream_txt(
                _url, chunksize=chunksize, httpx_client=client, **kwargs
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
        return {
            a: self._get_streamer(
                alias=a,
                chunksize=chunksize,
                httpx_client=client,
                max_skip=max_skip,
                **kwargs,
            )
            for a in aliases
        }

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

        # arg to do mixins
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

        # init async client once for all downloads
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
                    print(f"Connection error occurred while downloading {f}: {ce}")
                except Exception as e:
                    # flag and continue with downloads ..
                    print(f"Error occurred while downloading {f}: {e}")

    def get(self, url: Optional[HttpUrl] = None, alias: Optional[str] = None):
        """here this will get all or a specific dataset"""
        with self._init_client() as client:
            # make get request
            response = client.get(url)
            # validate
            response.raise_for_status()
            # return content as bytes
            return response.content


# class DatasetBuilder(MGnifier):

#     def __init__(
#         self,
#         accession: str,
#     ):
#         super().__init__(
#             accession=accession,
#         )
#         self.mpy_module = get_analysis_annotations

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
