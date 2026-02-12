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

T = TypeVar("T", bound="Run")


@_attrs_define
class Run:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            url (str):
            experiment_type (str):
            sample (str):
            analyses (str):
            study (str):
            assemblies (str):
            extra_annotations (str):
            pipelines (str):
            accession (None | str):
            secondary_accession (None | str):
            is_private (bool | Unset):
            ena_study_accession (None | str | Unset): ENA Study accession.
            instrument_platform (None | str | Unset):
            instrument_model (None | str | Unset):
    """

    url: str
    experiment_type: str
    sample: str
    analyses: str
    study: str
    assemblies: str
    extra_annotations: str
    pipelines: str
    accession: None | str
    secondary_accession: None | str
    is_private: bool | Unset = UNSET
    ena_study_accession: None | str | Unset = UNSET
    instrument_platform: None | str | Unset = UNSET
    instrument_model: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        experiment_type = self.experiment_type

        sample = self.sample

        analyses = self.analyses

        study = self.study

        assemblies = self.assemblies

        extra_annotations = self.extra_annotations

        pipelines = self.pipelines

        accession: None | str
        accession = self.accession

        secondary_accession: None | str
        secondary_accession = self.secondary_accession

        is_private = self.is_private

        ena_study_accession: None | str | Unset
        if isinstance(self.ena_study_accession, Unset):
            ena_study_accession = UNSET
        else:
            ena_study_accession = self.ena_study_accession

        instrument_platform: None | str | Unset
        if isinstance(self.instrument_platform, Unset):
            instrument_platform = UNSET
        else:
            instrument_platform = self.instrument_platform

        instrument_model: None | str | Unset
        if isinstance(self.instrument_model, Unset):
            instrument_model = UNSET
        else:
            instrument_model = self.instrument_model

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "experiment_type": experiment_type,
                "sample": sample,
                "analyses": analyses,
                "study": study,
                "assemblies": assemblies,
                "extra_annotations": extra_annotations,
                "pipelines": pipelines,
                "accession": accession,
                "secondary_accession": secondary_accession,
            }
        )
        if is_private is not UNSET:
            field_dict["is_private"] = is_private
        if ena_study_accession is not UNSET:
            field_dict["ena_study_accession"] = ena_study_accession
        if instrument_platform is not UNSET:
            field_dict["instrument_platform"] = instrument_platform
        if instrument_model is not UNSET:
            field_dict["instrument_model"] = instrument_model

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        experiment_type = d.pop("experiment_type")

        sample = d.pop("sample")

        analyses = d.pop("analyses")

        study = d.pop("study")

        assemblies = d.pop("assemblies")

        extra_annotations = d.pop("extra_annotations")

        pipelines = d.pop("pipelines")

        def _parse_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        accession = _parse_accession(d.pop("accession"))

        def _parse_secondary_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        secondary_accession = _parse_secondary_accession(d.pop("secondary_accession"))

        is_private = d.pop("is_private", UNSET)

        def _parse_ena_study_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ena_study_accession = _parse_ena_study_accession(
            d.pop("ena_study_accession", UNSET)
        )

        def _parse_instrument_platform(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        instrument_platform = _parse_instrument_platform(
            d.pop("instrument_platform", UNSET)
        )

        def _parse_instrument_model(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        instrument_model = _parse_instrument_model(d.pop("instrument_model", UNSET))

        run = cls(
            url=url,
            experiment_type=experiment_type,
            sample=sample,
            analyses=analyses,
            study=study,
            assemblies=assemblies,
            extra_annotations=extra_annotations,
            pipelines=pipelines,
            accession=accession,
            secondary_accession=secondary_accession,
            is_private=is_private,
            ena_study_accession=ena_study_accession,
            instrument_platform=instrument_platform,
            instrument_model=instrument_model,
        )

        run.additional_properties = d
        return run

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
