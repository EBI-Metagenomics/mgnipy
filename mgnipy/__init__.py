from importlib import metadata

from platformdirs import user_cache_dir

from mgnipy.mgnipy import MGnipy as MGnipy

APPNAME = "mgnipy"
APPAUTHOR = "MGnify"
CACHE_DIR = user_cache_dir(APPNAME, APPAUTHOR)

__version__ = metadata.version(APPNAME)

# TODO: at init cache the list of biomes
