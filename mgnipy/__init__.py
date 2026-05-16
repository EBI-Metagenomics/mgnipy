from importlib import metadata

from mgnipy.mgnipy import MGnipy as MGnipy
from mgnipy._models.config import MGnipyConfig as MGnipyConfig

__version__ = metadata.version("mgnipy")
