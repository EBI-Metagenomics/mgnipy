import logging
from importlib import metadata

from mgnipy._models.config import MGnipyConfig as MGnipyConfig
from mgnipy.mgnipy import MGnipy as MGnipy
from mgnipy.V2.mgnifier import MGnifier as MGnifier
from mgnipy.V2.datasets import MGazine as MGazine

# Do not configure logging handlers in libraries. Add a NullHandler so
# applications can configure logging as they wish without "No handler" warnings.
logging.getLogger("mgnipy").addHandler(logging.NullHandler())

__version__ = metadata.version("mgnipy")

__all__ = ["MGnipy", "MGnipyConfig", "MGnifier", "MGazine"]
