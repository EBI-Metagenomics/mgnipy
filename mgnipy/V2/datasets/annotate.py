import logging

logger = logging.getLogger(__name__)

import pandas as pd
import polars as pl
from typing import Any, Literal, Optional

from mgnipy.V2.mgnifier.endpoints import ID_PARAM
from mgnipy._models.constants.CONSTANTS import SupportedEndpoints
from mgnipy.V2.mgnifier.metadata import MGnifyMetadata, ResultsHandler


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
        return ResultsHandler(self._biosamples_metadata or [])

    @biosamples_metadata.setter
    def biosamples_metadata(self, value: list[dict[str, Any]]):
        self._set_cached_list("biosamples_metadata", value)

    def append_biosamples_metadata(self, value: dict[str, Any]):
        self._append_cached_item("biosamples_metadata", value)

    def metadata(
        self,
        df_engine: Literal["polars", "pandas"] = "pandas",
        expand_nested_dicts: bool = True,
        how="left",
        coalesce: bool = True,
        for_runs: Optional[list[str]] = None,
    ) -> pl.DataFrame | pd.DataFrame:

        _runs = for_runs or getattr(self, "runs_accessions", None)
        if _runs is None:
            logger.warning("No runs accessions provided. Returning empty dataframe.")
            return pl.DataFrame() if df_engine == "polars" else pd.DataFrame()

        # getting run accessions as sorted_index
        sorted_index = sorted(self.X(df_engine="polars").columns)

        base = pl.DataFrame(sorted_index, schema=["mgnify_run_accession_index"])

        if len(self.available_metadata_sets) == 0:
            logger.warning(
                "No non-empty metadata sets available. Returning empty dataframe."
            )

            if df_engine == "polars":
                logger.warning("Polars dataframe does not support empty df with index.")
                return base

            if df_engine == "pandas":
                return pd.DataFrame(index=sorted_index)

        # for runs
        if (
            "mgnify_runs" not in self.available_metadata_sets
            and "biosamples_metadata" not in self.available_metadata_sets
        ):
            logger.warning(
                "runs metadata set is not available. Returning empty dataframe."
            )
            return (
                pl.DataFrame(sorted_index)
                if df_engine == "polars"
                else pd.DataFrame(index=sorted_index)
            )

        elif (
            "mgnify_runs" in self.available_metadata_sets
            and "biosamples_metadata" not in self.available_metadata_sets
        ):
            pl_runs = self.mgnify_runs.to_polars(
                expand_nested_dicts=expand_nested_dicts
            )

            base = base.join(
                pl_runs,
                how=how,
                coalesce=coalesce,
                left_on="mgnify_run_accession_index",
                right_on=ID_PARAM[SupportedEndpoints.RUNS],
            )
        elif (
            "biosamples_metadata" in self.available_metadata_sets
            and "mgnify_runs" not in self.available_metadata_sets
        ):
            pl_biosamples = self.biosamples_metadata.to_polars(
                expand_nested_dicts=expand_nested_dicts
            )

            base = base.join(
                pl_biosamples,
                how=how,
                coalesce=coalesce,
                left_on="mgnify_run_accession_index",
                right_on="RunID",
            )
        elif (
            "biosamples_metadata" in self.available_metadata_sets
            and "mgnify_runs" in self.available_metadata_sets
        ):
            pl_biosamples = self.biosamples_metadata.to_polars(
                expand_nested_dicts=expand_nested_dicts
            )
            pl_runs = self.mgnify_runs.to_polars(
                expand_nested_dicts=expand_nested_dicts
            )

            base = base.join(
                pl_runs,
                how=how,
                coalesce=coalesce,
                left_on="mgnify_run_accession_index",
                right_on=ID_PARAM[SupportedEndpoints.RUNS],
            )

            base = base.join(
                pl_biosamples,
                how=how,
                coalesce=coalesce,
                left_on="mgnify_run_accession_index",
                right_on="RunID",
            )

        # now to the samples
        if (
            "mgnify_samples" in self.available_metadata_sets
            and "mgnify_runs" in self.available_metadata_sets
        ):

            right = self.mgnify_samples.to_polars(
                expand_nested_dicts=expand_nested_dicts
            )

            base = base.join(
                right,
                how=how,
                coalesce=coalesce,
                left_on="sample_accession",
                right_on=ID_PARAM[SupportedEndpoints.SAMPLES],
            )
            return (
                base
                if df_engine == "polars"
                else base.to_pandas().set_index("mgnify_run_accession_index")
            )

        if (
            "mgnify_samples" in self.available_metadata_sets
            and "biosamples_metadata" in self.available_metadata_sets
        ):

            right = self.biosamples_metadata.to_polars(
                expand_nested_dicts=expand_nested_dicts
            )

            base = base.join(
                right,
                how=how,
                coalesce=coalesce,
                left_on="sample_accession",
                right_on="SampleID",
            )
            return (
                base
                if df_engine == "polars"
                else base.to_pandas().set_index("mgnify_run_accession_index")
            )

        return (
            base
            if df_engine == "polars"
            else base.to_pandas().set_index("mgnify_run_accession_index")
        )
