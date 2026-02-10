from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MGnifyAnalysisTypedAnnotation")


@_attrs_define
class MGnifyAnalysisTypedAnnotation:
    """
    Attributes:
        count (int | None | Unset):
        description (None | str | Unset):
        organism (None | str | Unset):
    """

    count: int | None | Unset = UNSET
    description: None | str | Unset = UNSET
    organism: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        count: int | None | Unset
        if isinstance(self.count, Unset):
            count = UNSET
        else:
            count = self.count

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        organism: None | str | Unset
        if isinstance(self.organism, Unset):
            organism = UNSET
        else:
            organism = self.organism

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if count is not UNSET:
            field_dict["count"] = count
        if description is not UNSET:
            field_dict["description"] = description
        if organism is not UNSET:
            field_dict["organism"] = organism

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        count = _parse_count(d.pop("count", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_organism(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        organism = _parse_organism(d.pop("organism", UNSET))

        m_gnify_analysis_typed_annotation = cls(
            count=count,
            description=description,
            organism=organism,
        )

        m_gnify_analysis_typed_annotation.additional_properties = d
        return m_gnify_analysis_typed_annotation

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
