from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.annotated_result import AnnotatedResult


T = TypeVar("T", bound="GenomeSearchData")


@_attrs_define
class GenomeSearchData:
    """
    Attributes:
        results (list[AnnotatedResult]):
        query (None | str | Unset):
        threshold (float | None | Unset):
    """

    results: list[AnnotatedResult]
    query: None | str | Unset = UNSET
    threshold: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        query: None | str | Unset
        if isinstance(self.query, Unset):
            query = UNSET
        else:
            query = self.query

        threshold: float | None | Unset
        if isinstance(self.threshold, Unset):
            threshold = UNSET
        else:
            threshold = self.threshold

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "results": results,
            }
        )
        if query is not UNSET:
            field_dict["query"] = query
        if threshold is not UNSET:
            field_dict["threshold"] = threshold

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.annotated_result import AnnotatedResult

        d = dict(src_dict)
        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = AnnotatedResult.from_dict(results_item_data)

            results.append(results_item)

        def _parse_query(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        query = _parse_query(d.pop("query", UNSET))

        def _parse_threshold(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        threshold = _parse_threshold(d.pop("threshold", UNSET))

        genome_search_data = cls(
            results=results,
            query=query,
            threshold=threshold,
        )

        genome_search_data.additional_properties = d
        return genome_search_data

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
