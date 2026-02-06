from importlib import metadata

__version__ = metadata.version("mgnipy")

from .metadata._v1 import Mgnifier as Mgnifier
