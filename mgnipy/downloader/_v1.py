import asyncio
from pathlib import Path
from typing import (
    Any,
    Optional,
)
import pandas as pd
from mgni_py_v1 import Client
from mgni_py_v1.api.samples import samples_list

from mgnipy.metadata import Mgnifier
from urllib.parse import urlencode


class SampleFinder(Mgnifier):
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
            
            elif self._presearch._page_checkpoint == self._presearch.total_pages:
            # have all accessions in results already 
                presearch_results = pd.concat(self._presearch.results)

                acc_key = "study_accession" if (
                    presearch_results['type'].unique()[0]=='studies'
                ) else "accession"
                self._presearch_accessions = {acc_key: list(presearch_results['accession'])}
                # NOTE: a limitation of api is that only takes last study_accession, need workaround 
                #self._params.update(self._presearch_accessions)
            else: 
                self._params.update(self._presearch.params)
                # TODO for each planned page of presearch will get samples

        elif self._presearch is not None:
            raise TypeError("presearch must be a Mgnifier instance or None")
        
    def _collect_study(self):
        pass

    @property
    def sample_accessions(self) -> Optional[list[str]]:
        """
        Get the list of sample accessions from the results.

        Returns:
            Optional[list[str]]: List of sample accessions if results are available, otherwise None.
        """
        if self.results is None:
            return None

        accessions = []
        for df in self.results:
            if "accession" in df.columns:
                accessions.extend(df["accession"].tolist())
        return accessions

    # TODO
    


class AnalysesMgnifier(Mgnifier):
    """
    The Mgnipy AnalysesMgnifier class is a user-friendly interface for exploring analyses metadata from the MGnify API.

    """

    def __init__(
        self,
        *,
        analyses_params: Optional[dict[str, Any]] = None,
        checkpoint_dir: Optional[Path] = None,
        checkpoint_freq: Optional[int] = None,
        search: Optional[Mgnifier ] = None,
        **kwargs,
    ):
        super().__init__(
            db="analyses",
            params=analyses_params,
            checkpoint_dir=checkpoint_dir,
            checkpoint_freq=checkpoint_freq,
            **kwargs,
        )

        if search is None: 
            self._search = None
        elif isinstance(search, (Mgnifier)):
            self._search = search

            if self._search.results is None:
                print("search Mgnifier has no results. Ignoring.")
            else: 
                # extract analysis accessions from search results
                analysis_accessions = []
                for df in self._search.results:
                    if "analyses" in df.columns:
                        for analyses_list in df["analyses"]:
                            if isinstance(analyses_list, list):
                                analysis_accessions.extend(analyses_list)
                # update params to filter analyses by these accessions
                if "accession" in self._params:
                    print(
                        "Warning: 'accession' parameter in analyses_params will be overridden by search results."
                    )
                self._params["accession"] = ",".join(analysis_accessions)
                
        else:
            raise ValueError("search must be a Mgnifier or SampleMgnifier instance or None")
        


        if search is not None:

            if self._search.params.results is None: 
                pass

    # async def go_slim(self, accessions:Optional[list[str]]=None)-> dict:

    #     async with self._init_client() as client:
    #         self._go_slim_terms = await analyses_go_slim_list.asyncio_detailed(client, accession=acc)

    #     # return pd.DataFrame(self._go_slim_terms)