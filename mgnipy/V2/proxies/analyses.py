from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
)

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
