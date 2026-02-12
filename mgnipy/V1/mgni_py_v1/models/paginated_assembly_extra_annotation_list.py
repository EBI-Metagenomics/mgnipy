from __future__ import annotations

from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.assembly_extra_annotation import AssemblyExtraAnnotation


T = TypeVar("T", bound="PaginatedAssemblyExtraAnnotationList")


@_attrs_define
class PaginatedAssemblyExtraAnnotationList:
    """
    Attributes:
        count (int | Unset):  Example: 123.
        next_ (None | str | Unset):  Example: http://api.example.org/accounts/?page=4.
        previous (None | str | Unset):  Example: http://api.example.org/accounts/?page=2.
        results (list[AssemblyExtraAnnotation] | Unset):
    """

    count: int | Unset = UNSET
    next_: None | str | Unset = UNSET
    previous: None | str | Unset = UNSET
    results: list[AssemblyExtraAnnotation] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        count = self.count

        next_: None | str | Unset
        if isinstance(self.next_, Unset):
            next_ = UNSET
        else:
            next_ = self.next_

        previous: None | str | Unset
        if isinstance(self.previous, Unset):
            previous = UNSET
        else:
            previous = self.previous

        results: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.results, Unset):
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()
                results.append(results_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if count is not UNSET:
            field_dict["count"] = count
        if next_ is not UNSET:
            field_dict["next"] = next_
        if previous is not UNSET:
            field_dict["previous"] = previous
        if results is not UNSET:
            field_dict["results"] = results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.assembly_extra_annotation import AssemblyExtraAnnotation

        d = dict(src_dict)
        count = d.pop("count", UNSET)

        def _parse_next_(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        next_ = _parse_next_(d.pop("next", UNSET))

        def _parse_previous(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        previous = _parse_previous(d.pop("previous", UNSET))

        _results = d.pop("results", UNSET)
        results: list[AssemblyExtraAnnotation] | Unset = UNSET
        if _results is not UNSET:
            results = []
            for results_item_data in _results:
                results_item = AssemblyExtraAnnotation.from_dict(results_item_data)

                results.append(results_item)

        paginated_assembly_extra_annotation_list = cls(
            count=count,
            next_=next_,
            previous=previous,
            results=results,
        )

        paginated_assembly_extra_annotation_list.additional_properties = d
        return paginated_assembly_extra_annotation_list

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
