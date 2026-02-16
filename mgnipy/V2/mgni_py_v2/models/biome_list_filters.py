from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..._models_v2.types import (
    UNSET,
    Unset,
)

T = TypeVar("T", bound="BiomeListFilters")


@_attrs_define
class BiomeListFilters:
    """
    Attributes:
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        max_depth (int | None | Unset): Maximum depth of the biome lineage to include, e.g. `root` is 1 and `root:Host-
            Associated:Human` is level 3
    """

    biome_lineage: None | str | Unset = UNSET
    max_depth: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        biome_lineage: None | str | Unset
        if isinstance(self.biome_lineage, Unset):
            biome_lineage = UNSET
        else:
            biome_lineage = self.biome_lineage

        max_depth: int | None | Unset
        if isinstance(self.max_depth, Unset):
            max_depth = UNSET
        else:
            max_depth = self.max_depth

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if biome_lineage is not UNSET:
            field_dict["biome_lineage"] = biome_lineage
        if max_depth is not UNSET:
            field_dict["max_depth"] = max_depth

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_biome_lineage(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        biome_lineage = _parse_biome_lineage(d.pop("biome_lineage", UNSET))

        def _parse_max_depth(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_depth = _parse_max_depth(d.pop("max_depth", UNSET))

        biome_list_filters = cls(
            biome_lineage=biome_lineage,
            max_depth=max_depth,
        )

        biome_list_filters.additional_properties = d
        return biome_list_filters

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
