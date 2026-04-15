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
    from ..models.m_gnify_sample import MGnifySample
    from ..models.m_gnify_study import MGnifyStudy


T = TypeVar("T", bound="AnalysedRunDetail")


@_attrs_define
class AnalysedRunDetail:
    """
    Attributes:
        experiment_type (str): Experiment type refers to the type of sequencing data that was analysed, e.g. amplicon
            reads or a metagenome assembly
        accession (str):
        instrument_model (None | str):
        instrument_platform (None | str):
        sample (MGnifySample | None):
        study (MGnifyStudy | None):
        sample_accession (None | str | Unset): ENA accession of the sample associated with this run
        study_accession (None | str | Unset): ENA accession of the study associated with this run
    """

    experiment_type: str
    accession: str
    instrument_model: None | str
    instrument_platform: None | str
    sample: MGnifySample | None
    study: MGnifyStudy | None
    sample_accession: None | str | Unset = UNSET
    study_accession: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.m_gnify_sample import MGnifySample
        from ..models.m_gnify_study import MGnifyStudy

        experiment_type = self.experiment_type

        accession = self.accession

        instrument_model: None | str
        instrument_model = self.instrument_model

        instrument_platform: None | str
        instrument_platform = self.instrument_platform

        sample: dict[str, Any] | None
        if isinstance(self.sample, MGnifySample):
            sample = self.sample.to_dict()
        else:
            sample = self.sample

        study: dict[str, Any] | None
        if isinstance(self.study, MGnifyStudy):
            study = self.study.to_dict()
        else:
            study = self.study

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
                "sample": sample,
                "study": study,
            }
        )
        if sample_accession is not UNSET:
            field_dict["sample_accession"] = sample_accession
        if study_accession is not UNSET:
            field_dict["study_accession"] = study_accession

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.m_gnify_sample import MGnifySample
        from ..models.m_gnify_study import MGnifyStudy

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

        def _parse_sample(data: object) -> MGnifySample | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                sample_type_0 = MGnifySample.from_dict(data)

                return sample_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MGnifySample | None, data)

        sample = _parse_sample(d.pop("sample"))

        def _parse_study(data: object) -> MGnifyStudy | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                study_type_0 = MGnifyStudy.from_dict(data)

                return study_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MGnifyStudy | None, data)

        study = _parse_study(d.pop("study"))

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

        analysed_run_detail = cls(
            experiment_type=experiment_type,
            accession=accession,
            instrument_model=instrument_model,
            instrument_platform=instrument_platform,
            sample=sample,
            study=study,
            sample_accession=sample_accession,
            study_accession=study_accession,
        )

        analysed_run_detail.additional_properties = d
        return analysed_run_detail

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
