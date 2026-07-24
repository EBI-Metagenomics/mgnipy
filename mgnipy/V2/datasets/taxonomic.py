from __future__ import annotations

import functools as ft
import logging


logger = logging.getLogger(__name__)
from typing import TYPE_CHECKING, Any, Literal, Optional

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

if TYPE_CHECKING:
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


class TaxaSetup:

    def short_desc(self) -> str:
        if len(self.list_pipeline_version()) > 1:
            logger.warning(
                "Multiple pipeline versions detected -- MGazine methods may not work as expected."
            )

        if len(self.list_short_descriptions()) > 1:
            logger.warning(
                f"Multiple descriptions detected & `short_desc` not specified -- MGazine methods may not work as expected.\n'{self.mz.list_short_descriptions()[0]}' used for `long_short_mapping` determination and caching."
            )
        return self.list_short_descriptions()[0]

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

    def lazy_merged(self):

        lazyframes = [
            self.stream(url=u, chunksize=1000, dataframe_engine="polars")
            for u in self.url_list
        ]

        return pl.concat(lazyframes, how="vertical_relaxed")

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

    @property
    def runs_accessions(self) -> list:
        try:
            return self.lazy_merged.select("RunID").collect().to_series().to_list()
        except Exception as e:
            logger.error(f"Error retrieving runs accessions: {e}")
            return None


class DWCTaxaMGazine(TaxaSetup):

    def __init__(
        self,
        mgazine: "MGazine",
        config: Optional[MGnipyConfig] = None,
        *,
        long_short_mapping: Optional[dict[str, str]] = None,
        mgnify_assemblies: Optional[list[dict[str, Any]]] = None,
        mgnify_runs: Optional[list[dict[str, Any]]] = None,
        mgnify_samples: Optional[list[dict[str, Any]]] = None,
        mgnify_studies: Optional[list[dict[str, Any]]] = None,
        biosamples_metadata: Optional[list[dict[str, Any]]] = None,
        mgnify_analyses: Optional[list[dict[str, Any]]] = None,
    ):

        super().__init__(
            mgazine=mgazine,
            config=config,
            long_short_mapping=long_short_mapping,
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

    def load(self):
        """
        Lazy loading and merging of the datasets contained in `url_list`.
        This method should be called after instantiating to set up the internal state and load any cached results.
        """
        self._init_cache_handler_state()
        logger.info(
            f"{self.__class__.__name__} loaded with {len(self.url_list)} datasets. \nCached runs results: {len(self.mgnify_runs)} of total {len(self.runs_accessions)}."
        )

    def taxonomic_metadata(
        self,
        fill_na: Any = "NA",
        df_engine: Literal["polars", "pandas"] = "pandas",
        strict: bool = False,
    ) -> pl.DataFrame | pd.DataFrame:

        df = self.lazy_merged.select(list(self.long_short_mapping.keys())).collect()
        if df_engine == "pandas":
            return df.to_pandas()
        elif df_engine == "polars":
            return df


class TaxaMGazine(TaxaSetup):
    """not for dwc"""

    def __init__(
        self,
        mgazine: "MGazine",
        config: Optional[MGnipyConfig] = None,
        *,
        long_short_mapping: Optional[dict[str, str]] = None,
        mgnify_assemblies: Optional[list[dict[str, Any]]] = None,
        mgnify_runs: Optional[list[dict[str, Any]]] = None,
        mgnify_samples: Optional[list[dict[str, Any]]] = None,
        mgnify_studies: Optional[list[dict[str, Any]]] = None,
        biosamples_metadata: Optional[list[dict[str, Any]]] = None,
        mgnify_analyses: Optional[list[dict[str, Any]]] = None,
    ):

        self.TAX_COLS = (
            ["taxonomy", "#SampleID"]
            + ["kingdom", "phylum"]
            + SILVA_TAX_RANKS
            + PR2_TAX_RANKS
            + MOTUS_TAX_RANKS
        )
        super().__init__(
            mgazine=mgazine,
            config=config,
            long_short_mapping=long_short_mapping,
            mgnify_runs=mgnify_runs,
            mgnify_samples=mgnify_samples,
            mgnify_studies=mgnify_studies,
            biosamples_metadata=biosamples_metadata,
            mgnify_analyses=mgnify_analyses,
            mgnify_assemblies=mgnify_assemblies,
        )

        print(
            f"{self.__str__()}"
            "-----------------------\n"
            "Next steps: Use `.load()` to initialize.\n"
        )

    def load(self):
        """
        Lazy loading and merging of the datasets contained in `url_list`.
        This method should be called after instantiating to set up the internal state and load any cached results.
        """
        self._init_cache_handler_state()
        print(
            f"{self.__class__.__name__} loaded with {len(self.url_list)} datasets. \nCached runs results: {len(self.mgnify_runs)} of total {len(self.runs_accessions)}."
        )

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

    # overwrite
    def _lazy_merger(self):

        # lazyframes for given short_desc
        lazyframes = [
            self.mz.stream(url=u, chunksize=1000, dataframe_engine="polars").rename(
                {"#SampleID": "taxonomy"}, strict=False
            )
            for u in self.mz.url_list
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

    # overwrite
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
