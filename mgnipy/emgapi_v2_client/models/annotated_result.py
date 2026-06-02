from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field


if TYPE_CHECKING:
    from ..models.cobs_match import CobsMatch
    from ..models.genome_list import GenomeList


T = TypeVar("T", bound="AnnotatedResult")


@_attrs_define
class AnnotatedResult:
    """
    Attributes:
        mgnify (GenomeList):
        cobs (CobsMatch):
    """

    mgnify: GenomeList
    cobs: CobsMatch
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mgnify = self.mgnify.to_dict()

        cobs = self.cobs.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mgnify": mgnify,
                "cobs": cobs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cobs_match import CobsMatch
        from ..models.genome_list import GenomeList

        d = dict(src_dict)
        mgnify = GenomeList.from_dict(d.pop("mgnify"))

        cobs = CobsMatch.from_dict(d.pop("cobs"))

        annotated_result = cls(
            mgnify=mgnify,
            cobs=cobs,
        )

        annotated_result.additional_properties = d
        return annotated_result

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
