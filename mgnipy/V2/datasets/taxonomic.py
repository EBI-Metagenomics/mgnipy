from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

import functools as ft
import logging

from mgnipy.emgapi_v2_client.client import AuthenticatedClient, Client
from typing import Any, Literal, Optional
import anndata as ad
import pandas as pd
import polars as pl
from mgnipy._models.constants.tax_ranks import (
    MOTUS_TAX_RANKS,
    PR2_TAX_RANKS,
    SHORT_MOTUS_TAX_RANKS,
    SHORT_PR2_TAX_RANKS,
    SHORT_SILVA_TAX_RANKS,
    SILVA_TAX_RANKS,
)
from mgnipy._models.config import MGnipyConfig
from mgnipy.V2.datasets import MGazine


def prep_obs(
    df: pl.DataFrame,
    tax_col: Literal["taxonomy", "#SampleID"],
    long_short_mapping: Optional[dict[str, str]],
    fill_na: Any = "NA",
) -> pl.DataFrame:
    """
    Prepares the taxonomy DataFrame by splitting the taxonomy string into separate columns for each taxonomic rank.

    Parameters
    ----------
    df : pl.DataFrame
        A Polars DataFrame containing a column named 'taxonomy' with taxonomic classifications in a semicolon-separated format.
    tax_col : Literal["taxonomy", "#SampleID"]
        The name of the column in the DataFrame that contains the taxonomy string to be split.
    long_short_mapping : Optional[dict[str, str]]
        A dictionary mapping the long taxonomic rank names (e.g., "Superkingdom") to their corresponding short prefixes (e.g., "sk"). This is used to clean the taxonomic rank values by stripping the short prefixes.
    fill_na : Optional[Any], default="NA"
        The value to use for filling empty strings or null values in the taxonomic rank columns after stripping the short prefixes. If not provided, it defaults to "NA".

    Returns
    -------
    pl.DataFrame
        A Polars DataFrame with separate columns for each taxonomic rank based on the taxonomy ranks defined in the constants.
    """

    # getting taxonomy as own df
    df_ranks = (
        df.with_columns(
            df[tax_col]
            # split into n ranks
            .str.splitn(";", n=len(long_short_mapping))
            # rename n ranks to long name e.g., superkingdom
            .struct.rename_fields(list(long_short_mapping.keys()))
            # alias and unnest
            .alias("taxonomy_split")
        ).unnest("taxonomy_split")
        # select only these new columns
        .select(list(long_short_mapping.keys()))
    )

    # cleaning the ranks
    df_ranks = df_ranks.with_columns(
        *[
            # for each col
            df_ranks[col_name]
            # strip short prefix e.g., d__
            .str.strip_chars_start(f"{long_short_mapping[col_name]}__")
            # fill empty strings / nulls
            .replace("", fill_na).fill_null(fill_na)
            for col_name in long_short_mapping
        ]
    )
    return df_ranks


