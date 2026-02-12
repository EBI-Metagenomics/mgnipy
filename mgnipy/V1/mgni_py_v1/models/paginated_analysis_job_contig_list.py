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
    from ..models.analysis_job_contig import AnalysisJobContig


T = TypeVar("T", bound="PaginatedAnalysisJobContigList")


@_attrs_define
class PaginatedAnalysisJobContigList:
    """
    Attributes:
        next_ (None | str | Unset):
        previous (None | str | Unset):
        results (list[AnalysisJobContig] | Unset):
    """

    next_: None | str | Unset = UNSET
    previous: None | str | Unset = UNSET
    results: list[AnalysisJobContig] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        next_: None | str | Unset
        if isinstance(self.next_, Unset):
            next_ = UNSET
        else:
            next_ = self.next_

        previous: None | str | Unset
        if isinstance(self.previous, Unset):
            previous = UNSET
        else:
            previous = self.previous

        results: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.results, Unset):
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()
                results.append(results_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_ is not UNSET:
            field_dict["next"] = next_
        if previous is not UNSET:
            field_dict["previous"] = previous
        if results is not UNSET:
            field_dict["results"] = results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.analysis_job_contig import AnalysisJobContig

        d = dict(src_dict)

        def _parse_next_(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        next_ = _parse_next_(d.pop("next", UNSET))

        def _parse_previous(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        previous = _parse_previous(d.pop("previous", UNSET))

        _results = d.pop("results", UNSET)
        results: list[AnalysisJobContig] | Unset = UNSET
        if _results is not UNSET:
            results = []
            for results_item_data in _results:
                results_item = AnalysisJobContig.from_dict(results_item_data)

                results.append(results_item)

        paginated_analysis_job_contig_list = cls(
            next_=next_,
            previous=previous,
            results=results,
        )

        paginated_analysis_job_contig_list.additional_properties = d
        return paginated_analysis_job_contig_list

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
