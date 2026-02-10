from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="KeggClassMatch")


@_attrs_define
class KeggClassMatch:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            class_id (str):
            name (str):
            genome_count (int):
    """

    class_id: str
    name: str
    genome_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        class_id = self.class_id

        name = self.name

        genome_count = self.genome_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "class_id": class_id,
                "name": name,
                "genome_count": genome_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        class_id = d.pop("class_id")

        name = d.pop("name")

        genome_count = d.pop("genome_count")

        kegg_class_match = cls(
            class_id=class_id,
            name=name,
            genome_count=genome_count,
        )

        kegg_class_match.additional_properties = d
        return kegg_class_match

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
