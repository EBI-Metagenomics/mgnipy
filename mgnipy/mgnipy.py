from mgnipy._models.config import MgnipyConfig
from mgnipy._models.CONSTANTS import SupportedEndpoints
from mgnipy.V2.metadata import Mgnifier


class MGnipy:

    def __init__(self, **config):
        self._config = MgnipyConfig(**config)
        self._endpoints = self.list_resources()

    def __getattr__(self, name: str):
        if name in self._endpoints:
            return Mgnifier(resource=name)
        else:
            return self.__dict__[f"_{name}"]

    def list_resources(self):
        return [endpoint.value for endpoint in SupportedEndpoints]
