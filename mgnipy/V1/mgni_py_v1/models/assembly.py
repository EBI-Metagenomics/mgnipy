from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Assembly")


@_attrs_define
class Assembly:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            url (str):
            experiment_type (str):
            analyses (str):
            samples (str):
            extra_annotations (str):
            runs (str):
            pipelines (str):
            accession (None | str):
            wgs_accession (None | str):
            legacy_accession (None | str):
            is_private (bool | Unset):
            coverage (int | None | Unset):
            min_gap_length (int | None | Unset):
    """

    url: str
    experiment_type: str
    analyses: str
    samples: str
    extra_annotations: str
    runs: str
    pipelines: str
    accession: None | str
    wgs_accession: None | str
    legacy_accession: None | str
    is_private: bool | Unset = UNSET
    coverage: int | None | Unset = UNSET
    min_gap_length: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        experiment_type = self.experiment_type

        analyses = self.analyses

        samples = self.samples

        extra_annotations = self.extra_annotations

        runs = self.runs

        pipelines = self.pipelines

        accession: None | str
        accession = self.accession

        wgs_accession: None | str
        wgs_accession = self.wgs_accession

        legacy_accession: None | str
        legacy_accession = self.legacy_accession

        is_private = self.is_private

        coverage: int | None | Unset
        if isinstance(self.coverage, Unset):
            coverage = UNSET
        else:
            coverage = self.coverage

        min_gap_length: int | None | Unset
        if isinstance(self.min_gap_length, Unset):
            min_gap_length = UNSET
        else:
            min_gap_length = self.min_gap_length

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "experiment_type": experiment_type,
                "analyses": analyses,
                "samples": samples,
                "extra_annotations": extra_annotations,
                "runs": runs,
                "pipelines": pipelines,
                "accession": accession,
                "wgs_accession": wgs_accession,
                "legacy_accession": legacy_accession,
            }
        )
        if is_private is not UNSET:
            field_dict["is_private"] = is_private
        if coverage is not UNSET:
            field_dict["coverage"] = coverage
        if min_gap_length is not UNSET:
            field_dict["min_gap_length"] = min_gap_length

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        experiment_type = d.pop("experiment_type")

        analyses = d.pop("analyses")

        samples = d.pop("samples")

        extra_annotations = d.pop("extra_annotations")

        runs = d.pop("runs")

        pipelines = d.pop("pipelines")

        def _parse_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        accession = _parse_accession(d.pop("accession"))

        def _parse_wgs_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        wgs_accession = _parse_wgs_accession(d.pop("wgs_accession"))

        def _parse_legacy_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        legacy_accession = _parse_legacy_accession(d.pop("legacy_accession"))

        is_private = d.pop("is_private", UNSET)

        def _parse_coverage(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        coverage = _parse_coverage(d.pop("coverage", UNSET))

        def _parse_min_gap_length(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        min_gap_length = _parse_min_gap_length(d.pop("min_gap_length", UNSET))

        assembly = cls(
            url=url,
            experiment_type=experiment_type,
            analyses=analyses,
            samples=samples,
            extra_annotations=extra_annotations,
            runs=runs,
            pipelines=pipelines,
            accession=accession,
            wgs_accession=wgs_accession,
            legacy_accession=legacy_accession,
            is_private=is_private,
            coverage=coverage,
            min_gap_length=min_gap_length,
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
