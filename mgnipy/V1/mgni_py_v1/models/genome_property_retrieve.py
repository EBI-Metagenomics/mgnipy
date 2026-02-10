from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GenomePropertyRetrieve")


@_attrs_define
class GenomePropertyRetrieve:
    """Serializer for DynamicDocuments.

    Maps all undefined fields to :class:`fields.DynamicField`.

        Attributes:
            accession (str):
            url (str):
            presence (str):
            description (str):
    """

    accession: str
    url: str
    presence: str
    description: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accession = self.accession

        url = self.url

        presence = self.presence

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accession": accession,
                "url": url,
                "presence": presence,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        accession = d.pop("accession")

        url = d.pop("url")

        presence = d.pop("presence")

        description = d.pop("description")

        genome_property_retrieve = cls(
            accession=accession,
            url=url,
            presence=presence,
            description=description,
        )

        genome_property_retrieve.additional_properties = d
        return genome_property_retrieve

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
