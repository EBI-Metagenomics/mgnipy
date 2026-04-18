from __future__ import annotations

from collections.abc import Mapping
from typing import (
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

T = TypeVar("T", bound="AnalysedRun")


@_attrs_define
class AnalysedRun:
    """
    Attributes:
        experiment_type (str): Experiment type refers to the type of sequencing data that was analysed, e.g. amplicon
            reads or a metagenome assembly
        accession (str):
        instrument_model (None | str):
        instrument_platform (None | str):
        sample_accession (None | str | Unset): ENA accession of the sample associated with this run
        study_accession (None | str | Unset): ENA accession of the study associated with this run
    """

    experiment_type: str
    accession: str
    instrument_model: None | str
    instrument_platform: None | str
    sample_accession: None | str | Unset = UNSET
    study_accession: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        experiment_type = self.experiment_type

        accession = self.accession

        instrument_model: None | str
        instrument_model = self.instrument_model

        instrument_platform: None | str
        instrument_platform = self.instrument_platform

        sample_accession: None | str | Unset
        if isinstance(self.sample_accession, Unset):
            sample_accession = UNSET
        else:
            sample_accession = self.sample_accession

        study_accession: None | str | Unset
        if isinstance(self.study_accession, Unset):
            study_accession = UNSET
        else:
            study_accession = self.study_accession

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "experiment_type": experiment_type,
                "accession": accession,
                "instrument_model": instrument_model,
                "instrument_platform": instrument_platform,
            }
        )
        if sample_accession is not UNSET:
            field_dict["sample_accession"] = sample_accession
        if study_accession is not UNSET:
            field_dict["study_accession"] = study_accession

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        experiment_type = d.pop("experiment_type")

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

        def _parse_sample_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sample_accession = _parse_sample_accession(d.pop("sample_accession", UNSET))

        def _parse_study_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        study_accession = _parse_study_accession(d.pop("study_accession", UNSET))

        analysed_run = cls(
            experiment_type=experiment_type,
            accession=accession,
            instrument_model=instrument_model,
            instrument_platform=instrument_platform,
            sample_accession=sample_accession,
            study_accession=study_accession,
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
