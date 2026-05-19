from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
)
import pandas as pd
from mgnipy.V2.proxies import MGnifyDetail, MGnifyList

from mgnipy.V2.datasets import MGazine


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

    @property
    def details_downloads_list(self) -> list[dict[str, Any]]:
        return [
            item for sublist in self.details_df["downloads"].values for item in sublist
        ]

    @property
    def details_downloads_df(self) -> pd.DataFrame:
        # return self.details_df["downloads"]

        down_dict = self.details_df["downloads"]

        okie = {x: y for x, y in down_dict.items() if len(y) > 0}
        rows = [
            dict(study_id=study, **item)
            for study, items in okie.items()
            for item in items
        ]
        return pd.DataFrame(rows)

    @property
    def datasets(self):
        """A property that returns an MGazine instance containing the downloads information for the study."""
        return MGazine(
            downloads=self.details_downloads_list,
            config=self.config,
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
            downloads=self.to_df().loc[0, "downloads"],
            config=self.config,
        )
