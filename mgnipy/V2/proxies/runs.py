from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
)

from mgnipy.V2.mixins import BioSamplesMetadataMixin
from mgnipy.V2.proxies import MGnifyDetail, MGnifyList


class Runs(MGnifyList, BioSamplesMetadataMixin):

    RESOURCE: ClassVar[Literal["runs"]] = "runs"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)


class RunDetail(MGnifyDetail, BioSamplesMetadataMixin):
    RESOURCE: ClassVar[Literal["run"]] = "run"

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