class DWCTaxaMGazine(MGazine):

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
        """A specialized MGazine class for handling DwC-ready taxonomic datasets."""

        super().__init__(
            downloads=downloads,
            config=config,
            client=client,
            mgnify_runs=mgnify_runs,
            mgnify_samples=mgnify_samples,
            mgnify_studies=mgnify_studies,
            biosamples_metadata=biosamples_metadata,
            mgnify_analyses=mgnify_analyses,
            mgnify_assemblies=mgnify_assemblies,
        )
        # extra dwc check
        if ("dwc-ready" not in self.short_desc.lower()) or (
            "dwcready" not in self.short_desc.lower()
        ):
            logger.warning(
                f"Short description {self.short_desc} does not contain 'dwc-ready'. This curator is intended for DwC-ready datasets. Proceeding anyway but results may not be as expected."
            )

        self._run_accessions: list | None = None

        print(
            f"{self.__str__()}"
            "-----------------------\n"
            "Next steps: Use `.load()` to initialize.\n"
        )

    def load(self) -> None:
        """Lazy load taxonomic datasets.

        This method lazily loads and attempts to merge all the datasets contained in :meth:`url_list`.
        Lazy loads as a :class:`polars.LazyFrame` which can then be accessed via property :meth:`lazy_merged`).
        Doesnt return anything.
        """
        # lazy loading and merging of the datasets contained in `url_list`.
        _ = self.lazy_concat(urls=self.url_list)

    @property
    def runs_accessions(self) -> list:
        """The list of run accessions from the merged taxonomic datasets.

        Notes
        -----
        - This property retrieves the list of run accessions from the merged taxonomic datasets.
        - If the run accessions have already been computed and cached, it returns the cached value.
        - Otherwise, it attempts to compute the run accessions by selecting the "RunID" column from the merged dataset and collecting it into a list.
        """
        if self._run_accessions is not None:
            return self._run_accessions
        else:
            try:
                self._run_accessions = (
                    self.lazy_merged.select("RunID").collect().to_series().to_list()
                )
            except Exception as e:
                logger.error(f"Error retrieving runs accessions: {e}")
        return self._run_accessions

    def taxonomic_metadata(
        self,
        df_engine: Literal["polars", "pandas"] = "pandas",
    ) -> pl.DataFrame | pd.DataFrame:
        """Gets the taxonomic metadata.

        Prepares the taxonomic metadata DataFrame by splitting the taxonomy string into separate columns for each taxonomic rank.

        Parameters
        ----------
        df_engine : Literal["polars", "pandas"], optional
            The DataFrame engine to use for the output.
            If "polars" is specified, a :class:`polars.DataFrame` is returned;
            if "pandas" is specified, a :class:`pandas.DataFrame` is returned.
        """

        # the taxa columns to get
        col_names: list[str] = list(self.long_short_mapping.keys())
        # collect the lazyframe and select only the taxa columns
        df = self.lazy_merged.select(col_names).collect()
        # return the appropriate DataFrame engine
        if df_engine == "pandas":
            return df.to_pandas()
        elif df_engine == "polars":
            return df


