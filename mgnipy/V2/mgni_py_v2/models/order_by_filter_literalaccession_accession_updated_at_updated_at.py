from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.order_by_filter_literalaccession_accession_updated_at_updated_at_order_type_0 import (
    OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAtOrderType0,
)
from ..._mgnipy_models.types import (
    UNSET,
    Unset,
)

T = TypeVar("T", bound="OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAt")


@_attrs_define
class OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAt:
    """
    Attributes:
        order (None | OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAtOrderType0 | Unset):
    """

    order: (
        None
        | OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAtOrderType0
        | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        order: None | str | Unset
        if isinstance(self.order, Unset):
            order = UNSET
        elif isinstance(
            self.order,
            OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAtOrderType0,
        ):
            order = self.order.value
        else:
            order = self.order

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if order is not UNSET:
            field_dict["order"] = order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_order(
            data: object,
        ) -> (
            None
            | OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAtOrderType0
            | Unset
        ):
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                order_type_0 = (
                    OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAtOrderType0(
                        data
                    )
                )

                return order_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None
                | OrderByFilterLiteralaccessionAccessionUpdatedAtUpdatedAtOrderType0
                | Unset,
                data,
            )

        order = _parse_order(d.pop("order", UNSET))

        order_by_filter_literalaccession_accession_updated_at_updated_at = cls(
            order=order,
        )

        order_by_filter_literalaccession_accession_updated_at_updated_at.additional_properties = (
            d
        )
        return order_by_filter_literalaccession_accession_updated_at_updated_at

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
