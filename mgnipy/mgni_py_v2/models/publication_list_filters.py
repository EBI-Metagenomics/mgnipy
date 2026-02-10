from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PublicationListFilters")


@_attrs_define
class PublicationListFilters:
    """
    Attributes:
        published_after (int | None | Unset): Filter by minimum publication year
        published_before (int | None | Unset): Filter by maximum publication year
        title (None | str | Unset): Search within publication titles
    """

    published_after: int | None | Unset = UNSET
    published_before: int | None | Unset = UNSET
    title: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        published_after: int | None | Unset
        if isinstance(self.published_after, Unset):
            published_after = UNSET
        else:
            published_after = self.published_after

        published_before: int | None | Unset
        if isinstance(self.published_before, Unset):
            published_before = UNSET
        else:
            published_before = self.published_before

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if published_after is not UNSET:
            field_dict["published_after"] = published_after
        if published_before is not UNSET:
            field_dict["published_before"] = published_before
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_published_after(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        published_after = _parse_published_after(d.pop("published_after", UNSET))

        def _parse_published_before(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        published_before = _parse_published_before(d.pop("published_before", UNSET))

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        publication_list_filters = cls(
            published_after=published_after,
            published_before=published_before,
            title=title,
        )

        publication_list_filters.additional_properties = d
        return publication_list_filters

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
