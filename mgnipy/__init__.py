from importlib import metadata

__version__ = metadata.version("mgnipy")

from .metadata._v1 import Mgnifier

# import when "from example import *"
#__all__ = ["MgnifyClient"]

