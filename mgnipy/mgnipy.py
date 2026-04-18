from mgnipy._models.config import MgnipyConfig
from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.proxies import (
    Analyses,
    Assemblies,
    Biomes,
    Genomes,
    Runs,
    Samples,
    Studies,
)

ENDPOINT_PROXIES = {
    SupportedEndpoints.BIOMES: Biomes,
    SupportedEndpoints.STUDIES: Studies,
    SupportedEndpoints.SAMPLES: Samples,
    SupportedEndpoints.RUNS: Runs,
    SupportedEndpoints.ANALYSES: Analyses,
    SupportedEndpoints.GENOMES: Genomes,
    SupportedEndpoints.ASSEMBLIES: Assemblies,
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

    def describe_resources(self):
        # TODO from the API docs
        pass
