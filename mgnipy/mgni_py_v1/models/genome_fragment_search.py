from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..models.catalogues_filter_enum import CataloguesFilterEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="GenomeFragmentSearch")


@_attrs_define
class GenomeFragmentSearch:
    """
    Attributes:
        seq (str): DNA sequence (gene fragment) between 50 and 5000bp long.
        catalogues_filter (list[CataloguesFilterEnum]):
        threshold (float | Unset): Minimum k-mer similarity fraction for a MAG to be included in results. Default 0.4.
            Default: 0.4.
    """

    seq: str
    catalogues_filter: list[CataloguesFilterEnum]
    threshold: float | Unset = 0.4
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        seq = self.seq

        catalogues_filter = []
        for catalogues_filter_item_data in self.catalogues_filter:
            catalogues_filter_item = catalogues_filter_item_data.value
            catalogues_filter.append(catalogues_filter_item)

        threshold = self.threshold

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "seq": seq,
                "catalogues_filter": catalogues_filter,
            }
        )
        if threshold is not UNSET:
            field_dict["threshold"] = threshold

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("seq", (None, str(self.seq).encode(), "text/plain")))

        for catalogues_filter_item_element in self.catalogues_filter:
            files.append(
                ("catalogues_filter", (None, str(catalogues_filter_item_element.value).encode(), "text/plain"))
            )

        if not isinstance(self.threshold, Unset):
            files.append(("threshold", (None, str(self.threshold).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        seq = d.pop("seq")

        catalogues_filter = []
        _catalogues_filter = d.pop("catalogues_filter")
        for catalogues_filter_item_data in _catalogues_filter:
            catalogues_filter_item = CataloguesFilterEnum(catalogues_filter_item_data)

            catalogues_filter.append(catalogues_filter_item)

        threshold = d.pop("threshold", UNSET)

        genome_fragment_search = cls(
            seq=seq,
            catalogues_filter=catalogues_filter,
            threshold=threshold,
        )

        genome_fragment_search.additional_properties = d
        return genome_fragment_search

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
