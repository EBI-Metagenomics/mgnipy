from __future__ import annotations

from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
)

from mgnipy.V2.mixins import BiomesTreeMixin
from mgnipy.V2.proxies import MGnifyDetail, MGnifyList


class Biomes(BiomesTreeMixin, MGnifyList):
    RESOURCE: ClassVar[Literal["biomes"]] = "biomes"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(params=params, config=config, **kwargs)

    # @property
    # def metadata(self) -> MGnifyMetadata:
    #     return MGnifyMetadata(results=self._results, id_label="lineage")


class BiomeDetail(BiomesTreeMixin, MGnifyDetail):
    RESOURCE: ClassVar[Literal["biome"]] = "biome"

    def __init__(
        self,
        id: Optional[str] = None,
        *,
        biome_lineage: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):

        super().__init__(
            id=id or biome_lineage,
            config=config,
            **kwargs,
        )
