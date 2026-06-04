from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

T = TypeVar("T", bound="CobsMatch")


@_attrs_define
class CobsMatch:
    """
    Attributes:
        genome (str):
        percent_kmers_found (float | None | Unset):  Default: 0.0.
        num_kmers (int | None | Unset):
        num_kmers_found (int | None | Unset):
    """

    genome: str
    percent_kmers_found: float | None | Unset = 0.0
    num_kmers: int | None | Unset = UNSET
    num_kmers_found: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        genome = self.genome

        percent_kmers_found: float | None | Unset
        if isinstance(self.percent_kmers_found, Unset):
            percent_kmers_found = UNSET
        else:
            percent_kmers_found = self.percent_kmers_found

        num_kmers: int | None | Unset
        if isinstance(self.num_kmers, Unset):
            num_kmers = UNSET
        else:
            num_kmers = self.num_kmers

        num_kmers_found: int | None | Unset
        if isinstance(self.num_kmers_found, Unset):
            num_kmers_found = UNSET
        else:
            num_kmers_found = self.num_kmers_found

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "genome": genome,
            }
        )
        if percent_kmers_found is not UNSET:
            field_dict["percent_kmers_found"] = percent_kmers_found
        if num_kmers is not UNSET:
            field_dict["num_kmers"] = num_kmers
        if num_kmers_found is not UNSET:
            field_dict["num_kmers_found"] = num_kmers_found

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        genome = d.pop("genome")

        def _parse_percent_kmers_found(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        percent_kmers_found = _parse_percent_kmers_found(
            d.pop("percent_kmers_found", UNSET)
        )

        def _parse_num_kmers(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        num_kmers = _parse_num_kmers(d.pop("num_kmers", UNSET))

        def _parse_num_kmers_found(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        num_kmers_found = _parse_num_kmers_found(d.pop("num_kmers_found", UNSET))

        cobs_match = cls(
            genome=genome,
            percent_kmers_found=percent_kmers_found,
            num_kmers=num_kmers,
            num_kmers_found=num_kmers_found,
        )

        cobs_match.additional_properties = d
        return cobs_match

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
