from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="Assembly")



@_attrs_define
class Assembly:
    """ 
        Attributes:
            updated_at (datetime.datetime):
            accession (None | str | Unset):
     """

    updated_at: datetime.datetime
    accession: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        updated_at = self.updated_at.isoformat()

        accession: None | str | Unset
        if isinstance(self.accession, Unset):
            accession = UNSET
        else:
            accession = self.accession


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "updated_at": updated_at,
        })
        if accession is not UNSET:
            field_dict["accession"] = accession

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        updated_at = isoparse(d.pop("updated_at"))




        def _parse_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        accession = _parse_accession(d.pop("accession", UNSET))


        assembly = cls(
            updated_at=updated_at,
            accession=accession,
        )


        assembly.additional_properties = d
        return assembly

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
