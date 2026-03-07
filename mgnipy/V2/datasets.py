from mgnipy.V2.metadata import Mgnifier
from mgnipy.V2.mgni_py_v2.api.analyses import (
    analysis_get_mgnify_analysis_with_annotations_661c2d6a as get_analysis_annotations,
)


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
