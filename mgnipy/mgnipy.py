from mgnipy._models.config import MgnipyConfig
from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.metadata import (
    BiomesProxy,
    StudiesProxy,
    SamplesProxy,
    AnalysesProxy,
    GenomesProxy,
)

ENDPOINT_PROXIES = {
    SupportedEndpoints.BIOMES: BiomesProxy,
    SupportedEndpoints.STUDIES: StudiesProxy,
    SupportedEndpoints.SAMPLES: SamplesProxy,
    SupportedEndpoints.ANALYSES: AnalysesProxy,
    SupportedEndpoints.GENOMES: GenomesProxy,
}


class MGnipy:
    """ """

    def __init__(self, **config):
        self._config = MgnipyConfig(**config)
        self._endpoints = self.list_resources()

    def __getattr__(self, name: str):
        # TODO: better way to get diff objects??
        if name in self._endpoints:
            return ENDPOINT_PROXIES[SupportedEndpoints(name)]()
        else:
            return self.__dict__[f"_{name}"]

    def list_resources(self):
        return [endpoint.value for endpoint in SupportedEndpoints]
