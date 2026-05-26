from __future__ import annotations
import logging
from typing import Any, Optional, Literal, TYPE_CHECKING
import functools as ft
import polars as pl
import anndata as ad
import pandas as pd
from mgnipy._models.config import MGnipyConfig
from mgnipy.V2.proxies.runs import RunDetail
from mgnipy.V2.mixins import DiskCheckpointer, ResultsHandler
from tqdm import tqdm as tqdm_sync
from mgnify_pipelines_toolkit.constants.tax_ranks import (
    SILVA_TAX_RANKS,
    PR2_TAX_RANKS,
    MOTUS_TAX_RANKS,
    SHORT_SILVA_TAX_RANKS,
    SHORT_PR2_TAX_RANKS,
    SHORT_MOTUS_TAX_RANKS,
)

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


class TaxonomicCurator:

    TAX_COLS = ["taxonomy", "#SampleID"]

    def __init__(
        self,
        mgazine: "MGazine",
        short_desc: Optional[str] = None,
        config: Optional[MGnipyConfig] = None,
        long_short_mapping: Optional[dict[str, str]] = None,
        runs_results: Optional[list[dict[str, Any]]] = None,
        samples_results: Optional[list[dict[str, Any]]] = None,
        studies_results: Optional[list[dict[str, Any]]] = None,
        biosamples_results: Optional[list[dict[str, Any]]] = None,
    ):

        self.mz = mgazine
        self.config = config or mgazine.config

        if len(self.mz.list_pipeline_vers()) > 1:
            logging.warning(
                "Multiple pipeline versions detected in MGazine. Curator methods may not work as expected."
            )

        if len(self.mz.list_short_descriptions()) > 1:
            logging.warning(
                f"Multiple short descriptions detected in MGazine and `short_desc` was not specified. Only the first short description will be used (i.e., {self.mz.list_short_descriptions()[0]})."
            )
        self.short_desc = short_desc or self.mz.list_short_descriptions()[0]
        logging.info(
            f"TaxonomicCurator initialized for short description: {self.short_desc}"
        )

        # determine mapping
        if long_short_mapping is not None:
            self.long_short_mapping = long_short_mapping
        elif "PR2" in self.short_desc.upper():
            self.long_short_mapping = dict(
                zip(PR2_TAX_RANKS, SHORT_PR2_TAX_RANKS, strict=True)
            )
        elif "MOTUS" in self.short_desc.upper():
            self.long_short_mapping = dict(
                zip(MOTUS_TAX_RANKS, SHORT_MOTUS_TAX_RANKS, strict=True)
            )
        else:  # default to silva?
            self.long_short_mapping = dict(
                zip(SILVA_TAX_RANKS, SHORT_SILVA_TAX_RANKS, strict=True)
            )
        logging.info(
            f"TaxonomicCurator long to short rank mapping set: {self.long_short_mapping}"
        )

        self.is_dwcready: bool = "dwc-ready" in self.short_desc.lower()
        # cache
        self._lazy_merged: pl.LazyFrame = None
        self._runs_accessions: list = None
        self._runs_results: list = runs_results or []
        self.samples_results: list = samples_results or []
        self.studies_results: list = studies_results or []
        self.biosamples_results: list = biosamples_results or []

        # getting merged lazyframe for runs acessions
        self._lazy_merger()

        self.cache_handler = DiskCheckpointer(
            params_getter=lambda: {
                "mgazine": str(self.mz),
                "short_desc": self.short_desc,
                "runs_accessions": self.runs_accessions,
            },
            resource_str=f"TaxonomicCurator_{self.short_desc}",
            config=self.config,
        )
        self.cache_handler.load_cache()
        self._runs_results = self.cache_handler._results.get(1, [])
        self.samples_results = self.cache_handler._results.get(2, [])
        self.studies_results = self.cache_handler._results.get(3, [])
        self.biosamples_results = self.cache_handler._results.get(4, [])

    @property
    def lazy_merged(self) -> pl.LazyFrame:
        if self._lazy_merged is None:
            self._lazy_merger()
        return self._lazy_merged

    @property
    def runs_results(self) -> list[dict[str, Any]]:
        return self._runs_results

    @runs_results.setter
    def runs_results(self, value: list[dict[str, Any]]):
        self._runs_results = value
        self.cache_handler.write_results(1, self._runs_results)

    @property
    def runs_accessions(self) -> list:
        if self._runs_accessions is not None:
            return self._runs_accessions

        if self.is_dwcready:
            self._runs_accessions = self.lazy_merged["RunID"].to_list()
            return self._runs_accessions
        else:
            not_run_id = (
                self.TAX_COLS
                + ["kingdom", "phylum"]
                + SILVA_TAX_RANKS
                + PR2_TAX_RANKS
                + MOTUS_TAX_RANKS
            )
            self._runs_accessions = [
                run
                for run in self.lazy_merged.collect_schema().names()
                if run not in not_run_id
            ]
            return self._runs_accessions

    def clear_cache(self):
        from mgnipy.mgnipy import MGnipy

        MG = MGnipy(config=self.config)
        MG.clear_subcaches()
        logging.info("MGnipy cache cleared via TaxonomicCurator helper.")
        self._lazy_merged = None
        self._runs_accessions = None

    def _iter_runs(self) -> list[str]:
        run_results_accessions = [mg.get("accession") for mg in self.runs_results]
        leftovers = [x for x in self.runs_accessions if x not in run_results_accessions]
        return leftovers

    def enrich_runs(self, limit: Optional[int] = 200, hide_progress: bool = False):
        """
        Enriches the run metadata for the runs in the taxonomic dataset by iterating through the run accessions and retrieving their details using the RunDetail proxy. The results are cached using the DiskCheckpointer to avoid redundant API calls in future runs.

        Parameters
        ----------
        limit : Optional[int], default=200
            An optional integer to limit the number of runs to enrich. If not provided, it defaults to 200. This is useful for testing or when dealing with large datasets to avoid long runtimes during development. If set to None, there will be no limit on the number of runs enriched.

        Returns
        -------
        None
            The function does not return anything. It updates the `run_results` attribute of the TaxonomicCurator instance with the enriched run metadata.

        """

        logging.debug(
            f"Starting enrichment of runs for short description {self.short_desc} with limit {limit}."
        )

        runs_todo: list[str] = self._iter_runs()[:limit]

        for count, run in enumerate(
            tqdm_sync(
                runs_todo,
                total=len(self.runs_accessions),
                initial=len(self.runs_results),
                desc="Enriching runs",
                disable=hide_progress,
            )
        ):
            logging.info(
                f"Enriching run {run} for short description {self.short_desc}. Count: {count}"
            )
            # get metadata
            mg = RunDetail(id=run, config=self.config).get()
            if mg is not False:
                logging.debug(f"Enriched metadata for run {run}: {mg}")
                self._runs_results.append(mg)
                self.cache_handler.write_results(1, self._runs_results)
            else:
                logging.warning(f"Run {run} could not be retrieved. Skipping.")

    async def aenrich_runs(
        self, limit: Optional[int] = 200, hide_progress: bool = False
    ):
        # TODO
        pass

    def enrich_samples(self):
        pass

    def enrich_studies(self):
        pass

    def enrich_biosamples(self):
        pass

    def _lazy_merger(self):

        # lazyframes for given short_desc
        lazyframes = [
            self.mz.stream(url=u, chunksize=1000, dataframe_engine="polars")
            for u in self.mz.url_list
        ]

        # if dwc then just concat
        if self.is_dwcready:
            self._lazy_merged = pl.concat(lazyframes, how="vertical_relaxed")
            return

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
            logging.warning(
                "Could not determine common column to merge on in taxonomic datasets. Returning concatenated lazyframes without merging."
            )
            self._lazy_merged = pl.concat(lazyframes, how="vertical_relaxed")

    def taxonomic_metadata(
        self,
        fill_na: Any = "NA",
        df_engine: Literal["polars", "pandas"] = "pandas",
    ) -> pl.DataFrame | pd.DataFrame:

        if self.is_dwcready:
            logging.warning(
                "Dataset is dwc-ready. Returning concatenated lazyframes without taxonomic splitting."
            )
            df = self.lazy_merged.collect()
            if df_engine == "pandas":
                return df.to_pandas()
            elif df_engine == "polars":
                return df

        try:
            df = prep_obs(
                df=self.lazy_merged.collect(),
                tax_col="taxonomy",
                long_short_mapping=self.long_short_mapping,
                fill_na=fill_na,
            )
        except KeyError:
            df = prep_obs(
                df=self.lazy_merged.collect(),
                tax_col="#SampleID",
                long_short_mapping=self.long_short_mapping,
                fill_na=fill_na,
            )
        if df_engine == "pandas":
            return df.to_pandas()
        elif df_engine == "polars":
            return df

    def metadata(
        self,
        df_engine: Literal["polars", "pandas"] = "pandas",
        strict: bool = False,
        expand_nested_dicts: bool = True,
    ) -> pl.DataFrame | pd.DataFrame:

        results_helper = ResultsHandler(
            data=self.runs_results,
        )

        if strict and len(self.runs_results) < len(self.runs_accessions):
            logging.warning(
                f"Strict mode is on but only {len(self.runs_results)} runs have been enriched out of {len(self.runs_accessions)} total runs. Returning without enrichment."
            )
            if df_engine == "pandas":
                return pd.DataFrame(
                    self.runs_accessions, columns=["accession"]
                ).set_index("accession")
            elif df_engine == "polars":
                return pl.DataFrame(
                    self.runs_accessions,
                    columns=["accession"],
                )

        if df_engine == "pandas":
            return results_helper.to_df(
                expand_nested_dicts=expand_nested_dicts
            ).set_index("accession")
        elif df_engine == "polars":
            return results_helper.to_polars(
                expand_nested_dicts=expand_nested_dicts,
            )  # .with_row_index("accession")

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
        return ad.AnnData(
            self.X(),
            obs=self.taxonomic_metadata(),
            var=self.metadata(),
            **anndata_kwargs,
        )
