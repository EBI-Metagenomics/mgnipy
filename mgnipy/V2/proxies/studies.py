from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
)

from mgnipy.V2.proxies import MGnifyDetail, MGnifyList


class Studies(MGnifyList):

    RESOURCE: ClassVar[Literal["studies"]] = "studies"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)

    @property
    def details_downloads(self):
        return self.details_df["downloads"]


class StudyDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["study"]] = "study"

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
    def downloads(self):
        return self.to_df().loc[0, "downloads"]


class PrivateStudies(MGnifyList):

    RESOURCE: ClassVar[Literal["private_studies"]] = "private_studies"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)

    @property
    def downloads(self):
        return self.to_df().loc[0, "downloads"]
