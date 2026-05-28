from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)
from pathlib import Path
from pprint import pformat
from typing import Any, Optional

import aiofiles
import httpx
import pandas as pd
from pydantic import DirectoryPath, HttpUrl
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm as tqdm_async

from mgnipy._models.config import MGnipyConfig
from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy.V2.core import MGnifier
from mgnipy.V2.mixins import StreamMixin

semaphore = get_semaphore()


class MGazine(StreamMixin):
    """
    Helper for handling MGnify analysis/study downloads.

    This class accepts a list of download-like dictionaries (for example
    the objects returned by the MGnify API for downloads) and provides
    simple streaming and download helpers.

    Parameters
    ----------
    downloads : list[dict]
        List of download descriptors with keys such as ``alias``, ``url``
        and ``file_type``.
    config : MGnipyConfig, optional
        Optional configuration to use; when omitted the global
        :class:`MGnipyConfig` is used.

    Examples
    --------
    >>> downloads = [
    ...     {"alias": "a", "url": "/tmp/a.txt", "file_type": "txt"},
    ... ]
    >>> mg = MGazine(downloads)
    >>> isinstance(mg, MGazine)
    True
    >>> mg.url_dict['a']
    '/tmp/a.txt'
    >>> mg.url_list
    ['/tmp/a.txt']
    """

    def __init__(
        self,
        downloads: list[dict[str, Any]],
        config: Optional[MGnipyConfig] = None,
    ):
        self.downloads = downloads
        self.config = config or MGnipyConfig()

    def __str__(self):
        return (
            f"MGazine containing:\n"
            f"- MGnify pipeline versions: {self.list_pipeline_version()}\n"
            f"- Number of downloads: {len(self.downloads)}\n"
            f"- Short descriptions: {pformat(self.list_short_descriptions())}\n"
        )

    def _mgnifier_helper(
        self, url: str = "", cache_dir: Optional[DirectoryPath] = None
    ) -> MGnifier:
        """
        Helper to create an MGnifier instance for a given download URL.
        Default settings is no cache (cache_dir=None)
        """
        _config = self.config.model_copy(update={"cache_dir": cache_dir}, deep=True)

        # init
        mg = MGnifier(
            resource="_downloads",
            config=_config,
            url=url,
        )
        logger.info(f"MGnifier initialized with resource={mg.resource} and url={url}")
        return mg

    @property
    def aliases(self) -> list[str]:
        """Return a list of all download aliases.

        Examples
        --------
        >>> downloads = [
        ...     {"alias": "example.txt", "url": "http://ex/x", "file_type": "txt"},
        ... ]
        >>> MGazine(downloads).aliases
        ['example.txt']
        """

        return [f["alias"] for f in self.downloads if "alias" in f]

    @property
    def url_dict(self) -> dict[str, dict]:
        """
        Return mapping of alias to URL for all downloads.

        Returns
        -------
        dict
            Dictionary mapping alias -> url (or ``None`` when no url is
            available).

        Examples
        --------
        >>> downloads = [
        ...     {"alias": "example.txt", "url": "http://ex/x", "file_type": "txt"},
        ... ]
        >>> MGazine(downloads).url_dict['example.txt']
        'http://ex/x'
        """

        return {f["alias"]: f.get("url", None) for f in self.downloads}

    @property
    def downloads_df(self) -> pd.DataFrame:
        """Return a ``pandas.DataFrame`` of all downloads.

        The dataframe will contain columns such as ``alias``, ``url`` and
        ``file_type`` when those keys exist in the provided download dicts.

        Examples
        --------
        >>> downloads = [
        ...     {"alias": "example.txt", "url": "http://ex/x", "file_type": "txt"},
        ... ]
        >>> df = MGazine(downloads).downloads_df
        >>> list(df.columns)
        ['alias', 'url', 'file_type']
        """
        df = pd.DataFrame(self.downloads)
        # add pipeline version column if possible
        #    df = self._add_pipeline_col(df)

        return df

    def by_pipeline_version(self) -> dict[str, list[dict[str, Any]]]:
        """
        Group downloads by pipeline version based on the 'pipeline_version' column in the downloads dataframe.

        Returns
        -------
        dict
            A dictionary where keys are pipeline versions and values are lists of download dictionaries.
        """

        df = self.downloads_df
        if "pipeline_version" not in df.columns:
            raise ValueError(
                "Cannot group by version because 'pipeline_version' column is missing."
            )
        grouped = self.downloads_df.groupby("pipeline_version")

        groups = {
            version: group.to_dict(orient="records") for version, group in grouped
        }
        return groups

    def by_short_desc(self) -> dict[str, list[dict[str, Any]]]:
        """
        Group downloads by short description based on the 'short_description' column in the downloads dataframe.

        Returns
        -------
        dict
            A dictionary where keys are short descriptions and values are lists of download dictionaries.
        """

        df = self.downloads_df
        if "short_description" not in df.columns:
            raise ValueError(
                "Cannot group by short description because 'short_description' column is missing."
            )
        grouped = self.downloads_df.groupby("short_description")

        groups = {desc: group.to_dict(orient="records") for desc, group in grouped}
        return groups

    def list_pipeline_version(self):
        """Return a list of pipeline versions extracted from the download groups.

        This looks for patterns like '.v4.1' in the 'download_group' field
        of the downloads and extracts the version number.

        Examples
        --------
        >>> downloads = [
        ...     {"alias": "example.txt", "url": "http://ex/x", "file_type": "txt", "download_group": "group.v4.1", "pipeline_version": 'v4_1'},
        ...     {"alias": "example2.txt", "url": "http://ex/x2", "file_type": "txt", "download_group": "group.v5", "pipeline_version": 'v5'},
        ... ]
        >>> MGazine(downloads).list_pipeline_version()
        ['v4_1', 'v5']
        """

        avail_vers = sorted(self.downloads_df["pipeline_version"].unique().tolist())

        return avail_vers

    def list_short_descriptions(self):
        """Return a list of short descriptions extracted from the download groups.

        This looks for patterns like 'shortdesc' in the 'download_group' field
        of the downloads and extracts the short description.

        Examples
        --------
        >>> downloads = [
        ...     {"alias": "example.txt", "url": "http://ex/x", "file_type": "txt", "download_group": "group.shortdesc1", "pipeline_version": 4.1, "short_description": "shortdesc1"},
        ...     {"alias": "example2.txt", "url": "http://ex/x2", "file_type": "txt", "download_group": "group.shortdesc2", "pipeline_version": 4.1, "short_description": "shortdesc2"},
        ... ]
        >>> MGazine(downloads).list_short_descriptions()
        ['shortdesc1', 'shortdesc2']
        """

        avail_descs = sorted(self.downloads_df["short_description"].unique().tolist())

        return avail_descs

    def __getattr__(self, name):
        if name in self.list_pipeline_version():
            logger.info(
                f"Setting up mgazine only for datasets of pipeline version {name} via attribute access."
            )
            return MGazine(self.by_pipeline_version()[name], config=self.config)

        raise AttributeError(
            f"'{self.__class__.__name__}' has no version '{name}'. Available versions: {self.list_pipeline_version()}"
        )

    def __getitem__(self, key):
        if key in self.list_short_descriptions():

            new_mz = MGazine(self.by_short_desc()[key], config=self.config)

            download_type = (
                self.downloads_df[self.downloads_df["short_description"] == key][
                    "download_type"
                ]
                .unique()[0]
                .lower()
            )
            logger.info(f"Download type for {key}: {download_type}")

            if "taxonom" in download_type and "dwc-ready" in key.lower():
                logger.debug(
                    f"getting dwc-ready taxonomic datasets of short description {key} via item access."
                )
                return DWCTaxaCurator(mgazine=new_mz, config=self.config)

            if "taxonom" in download_type and "dwc-ready" not in key.lower():
                logger.debug(
                    f"getting taxonomic datasets of short description {key} via item access."
                )
                return TaxaCurator(mgazine=new_mz, config=self.config)

            # TODO other download types
            return new_mz

    @property
    def url_list(self):
        """Return a list of all download URLs.

        Examples
        --------
        >>> downloads = [
        ...     {"alias": "example.txt", "url": "http://ex/x", "file_type": "txt"},
        ... ]
        >>> MGazine(downloads).url_list
        ['http://ex/x']
        """

        return [f.get("url", None) for f in self.downloads]

    # downloading methods
    def download(
        self,
        to_dir: DirectoryPath,
        alias: Optional[str] = None,
        *,
        url: Optional[str] = None,
        filename: Optional[str] = None,
        httpx_client: Optional[httpx.Client] = None,
        overwrite: bool = False,
        hide_progress: bool = False,
    ):
        """
        Download a file from an alias or URL to a local directory.

        Parameters
        ----------
        to_dir : DirectoryPath
            Directory where the file will be saved.
        alias : str or None, optional
            Download alias known to this ``MGazine`` instance. When
            provided the corresponding URL from the instance's downloads
            list is used.
        url : str or None, optional
            Direct URL to fetch. Either ``alias`` or ``url`` must be
            provided.
        filename : str or None, optional
            Filename to use for the saved file. When omitted the alias
            is used.
        httpx_client : httpx.Client, optional
            Optional `httpx.Client` to use for the HTTP request. If not
            supplied a temporary client from `_mgnifier_helper` is
            used.
        overwrite : bool, optional
            If ``False`` and the destination file already exists the
            download is skipped. When ``True`` the existing file will be
            overwritten.
        hide_progress : bool, optional
            Disable the progress bar when ``True``.

        Raises
        ------
        ValueError
            If neither ``alias`` nor ``url`` is provided.

        Examples
        --------
        downloads = [
        ... {
        ... "alias": "example.txt",
        ... "url": "http://ex/x",
        ... "file_type": "txt",
        ... }]
        mg = MGazine(downloads)
        mg.download("download_to_here", alias="example.txt") # doctest: +SKIP
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
        logger.debug(f"Ensuring download directory exists: {to_dir}")
        to_dir.mkdir(parents=True, exist_ok=True)

        # prep full path
        filepath = to_dir / filename if filename else to_dir / _alias
        logger.debug(f"Prepared file path for download: {filepath}")

        # check if file exists and handle overwrite behavior
        if filepath.exists() and not overwrite:
            logger.info(
                f"File already exists and overwrite is False, skipping download: {filepath}"
            )
            return
        elif filepath.exists() and overwrite:
            logger.info(
                f"File already exists but overwrite is True, will overwrite: {filepath}"
            )

        # leveraging mgnifier for config, auth, but no cache for downloads
        client = (
            httpx_client
            or self._mgnifier_helper(_url, cache_dir=None).exec.httpx_client
        )
        logger.debug(
            f"Starting download: alias={_alias} url={_url} dest={filepath} overwrite={overwrite} client={getattr(client, '__class__', str(client))}",
        )

        with client.stream("GET", _url) as response:
            # http errors raise here
            response.raise_for_status()
            # for progress bar, get total size from headers if available
            total = int(response.headers.get("content-length", 0))
            with (
                open(filepath, "wb") as f,
                tqdm_sync(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    desc=f"Downloading {filename or _alias} to {filepath}",
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
        overwrite: bool = False,
        hide_progress: bool = False,
    ):
        """
        Asynchronously download a file from an alias or URL.

        Parameters
        ----------
        to_dir : DirectoryPath
            Directory where the file will be saved.
        alias : str or None, optional
            Download alias known to this ``MGazine`` instance.
        url : str or None, optional
            Direct URL to fetch. Either ``alias`` or ``url`` must be
            provided.
        filename : str or None, optional
            Filename to use for the saved file. When omitted the alias
            is used.
        httpx_aclient : httpx.AsyncClient, optional
            Optional `httpx.AsyncClient` to use for the HTTP request.
        overwrite : bool, optional
            If ``False`` and the destination file already exists the
            download is skipped. When ``True`` the existing file will be
            overwritten.
        hide_progress : bool, optional
            Disable the progress bar when ``True``.

        Raises
        ------
        ValueError
            If neither ``alias`` nor ``url`` is provided.

        Examples
        --------
        downloads = [
        ... {
        ... "alias": "example.txt",
        ... "url": "http://ex/x",
        ... "file_type": "txt",
        ... }]
        mg = MGazine(downloads)
        await mg.adownload("download_to_here", alias="example.txt") # doctest: +SKIP
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
        logger.debug(f"Creating directory (if not exists): {to_dir}")
        to_dir.mkdir(parents=True, exist_ok=True)

        # prep full path
        filepath = to_dir / filename if filename else to_dir / _alias
        logger.debug(f"Prepared file path for async download: {filepath}")
        # check if file exists and handle overwrite behavior
        if filepath.exists() and not overwrite:
            logger.info(
                f"File already exists and overwrite is False, skipping download: {filepath}"
            )
            return
        elif filepath.exists() and overwrite:
            logger.info(
                f"File already exists but overwrite is True, will overwrite: {filepath}"
            )

        # semaphore to limit concurrent downloads, can be adjusted in config
        async with semaphore:
            # If caller provided an async client, use it (don't re-enter context).
            if httpx_aclient is not None:
                client = httpx_aclient
                async with client.stream("GET", _url) as response:
                    response.raise_for_status()
                    total = int(response.headers.get("content-length", 0))
                    with tqdm_sync(
                        total=total,
                        unit="B",
                        unit_scale=True,
                        desc=f"Downloading {filename or _alias}",
                        disable=hide_progress,
                    ) as pbar:
                        async with aiofiles.open(filepath, "wb") as f:
                            async for chunk in response.aiter_bytes():
                                await f.write(chunk)
                                pbar.update(len(chunk))
            else:
                # create a temporary client from the MGnifier helper
                async with self._mgnifier_helper(
                    _url, cache_dir=None
                ).exec.httpx_aclient as client:
                    async with client.stream("GET", _url) as response:
                        response.raise_for_status()
                        total = int(response.headers.get("content-length", 0))
                        with tqdm_sync(
                            total=total,
                            unit="B",
                            unit_scale=True,
                            desc=f"Downloading {filename or _alias}",
                            disable=hide_progress,
                        ) as pbar:
                            async with aiofiles.open(filepath, "wb") as f:
                                async for chunk in response.aiter_bytes():
                                    await f.write(chunk)
                                    pbar.update(len(chunk))

    def download_all(
        self,
        to_dir: DirectoryPath,
        hide_progress: bool = False,
        overwrite: bool = False,
    ):
        """
        Download all files known to this ``MGazine`` instance.

        Parameters
        ----------
        to_dir : DirectoryPath
            Directory where the files will be saved.
        hide_progress : bool, optional
            Disable per-file and overall progress bars when ``True``.
        overwrite : bool, optional
            Passed to `download` to control overwriting behavior.

        Notes
        -----
        This helper calls `download` for each alias present in the
        instance's downloads list.

        Examples
        --------
        >>> downloads = [
        ...     {"alias": "example.txt", "url": "http://ex/x", "file_type": "txt"},
        ...     {"alias": "example2.fasta.gz", "url": "http://ex/x2", "file_type": "fasta"},
        ... ]
        >>> mg = MGazine(downloads)
        >>> mg.download_all("download_to_here") # doctest: +SKIP
        """

        logger.debug("Initializing client once for all downloads")
        mg = self._mgnifier_helper()
        logger.debug(f"MGnifier helper created: {mg}")

        with mg.exec.httpx_client as client:
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
                        overwrite=overwrite,
                    )
                except httpx.ConnectError as ce:
                    logger.error(
                        f"Connection error occurred while downloading {alias}: {ce}"
                    )
                except Exception as e:
                    logger.error(f"Error occurred while downloading {alias}: {e}")

    async def adownload_all(
        self,
        to_dir: DirectoryPath,
        overwrite: bool = False,
        hide_progress: bool = False,
    ):
        """
        Asynchronously download all files known to this ``MGazine``.

        Parameters
        ----------
        to_dir : DirectoryPath
            Directory where the files will be saved.
        overwrite : bool, optional
            Passed to `adownload` to control overwriting behavior.
        hide_progress : bool, optional
            Disable progress bars when ``True``.

        Notes
        -----
        This helper creates a single async HTTP client and schedules
        concurrent `adownload` calls for all aliases.

        Examples
        ---------
        >>> downloads = [
        ...     {"alias": "example.txt", "url": "http://ex/x", "file_type": "txt"},
        ...     {"alias": "example2.fasta.gz", "url": "http://ex/x2", "file_type": "fasta"},
        ... ]
        >>> mg = MGazine(downloads)
        >>> await mg.adownload_all("download_to_here") # doctest: +SKIP

        """

        logger.debug("Initializing async client once for all downloads")
        mg = self._mgnifier_helper()
        logger.debug(f"MGnifier helper created: {mg}")

        async with mg.exec.httpx_aclient as client:

            # create tasks for each download
            tasks = [
                self.adownload(
                    to_dir=to_dir,
                    alias=a,
                    httpx_aclient=client,
                    overwrite=overwrite,
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
                    logger.error(
                        f"Connection error occurred while downloading {f}: {ce}"
                    )
                except Exception as e:
                    # flag and continue with downloads ..
                    logger.error(f"Error occurred while downloading {f}: {e}")

    # helpers for getting naming things
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
        """Prioritize ``alias`` over ``url`` and return resolved pair.

        If both ``alias`` and ``url`` are provided, the alias is used and the
        corresponding url from the downloads is returned.

        Parameters
        ----------
        alias : str or None
            Download alias known to this MGazine instance.
        url : str or None
            Direct URL to a resource.
        required : bool, optional
            When True, raise ``ValueError`` if neither ``alias`` nor ``url`` is
            provided.

        Returns
        -------
        (alias, url)
            Tuple containing the resolved alias (or ``None``) and url (or
            ``None``).

        Examples
        --------
        >>> downloads = [{"alias":"x","url":"http://ex/x","file_type":"txt", "download_group":"blah", "short_description":"blah", "pipeline_vers":4.1}]
        >>> mg = MGazine(downloads)
        >>> mg._prioritize_alias(alias='x', url=None)
        ('x', 'http://ex/x')
        >>> mg._prioritize_alias(alias=None, url='http://ex/x')
        ('x', 'http://ex/x')
        """

        if alias and url:
            logger.debug("Both `alias` and `url` provided, ignoring `url`.")
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


from .taxonomic import DWCTaxaCurator, TaxaCurator
