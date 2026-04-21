from mgnipy._models.config import MgnipyConfig
from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.proxies import (
    Analyses,
    AnalysisDetail,
    Assemblies,
    AssemblyDetail,
    BiomeDetail,
    Biomes,
    GenomeDetail,
    Genomes,
    RunDetail,
    Runs,
    SampleDetail,
    Samples,
    Studies,
    StudyDetail,
)

V2_ENDPOINT_LIST_PROXIES = {
    SupportedEndpoints.BIOMES: Biomes,
    SupportedEndpoints.STUDIES: Studies,
    SupportedEndpoints.SAMPLES: Samples,
    SupportedEndpoints.RUNS: Runs,
    SupportedEndpoints.ANALYSES: Analyses,
    SupportedEndpoints.GENOMES: Genomes,
    SupportedEndpoints.ASSEMBLIES: Assemblies,
}

V2_ENDPOINT_DETAIL_PROXIES = {
    SupportedEndpoints.BIOME: BiomeDetail,
    SupportedEndpoints.STUDY: StudyDetail,
    SupportedEndpoints.SAMPLE: SampleDetail,
    SupportedEndpoints.RUN: RunDetail,
    SupportedEndpoints.ANALYSIS: AnalysisDetail,
    SupportedEndpoints.GENOME: GenomeDetail,
    SupportedEndpoints.ASSEMBLY: AssemblyDetail,
}

V2_ENDPOINT_ALL_PROXIES = V2_ENDPOINT_LIST_PROXIES | V2_ENDPOINT_DETAIL_PROXIES


class MGnipy:
    """ """

    def __init__(self, **config):
        self._config = MgnipyConfig(**config)
        self._endpoints = self.list_resources()

    def __getattr__(self, name: str):
        _end = SupportedEndpoints.validate(name)
        return V2_ENDPOINT_ALL_PROXIES[_end]()

    def list_resources(self):
        return [endpoint.value for endpoint in SupportedEndpoints]

    def describe_resources(self):
        # TODO from the API docs
        pass
