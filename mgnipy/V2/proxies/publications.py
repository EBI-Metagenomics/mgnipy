from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
)

from mgnipy.V2.proxies import MGnifyDetail, MGnifyList


class Publications(MGnifyList):
    RESOURCE: ClassVar[Literal["publications"]] = "publications"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(params=params, config=config, **kwargs)


class PublicationDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["publication"]] = "publication"

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
