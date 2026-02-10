from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ExperimentType")


@_attrs_define
class ExperimentType:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            samples_count (int):
            analyses (str):
            samples (str):
            runs_count (int):
            runs (str):
            url (str):
            experiment_type (str): Experiment type, e.g. metagenomic
    """

    samples_count: int
    analyses: str
    samples: str
    runs_count: int
    runs: str
    url: str
    experiment_type: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        samples_count = self.samples_count

        analyses = self.analyses

        samples = self.samples

        runs_count = self.runs_count

        runs = self.runs

        url = self.url

        experiment_type = self.experiment_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "samples_count": samples_count,
                "analyses": analyses,
                "samples": samples,
                "runs_count": runs_count,
                "runs": runs,
                "url": url,
                "experiment_type": experiment_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        samples_count = d.pop("samples_count")

        analyses = d.pop("analyses")

        samples = d.pop("samples")

        runs_count = d.pop("runs_count")

        runs = d.pop("runs")

        url = d.pop("url")

        experiment_type = d.pop("experiment_type")

        experiment_type = cls(
            samples_count=samples_count,
            analyses=analyses,
            samples=samples,
            runs_count=runs_count,
            runs=runs,
            url=url,
            experiment_type=experiment_type,
        )

        experiment_type.additional_properties = d
        return experiment_type

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
