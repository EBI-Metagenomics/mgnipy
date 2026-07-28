import logging

logger = logging.getLogger(__name__)

import pandas as pd
import polars as pl
from typing import (
    Any,
    Literal,
)

from mgnipy.V2.mgnifier.endpoints import ID_PARAM
from mgnipy.V2.mixins import CheckpointMixin
from mgnipy._models.constants.CONSTANTS import SupportedEndpoints
from mgnipy.V2.mgnifier.metadata import MGnifyMetadata, ResultsHandler

_RESULT_PAGE_BY_FIELD = {
    "mgnify_runs": 1,
    "mgnify_samples": 2,
    "mgnify_studies": 3,
    "biosamples_metadata": 4,
    "mgnify_analyses": 5,
    "mgnify_assemblies": 6,
}

_JOIN_ON = {
    "mgnify_runs__mgnify_samples": {
        "left_on": "sample_accession",
        "right_on": ID_PARAM[SupportedEndpoints.SAMPLES],
    },
    "mgnify_runs__mgnify_studies": {
        "left_on": "study_accession",
        "right_on": ID_PARAM[SupportedEndpoints.STUDIES],
    },
    "mgnify_assemblies__mgnify_runs": {
        "left_on": "run_accession",
        "right_on": ID_PARAM[SupportedEndpoints.RUNS],
    },
    "mgnify_assemblies__mgnify_samples": {
        "left_on": "sample_accession",
        "right_on": ID_PARAM[SupportedEndpoints.SAMPLES],
    },
    "mgnify_assemblies__mgnify_studies": {
        "left_on": "assembly_study_accession",
        "right_on": ID_PARAM[SupportedEndpoints.STUDIES],
    },
    "biosamples_metadata__mgnify_runs": {
        "left_on": "GivenID",
        "right_on": "sample_accession",
    },
}


class MetadataSettersMixin:

    def _set_cached_list(self, field: str, value: list[dict[str, Any]]) -> None:
        setattr(self, f"_{field}", value)
        try:
            self.write_results(self._RESULT_PAGE_BY_FIELD[field], value)
            logger.debug(f"Results written for field '{field}'.")
        except AttributeError as e:
            logger.debug(
                f"CheckpointMixin not enabled. Cannot write results for field '{field}'. {e}"
            )

    def _append_cached_item(self, field: str, value: dict[str, Any]) -> None:
        current = getattr(self, f"_{field}")
        current.append(value)
        try:
            self.write_results(self._RESULT_PAGE_BY_FIELD[field], current)
        except AttributeError as e:
            logger.debug(
                f"CheckpointMixin not enabled. Cannot write results for field '{field}'. {e}"
            )

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
        how="full",
        coalesce: bool = True,
    ) -> pl.DataFrame | pd.DataFrame:

        # init dict
        paired_dfs: dict[str, pl.DataFrame] = {}
        # go through each pair in _JOIN_ON and perform the join
        for pair in _JOIN_ON:
            left, right = pair.split("__")
            left_data: MGnifyMetadata = getattr(self, left)
            if len(left_data) == 0:
                logger.warning(
                    f"Dataset '{left}' is empty. Skipping join for this pair."
                )
                continue
            right_data: MGnifyMetadata = getattr(self, right)
            if len(right_data) == 0:
                logger.warning(
                    f"Dataset '{right}' is empty. Skipping join for this pair."
                )
                continue

            left_df: pl.DataFrame = left_data.to_polars(
                expand_nested_dicts=expand_nested_dicts
            )
            right_df: pl.DataFrame = right_data.to_polars(
                expand_nested_dicts=expand_nested_dicts
            )
            join_params: dict[str, str] = _JOIN_ON[pair]
            merged: pl.DataFrame = left_df.join(
                right_df, how=how, coalesce=coalesce, **join_params
            )
            paired_dfs[pair] = merged

        return paired_dfs


class MetadataCheckpointMixin(CheckpointMixin):

    @property
    def resource(self) -> SupportedEndpoints:
        """for checkpointmixin"""
        return getattr(self, "_resource", None) or SupportedEndpoints(
            "_custom_endpoint"
        )

    @property
    def params(self) -> dict[str, Any]:
        if getattr(self, "_params", None) is not None:
            return self._params
        else:
            return {
                "mgazine": str(self),
                "short_desc": self.short_desc,
                "resource": self.resource.value,
            }

    def load_cache(self):
        self._results = None
        page_nums = self.load_cache_results()
        if self._results:
            for each in _RESULT_PAGE_BY_FIELD:
                setattr(
                    self, f"_{each}", self._results.get(_RESULT_PAGE_BY_FIELD[each], [])
                )
        return page_nums
