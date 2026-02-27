from typing import (
    Any,
    Dict,
    Literal,
    Optional,
)

from pydantic import BaseModel, HttpUrl

from mgnipy.V2.metadata import Mgnifier
from mgnipy.V2.mgni_py_v2.api.analyses import (
    analysis_get_mgnify_analysis_with_annotations_661c2d6a as get_analysis_annotations,
    analysis_get_mgnify_analysis_with_annotations_of_type_c486b404 as get_analysis_annotations_of_type,
)


# class MgnifyBiome(BaseModel):
#     biome_name: str
#     lineage: str


# class MgnifyRun(BaseModel):
#     accession: str
#     instrument_model: Optional[str]
#     instrument_platform: Optional[str]


# class MgnifySample(BaseModel):
#     accession: str
#     ena_accessions: list[str]
#     sample_title: Optional[str]
#     biome: MgnifyBiome
#     description: Optional[str]
#     updated_at: str


# class MgnifyDownloadItem(BaseModel):
#     file_type: str
#     download_type: str
#     short_description: str
#     long_description: Optional[str]
#     alias: Optional[str]
#     download_group: Optional[str]
#     file_size_bytes: Optional[Any]
#     index_files: Optional[list[Any]]
#     url: HttpUrl


# class MgnifyAnalysis(BaseModel):
#     accession: str
#     study_accession: str
#     experiment_type: str
#     run: MgnifyRun
#     sample: MgnifySample
#     assembly: Optional[str]
#     pipeline_version: Literal["V5", "V6"]
#     downloads: list[MgnifyDownloadItem]
#     # TODO finish

#     def __getattr__(self, name):
#         glass = Mgnifier(
#             resource="analyses",
#             accession=self.accession,
#             annotation_type=name,
#         )
#         # set new module
#         glass.mpy_module = get_analysis_annotations_of_type
#         return glass


class DatasetBuilder(Mgnifier):

    def __init__(
        self,
        accession: str,
    ):
        super().__init__(
            # not really needed
            resource="analyses",
            accession=accession,
        )
        self.mpy_module = get_analysis_annotations

    def __getitem__(self, name):
        if name == "annotations":
            return self
        else:
            raise KeyError(f"DatasetBuilder object has no attribute {name}")

    def export(self):
        pass
