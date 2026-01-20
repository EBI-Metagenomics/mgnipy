from pydantic import BaseModel
from pathlib import Path

class ConfigModel(BaseModel):
    cache_dir: Path
