from __future__ import annotations

from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
)

from mgnipy.V2.collect.biosampler import BioSampler
from mgnipy.V2.proxies import MGnifyDetail, MGnifyList


class Assemblies(MGnifyList):
    RESOURCE: ClassVar[Literal["assemblies"]] = "assemblies"

    def __init__(
        self,
        *,
        params: Optional[dict[str, Any]] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(params=params, config=config, **kwargs)

        self._biosampler = None

    @property
    def biosampler(self):
        if self._biosampler is None:
            # init it
            self._biosampler = BioSampler(
                sample_ids=self.search_results.ids, config=self.config
            )
        return self._biosampler


class AssemblyDetail(MGnifyDetail):
    RESOURCE: ClassVar[Literal["assembly"]] = "assembly"

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

        self._biosampler = None

    @property
    def biosampler(self):
        if self._biosampler is None:
            # init it
            self._biosampler = BioSampler(
                sample_id=[self.identifier], config=self.config
            )
        return self._biosampler
