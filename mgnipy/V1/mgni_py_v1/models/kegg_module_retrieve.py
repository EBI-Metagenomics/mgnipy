from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="KeggModuleRetrieve")


@_attrs_define
class KeggModuleRetrieve:
    """Serializer for DynamicDocuments.

    Maps all undefined fields to :class:`fields.DynamicField`.

        Attributes:
            accession (str):
            url (str):
            completeness (float):
            matching_kos (list[Any]):
            missing_kos (list[Any]):
            description (str):
            name (str):
    """

    accession: str
    url: str
    completeness: float
    matching_kos: list[Any]
    missing_kos: list[Any]
    description: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accession = self.accession

        url = self.url

        completeness = self.completeness

        matching_kos = self.matching_kos

        missing_kos = self.missing_kos

        description = self.description

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accession": accession,
                "url": url,
                "completeness": completeness,
                "matching_kos": matching_kos,
                "missing_kos": missing_kos,
                "description": description,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        accession = d.pop("accession")

        url = d.pop("url")

        completeness = d.pop("completeness")

        matching_kos = cast(list[Any], d.pop("matching_kos"))

        missing_kos = cast(list[Any], d.pop("missing_kos"))

        description = d.pop("description")

        name = d.pop("name")

        kegg_module_retrieve = cls(
            accession=accession,
            url=url,
            completeness=completeness,
            matching_kos=matching_kos,
            missing_kos=missing_kos,
            description=description,
            name=name,
        )

        kegg_module_retrieve.additional_properties = d
        return kegg_module_retrieve

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
