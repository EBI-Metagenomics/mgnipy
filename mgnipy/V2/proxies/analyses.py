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
        return pd.DataFrame(self.details_downloads, **pd_kwargs)

    @property
    def datasets(self):
        """A property that returns an MGazine instance containing the downloads information for the study."""
        return MGazine(
            downloads=self.details_downloads,
            config=self.config,
            analyses_details=self.details_results,
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
            analyses_details=self._results.get(1, None),
        )
