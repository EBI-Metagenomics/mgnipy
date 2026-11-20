from enum import Enum


class DownloadFileIndexFileIndexType(str, Enum):
    CSI = "csi"
    FAI = "fai"
    GZI = "gzi"

    def __str__(self) -> str:
        return str(self.value)
