from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from typing import Any, Literal, Optional

import pandas as pd
import polars as pl

from mgnipy._models.constants.CONSTANTS import SupportedEndpoints
from mgnipy._shared_helpers.biosamples_helper import (
    RUN_ID as BIOSAMPLES_RUN_ID,
    SAMPLE_ID as BIOSAMPLES_SAMPLE_ID,
)
from mgnipy.V2.mgnifier.endpoints import ID_PARAM
from mgnipy.V2.mgnifier.metadata import MGnifyMetadata, ResultsHandler

UNIQUE_RUN_ID_COL_NAME = "_mgnipy_runs_accs"
EXCLUDE_FROM_INDEX = [
    "taxonomy",
    UNIQUE_RUN_ID_COL_NAME,
    BIOSAMPLES_SAMPLE_ID,
    BIOSAMPLES_RUN_ID,
]


class MetadataSettersMixin:
    def _set_cached_list(self, field: str, value: list[dict[str, Any]]) -> None:
        setattr(self, f"_{field}", value)

    def _append_cached_item(self, field: str, value: dict[str, Any]) -> None:
        current = getattr(self, f"_{field}")
        current.append(value)

    @property
    def mgnify_studies(self) -> MGnifyMetadata:
        return MGnifyMetadata(self._mgnify_studies)

    @mgnify_studies.setter
    def mgnify_studies(self, value: list[dict[str, Any]]):
        self._set_cached_list("mgnify_studies", value)

    def append_mgnify_studies(self, value: dict[str, Any]):
        self._append_cached_item("mgnify_studies", value)

    @property
    def mgnify_samples(self) -> MGnifyMetadata:
        return MGnifyMetadata(self._mgnify_samples)

    @mgnify_samples.setter
    def mgnify_samples(self, value: list[dict[str, Any]]):
        self._set_cached_list("mgnify_samples", value)

    def append_mgnify_samples(self, value: dict[str, Any]):
        self._append_cached_item("mgnify_samples", value)

    @property
    def mgnify_analyses(self) -> MGnifyMetadata:
        return MGnifyMetadata(self._mgnify_analyses)

    @mgnify_analyses.setter
    def mgnify_analyses(self, value: list[dict[str, Any]]):
        self._set_cached_list("mgnify_analyses", value)

    def append_mgnify_analyses(self, value: dict[str, Any]):
        self._append_cached_item("mgnify_analyses", value)

    @property
    def mgnify_runs(self) -> MGnifyMetadata:
        return MGnifyMetadata(self._mgnify_runs)

    @mgnify_runs.setter
    def mgnify_runs(self, value: list[dict[str, Any]]):
        self._set_cached_list("mgnify_runs", value)

    def append_mgnify_runs(self, value: dict[str, Any]):
        self._append_cached_item("mgnify_runs", value)

    @property
    def mgnify_assemblies(self) -> MGnifyMetadata:
        return MGnifyMetadata(self._mgnify_assemblies)

    @mgnify_assemblies.setter
    def mgnify_assemblies(self, value: list[dict[str, Any]]):
        self._set_cached_list("mgnify_assemblies", value)

    def append_mgnify_assemblies(self, value: dict[str, Any]):
        self._append_cached_item("mgnify_assemblies", value)

    @property
    def biosamples_metadata(self) -> ResultsHandler:
        return ResultsHandler(self._biosamples_metadata or None)

    @biosamples_metadata.setter
    def biosamples_metadata(self, value: list[dict[str, Any]]):
        self._set_cached_list("biosamples_metadata", value)

    def append_biosamples_metadata(self, value: dict[str, Any]):
        self._append_cached_item("biosamples_metadata", value)

    def _merge_meta(
        self,
        df_engine: Literal["polars", "pandas"] = "pandas",
        expand_nested_dicts: bool = True,
        drop_duplicates: bool = False,
        how="left",
        coalesce: bool = True,
        for_runs: Optional[list[str]] = None,
        index_col_name: str = UNIQUE_RUN_ID_COL_NAME,
    ) -> pl.DataFrame | pd.DataFrame:

        ## getting the runs accessions to filter on
        _runs = for_runs or getattr(self, "runs_accessions", None)
        if _runs is None:
            logger.warning("No runs accessions provided. Returning empty dataframe.")
            return pl.DataFrame() if df_engine == "polars" else pd.DataFrame()
        # getting run accessions as sorted_index
        sorted_index = sorted(
            [
                x
                for x in self.to_polars().columns
                if x
                not in EXCLUDE_FROM_INDEX
                + getattr(self, "var_cols", [])
                + ([self.var_index] if getattr(self, "var_index", None) else [])
                + ([self.obs_index] if getattr(self, "obs_index", None) else [])
            ]
        )

        # creating base dataframe with index
        base = pl.DataFrame(sorted_index, schema=[index_col_name])

        ## if no meta then return empty dataframe with index
        if len(self.available_metadata_sets) == 0:
            logger.warning(
                "No non-empty metadata sets available. Returning empty dataframe."
            )

            return (
                base
                if df_engine == "polars"
                else base.to_pandas().set_index(index_col_name)
            )

        ## otherwise, need runs first
        # if only runs
        if (
            "mgnify_runs" in self.available_metadata_sets
            and "biosamples_metadata" not in self.available_metadata_sets
        ):
            pl_runs = self.mgnify_runs.to_polars(
                expand_nested_dicts=expand_nested_dicts, drop_duplicates=drop_duplicates
            )

            base = base.join(
                pl_runs,
                how=how,
                coalesce=coalesce,
                left_on=index_col_name,
                right_on=ID_PARAM[SupportedEndpoints.RUNS],
                suffix="__mgnify_runs",
            )
        # if only biosamples
        elif (
            "biosamples_metadata" in self.available_metadata_sets
            and "mgnify_runs" not in self.available_metadata_sets
        ):
            pl_biosamples = self.biosamples_metadata.to_polars(
                expand_nested_dicts=expand_nested_dicts, drop_duplicates=drop_duplicates
            )

            # make sure RunIDs isnt null (ie., incl_ena = False)
            if len(pl_biosamples.filter(pl.col(BIOSAMPLES_RUN_ID).is_not_null())) == 0:
                logger.warning(
                    ".biosamples_metadata set is available but no RunIDs found. Returning empty dataframe."
                )
                return (
                    base
                    if df_engine == "polars"
                    else base.to_pandas().set_index(index_col_name)
                )

            base = base.join(
                pl_biosamples,
                how=how,
                coalesce=coalesce,
                left_on=index_col_name,
                right_on=BIOSAMPLES_RUN_ID,
                suffix="__biosamples_metadata",
            )
        # if both runs and biosamples are available
        elif (
            "biosamples_metadata" in self.available_metadata_sets
            and "mgnify_runs" in self.available_metadata_sets
        ):
            pl_biosamples = self.biosamples_metadata.to_polars(
                expand_nested_dicts=expand_nested_dicts, drop_duplicates=drop_duplicates
            )
            pl_runs = self.mgnify_runs.to_polars(
                expand_nested_dicts=expand_nested_dicts, drop_duplicates=drop_duplicates
            )

            base = base.join(
                pl_runs,
                how=how,
                coalesce=coalesce,
                left_on=index_col_name,
                right_on=ID_PARAM[SupportedEndpoints.RUNS],
                suffix="__mgnify_runs",
            )

            base = base.join(
                pl_biosamples,
                how=how,
                coalesce=coalesce,
                left_on="sample_accession",
                right_on=BIOSAMPLES_SAMPLE_ID,
                suffix="__biosamples_metadata",
            )
        else:
            logger.warning(
                "No non-empty metadata sets available. Returning empty dataframe."
            )
            return (
                base
                if df_engine == "polars"
                else base.to_pandas().set_index(index_col_name)
            )

        ## now to the samples
        if (
            "mgnify_samples" in self.available_metadata_sets
            and "sample_accession" not in base.columns
            and BIOSAMPLES_SAMPLE_ID not in base.columns
        ):
            logger.error(
                f".mgnify_samples set is available but .mgnify_runs/.biosamples_metadata set does not provide a 'sample_accession'/'{BIOSAMPLES_SAMPLE_ID}' column for joining. Returning without .mgnify_samples metadata."
            )
        elif (
            "mgnify_samples" in self.available_metadata_sets
            and "sample_accession" in base.columns
        ):
            # getting the samples metadata as polars dataframe
            pl_samples = self.mgnify_samples.to_polars(
                expand_nested_dicts=expand_nested_dicts, drop_duplicates=drop_duplicates
            )

            base = base.join(
                pl_samples,
                how=how,
                coalesce=coalesce,
                left_on="sample_accession",
                right_on=ID_PARAM[SupportedEndpoints.SAMPLES],
                suffix="__mgnify_samples",
            )
        elif (
            "mgnify_samples" in self.available_metadata_sets
            and "sample_accession" in base.columns
        ):
            pl_samples = self.mgnify_samples.to_polars(
                expand_nested_dicts=expand_nested_dicts, drop_duplicates=drop_duplicates
            )
            base = base.join(
                pl_samples,
                how=how,
                coalesce=coalesce,
                left_on=BIOSAMPLES_SAMPLE_ID,
                right_on=ID_PARAM[SupportedEndpoints.SAMPLES],
                suffix="__biosamples_metadata",
            )

        return (
            base
            if df_engine == "polars"
            else base.to_pandas().set_index(index_col_name)
        )

    @property
    def obs(self) -> ResultsHandler:
        return ResultsHandler(self._obs or None)

    @obs.setter
    def obs(self, value: list[dict[str, Any]]):
        self._set_cached_list("obs", value)

    def append_obs(self, value: dict[str, Any]):
        self._append_cached_item("obs", value)

    def obs_metadata(
        self,
        df_engine: Literal["polars", "pandas"] = "pandas",
        expand_nested_dicts: bool = True,
        drop_duplicates: bool = False,
        how="left",
        coalesce: bool = True,
        for_runs: Optional[list[str]] = None,
        index_col_name: str = UNIQUE_RUN_ID_COL_NAME,
    ) -> pl.DataFrame | pd.DataFrame:

        if self._obs is None:
            return self._merge_meta(
                df_engine=df_engine,
                expand_nested_dicts=expand_nested_dicts,
                drop_duplicates=drop_duplicates,
                how=how,
                coalesce=coalesce,
                for_runs=for_runs,
                index_col_name=index_col_name,
            )

        if len(self.available_metadata_sets) > 0:
            logger.warning(
                "Observations metadata has already been set. Ignoring any new metadata sets provided."
            )

        return (
            pl.DataFrame(self._obs, schema=[index_col_name])
            if df_engine == "polars"
            else pd.DataFrame(self._obs).set_index(index_col_name)
        )
