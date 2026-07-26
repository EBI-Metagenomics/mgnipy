from __future__ import annotations

import logging

from mgnipy.emgapi_v2_client.client import AuthenticatedClient, Client

logger = logging.getLogger(__name__)
from pathlib import Path
from pprint import pformat
from typing import Any, Optional

import aiofiles
import httpx
import pandas as pd
import polars as pl
from pydantic import DirectoryPath, HttpUrl
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm_asyncio

from mgnipy._models.config import MGnipyConfig
from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy._shared_helpers.httpx_helpers import init_httpx_client
from mgnipy.V2.mixins import (
    ClientManagerMixin,
    StreamMixin,
)
from mgnipy.V2.datasets.annotate import MetadataSettersMixin


class MGazine(StreamMixin, ClientManagerMixin, MetadataSettersMixin):
    """
    MGazine is a class for managing and downloading datasets from MGnify.
    - Accepts a list of download-like dictionaries (for example
    the objects returned by the MGnify API for downloads) and provides
    simple streaming and download helpers.
    - Supports grouping datasets by pipeline version and short description, and provides methods for downloading individual files or all files in the MGazine.

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
        *,
        client: Optional[Client | AuthenticatedClient] = None,
        mgnify_studies: Optional[list[dict[str, Any]]] = None,
        mgnify_analyses: Optional[list[dict[str, Any]]] = None,
        mgnify_runs: Optional[list[dict[str, Any]]] = None,
        mgnify_samples: Optional[list[dict[str, Any]]] = None,
        mgnify_assemblies: Optional[list[dict[str, Any]]] = None,
        biosamples_metadata: Optional[list[dict[str, Any]]] = None,
    ):
        self.downloads = downloads
        self.config = config or MGnipyConfig()
        self.client = client or init_httpx_client(self.config)
        self.httpx_client = self.client.get_httpx_client()
        self.async_httpx_client = self.client.get_async_httpx_client()
        self.semaphore = get_semaphore()

        self._mgnify_studies = mgnify_studies
        self._mgnify_analyses = mgnify_analyses
        self._mgnify_runs = mgnify_runs
        self._mgnify_samples = mgnify_samples
        self._mgnify_assemblies = mgnify_assemblies
        self._biosamples_metadata = biosamples_metadata

        self._lazy_merged: list[pl.LazyFrame] | None = None

    def __str__(self):
        return (
            f"MGazine containing:\n"
            f"- MGnify pipeline versions: {self.list_pipeline_version()}\n"
            f"- Number of downloads: {len(self.downloads)}\n"
            f"- Short descriptions: {pformat(self.list_short_descriptions())}\n"
        )

    def __add__(self, other):
        if not isinstance(other, MGazine):
            raise ValueError(
                f"Can only add another MGazine instance, got {type(other)}"
            )
        combined_downloads = self.downloads + other.downloads
        new_mz = MGazine(
            combined_downloads,
            config=self.config,
            client=self.client,
            mgnify_studies=(self.mgnify_studies + other.mgnify_studies).to_list(),
            mgnify_analyses=(self.mgnify_analyses + other.mgnify_analyses).to_list(),
            mgnify_runs=(self.mgnify_runs + other.mgnify_runs).to_list(),
            mgnify_samples=(self.mgnify_samples + other.mgnify_samples).to_list(),
            mgnify_assemblies=(
                self.mgnify_assemblies + other.mgnify_assemblies
            ).to_list(),
            biosamples_metadata=(
                self.biosamples_metadata + other.biosamples_metadata
            ).to_list(),
        )
        if new_mz.__class__ != self.__class__:
            try:
                return self.__class__(
                    mgazine=new_mz,
                    config=self.config,
                    client=self.client,
                    mgnify_studies=(
                        self.mgnify_studies + other.mgnify_studies
                    ).to_list(),
                    mgnify_analyses=(
                        self.mgnify_analyses + other.mgnify_analyses
                    ).to_list(),
                    mgnify_runs=(self.mgnify_runs + other.mgnify_runs).to_list(),
                    mgnify_samples=(
                        self.mgnify_samples + other.mgnify_samples
                    ).to_list(),
                    mgnify_assemblies=(
                        self.mgnify_assemblies + other.mgnify_assemblies
                    ).to_list(),
                    biosamples_metadata=(
                        self.biosamples_metadata + other.biosamples_metadata
                    ).to_list(),
                )
            except Exception as e:
                logger.warning(
                    f"Failed to create instance of {self.__class__} with combined MGazine: {e}. Returning base MGazine instead."
                )
        return new_mz

    def __getattr__(self, name):
        if name.startswith("taxonomic"):

            taxonom_downloads = []
            for k, v in self.by_downloads_col("download_type").items():
                if "taxonom" in k.lower():
                    taxonom_downloads.extend(v)

            if len(taxonom_downloads) == 0:
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{name}' because no taxonomic downloads are available."
                )

            no_dwc = [
                d
                for d in taxonom_downloads
                if "dwc-ready" not in d.get("short_description", "").lower()
            ]

            dwc_ready = [
                d
                for d in taxonom_downloads
                if "dwc-ready" in d.get("short_description", "").lower()
            ]

            if name == "taxonomic" and len(no_dwc) > 0:
                return TaxaMGazine(
                    downloads=no_dwc,
                    config=self.config,
                    client=self.client,
                    mgnify_studies=self.mgnify_studies,
                    mgnify_analyses=self.mgnify_analyses,
                    mgnify_runs=self.mgnify_runs,
                    mgnify_samples=self.mgnify_samples,
                    mgnify_assemblies=self.mgnify_assemblies,
                    biosamples_metadata=self.biosamples_metadata,
                )
            elif name == "taxonomic" and len(no_dwc) == 0:
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{name}' because no taxonomic downloads are available."
                )
            elif name == "taxonomic_dwc_ready" and len(dwc_ready) == 0:
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{name}' because no DWC-ready taxonomic downloads are available."
                )
            elif name == "taxonomic_dwc_ready" and len(dwc_ready) > 0:
                return DWCTaxaMGazine(
                    downloads=dwc_ready,
                    config=self.config,
                    client=self.client,
                    mgnify_studies=self.mgnify_studies,
                    mgnify_analyses=self.mgnify_analyses,
                    mgnify_runs=self.mgnify_runs,
                    mgnify_samples=self.mgnify_samples,
                    mgnify_assemblies=self.mgnify_assemblies,
                    biosamples_metadata=self.biosamples_metadata,
                )
            else:
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{name}'"
                )
        # elif TODO other types

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __getitem__(self, key):
        if key in self.list_pipeline_version():
            downloads_list: list[dict[str, Any]] = self.by_downloads_col(
                "pipeline_version"
            )[key]
        elif key in self.list_short_descriptions():
            downloads_list: list[dict[str, Any]] = self.by_downloads_col(
                "short_description"
            )[key]
        else:
            raise KeyError(
                f"'{self.__class__.__name__}' has no pipeline version or short description: '{key}'."
            )

        return MGazine(
            downloads_list,
            config=self.config,
            client=self.client,
            mgnify_studies=self.mgnify_studies,
            mgnify_analyses=self.mgnify_analyses,
            mgnify_runs=self.mgnify_runs,
            mgnify_samples=self.mgnify_samples,
            mgnify_assemblies=self.mgnify_assemblies,
            biosamples_metadata=self.biosamples_metadata,
        )

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
    def urls(self) -> list[Optional[str]]:
        """
        Return a list of all download URLs. Same as ``url_list``.

        Examples
        --------
        >>> downloads = [
        ...     {"alias": "example.txt", "url": "http://ex/x", "file_type": "txt"},
        ... ]
        >>> MGazine(downloads).urls
        ['http://ex/x']
        """

        return self.url_list

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

    def downloads_df(self, **pd_kwargs) -> pd.DataFrame:
        """Return a ``pandas.DataFrame`` of all downloads.

        The dataframe will contain columns such as ``alias``, ``url`` and
        ``file_type`` when those keys exist in the provided download dicts.

        Examples
        --------
        >>> downloads = [
        ...     {"alias": "example.txt", "url": "http://ex/x", "file_type": "txt"},
        ... ]
        >>> df = MGazine(downloads).downloads_df()
        >>> list(df.columns)
        ['alias', 'url', 'file_type']
        """
        df = pd.DataFrame(self.downloads, **pd_kwargs)
        # add pipeline version column if possible
        #    df = self._add_pipeline_col(df)

        return df

    def by_downloads_col(self, col: str) -> dict[str, list[dict[str, Any]]]:
        """
        Group downloads by a specified column in the downloads dataframe.

        Parameters
        ----------
        col : str
            The column name to group by.

        Returns
        -------
        dict
            A dictionary where keys are unique values from the specified column and values are lists of download dictionaries.

        Raises
        ------
        ValueError
            If the specified column is not present in the downloads dataframe.
        """

        df = self.downloads_df()
        if col not in df.columns:
            raise ValueError(
                f"Cannot group by {col} because '{col}' column is missing."
            )
        grouped = self.downloads_df().groupby(col)

        groups = {value: group.to_dict(orient="records") for value, group in grouped}
        return groups

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
        df = df or self.downloads_df()
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
        df = df or self.downloads_df()
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
        df = df or self.downloads_df()
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

    @property
    def short_desc(self) -> str:
        if len(self.list_pipeline_version()) > 1:
            logger.warning(
                "Multiple pipeline versions detected -- MGazine methods may not work as expected."
            )

        if len(self.list_short_descriptions()) > 1:
            logger.warning(
                f"Multiple descriptions detected & `short_desc` not specified -- MGazine methods may not work as expected.\n'{self.list_short_descriptions()[0]}' may be used for e.g., caching, `long_short_mapping`."
            )
        return self.list_short_descriptions()[0]

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

        if self.downloads_df().empty:
            return []

        avail_vers = sorted(self.downloads_df()["pipeline_version"].unique().tolist())

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

        if self.downloads_df().empty:
            return []

        avail_descs = sorted(self.downloads_df()["short_description"].unique().tolist())

        return avail_descs

    # downloading methods
    def download(
        self,
        to_dir: DirectoryPath,
        alias: Optional[str] = None,
        *,
        url: Optional[str] = None,
        filename: Optional[str] = None,
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

        logger.debug(
            f"Starting download: alias={_alias} url={_url} dest={filepath} overwrite={overwrite} client={self.client}",
        )

        with self.httpx_client.stream("GET", _url) as response:
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
        async with self.semaphore:
            # If caller provided an async client, use it (don't re-enter context).

            async with self.async_httpx_client.stream("GET", _url) as response:
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

        with self.httpx_client:
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

        async with self.async_httpx_client:

            # create tasks for each download
            tasks = [
                self.adownload(
                    to_dir=to_dir,
                    alias=a,
                    overwrite=overwrite,
                    hide_progress=hide_progress,
                )
                for a in self.url_dict
            ]
            # Overall progress bar
            for f in tqdm_asyncio.as_completed(
                tasks,
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

    # streaming to combine
    def lazy_concat(
        self,
        aliases: list[str] | None = None,
        urls: list[str] | None = None,
        how="vertical_relaxed",
        **pl_kwargs,
    ) -> pl.LazyFrame:
        """
        Return a concatenated Polars LazyFrame of the datasets corresponding to the provided aliases or URLs.

        Parameters
        ----------
        aliases : list[str] or None, optional
            List of download aliases to stream and concatenate. If provided, this takes precedence over `urls`.
        urls : list[str] or None, optional
            List of download URLs to stream and concatenate. Used only if `aliases` is not provided.
        how : str, optional
            Concatenation method. Options include 'vertical', 'horizontal', 'vertical_relaxed', etc. See Polars documentation for details.
        **pl_kwargs
            Additional keyword arguments to pass to the Polars concatenation function.

        Returns
        -------
        pl.LazyFrame
            A Polars LazyFrame representing the concatenated datasets.
        """

        if not aliases and not urls:
            raise ValueError("Either `aliases` or `urls` must be provided.")

        if urls and aliases:
            logger.warning("Both `aliases` and `urls` provided. Ignoring urls.")

        if aliases:
            self._lazy_merged = pl.concat(
                [
                    self.stream(alias=alias, chunksize=1000, dataframe_engine="polars")
                    for alias in aliases
                ],
                how=how,
                **pl_kwargs,
            )

        if urls:
            self._lazy_merged = pl.concat(
                [
                    self.stream(url=url, chunksize=1000, dataframe_engine="polars")
                    for url in urls
                ],
                how=how,
                **pl_kwargs,
            )

        return self.lazy_merged

    @property
    def lazy_merged(self) -> pl.LazyFrame | None:
        """
        Return the current lazy merged Polars LazyFrame if available.

        Returns
        -------
        pl.LazyFrame or None
            The current lazy merged Polars LazyFrame, or None if not set.
        """
        return self._lazy_merged

    def lazy_to_pandas(self, **pd_kwargs) -> pd.DataFrame:
        if self._lazy_merged is None:
            logger.warning(
                "Lazy merged DataFrame not available. Returning empty DataFrame."
            )
            return pd.DataFrame()
        return self.lazy_merged.collect().to_pandas(**pd_kwargs)

    def lazy_to_polars(self) -> pl.DataFrame:
        if self._lazy_merged is None:
            logger.warning(
                "Lazy merged DataFrame not available. Returning empty DataFrame."
            )
            return pl.DataFrame()
        return self.lazy_merged.collect()

    def renew_client(self):
        """Overwrite of the renew_client method in ClientManagerMixin"""

        self.client = init_httpx_client(self.config)
        self.httpx_client = self.client.get_httpx_client()
        self.async_httpx_client = self.client.get_async_httpx_client()


from .taxonomic import DWCTaxaMGazine, TaxaMGazine
