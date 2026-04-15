from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.experiment_types import ExperimentTypes
from ..types import (
    UNSET,
    Unset,
)

T = TypeVar("T", bound="RunListFilters")


@_attrs_define
class RunListFilters:
    """
    Attributes:
        has_experiment_type (ExperimentTypes | None | Unset): If set, will only show runs with the specified experiment
            type
    """

    has_experiment_type: ExperimentTypes | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        has_experiment_type: None | str | Unset
        if isinstance(self.has_experiment_type, Unset):
            has_experiment_type = UNSET
        elif isinstance(self.has_experiment_type, ExperimentTypes):
            has_experiment_type = self.has_experiment_type.value
        else:
            has_experiment_type = self.has_experiment_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if has_experiment_type is not UNSET:
            field_dict["has_experiment_type"] = has_experiment_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_has_experiment_type(data: object) -> ExperimentTypes | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                has_experiment_type_type_0 = ExperimentTypes(data)

                return has_experiment_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ExperimentTypes | None | Unset, data)

        has_experiment_type = _parse_has_experiment_type(
            d.pop("has_experiment_type", UNSET)
        )

        run_list_filters = cls(
            has_experiment_type=has_experiment_type,
        )

        run_list_filters.additional_properties = d
        return run_list_filters

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
