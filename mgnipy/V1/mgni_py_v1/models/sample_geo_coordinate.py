from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SampleGeoCoordinate")


@_attrs_define
class SampleGeoCoordinate:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            id (str):
            pk (str):
            longitude (float):
            latitude (float):
            samples_count (int):
    """

    id: str
    pk: str
    longitude: float
    latitude: float
    samples_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        pk = self.pk

        longitude = self.longitude

        latitude = self.latitude

        samples_count = self.samples_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "pk": pk,
                "longitude": longitude,
                "latitude": latitude,
                "samples_count": samples_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        pk = d.pop("pk")

        longitude = d.pop("longitude")

        latitude = d.pop("latitude")

        samples_count = d.pop("samples_count")

        sample_geo_coordinate = cls(
            id=id,
            pk=pk,
            longitude=longitude,
            latitude=latitude,
            samples_count=samples_count,
        )

        sample_geo_coordinate.additional_properties = d
        return sample_geo_coordinate

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
