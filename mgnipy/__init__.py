from importlib import metadata

__version__ = metadata.version("mgnipy")

from ._v1.MGniPy import MgnifyClient

# import when "from example import *"
__all__ = ["MgnifyClient"]

