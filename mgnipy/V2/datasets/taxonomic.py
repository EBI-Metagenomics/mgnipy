from __future__ import annotations

import functools as ft
import logging

from mgnipy._shared_helpers.biosamples_helper import (
    get_biosample_metadata,
)

logger = logging.getLogger(__name__)
from pprint import pformat
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
from tqdm import tqdm as tqdm_sync
from tqdm.asyncio import tqdm_asyncio
import asyncio
from mgnipy._models.config import MGnipyConfig
from mgnipy.V2.datasets import MGazine
from mgnipy.V2.mixins import DiskCheckpointer, ResultsHandler
from mgnipy.V2.proxies.assemblies import AssemblyDetail
from mgnipy.V2.proxies.runs import RunDetail

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


class _MGazineSetup(MGazine):

    def __init__(
        self,
        mgazine: "MGazine",
        config: Optional[MGnipyConfig] = None,
        *,
        long_short_mapping: Optional[dict[str, str]] = None,
        assemblies_details: Optional[list[dict[str, Any]]] = None,
        runs_details: Optional[list[dict[str, Any]]] = None,
        samples_details: Optional[list[dict[str, Any]]] = None,
        studies_details: Optional[list[dict[str, Any]]] = None,
        biosamples_details: Optional[list[dict[str, Any]]] = None,
        analyses_details: Optional[list[dict[str, Any]]] = None,
    ):

        super().__init__(downloads=mgazine.downloads, config=config or mgazine.config)
        self.mz = mgazine

        if len(self.mz.list_pipeline_version()) > 1:
            logger.warning(
                "Multiple pipeline versions detected -- MGazine methods may not work as expected."
            )

        if len(self.mz.list_short_descriptions()) > 1:
            logger.warning(
                f"Multiple descriptions detected & `short_desc` not specified -- MGazine methods may not work as expected.\n'{self.mz.list_short_descriptions()[0]}' used for `long_short_mapping` determination and caching."
            )
        self.short_desc = self.mz.list_short_descriptions()[0]
        logger.info(f"TaxaMGazine initialized for short description: {self.short_desc}")

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
        logger.info(
            f"{self.__class__.__name__} long to short rank mapping set: {self.long_short_mapping}"
        )
        # cache
        self.cache_handler: DiskCheckpointer = None
        self._lazy_merged: pl.LazyFrame = None
        self._runs_accessions: list = None
        self._runs_details: list = runs_details or []
        self._samples_details: list = samples_details or []
        self._studies_details: list = studies_details or []
        self._biosamples_details: list = biosamples_details or []
        self._analyses_details: list = analyses_details or []
        self._assemblies_details: list = assemblies_details or []

    def __str__(self):
        return (
            f"MGazine Curation {self.__class__.__name__} containing:\n"
            f"- MGnify pipeline versions: {self.mz.list_pipeline_version()}\n"
            f"- Number of downloads: {len(self.mz.downloads)}\n"
            f"- Short descriptions: {pformat(self.mz.list_short_descriptions())}\n"
        )

    def _init_cache_handler_state(self):
        # getting merged lazyframe for runs acessions
        self._lazy_merger()

        self.cache_handler = DiskCheckpointer(
            params_getter=lambda: {
                "mgazine": str(self.mz),
                "short_desc": self.short_desc,
                "runs_accessions": self.runs_accessions,
            },
            resource_str=f"TaxaMGazine_{self.short_desc}",
            config=self.config,
        )
        self.cache_dir = self.cache_handler._cache_dir
        logger.info(
            f"Initialized DiskCheckpointer for TaxaMGazine with cache dir: {self.cache_dir}"
        )
        self.cache_handler.load_cache()
        self._runs_details = self.cache_handler._results.get(1, [])
        self._samples_details = self.cache_handler._results.get(2, [])
        self._studies_details = self.cache_handler._results.get(3, [])
        self._biosamples_details = self.cache_handler._results.get(4, [])
        self._analyses_details = self.cache_handler._results.get(5, [])
        self._assemblies_details = self.cache_handler._results.get(6, [])

    @property
    def runs_details(self) -> list[dict[str, Any]]:
        return self._runs_details

    @runs_details.setter
    def runs_details(self, value: list[dict[str, Any]]):
        self._runs_details = value
        self.cache_handler.write_results(1, self._runs_details)

    def append_runs_details(self, value: dict[str, Any]):
        self._runs_details.append(value)
        self.cache_handler.write_results(1, self._runs_details)

    @property
    def samples_details(self) -> list[dict[str, Any]]:
        return self._samples_details

    @samples_details.setter
    def samples_details(self, value: list[dict[str, Any]]):
        self._samples_details = value
        self.cache_handler.write_results(2, self._samples_details)

    def append_samples_details(self, value: dict[str, Any]):
        self._samples_details.append(value)
        self.cache_handler.write_results(2, self._samples_details)

    @property
    def studies_details(self) -> list[dict[str, Any]]:
        return self._studies_details

    @studies_details.setter
    def studies_details(self, value: list[dict[str, Any]]):
        self._studies_details = value
        self.cache_handler.write_results(3, self._studies_details)

    def append_studies_details(self, value: dict[str, Any]):
        self._studies_details.append(value)
        self.cache_handler.write_results(3, self._studies_details)

    @property
    def biosamples_details(self) -> list[dict[str, Any]]:
        return self._biosamples_details

    @biosamples_details.setter
    def biosamples_details(self, value: list[dict[str, Any]]):
        self._biosamples_details = value
        self.cache_handler.write_results(4, self._biosamples_details)

    def append_biosamples_details(self, value: dict[str, Any]):
        self._biosamples_details.append(value)
        self.cache_handler.write_results(4, self._biosamples_details)

    @property
    def analyses_details(self) -> list[dict[str, Any]]:
        return self._analyses_details

    @analyses_details.setter
    def analyses_details(self, value: list[dict[str, Any]]):
        self._analyses_details = value
        self.cache_handler.write_results(5, self._analyses_details)

    def append_analyses_details(self, value: dict[str, Any]):
        self._analyses_details.append(value)
        self.cache_handler.write_results(5, self._analyses_details)

    @property
    def assemblies_details(self) -> list[dict[str, Any]]:
        return self._assemblies_details

    @assemblies_details.setter
    def assemblies_details(self, value: list[dict[str, Any]]):
        self._assemblies_details = value
        self.cache_handler.write_results(6, self._assemblies_details)

    def append_assemblies_details(self, value: dict[str, Any]):
        self._assemblies_details.append(value)
        self.cache_handler.write_results(6, self._assemblies_details)

    @property
    def lazy_merged(self) -> pl.LazyFrame:
        if self._lazy_merged is None:
            self._lazy_merger()
        return self._lazy_merged

    def _lazy_merger(self):

        lazyframes = [
            self.mz.stream(url=u, chunksize=1000, dataframe_engine="polars")
            for u in self.mz.url_list
        ]

        self._lazy_merged = pl.concat(lazyframes, how="vertical_relaxed")

    def to_pandas(self, **pd_kwargs) -> pd.DataFrame:
        if self.cache_handler is None and self._lazy_merged is None:
            logger.warning(
                "Cache handler not initialized and lazy merged DataFrame not available. Returning empty DataFrame."
            )
            return pd.DataFrame()
        return self.lazy_merged.collect().to_pandas(**pd_kwargs)

    def to_polars(self) -> pl.DataFrame:
        if self.cache_handler is None and self._lazy_merged is None:
            logger.warning(
                "Cache handler not initialized and lazy merged DataFrame not available. Returning empty DataFrame."
            )
            return pl.DataFrame()
        return self.lazy_merged.collect()

    @property
    def runs_accessions(self) -> list:
        if self._runs_accessions is not None:
            return self._runs_accessions

        self._runs_accessions = (
            self.lazy_merged.select("RunID").collect().to_series().to_list()
        )
        return self._runs_accessions

    def _iter_runs(self) -> list[str]:
        run_results_accessions = [mg.get("accession") for mg in self.runs_details]
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
            The function does not return anything. It updates the `run_results` attribute of the TaxaMGazine instance with the enriched run metadata.

        """

        logger.debug(
            f"Starting enrichment of runs for short description {self.short_desc} with limit {limit}."
        )

        runs_todo: list[str] = self._iter_runs()[:limit]

        for count, run in enumerate(
            tqdm_sync(
                runs_todo,
                total=len(self.runs_accessions),
                initial=len(self.runs_details),
                desc="Enriching runs",
                disable=hide_progress,
            )
        ):
            logger.info(
                f"Enriching run {run} for short description {self.short_desc}. Count: {count}"
            )
            # get metadata
            if "ERZ" in run:
                logger.debug(
                    f"Run {run} appears to be an assembly. Using AssemblyDetail proxy for enrichment."
                )

                proxy = AssemblyDetail
            else:
                proxy = RunDetail

            try:
                mg = proxy(accession=run, config=self.config).get()
            except Exception as e:
                logger.error(f"Error occurred while enriching run {run}: {e}")
                mg = {"accession": run}

            self.append_runs_details(mg)

    async def aenrich_runs(
        self, limit: Optional[int] = 200, hide_progress: bool = False
    ):
        """
        Asynchronously enriches the run metadata for the runs in the taxonomic dataset by iterating through the run accessions and retrieving their details using the RunDetail proxy. The results are cached using the DiskCheckpointer to avoid redundant API calls in future runs.

        Parameters
        ----------
        limit : Optional[int], default=200
            An optional integer to limit the number of runs to enrich. If not provided, it defaults to 200. This is useful for testing or when dealing with large datasets to avoid long runtimes during development. If set to None, there will be no limit on the number of runs enriched.

        hide_progress : bool, default=False
            Whether to hide the progress bar during enrichment. Defaults to False.

        Returns
        -------
        None
            The function does not return anything. It updates the `run_results` attribute of the TaxaMGazine instance with the enriched run metadata.

        """
        logger.debug(
            f"Starting asynchronous enrichment of runs for short description {self.short_desc} with limit {limit}."
        )

        runs_todo: list[str] = self._iter_runs()[:limit]

        logger.warning(
            f"Enriching {len(runs_todo)} runs for short description {self.short_desc}. Total runs: {len(self.runs_accessions)}. Already enriched: {len(self.runs_details)}. Starting run: {runs_todo[0]}, Ending run: {runs_todo[-1]}."
        )

        # helper that offloads synchronous proxy construction to a thread
        async def _fetch(run: str) -> dict[str, Any]:
            proxy_ctor = AssemblyDetail if "ERZ" in run else RunDetail
            try:
                # Construct proxy in a thread (avoids blocking event loop)
                proxy = await asyncio.to_thread(
                    lambda: proxy_ctor(accession=run, config=self.config)
                )
                # Now call its async getter
                mg = await proxy.aget()
            except Exception as e:
                logger.error(f"Error occurred while enriching run {run}: {e}")
                mg = {"accession": run, "error": str(e)}
            return mg

        # schedule tasks (cheap now because construction is deferred into _fetch)
        tasks = [asyncio.create_task(_fetch(run)) for run in runs_todo]

        # progress over completions using the actual number of tasks
        for done in tqdm_asyncio.as_completed(
            tasks,
            total=len(self.runs_accessions),
            initial=len(self.runs_details),
            desc="Enriching runs",
            disable=hide_progress,
        ):
            mg = await done
            # append the result (getter already guarantees an accession key)
            self.append_runs_details(mg)

        # sanity: detect any runs still missing and append placeholders
        enriched_accessions = {
            r.get("accession") for r in self.runs_details if isinstance(r, dict)
        }
        failed = [r for r in runs_todo if r not in enriched_accessions]
        for run in failed:
            logger.error(f"Run {run} failed to enrich in asynchronous enrichment.")
            self.append_runs_details({"accession": run})

    def enrich_samples(self):
        pass

    def enrich_studies(self):
        pass

    @property
    def runs_to_samples(self) -> dict[str, str]:
        return {
            mg.get("accession"): mg.get("sample", {}).get("accession")
            for mg in self.runs_details
            if isinstance(mg, dict)
        }

    @property
    def _retrieved_biosamples_sample_ids(self) -> list[str]:
        return [
            x.get("SampleID") for x in self.biosamples_details if isinstance(x, dict)
        ]

    @property
    def _retrieved_biosamples_runs_ids(self) -> list[str]:
        return [x.get("RunID") for x in self.biosamples_details if isinstance(x, dict)]

    def _iter_biosamples(self) -> list[str]:
        leftovers = [
            x
            for x in self.runs_accessions
            if x not in self._retrieved_biosamples_runs_ids
        ]
        return leftovers

    def enrich_biosamples(
        self,
        limit: Optional[int] = 200,
        hide_progress: bool = False,
        incl_ena: bool = True,
    ):
        """
        Enriches the biosample metadata for the biosamples in the taxonomic dataset by iterating through the biosample accessions and retrieving their details using the BiosampleDetail proxy. The results are cached using the DiskCheckpointer to avoid redundant API calls in future runs.

        Parameters
        ----------
        limit : Optional[int], default=200
            An optional integer to limit the number of biosamples to enrich. If not provided, it defaults to 200. This is useful for testing or when dealing with large datasets to avoid long runtimes during development. If set to None, there will be no limit on the number of biosamples enriched.

        Returns
        -------
        None
            The function does not return anything. It updates the `run_results` attribute of the TaxaMGazine instance with the enriched run metadata.

        """

        logger.debug(
            f"Starting enrichment of biosample meta for short description {self.short_desc} with limit {limit}."
        )

        runs_todo: list[str] = self._iter_biosamples()[:limit]

        for count, run in enumerate(
            tqdm_sync(
                runs_todo,
                total=len(self.runs_accessions),
                initial=len(self.biosamples_details),
                desc="Enriching biosamples",
                disable=hide_progress,
            )
        ):
            logger.info(
                f"Enriching biosample {run} for short description {self.short_desc}. Count: {count}"
            )
            # get metadata
            try:
                bm = get_biosample_metadata(run, incl_ena=incl_ena)
                self.append_biosamples_details(bm.iloc[0].to_dict())
            except Exception as e:
                logger.error(f"Error occurred while enriching run {run}: {e}")
                self.append_biosamples_details({"RunID": run})

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

    def metadata(
        self,
        df_engine: Literal["polars", "pandas"] = "pandas",
        strict: bool = False,
        expand_nested_dicts: bool = True,
        incl_runs_details: bool = True,
        incl_samples_details: bool = True,
        incl_studies_details: bool = True,
        incl_biosamples_details: bool = True,
        incl_analyses_details: bool = True,
        incl_assemblies_details: bool = True,
    ) -> pl.DataFrame | pd.DataFrame:

        if not self.runs_details:
            logger.warning(
                "No runs have been enriched yet. Returning empty metadata DataFrame. Please run `enrich_runs()` first to populate the metadata."
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

        results_helper = ResultsHandler(
            data=self.runs_details,
        )

        if strict and len(self.runs_details) < len(self.runs_accessions):
            logger.warning(
                f"Strict mode is on but only {len(self.runs_details)} runs have been enriched out of {len(self.runs_accessions)} total runs. Returning without enrichment."
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
            return results_helper.to_pandas(
                expand_nested_dicts=expand_nested_dicts
            ).set_index("accession")
        elif df_engine == "polars":
            return results_helper.to_polars(
                expand_nested_dicts=expand_nested_dicts,
            )  # .with_row_index("accession")

    def clear_cache(self):
        from mgnipy.mgnipy import MGnipy

        MG = MGnipy(config=self.config)
        MG.clear_subcaches()
        logger.info("MGnipy cache cleared via TaxaMGazine helper.")
        self._lazy_merged = None
        self._runs_accessions = None


class DWCTaxaMGazine(_MGazineSetup):

    def __init__(
        self,
        mgazine: "MGazine",
        config: Optional[MGnipyConfig] = None,
        *,
        long_short_mapping: Optional[dict[str, str]] = None,
        assemblies_details: Optional[list[dict[str, Any]]] = None,
        runs_details: Optional[list[dict[str, Any]]] = None,
        samples_details: Optional[list[dict[str, Any]]] = None,
        studies_details: Optional[list[dict[str, Any]]] = None,
        biosamples_details: Optional[list[dict[str, Any]]] = None,
        analyses_details: Optional[list[dict[str, Any]]] = None,
    ):

        super().__init__(
            mgazine=mgazine,
            config=config,
            long_short_mapping=long_short_mapping,
            runs_details=runs_details,
            samples_details=samples_details,
            studies_details=studies_details,
            biosamples_details=biosamples_details,
            analyses_details=analyses_details,
            assemblies_details=assemblies_details,
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
            f"{self.__class__.__name__} loaded with {len(self.url_list)} datasets. \nCached runs results: {len(self.runs_details)} of total {len(self.runs_accessions)}."
        )


class TaxaMGazine(_MGazineSetup):
    """not for dwc"""

    def __init__(
        self,
        mgazine: "MGazine",
        config: Optional[MGnipyConfig] = None,
        *,
        long_short_mapping: Optional[dict[str, str]] = None,
        assemblies_details: Optional[list[dict[str, Any]]] = None,
        runs_details: Optional[list[dict[str, Any]]] = None,
        samples_details: Optional[list[dict[str, Any]]] = None,
        studies_details: Optional[list[dict[str, Any]]] = None,
        biosamples_details: Optional[list[dict[str, Any]]] = None,
        analyses_details: Optional[list[dict[str, Any]]] = None,
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
            runs_details=runs_details,
            samples_details=samples_details,
            studies_details=studies_details,
            biosamples_details=biosamples_details,
            analyses_details=analyses_details,
            assemblies_details=assemblies_details,
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
            f"{self.__class__.__name__} loaded with {len(self.url_list)} datasets. \nCached runs results: {len(self.runs_details)} of total {len(self.runs_accessions)}."
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
                self.X(),
                obs=self.taxonomic_metadata(),
                var=self.metadata(),
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
