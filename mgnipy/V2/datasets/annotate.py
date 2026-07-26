import logging

logger = logging.getLogger(__name__)
from typing import (
    Any,
)

from mgnipy.V2.mgnifier.metadata import MGnifyMetadata, ResultsHandler
from mgnipy.V2.mixins import CheckpointMixin
from mgnipy._models.constants.CONSTANTS import SupportedEndpoints

_RESULT_PAGE_BY_FIELD = {
    "mgnify_runs": 1,
    "mgnify_samples": 2,
    "mgnify_studies": 3,
    "biosamples_metadata": 4,
    "mgnify_analyses": 5,
    "mgnify_assemblies": 6,
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


# class EnrichRunsMixin:

#     # PICK UP HERE
#     def metadata(
#         self,
#         df_engine: Literal["polars", "pandas"] = "pandas",
#         strict: bool = False,
#         expand_nested_dicts: bool = True,
#         incl_mgnify_runs: bool = True,
#         incl_mgnify_samples: bool = True,
#         incl_mgnify_studies: bool = True,
#         incl_biosamples_metadata: bool = True,
#         incl_mgnify_analyses: bool = True,
#         incl_mgnify_assemblies: bool = True,
#     ) -> pl.DataFrame | pd.DataFrame:

#         merge_these = {}

#         if incl_mgnify_runs and self.mgnify_runs:
#             runs_results = ResultsHandler(
#                 data=self.mgnify_runs,
#             )
#             merge_these["runs"] = runs_results
#         else:
#             logger.warning(
#                 "No runs have been enriched yet. Returning empty metadata DataFrame. Please run `enrich_runs()` first to populate the metadata."
#             )
#             if df_engine == "pandas":
#                 return pd.DataFrame(
#                     self.runs_accessions, columns=["accession"]
#                 ).set_index("accession")
#             elif df_engine == "polars":
#                 return pl.DataFrame(
#                     self.runs_accessions,
#                     columns=["accession"],
#                 )

#         if incl_mgnify_samples and self.mgnify_samples:
#             samples_results = ResultsHandler(
#                 data=self.mgnify_samples,
#             )
#             merge_these["samples"] = samples_results

#         if incl_mgnify_studies and self.mgnify_studies:
#             studies_results = ResultsHandler(
#                 data=self.mgnify_studies,
#             )
#             merge_these["studies"] = studies_results

#         if incl_biosamples_metadata and self.biosamples_metadata:
#             biosamples_results = ResultsHandler(
#                 data=self.biosamples_metadata,
#             )
#             merge_these["biosamples"] = biosamples_results

#         if incl_mgnify_analyses and self.mgnify_analyses:
#             analyses_results = ResultsHandler(
#                 data=self.mgnify_analyses,
#             )
#             merge_these["analyses"] = analyses_results

#         if incl_mgnify_assemblies and self.mgnify_assemblies:
#             assemblies_results = ResultsHandler(
#                 data=self.mgnify_assemblies,
#             )
#             merge_these["assemblies"] = assemblies_results

#         if strict and len(self.mgnify_runs) < len(self.runs_accessions):
#             logger.warning(
#                 f"Strict mode is on but only {len(self.mgnify_runs)} runs have been enriched out of {len(self.runs_accessions)} total runs. Returning without enrichment."
#             )
#             if df_engine == "pandas":
#                 return pd.DataFrame(
#                     self.runs_accessions, columns=["accession"]
#                 ).set_index("accession")
#             elif df_engine == "polars":
#                 return pl.DataFrame(
#                     self.runs_accessions,
#                     columns=["accession"],
#                 )

#         # if df_engine == "pandas":
#         #     return results_helper.to_pandas(
#         #         expand_nested_dicts=expand_nested_dicts
#         #     ).set_index("accession")
#         # elif df_engine == "polars":
#         #     return results_helper.to_polars(
#         #         expand_nested_dicts=expand_nested_dicts,
#         #     )  # .with_row_index("accession")

#     def _iter_leftovers(self, results: ResultsHandler, all_ids: list[str]) -> list[str]:
#         """
#         Identify and return the list of run accessions that have not yet been enriched.

#         Parameters
#         ----------
#         all_ids : list of str
#             The complete list of run accessions.
#         enriched_ids : list of str
#             The list of run accessions that have already been enriched.

#         Returns
#         -------
#         list of str
#             A list of run accessions that are present in `all_ids` but not in `enriched_ids`.
#         """
#         return [x for x in all_ids if x not in results.get_ids()]

#     @property
#     def runs_accessions(self) -> list:
#         try:
#             return self.lazy_merged.select("RunID").collect().to_series().to_list()
#         except Exception as e:
#             logger.error(f"Error occurred while fetching run accessions: {e}")
#             return []

#     def enrich_mgnify(
#         self,
#         resource: Literal["runs", "samples", "assemblies"],
#         limit: Optional[int] = 200,
#         hide_progress: bool = False,
#         strict: bool = True,
#     ):

#         resource_map = {
#             "runs": self.mgnify_runs,
#             "samples": self.mgnify_samples,
#             "assemblies": self.mgnify_assemblies,
#         }

#         # PICK UP HERE
#         all_ids_map = {
#             "runs": self.runs_accessions,
#             "samples": [s.get("accession") for s in self.mgnify_samples],
#             "assemblies": [a.get("accession") for a in self.mgnify_assemblies],
#         }

#         detail_proxy_map = {
#             "runs": RunDetail,
#             "assemblies": AssemblyDetail,
#             "samples": SampleDetail,
#         }

#         appender_map = {
#             "runs": self.append_mgnify_runs,
#             "assemblies": self.append_mgnify_assemblies,
#             "samples": self.append_mgnify_samples,
#         }

#         logger.debug(
#             f"Starting enrichment of {resource} for short description {self.short_desc} with limit {limit}."
#         )

#         ids_todo: list[str] = self._iter_leftovers(
#             resource_map[resource], all_ids_map[resource]
#         )[:limit]

#         logger.warning(
#             f"Enriching {len(ids_todo)} {resource} for short description {self.short_desc}. Total {resource}: {len(all_ids_map[resource])}. Already enriched: {len(resource_map[resource])}."
#         )

#         for count, the_id in enumerate(
#             tqdm_sync(
#                 ids_todo,
#                 total=len(all_ids_map[resource]),
#                 initial=len(resource_map[resource]),
#                 desc=f"Enriching {resource}",
#                 disable=hide_progress,
#             )
#         ):
#             logger.debug(
#                 f"Enriching {resource} {the_id} for short description {self.short_desc}. Count: {count}"
#             )

#             proxy = detail_proxy_map.get(resource)

#             try:
#                 mg = proxy(
#                     accession=the_id, config=self.config, client=self.client
#                 ).get()
#             except Exception:
#                 if "ERZ" in the_id:
#                     logger.debug(
#                         f"Run {the_id} appears to be an assembly. Using AssemblyDetail proxy for enrichment."
#                     )

#                     proxy = AssemblyDetail
#                 else:
#                     proxy = RunDetail
#                 try:
#                     mg = proxy(
#                         accession=the_id, config=self.config, client=self.client
#                     ).get()
#                 except Exception as e:
#                     logger.error(f"Error occurred while enriching run {the_id}: {e}")
#                     mg = None

#             if not strict and mg is None:
#                 logger.error(
#                     f"Strict mode is on and enrichment failed for run {the_id}. Appending placeholder with accession only."
#                 )
#                 mg = {ID_PARAM[resource]: the_id}
#             elif strict and mg is None:
#                 logger.error(
#                     f"Strict mode is on and enrichment failed for run {the_id}. Skipping appending to results."
#                 )

#             if mg is not None:
#                 appender_map.get(resource)(mg)

#     async def aenrich_runs(
#         self,
#         limit: Optional[int] = 200,
#         hide_progress: bool = False,
#         strict: bool = True,
#     ):
#         """
#         Asynchronously enriches the run metadata for the runs in the taxonomic dataset by iterating through the run accessions and retrieving their details using the RunDetail proxy. The results are cached using the CheckpointMixin to avoid redundant API calls in future runs.

#         Parameters
#         ----------
#         limit : Optional[int], default=200
#             An optional integer to limit the number of runs to enrich. If not provided, it defaults to 200. This is useful for testing or when dealing with large datasets to avoid long runtimes during development. If set to None, there will be no limit on the number of runs enriched.

#         hide_progress : bool, default=False
#             Whether to hide the progress bar during enrichment. Defaults to False.

#         Returns
#         -------
#         None
#             The function does not return anything. It updates the `run_results` attribute of the TaxaMGazine instance with the enriched run metadata.

#         """
#         logger.debug(
#             f"Starting asynchronous enrichment of runs for short description {self.short_desc} with limit {limit}."
#         )

#         runs_todo: list[str] = self._iter_runs()[:limit]

#         logger.warning(
#             f"Enriching {len(runs_todo)} runs for short description {self.short_desc}. Total runs: {len(self.runs_accessions)}. Already enriched: {len(self.mgnify_runs)}."
#         )

#         # helper that offloads synchronous proxy construction to a thread
#         async def _fetch(run: str) -> dict[str, Any]:
#             proxy_ctor = AssemblyDetail if "ERZ" in run else RunDetail
#             try:
#                 # Construct proxy in a thread (avoids blocking event loop)
#                 proxy = await asyncio.to_thread(
#                     lambda: proxy_ctor(accession=run, config=self.config)
#                 )
#                 # Now call its async getter
#                 mg = await proxy.aget()
#             except Exception as e:
#                 logger.error(f"Error occurred while enriching run {run}: {e}")
#                 mg = None

#             if not strict and mg is None:
#                 logger.error(
#                     f"Strict mode is on and enrichment failed for run {run}. Appending placeholder with accession only."
#                 )
#                 mg = {"accession": run}
#             elif strict and mg is None:
#                 logger.error(
#                     f"Strict mode is on and enrichment failed for run {run}. Skipping appending to results."
#                 )
#             return mg

#         # schedule tasks (cheap now because construction is deferred into _fetch)
#         tasks = [asyncio.create_task(_fetch(run)) for run in runs_todo]

#         # progress over completions using the actual number of tasks
#         for done in tqdm_asyncio.as_completed(
#             tasks,
#             total=len(self.runs_accessions),
#             initial=len(self.mgnify_runs),
#             desc="Enriching runs",
#             disable=hide_progress,
#         ):
#             mg = await done
#             if mg is not None:
#                 self.append_mgnify_runs(mg)

#                 if "ERZ" in mg.get("accession", ""):
#                     logger.debug(f"Enriching assembly {mg.get('accession')}")
#                     self.append_mgnify_assemblies(mg)


# class BioSamplesMixin:

#     @property
#     def runs_to_samples(self) -> dict[str, str]:
#         return {
#             mg.get("accession"): mg.get("sample", {}).get("accession")
#             or mg.get("sample_accession")
#             for mg in self.mgnify_runs
#             if isinstance(mg, dict)
#         }

#     @property
#     def assemblies_to_samples(self) -> dict[str, str]:
#         return {
#             mg.get("accession"): mg.get("sample_accession")
#             for mg in self.mgnify_runs
#             if isinstance(mg, dict)
#         }

#     @property
#     def assemblies_to_runs(self) -> dict[str, str]:
#         return {
#             mg.get("accession"): mg.get("run_accession")
#             for mg in self.mgnify_assemblies
#             if isinstance(mg, dict)
#         }

#     @property
#     def _retrieved_biosamples_given_ids(self) -> list[str]:
#         return [
#             x.get("GivenID") for x in self.biosamples_metadata if isinstance(x, dict)
#         ]

#     def _iter_biosamples(self) -> list[str]:

#         copied_mapping = self.runs_to_samples.copy()

#         for k, v in self.runs_to_samples.items():
#             if v in self._retrieved_biosamples_given_ids:
#                 del copied_mapping[k]

#         return list(copied_mapping.values())

#     def enrich_biosamples(
#         self,
#         limit: Optional[int] = 200,
#         hide_progress: bool = False,
#         incl_ena: bool = False,
#         strict: bool = True,
#     ):
#         """
#         Enriches the biosample metadata for the biosamples in the taxonomic dataset by iterating through the biosample accessions and retrieving their details using the BiosampleDetail proxy. The results are cached using the CheckpointMixin to avoid redundant API calls in future runs.

#         Parameters
#         ----------
#         limit : Optional[int], default=200
#             An optional integer to limit the number of biosamples to enrich. If not provided, it defaults to 200. This is useful for testing or when dealing with large datasets to avoid long runtimes during development. If set to None, there will be no limit on the number of biosamples enriched.

#         Returns
#         -------
#         None
#             The function does not return anything. It updates the `run_results` attribute of the TaxaMGazine instance with the enriched run metadata.

#         """

#         logger.debug(
#             f"Starting enrichment of biosample meta for short description with limit {limit}."
#         )

#         runs_todo: list[str] = self._iter_biosamples()[:limit]
#         logger.warning(
#             f"Enriching {len(runs_todo)} biosamples. Total samples (with runs enriched): {len(self.runs_to_samples)}. Already enriched: {len(self.biosamples_metadata)}."
#         )

#         for count, run in enumerate(
#             tqdm_sync(
#                 runs_todo,
#                 total=len(self.runs_accessions),
#                 initial=len(self.biosamples_metadata),
#                 desc="Enriching biosamples",
#                 disable=hide_progress,
#             )
#         ):
#             logger.info(f"Enriching biosample {run}. Count: {count}")
#             # get metadata
#             try:
#                 bm = get_biosample_metadata(run, incl_ena=incl_ena)
#             except Exception as e:
#                 logger.error(f"Error occurred while enriching run {run}: {e}")
#                 bm = False

#             if isinstance(bm, bool) and not strict:
#                 logger.error(
#                     f"Strict mode is on and enrichment failed for biosample {run}. Appending placeholder with GivenID only."
#                 )
#                 bm = {"GivenID": run}
#             elif isinstance(bm, bool) and strict:
#                 logger.error(
#                     f"Strict mode is on and enrichment failed for biosample {run}. Skipping appending to results."
#                 )
#             elif isinstance(bm, pd.DataFrame) and not bm.empty:
#                 self.append_biosamples_metadata(bm.iloc[0].to_dict())
#             else:
#                 logger.error(
#                     f"Enrichment for biosample {run} did not return a valid DataFrame. Skipping appending to results."
#                 )

#     def aenrich_biosamples(
#         self,
#         limit: Optional[int] = 200,
#         hide_progress: bool = False,
#         incl_ena: bool = False,
#         strict: bool = True,
#     ):
#         # TODO
#         pass
