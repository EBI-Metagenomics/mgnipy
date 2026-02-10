from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GoTermRetrive")


@_attrs_define
class GoTermRetrive:
    """Serializer for DynamicDocuments.

    Maps all undefined fields to :class:`fields.DynamicField`.

        Attributes:
            accession (str):
            url (str):
            description (str):
            lineage (str):
            count (int | Unset):
    """

    accession: str
    url: str
    description: str
    lineage: str
    count: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accession = self.accession

        url = self.url

        description = self.description

        lineage = self.lineage

        count = self.count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accession": accession,
                "url": url,
                "description": description,
                "lineage": lineage,
            }
        )
        if count is not UNSET:
            field_dict["count"] = count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        accession = d.pop("accession")

        url = d.pop("url")

        description = d.pop("description")

        lineage = d.pop("lineage")

        count = d.pop("count", UNSET)

        go_term_retrive = cls(
            accession=accession,
            url=url,
            description=description,
            lineage=lineage,
            count=count,
        )

        go_term_retrive.additional_properties = d
        return go_term_retrive

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
