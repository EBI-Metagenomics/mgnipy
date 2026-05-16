import json
from pathlib import Path
from typing import Any


def atomic_write_json(filepath: Path, data: Any) -> None:
    """
    Atomically write data as JSON to a file using a temporary file.

    Parameters
    ----------
    filepath : Path
        The destination file path.
    data : Any
        The data to write as JSON.
    """
    tmp = filepath.with_suffix(filepath.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)
    tmp.replace(filepath)
