from __future__ import annotations

from importlib import metadata
import logging

from mgnipy._models.config import MGnipyConfig as MGnipyConfig
from mgnipy.mgnipy import MGnipy as MGnipy
from mgnipy.V2.collect.biosampler import BioSampler as BioSampler
from mgnipy.V2.collect.mgnetizer import MGnetizer as MGnetizer
from mgnipy.V2.datasets import (
    MTG as MTG,
    MGazine as MGazine,
)
from mgnipy.V2.mgnifier import MGnifier as MGnifier

# Do not configure logging handlers in libraries. Add a NullHandler so
# applications can configure logging as they wish without "No handler" warnings.
logging.getLogger("mgnipy").addHandler(logging.NullHandler())

__version__ = metadata.version("mgnipy")

__all__ = [
    "MGnipy",
    "MGnipyConfig",
    "MGnifier",
    "MGazine",
    "MTG",
    "MGnetizer",
    "BioSampler",
]
