from enum import Enum

class DownloadFileType(str, Enum):
    BIOM = "biom"
    CSV = "csv"
    FASTA = "fasta"
    GFF = "gff"
    HTML = "html"
    JSON = "json"
    OTHER = "other"
    SVG = "svg"
    TREE = "tree"
    TSV = "tsv"

    def __str__(self) -> str:
        return str(self.value)