class TaxaMGazine(MGazine):
    """not for dwc"""

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

        self.TAX_COLS = (
            ["taxonomy", "#SampleID"]
            + ["kingdom", "phylum"]
            + SILVA_TAX_RANKS
            + PR2_TAX_RANKS
            + MOTUS_TAX_RANKS
        )

        super().__init__(
            downloads=downloads,
            config=config,
            client=client,
            mgnify_runs=mgnify_runs,
            mgnify_samples=mgnify_samples,
            mgnify_studies=mgnify_studies,
            biosamples_metadata=biosamples_metadata,
            mgnify_analyses=mgnify_analyses,
            mgnify_assemblies=mgnify_assemblies,
        )

        self._runs_accessions = None
        self._params: dict[str, Any] = {
            "mgazine": str(self),
            "short_desc": self.short_desc,
        }
        print(
            f"{self.__str__()}"
            "-----------------------\n"
            "Next steps: Use `.load()` to initialize.\n"
        )

    def load(self) -> None:
        # lazy loading and merging of the datasets contained in `url_list`.
        _ = self._lazy_merger()
        # now get run accessions and params for cachekey
        self._params: dict[str, Any] = {
            "mgazine": str(self),
            "short_desc": self.short_desc,
            "runs_accessions": sorted(self.runs_accessions),
        }
        # load cache
        self.load_cache()

    @property
    def runs_accessions(self) -> list:
        if self._runs_accessions is not None:
            return self._runs_accessions

        self._runs_accessions = [
            run
            for run in self.lazy_merged.collect_schema().names()
            if run not in self.TAX_COLS
        ]
        return self._runs_accessions

    def long_short_mapping(self, value: dict[str, str] = None) -> dict[str, str]:
        # determine mapping
        if value is not None:
            return value
        elif "PR2" in self.short_desc.upper():
            return dict(zip(PR2_TAX_RANKS, SHORT_PR2_TAX_RANKS, strict=True))
        elif "MOTUS" in self.short_desc.upper():
            return dict(zip(MOTUS_TAX_RANKS, SHORT_MOTUS_TAX_RANKS, strict=True))
        else:  # default to silva?
            return dict(zip(SILVA_TAX_RANKS, SHORT_SILVA_TAX_RANKS, strict=True))

    def _lazy_merger(self):

        # lazyframes for given short_desc
        lazyframes = [
            self.stream(url=u, chunksize=1000, dataframe_engine="polars").rename(
                {"#SampleID": "taxonomy"}, strict=False
            )
            for u in self.url_list
        ]

        # otherwise
        reader_cols = [r.collect_schema().names() for r in lazyframes]

        if all(["#SampleID" in cols for cols in reader_cols]):
            on_col = "#SampleID"
        elif all(["taxonomy" in cols for cols in reader_cols]):
            on_col = "taxonomy"
        elif all(["kingdom" in cols for cols in reader_cols]) and all(
            ["phylum" in cols for cols in reader_cols]
        ):
            on_col = ["kingdom", "phylum"]
        else:
            on_col = None

        if on_col is not None:
            merged = ft.reduce(
                lambda left, right: left.join(
                    right, on=on_col, how="full", coalesce=True
                ),
                lazyframes,
            )
            self._lazy_merged = merged
        else:
            logger.warning(
                "Could not determine common column to merge on in taxonomic datasets. Returning concatenated lazyframes without merging."
            )
            self._lazy_merged = pl.concat(lazyframes, how="vertical_relaxed")

    def taxonomic_metadata(
        self,
        fill_na: Any = "NA",
        df_engine: Literal["polars", "pandas"] = "pandas",
    ) -> pl.DataFrame | pd.DataFrame:

        col_names = self.lazy_merged.collect_schema().names()

        if "taxonomy" in col_names:
            df = prep_obs(
                df=self.lazy_merged.collect(),
                tax_col="taxonomy",
                long_short_mapping=self.long_short_mapping,
                fill_na=fill_na,
            )
        elif "#SampleID" in col_names:
            df = prep_obs(
                df=self.lazy_merged.collect(),
                tax_col="#SampleID",
                long_short_mapping=self.long_short_mapping,
                fill_na=fill_na,
            )
        elif ("kingdom" in col_names) and ("phylum" in col_names):
            df = self.lazy_merged.select(["kingdom", "phylum"]).collect()
        else:
            logger.warning(
                f"Could not determine taxonomy column in taxonomic dataset. Expected one of 'taxonomy' or '#SampleID' or at least 'kingdom' and 'phylum'. Attempting to match known taxonomic ranks in `long_short_mapping`. e.g. {list(self.long_short_mapping.keys())}"
            )
            existing_tax_cols = [
                col for col in self.long_short_mapping if col in col_names
            ]
            df = self.lazy_merged.select(existing_tax_cols).collect()

        if df_engine == "pandas":
            return df.to_pandas()
        elif df_engine == "polars":
            return df

    def X(
        self, df_engine: Literal["polars", "pandas"] = "pandas"
    ) -> pl.DataFrame | pd.DataFrame:
        df_pl = self.lazy_merged.collect()
        df_pl = df_pl.drop(self.TAX_COLS, strict=False)
        if df_engine == "pandas":
            return df_pl.to_pandas()
        elif df_engine == "polars":
            return df_pl

    def to_anndata(self, **anndata_kwargs) -> ad.AnnData:
        """
        Converts the taxonomic metadata to an AnnData object. The taxonomic ranks are stored in the `obs` attribute of the AnnData object.

        Parameters
        ----------
        **anndata_kwargs
            Additional keyword arguments to pass to the `AnnData` constructor.

        Returns
        -------
        ad.AnnData
            An AnnData object containing the taxonomic metadata in the `obs` attribute.
        """
        try:
            return ad.AnnData(
                self.X()[sorted(self.X().columns)],
                obs=self.taxonomic_metadata(),
                var=self.metadata().sort_index(),
                **anndata_kwargs,
            )
        except ValueError as e:
            logger.error(
                f"Returning without metadata() as var - Error occurred while converting to AnnData: {e}"
            )
            return ad.AnnData(
                self.X(),
                obs=self.taxonomic_metadata(),
                var=None,
                **anndata_kwargs,
            )
