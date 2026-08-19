from __future__ import annotations

import logging

from mgnipy.emgapi_v2_client.client import AuthenticatedClient, Client

logger = logging.getLogger(__name__)
from pathlib import Path
from pprint import pformat
from typing import Any, Literal, Optional

import aiofiles
import anndata as ad
import httpx
import pandas as pd
import polars as pl
from pydantic import DirectoryPath, HttpUrl
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm_asyncio

from mgnipy._models.config import MGnipyConfig
from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy._shared_helpers.httpx_helpers import init_httpx_client
from mgnipy.V2.datasets.annotate import UNIQUE_RUN_ID_COL_NAME, MetadataSettersMixin
from mgnipy.V2.mixins import (
    ClientManagerMixin,
    StreamMixin,
)

METADATA_SETS = [
    "mgnify_runs",
    "mgnify_assemblies",
    "mgnify_samples",
    "mgnify_studies",
    "mgnify_analyses",
    "biosamples_metadata",
    "obs",
]


class MTG(MetadataSettersMixin):
    """MGic the Gatherer combines a MGnify dataset with its metadata.

    The MGic gatherer (MTG) takes a dataset as pandas or polars dataframe and MGnify or BioSamples metadata and combines them into a single object. MTG can be used to enrich the dataset with metadata, and to convert the dataset into different formats such as pandas, polars, or anndata.


    Parameters
    ----------
    dataset : pandas.DataFrame or polars.DataFrame
        The dataset to be combined with metadata. This can be a pandas or polars dataframe.
    var_cols : list of str, optional
        A list of column names in the dataset that are considered variable columns. These columns will be in var_metadata() and excluded from obs_metadata()
    mgnify_[studies|analyses|runs|samples|assemblies] : list of dict, optional
        Lists of dictionaries containing metadata for each respective MGnify dataset.
    biosamples_metadata : list of dict, optional
        A list of dictionaries containing metadata for BioSamples.

    Attributes
    ----------
    runs_accessions : list
        A list of all run accessions in the dataset. This is derived from the columns of the dataset that are not in var_cols.
    """

    def __init__(
        self,
        dataset: pd.DataFrame | pl.DataFrame,
        *,
        var_cols: list[str] | None = None,
        var_index: str | None = None,
        obs_index: str = UNIQUE_RUN_ID_COL_NAME,
        mgnify_studies: list[dict[str, Any]] | None = None,
        mgnify_analyses: list[dict[str, Any]] | None = None,
        mgnify_runs: list[dict[str, Any]] | None = None,
        mgnify_samples: list[dict[str, Any]] | None = None,
        mgnify_assemblies: list[dict[str, Any]] | None = None,
        biosamples_metadata: list[dict[str, Any]] | None = None,
        obs: list[dict[str, Any]] | None = None,
    ):
        self.dataset = dataset
        self.var_cols = var_cols or []
        if var_index is None:
            # add row "index" if dataset isnt None
            if isinstance(self.dataset, pl.DataFrame):
                self.dataset = self.dataset.with_row_index()
            if isinstance(self.dataset, pd.DataFrame):
                self.dataset = self.dataset.reset_index(drop=False)
            self.var_index = "index"
        else:
            self.var_index = var_index
        self.obs_index = obs_index
        self._mgnify_studies: list[dict[str, Any]] | None = mgnify_studies
        self._mgnify_analyses: list[dict[str, Any]] | None = mgnify_analyses
        self._mgnify_runs: list[dict[str, Any]] | None = mgnify_runs
        self._mgnify_samples: list[dict[str, Any]] | None = mgnify_samples
        self._mgnify_assemblies: list[dict[str, Any]] | None = mgnify_assemblies
        self._biosamples_metadata: list[dict[str, Any]] | None = biosamples_metadata
        self._obs: list[dict[str, Any]] | None = obs

    def __call__(
        self,
        dataset,
        *,
        var_cols: list[str] | None = None,
        var_index: str | None = None,
        obs_index: str = UNIQUE_RUN_ID_COL_NAME,
        mgnify_studies: list[dict[str, Any]] | None = None,
        mgnify_analyses: list[dict[str, Any]] | None = None,
        mgnify_runs: list[dict[str, Any]] | None = None,
        mgnify_samples: list[dict[str, Any]] | None = None,
        mgnify_assemblies: list[dict[str, Any]] | None = None,
        biosamples_metadata: list[dict[str, Any]] | None = None,
        obs: list[dict[str, Any]] | None = None,
    ) -> "MGazine":
        """
        Creates a new instance of MGnetizer with the specified resource, :meth:`all_ids`, :meth:`mgnify_metadata`, and detail_proxy. This allows for creating a new MGnetizer instance with different parameters without modifying the existing instance.
        """
        return self.__class__(
            dataset,
            var_cols=var_cols or self.var_cols,
            var_index=var_index or self.var_index,
            obs_index=obs_index or self.obs_index,
            mgnify_studies=mgnify_studies or self._mgnify_studies,
            mgnify_analyses=mgnify_analyses or self._mgnify_analyses,
            mgnify_runs=mgnify_runs or self._mgnify_runs,
            mgnify_samples=mgnify_samples or self._mgnify_samples,
            mgnify_assemblies=mgnify_assemblies or self._mgnify_assemblies,
            biosamples_metadata=biosamples_metadata or self._biosamples_metadata,
            obs=obs or self._obs,
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(dataset is {type(self.dataset)}, var_cols={self.var_cols}, var_index={self.var_index}, obs_index={self.obs_index}, available_metadata_sets={self.available_metadata_sets})"

    def __str__(self):
        return (
            f"{self.__class__.__name__} containing:\n"
            f"- Dataset type: {type(self.dataset)}\n"
            f"- var_cols: {self.var_cols}\n"
            f"- var_index: '{self.var_index}'\n"
            f"- obs_index: '{self.obs_index}'\n"
            f"- Nonempty metadata sets: {', '.join([f'.{m}' for m in self.available_metadata_sets])}\n"
        )

    def to_pandas(self) -> pd.DataFrame:
        if isinstance(self.dataset, pl.DataFrame):
            return self.dataset.to_pandas().set_index(self.var_index)
        elif isinstance(self.dataset, pd.DataFrame):
            return self.dataset.set_index(self.var_index)
        elif self.dataset is None:
            raise ValueError("No dataset is loaded in the MTG.")

    def to_polars(self) -> pl.DataFrame:
        if isinstance(self.dataset, pl.DataFrame):
            return self.dataset  # .select(pl.exclude(self.var_cols))
        elif isinstance(self.dataset, pd.DataFrame):
            return pl.from_pandas(
                self.dataset  # .drop(columns=self.var_cols, errors="ignore")
            )
        elif self.dataset is None:
            raise ValueError("No dataset is loaded in the MTG.")

    def X(
        self, df_engine: Literal["polars", "pandas"] = "pandas"
    ) -> pl.DataFrame | pd.DataFrame:
        """Gets the feature matrix (X) from the dataset.

        Basically transposes.

        Parameters
        ----------
        df_engine : Literal["polars", "pandas"], optional
            The DataFrame engine to use for the output.
            If "polars" is specified, a :class:`polars.DataFrame` is returned;
            if "pandas" is specified, a :class:`pandas.DataFrame` is returned.

        Returns
        -------
        pl.DataFrame or pd.DataFrame
            The feature matrix (X) containing the non-var columns from the dataset
        """

        df_pl = (
            self.to_polars()
            .select(pl.exclude(self.var_cols))
            .transpose(
                include_header=True,
                header_name=self.obs_index,
                column_names=self.var_index,
            )
        )
        # sort columns
        df_pl = df_pl.select(self.obs_index, *sorted(df_pl.columns[1:]))

        if df_engine == "pandas":
            return df_pl.to_pandas().set_index(self.obs_index)
        elif df_engine == "polars":
            return df_pl
        else:
            raise ValueError(
                f"Invalid df_engine: {df_engine}. Must be 'polars' or 'pandas'."
            )

    @property
    def available_metadata_sets(self) -> list[str]:
        """Return a list of available metadata sets in the MTG.

        This property checks which metadata sets (e.g., studies, analyses, runs, samples, assemblies, biosamples) are non-empty and returns their names as a list.

        Returns
        -------
        list of str
            A list of names of non-empty metadata sets available in the MTG.

        """
        return [f for f in METADATA_SETS if len(getattr(self, f)) > 0]

    @property
    def runs_accessions(self) -> list:
        return [x for x in self.to_polars().columns if x not in self.var_cols]

    def var_metadata(
        self,
        df_engine: Literal["polars", "pandas"] = "pandas",
    ) -> pl.DataFrame | pd.DataFrame:
        """Return the variable metadata as a dataframe.

        Parameters
        ----------
        df_engine : str, optional
            The dataframe engine to use. Can be "polars" or "pandas". Default is "pandas".

        Returns
        -------
        pd.DataFrame or pl.DataFrame
            A dataframe containing the variable metadata.
        """
        if df_engine == "polars":
            return self.to_polars().select([self.var_index] + self.var_cols)
        elif df_engine == "pandas":
            return self.to_pandas()[self.var_cols].copy()
        else:
            raise ValueError(
                f"Invalid df_engine: {df_engine}. Must be 'polars' or 'pandas'."
            )

    def obs_metadata(self, *args, **kwargs) -> pl.DataFrame | pd.DataFrame:
        return super().obs_metadata(*args, **kwargs, index_col_name=self.obs_index)

    def to_anndata(self, drop_duplicates: bool = True, **anndata_kwargs) -> ad.AnnData:
        if len(self.X()) == len(self.obs_metadata(drop_duplicates=drop_duplicates)):
            return ad.AnnData(
                self.X()[sorted(self.X().columns)].sort_index(),
                var=self.var_metadata().sort_index(),
                obs=self.obs_metadata(drop_duplicates=drop_duplicates).sort_index(),
                **anndata_kwargs,
            )
        elif len(self.X()) != len(self.obs_metadata(drop_duplicates=drop_duplicates)):
            intersection = list(
                set(self.X().index).intersection(
                    self.obs_metadata(drop_duplicates=drop_duplicates).index
                )
            )
            return ad.AnnData(
                self.X().loc[intersection, sorted(self.X().columns)].sort_index(),
                var=self.var_metadata().sort_index(),
                obs=self.obs_metadata(drop_duplicates=drop_duplicates)
                .loc[intersection]
                .sort_index(),
                **anndata_kwargs,
            )


class MGazine(StreamMixin, ClientManagerMixin, MetadataSettersMixin):
    """Reads or downloads datasets from MGnify.

    MGazine is a class for managing and downloading datasets from MGnify.
    - Accepts a list of download-like dictionaries (for example
    the objects returned by the MGnify API for downloads) and provides
    simple streaming and download helpers.
    - Supports grouping datasets by pipeline version and short description, and provides methods for downloading individual files or all files in the MGazine.

    Parameters
    ----------
    downloads : list of dict
        A list of download-like dictionaries, each containing keys such as ``alias``, ``url``, ``file_type``, ``download_group``, ``short_description``, and ``pipeline_version``.
    config : MGnipyConfig, optional
        An optional configuration object for MGnipy. If not provided, a default configuration is used.
    client : Client or AuthenticatedClient, optional
        An optional client object for making HTTP requests. If not provided, a default client is used.
    mgnify_[studies|analyses|runs|samples|assemblies] : list of dict, optional
        Lists of dictionaries containing metadata for each respective MGnify dataset.
    biosamples_metadata : list of dict, optional
        A list of dictionaries containing metadata for BioSamples.

    Attributes
    ----------
    downloads : list of dict
        The list of download-like dictionaries provided during initialization.
    downloads_df : pandas.DataFrame
        A DataFrame representation of the downloads, with columns such as ``alias``, ``url``, and ``file_type``.
    aliases: list of str
        A list of all download aliases extracted from the downloads.
    urls: list of str
        An alias for ``url_list``, providing a list of all download URLs.
    url_list : list of str
        A list of URLs extracted from the downloads.
    url_dict : dict
        A dictionary mapping each download alias to its corresponding URL.
    lazy_merged : polars.LazyFrame or None
        A lazy frame containing the merged datasets, if initialized.
    short_desc : str
        The short description of the MGazine, derived from the downloads. If multiple short descriptions are present, a warning is issued.

    Example
    -------
    >>> downloads = [
    ...    {"alias": "a", "url": "/tmp/a.txt", "file_type": "txt", "short_description": "desc1", "pipeline_version": "v5"},
    ...    {"alias": "boop", "url": "/tmp/b.fasta", "file_type": "fasta", "short_description": "desc2", "pipeline_version": "v5"},
    ... ]
    >>> mg = MGazine(downloads)
    >>> print(mg)
    MGazine containing:
    - MGnify pipeline versions: ['v5']
    - Number of downloads: 2
    - Short descriptions: ['desc1', 'desc2']
    - Nonempty metadata sets:

    """

    def __init__(
        self,
        downloads: list[dict[str, Any]],
        config: Optional[MGnipyConfig] = None,
        *,
        client: Optional[Client | AuthenticatedClient] = None,
        mgnify_studies: list[dict[str, Any]] | None = None,
        mgnify_analyses: list[dict[str, Any]] | None = None,
        mgnify_runs: list[dict[str, Any]] | None = None,
        mgnify_samples: list[dict[str, Any]] | None = None,
        mgnify_assemblies: list[dict[str, Any]] | None = None,
        biosamples_metadata: list[dict[str, Any]] | None = None,
        obs: list[dict[str, Any]] | None = None,
    ):
        self.downloads = downloads
        self.config = config or MGnipyConfig()
        self.client = client or init_httpx_client(self.config)
        self.httpx_client = self.client.get_httpx_client()
        self.async_httpx_client = self.client.get_async_httpx_client()
        self.semaphore = get_semaphore()

        self._mgnify_studies: list[dict[str, Any]] | None = mgnify_studies
        self._mgnify_analyses: list[dict[str, Any]] | None = mgnify_analyses
        self._mgnify_runs: list[dict[str, Any]] | None = mgnify_runs
        self._mgnify_samples: list[dict[str, Any]] | None = mgnify_samples
        self._mgnify_assemblies: list[dict[str, Any]] | None = mgnify_assemblies
        self._biosamples_metadata: list[dict[str, Any]] | None = biosamples_metadata
        self._obs: list[dict[str, Any]] | None = obs
        self._lazy_merged: list[pl.LazyFrame] | None = None

    def __call__(
        self,
        downloads: list[dict[str, Any]],
        *,
        mgnify_studies: list[dict[str, Any]] | None = None,
        mgnify_analyses: list[dict[str, Any]] | None = None,
        mgnify_runs: list[dict[str, Any]] | None = None,
        mgnify_samples: list[dict[str, Any]] | None = None,
        mgnify_assemblies: list[dict[str, Any]] | None = None,
        biosamples_metadata: list[dict[str, Any]] | None = None,
        obs: list[dict[str, Any]] | None = None,
    ) -> "MGazine":
        """
        Creates a new instance of MGnetizer with the specified resource, :meth:`all_ids`, :meth:`mgnify_metadata`, and detail_proxy. This allows for creating a new MGnetizer instance with different parameters without modifying the existing instance.
        """
        return self.__class__(
            downloads,
            config=self.config,
            client=self.client,
            mgnify_studies=mgnify_studies or self._mgnify_studies,
            mgnify_analyses=mgnify_analyses or self._mgnify_analyses,
            mgnify_runs=mgnify_runs or self._mgnify_runs,
            mgnify_samples=mgnify_samples or self._mgnify_samples,
            mgnify_assemblies=mgnify_assemblies or self._mgnify_assemblies,
            biosamples_metadata=biosamples_metadata or self._biosamples_metadata,
            obs=obs or self._obs,
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(downloads={len(self.downloads)}, "
            f"pipeline_versions={self.list_pipeline_version()}, "
            f"short_descriptions={self.list_short_descriptions()}, "
            f"available_metadata_sets={self.available_metadata_sets})"
        )

    def __str__(self):
        return (
            f"{self.__class__.__name__} containing:\n"
            f"- MGnify pipeline versions: {self.list_pipeline_version()}\n"
            f"- Number of downloads: {len(self.downloads)}\n"
            f"- Short descriptions: {pformat(self.list_short_descriptions())}\n"
            f"- Nonempty metadata sets: {', '.join([f'.{m}' for m in self.available_metadata_sets])}\n"
        )

    def __add__(self, other):
        combined_downloads = self.downloads + other.downloads
        return MGazine(
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
            obs=(self.obs + other.obs).to_list(),
        )

    def __getattr__(self, name):
        """Can access dataset types by name.

        Right now only "taxonomic" and "taxonomic_dwc_ready" are supported.

        Returns
        -------
        TaxaMGazine or DWCTaxaMGazine
            These are specialized subclasses of :class:`MGazine` that provide additional methods for working with taxonomic datasets. See :class:`TaxaMGazine` and :class:`DWCTaxaMGazine` for more details.

        Examples
        --------
        mg = MGazine(downloads) # doctest: +SKIP
        mg.taxonomic # doctest: +SKIP
        # Or if you want the Darwin core ready files
        mg.taxonomic_dwc_ready # doctest: +SKIP
        """
        if name.startswith("taxonomic"):
            # get all downloads with "taxonom" in the download_type
            taxonom_downloads = []
            for k, v in self.by_downloads_col("download_type").items():
                if "taxonom" in k.lower():
                    taxonom_downloads.extend(v)

            if len(taxonom_downloads) == 0:
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{name}' because no taxonomic downloads are available."
                )

            # split into dwc-ready and non-dwc-ready
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
                    mgnify_studies=self._mgnify_studies,
                    mgnify_analyses=self._mgnify_analyses,
                    mgnify_runs=self._mgnify_runs,
                    mgnify_samples=self._mgnify_samples,
                    mgnify_assemblies=self._mgnify_assemblies,
                    biosamples_metadata=self._biosamples_metadata,
                    obs=self._obs,
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
                    mgnify_studies=self._mgnify_studies,
                    mgnify_analyses=self._mgnify_analyses,
                    mgnify_runs=self._mgnify_runs,
                    mgnify_samples=self._mgnify_samples,
                    mgnify_assemblies=self._mgnify_assemblies,
                    biosamples_metadata=self._biosamples_metadata,
                    obs=self._obs,
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
        """Filter the MGazine by a specific pipeline version or short description."""
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
            mgnify_studies=self._mgnify_studies,
            mgnify_analyses=self._mgnify_analyses,
            mgnify_runs=self._mgnify_runs,
            mgnify_samples=self._mgnify_samples,
            mgnify_assemblies=self._mgnify_assemblies,
            biosamples_metadata=self._biosamples_metadata,
            obs=self._obs,
        )

    @property
    def available_metadata_sets(self) -> list[str]:
        """Return a list of available metadata sets in the MGazine.

        This property checks which metadata sets (e.g., studies, analyses, runs, samples, assemblies, biosamples) are non-empty and returns their names as a list.

        Returns
        -------
        list of str
            A list of names of non-empty metadata sets available in the MGazine.

        Examples
        --------
        >>> mg = MGazine(downloads) # doctest: +SKIP
        >>> mg.available_metadata_sets # doctest: +SKIP
        ['mgnify_studies', 'mgnify_analyses', 'mgnify_runs']
        """

        return [f for f in METADATA_SETS if len(getattr(self, f)) > 0]

    @property
    def aliases(self) -> list[str]:
        """Return a list of all download aliases.

        Example
        --------
        >>> downloads = [{"alias": "example.txt", "url": "http://ex/x"}]
        >>> MGazine(downloads).aliases
        ['example.txt']
        """
        return [f["alias"] for f in self.downloads if "alias" in f]

    @property
    def urls(self) -> list[Optional[str]]:
        """
        Return a list of all download URLs. Same as :meth:`url_list`.

        Examples
        --------
        >>> downloads = [{"alias": "example.txt", "url": "http://ex/x"}]
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
        >>> downloads = [{"alias": "example.txt", "url": "http://ex/x"}]
        >>> MGazine(downloads).url_dict
        {'example.txt': 'http://ex/x'}
        """

        return {f["alias"]: f.get("url", None) for f in self.downloads}

    @property
    def url_list(self):
        """Return a list of all download URLs.

        Examples
        --------
        >>> downloads = [{"alias": "example.txt", "url": "http://ex/x"}]
        >>> MGazine(downloads).urls
        ['http://ex/x']
        """
        return [f.get("url", None) for f in self.downloads]

    def downloads_df(self, **pd_kwargs) -> pd.DataFrame:
        """The downloads as a DataFrame.

        This returns a :class:`pandas.DataFrame` of all downloads. The dataframe should contain columns such as ``alias``, ``url`` and ``file_type`` (TODO pandera).

        Parameters
        ----------
        pd_kwargs : dict
            Additional keyword arguments to pass to the :class:`pandas.DataFrame` constructor.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the downloads information

        Examples
        --------
        >>> downloads = [{"alias": "example.txt", "url": "http://ex/x", "file_type": "txt"}]
        >>> mag = MGazine(downloads)
        >>> df = mag.downloads_df(index=["boop"])
        >>> list(df.columns)
        ['alias', 'url', 'file_type']
        >>> df.index
        Index(['boop'], dtype='object')
        """
        df = pd.DataFrame(self.downloads, **pd_kwargs)
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
        """The short description of the MGazine.

        This property returns the FIRST short description of the MGazine, which is derived from the downloads.
        If multiple short descriptions are present, a warning is issued.
        """
        if len(self.list_pipeline_version()) > 1:
            logger.warning(
                "Multiple pipeline versions detected -- MGazine methods may not work as expected."
            )

        if len(self.list_short_descriptions()) > 1:
            logger.warning(
                f"Multiple descriptions detected & `short_desc` not specified -- MGazine methods may not work as expected.\n'{self.list_short_descriptions()[0]}' may be used for e.g., caching, `long_short_mapping`."
            )
        return self.list_short_descriptions()[0]

    def list_pipeline_version(self) -> list[str]:
        """A list of unique pipeline versions in the MGazine.

        Returns
        -------
        list of str
            A list of unique pipeline versions extracted from the downloads.

        Examples
        --------
        >>> downloads = [
        ...     {"alias": "example.txt", "url": "http://ex/x", "pipeline_version": 'v4_1'},
        ...     {"alias": "example2.txt", "url": "http://ex/x2", "pipeline_version": 'v5'},
        ... ]
        >>> MGazine(downloads).list_pipeline_version()
        ['v4_1', 'v5']
        """

        if self.downloads_df().empty:
            return []

        avail_vers = sorted(self.downloads_df()["pipeline_version"].unique().tolist())

        return avail_vers

    def list_short_descriptions(self) -> list[str]:
        """A list of unique short descriptions of the downloads.

        The unique short descriptions in the given column

        Returns
        -------
        list of str
            A list of unique short descriptions extracted from the downloads.

        Examples
        --------
        >>> downloads = [
        ...     {"alias": "example.txt", "short_description": "shortdesc1"},
        ...     {"alias": "boo.txt", "short_description": "shortdesc1"},
        ...     {"alias": "example2.txt", "short_description": "shortdesc2"},
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
        """Download a file by its alias or URL.

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
        mg = MGazine(downloads) # doctest: +SKIP
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

        with (
            init_httpx_client(self.config).get_httpx_client()
            if self.httpx_client.is_closed
            else self.httpx_client
        ):
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
                except RuntimeError as re:
                    logger.error(
                        f"Runtime error occurred while downloading {alias}: {re}. Attempting to renew_client and retry"
                    )
                    self.renew_client()
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

        async with (
            init_httpx_client(self.config).get_async_httpx_client()
            if self.async_httpx_client.is_closed
            else self.async_httpx_client
        ):
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
                except RuntimeError as re:
                    logger.error(
                        f"Runtime error occurred while downloading {f}: {re}. Attempting to renew_client and retry"
                    )
                    self.renew_client()
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
                    self.stream(alias=alias, chunksize=1000, df_engine="polars")
                    for alias in aliases
                ],
                how=how,
                **pl_kwargs,
            )

        if urls:
            self._lazy_merged = pl.concat(
                [
                    self.stream(url=url, chunksize=1000, df_engine="polars")
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

    def to_pandas(self, **pd_kwargs) -> pd.DataFrame:
        if self._lazy_merged is None:
            logger.warning(
                "Lazy merged DataFrame not available. Returning empty DataFrame."
            )
            return pd.DataFrame()
        return self.lazy_merged.collect().to_pandas(**pd_kwargs)

    def to_polars(self) -> pl.DataFrame:
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
