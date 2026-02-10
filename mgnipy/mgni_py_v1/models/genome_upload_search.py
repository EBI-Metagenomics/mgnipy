from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..models.mag_catalogue_enum import MagCatalogueEnum

T = TypeVar("T", bound="GenomeUploadSearch")


@_attrs_define
class GenomeUploadSearch:
    """
    Attributes:
        file_uploaded (str):
        mag_catalogue (MagCatalogueEnum): * `human-gut-v2-0-2` - Unified Human Gastrointestinal Genome (UHGG) v2.0.2
            * `cow-rumen-v1-0-1` - Cow Rumen v1.0.1
            * `human-oral-v1-0-1` - Human Oral v1.0.1
            * `zebrafish-fecal-v1-0` - Zebrafish Fecal v1.0
            * `pig-gut-v1-0` - Pig Gut v1.0
            * `chicken-gut-v1-0-1` - Chicken Gut v1.0.1
            * `non-model-fish-gut-v2-0` - Non-model Fish Gut v2.0
            * `honeybee-gut-v1-0-1` - Honeybee gut v1.0.1
            * `human-vaginal-v1-0` - Human Vaginal v1.0
            * `mouse-gut-v1-0` - Mouse Gut v1.0
            * `marine-v2-0` - Marine v2.0
            * `sheep-rumen-v1-0` - Sheep rumen v1.0
            * `marine-eukaryotes-vbeta` - Marine Eukaryotes vbeta
            * `soil-v1-0` - Soil v1.0
            * `human-skin-v1-0` - Human Skin v1.0
            * `maize-rhizosphere-v1-0` - Maize Rhizosphere v1.0
            * `tomato-rhizosphere-v1-0` - Tomato Rhizosphere v1.0
            * `marine-sediment-v1-0` - Marine Sediment v1.0
            * `barley-rhizosphere-v2-0` - Barley Rhizosphere v2.0
    """

    file_uploaded: str
    mag_catalogue: MagCatalogueEnum
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_uploaded = self.file_uploaded

        mag_catalogue = self.mag_catalogue.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file_uploaded": file_uploaded,
                "mag_catalogue": mag_catalogue,
            }
        )

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("file_uploaded", (None, str(self.file_uploaded).encode(), "text/plain")))

        files.append(("mag_catalogue", (None, str(self.mag_catalogue.value).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file_uploaded = d.pop("file_uploaded")

        mag_catalogue = MagCatalogueEnum(d.pop("mag_catalogue"))

        genome_upload_search = cls(
            file_uploaded=file_uploaded,
            mag_catalogue=mag_catalogue,
        )

        genome_upload_search.additional_properties = d
        return genome_upload_search

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
