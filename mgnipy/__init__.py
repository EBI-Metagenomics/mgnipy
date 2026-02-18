from importlib import metadata
from platformdirs import user_cache_dir

APPNAME = "mgnipy"
APPAUTHOR = "MGnify"
CACHE_DIR = user_cache_dir(APPNAME, APPAUTHOR)
BASE_URL = "https://www.ebi.ac.uk/"

__version__ = metadata.version(APPNAME)

# TODO: at init cache the list of biomes

