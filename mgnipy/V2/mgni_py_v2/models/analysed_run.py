from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast






T = TypeVar("T", bound="AnalysedRun")



@_attrs_define
class AnalysedRun:
    """ 
        Attributes:
            accession (str):
            instrument_model (None | str):
            instrument_platform (None | str):
     """

    accession: str
    instrument_model: None | str
    instrument_platform: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        accession = self.accession

        instrument_model: None | str
        instrument_model = self.instrument_model

        instrument_platform: None | str
        instrument_platform = self.instrument_platform


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "accession": accession,
            "instrument_model": instrument_model,
            "instrument_platform": instrument_platform,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        accession = d.pop("accession")

        def _parse_instrument_model(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        instrument_model = _parse_instrument_model(d.pop("instrument_model"))


        def _parse_instrument_platform(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        instrument_platform = _parse_instrument_platform(d.pop("instrument_platform"))


        analysed_run = cls(
            accession=accession,
            instrument_model=instrument_model,
            instrument_platform=instrument_platform,
        )


        analysed_run.additional_properties = d
        return analysed_run

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
