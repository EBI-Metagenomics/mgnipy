from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.m_gnify_sample import MGnifySample





T = TypeVar("T", bound="NinjaPaginationResponseSchemaMGnifySample")



@_attrs_define
class NinjaPaginationResponseSchemaMGnifySample:
    """ 
        Attributes:
            count (int):
            items (list[MGnifySample]):
     """

    count: int
    items: list[MGnifySample]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.m_gnify_sample import MGnifySample
        count = self.count

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "count": count,
            "items": items,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.m_gnify_sample import MGnifySample
        d = dict(src_dict)
        count = d.pop("count")

        items = []
        _items = d.pop("items")
        for items_item_data in (_items):
            items_item = MGnifySample.from_dict(items_item_data)



            items.append(items_item)


        ninja_pagination_response_schema_m_gnify_sample = cls(
            count=count,
            items=items,
        )


        ninja_pagination_response_schema_m_gnify_sample.additional_properties = d
        return ninja_pagination_response_schema_m_gnify_sample

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
