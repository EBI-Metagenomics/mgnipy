from __future__ import annotations

from typing import Any, ClassVar, Literal, Optional

import pandas as pd

from mgnipy.V2.datasets import MGazine
from mgnipy.V2.proxies import MGnifyDetail, MGnifyList


class Analyses(MGnifyList):
    RESOURCE: ClassVar[Literal["analyses"]] = "analyses"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)

    def downloads_df(self, **pd_kwargs) -> pd.DataFrame:
        return pd.DataFrame(self.downloads, **pd_kwargs)

    @property
    def downloads(self) -> list[dict[str, Any]] | None:
        """
        Get a list of all download links from the detailed metadata.

        Returns
        -------
        list[dict[str, Any]] or None
            A list of dictionaries containing download information, or None if no details are available.
        """
        if self.mgnify_details:
            return super().downloads

        return self.search_results.downloads

    @property
    def datasets(self):
        """A property that returns an MGazine instance containing the downloads information for the study."""
        if self.mgnify_details:
            return MGazine(
                downloads=self.downloads,
                config=self.config,
                mgnify_analyses=self.mgnify_details.to_list(),
            )
        return MGazine(
            downloads=self.downloads,
            config=self.config,
            mgnify_analyses=self.search_results.to_list(),
        )


class AnalysisDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["analysis"]] = "analysis"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or accession,
            config=config,
            **kwargs,
        )

    @property
    def datasets(self):
        """Access the downloads for this analysis as a MGazine object."""

        return MGazine(
            downloads=self.downloads,
            config=self.config,
            mgnify_analyses=self._results.get(1, None),
        )
