from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
)
from mgnipy.V2.mixins import BioSamplesMetadataMixin
from mgnipy.V2.proxies import MGnifyDetail, MGnifyList


class Assemblies(MGnifyList, BioSamplesMetadataMixin):
    RESOURCE: ClassVar[Literal["assemblies"]] = "assemblies"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):
        self._init_biosamples_cache()
        super().__init__(params=params, config=config, **kwargs)


class AssemblyDetail(MGnifyDetail, BioSamplesMetadataMixin):
    RESOURCE: ClassVar[Literal["assembly"]] = "assembly"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        accession: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):
        self._init_biosamples_cache()
        super().__init__(
            id=id or accession,
            config=config,
            **kwargs,
        )
