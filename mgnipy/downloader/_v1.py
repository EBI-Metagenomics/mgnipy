import asyncio
from copy import deepcopy
from pathlib import Path
from typing import (
    Any,
    Optional,
)
import pandas as pd
from mgni_py_v1.api.samples import samples_list
from mgnipy.metadata import Mgnifier
from mgnipy._internal_functions import get_semaphore

semaphore = get_semaphore()

class Samplifier(Mgnifier):
    """
    The Mgnipy SampleFinder class is a user-friendly interface for exploring sample metadata from the MGnify API.

    """

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        checkpoint_dir: Optional[Path] = None,
        checkpoint_freq: Optional[int] = None,
        presearch: Optional[Mgnifier] = None,
        **kwargs,
    ):
        super().__init__(
            db="samples",
            params=params,
            checkpoint_dir=checkpoint_dir,
            checkpoint_freq=checkpoint_freq,
            **kwargs,
        )
        # overwrite, with this can search by biome, experiment, study etc
        self.mpy_module = samples_list

        self._presearch = presearch
        self._presearch_accessions: Optional[dict[str, str]] = None
        self._repeat_params: bool = False
        if isinstance(self._presearch, Mgnifier):
            if self._presearch.total_pages is None:
                raise AssertionError(
                    "the presearch Mgnifier must be planned or previewed first" 
                    "(Mgnifier.plan() or .preview()))"
                )
            
            elif self._presearch.db not in ["biomes", "studies"]:
                raise ValueError(
                    "the presearch Mgnifier must be of db type 'biomes' or 'studies'"
                )
            
            elif self._presearch.total_pages == 0:
                print("presearch Mgnifier has no results. Ignoring.")
                self._presearch = None
            
            elif len(self._presearch.results) == self._presearch.total_pages:
            # have all accessions in results already 
                # get presearch results as df and extract accessions
                presearch_results = pd.concat(self._presearch.results)
                acc_list = list(presearch_results['accession'])
                # determining if study or other accessions
                acc_key = "study_accession" if (
                    presearch_results['type'].unique()[0]=='studies'
                ) else "accession"
                # save as potential kwarg
                self._presearch_accessions = {acc_key: acc_list}

                # NOTE: a limitation of api is that only takes last study_accession, need other workaround
                if len(acc_list) == 1:
                    self._params.update(self._presearch_accessions)
                elif acc_key == "accession":
                    self._params.update(self._presearch_accessions)
                elif acc_key == "study_accession":
                    self._repeat_params = True
            else: 
                # ? TODO for each planned page of presearch will get samples
                # TEMPORARY: 
                print("presearch Mgnifier has incomplete results. Ignoring.")
                self._presearch = None
        elif self._presearch is not None:
            raise TypeError("presearch must be a Mgnifier instance or None")
        
        if "study_accession" in self._params:
            # add to presearch accessions..
            self._presearch_accessions = self._presearch_accessions or {}
            self._presearch_accessions.setdefault(
                "study_accession", []
            ).extend(self._params["study_accession"])
            # dedupe
            self._presearch_accessions["study_accession"] = list(
                set(self._presearch_accessions["study_accession"])
            )
            # flag on
            self._repeat_params = True
            # rm from params
            self._params.pop("study_accession", None)


    # overwrite 
    def __str__(self):
        base = super().__str__()
        study_acc = f"Repeating params: study_accession: {self._presearch_accessions.get('study_accession', None)}"
        return f"{base}\n{study_acc}"


    def plan(self):
        if self._repeat_params:
            print("Multiplanner with presearch conditions...")

            # treat as dict instead of int or list instead .. is this ok
            self._total_pages = {}
            self._count = {}
            self._cached_first_page = {}

            for acc in self._presearch_accessions['study_accession']:
                print(f"Planning for study_accession: {acc}...")
                # update params for this accession
                temp_params = self._temp_param_updater(acc)
                print("Planning the API call with params:")
                print(temp_params)
                print(
                    f"Acquiring meta for {temp_params.get('page_size', 25)} {self._db} per page..."
                )
                print(f"Request URL: {self._build_url(params=temp_params)}")
                # make get request using mgni_py client
                resp_dict = self._get_request(temp_params)
                if resp_dict is None:
                    raise RuntimeError("Failed to get response from MGnify API.")
                # set
                self._total_pages[acc] = resp_dict["meta"]["pagination"]["pages"]
                self._count[acc] = resp_dict["meta"]["pagination"]["count"]
                self._cached_first_page[acc] = [resp_dict["data"]]

                print(f"Total pages to retrieve: {self._total_pages[acc]}")
                print(f"Total records to retrieve: {self._count[acc]}\n")
        else:
            super().plan()


    def preview(self, study_accession: Optional[str] = None):
        """
        Previews the metadata of the first page of results as a DataFrame.
        """
        if self._repeat_params:
            if self._cached_first_page is None:
                print("Plan not yet checked. Running now...")
                self.plan()

            if study_accession is None: 
                return {
                    acc: self.response_df(
                        self._cached_first_page[acc]
                    ) for acc in self._cached_first_page
                }
            else: 
                return self.response_df(self._cached_first_page.get(study_accession, []))
        else: 
            return super().preview()


    def _temp_param_updater(self, study_accession: str):
        temp_params = deepcopy(self._params)
        temp_params['study_accession'] = study_accession
        return temp_params


    async def collect(
        self, 
        *,
        pages: Optional[list[int]] = None,
        study_accession: Optional[str] = None
    ):
        if self._repeat_params:
            # require planning before 
            if self._total_pages is None:
                raise AssertionError(
                    "Please run Mgnifier.plan or .preview before"
                    "deciding to collect"
                )
            
            async def collect_one(acc) -> tuple[str, pd.DataFrame]:
                #print(f"Collecting for study_accession: {acc}...")
                temp_params = self._temp_param_updater(acc)
                #print(self._build_url(params=temp_params))
                async with self._init_client() as client:
                    return acc, await self._collector(
                        client, 
                        pages=pages, 
                        params=temp_params,
                        cached_pages=self._cached_first_page.get(acc, None),
                        total_pages=self._total_pages.get(acc, None)
                    )

            # ignore pages if repeating params ..
            if pages is not None: 
                print(
                    "Custom page collection not supported "
                    "with repeating parameter: `study_accession` "
                    "Ignoring pages argument."
                )

            if isinstance(study_accession, str) and study_accession not in self._total_pages:
                raise ValueError(f"Study accession {study_accession} not found: {self._total_pages}")
            
            elif isinstance(study_accession, str) and study_accession in self._total_pages:
                self._results = await collect_one(study_accession)
                return pd.concat(self._results[1])

            elif study_accession is None: 
                print(
                    "No study_accession specified, " 
                    "collecting pages for all accessions:",
                    list(self._total_pages)
                )
                tasks = [collect_one(acc) for acc in self._total_pages]
                self._results = await asyncio.gather(*tasks)
                return {acc: pd.concat(df) for acc, df in self._results}
            else: 
                raise TypeError("study_accession must be a string or None")
        else: 
            return await super().collect(pages=pages)
    
