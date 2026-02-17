from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..._mgnipy_models.types import (
    UNSET,
    Unset,
)
from ..models.pipeline_versions import PipelineVersions

T = TypeVar("T", bound="StudyListFilters")


@_attrs_define
class StudyListFilters:
    """
    Attributes:
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        has_analyses_from_pipeline (None | PipelineVersions | Unset): If set, will only show studies with analyses from
            the specified MGnify pipeline version
        search (None | str | Unset): Search within study titles and accessions
    """

    biome_lineage: None | str | Unset = UNSET
    has_analyses_from_pipeline: None | PipelineVersions | Unset = UNSET
    search: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        biome_lineage: None | str | Unset
        if isinstance(self.biome_lineage, Unset):
            biome_lineage = UNSET
        else:
            biome_lineage = self.biome_lineage

        has_analyses_from_pipeline: None | str | Unset
        if isinstance(self.has_analyses_from_pipeline, Unset):
            has_analyses_from_pipeline = UNSET
        elif isinstance(self.has_analyses_from_pipeline, PipelineVersions):
            has_analyses_from_pipeline = self.has_analyses_from_pipeline.value
        else:
            has_analyses_from_pipeline = self.has_analyses_from_pipeline

        search: None | str | Unset
        if isinstance(self.search, Unset):
            search = UNSET
        else:
            search = self.search

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if biome_lineage is not UNSET:
            field_dict["biome_lineage"] = biome_lineage
        if has_analyses_from_pipeline is not UNSET:
            field_dict["has_analyses_from_pipeline"] = has_analyses_from_pipeline
        if search is not UNSET:
            field_dict["search"] = search

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_biome_lineage(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        biome_lineage = _parse_biome_lineage(d.pop("biome_lineage", UNSET))

        def _parse_has_analyses_from_pipeline(
            data: object,
        ) -> None | PipelineVersions | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                has_analyses_from_pipeline_type_0 = PipelineVersions(data)

                return has_analyses_from_pipeline_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PipelineVersions | Unset, data)

        has_analyses_from_pipeline = _parse_has_analyses_from_pipeline(
            d.pop("has_analyses_from_pipeline", UNSET)
        )

        def _parse_search(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        search = _parse_search(d.pop("search", UNSET))

        study_list_filters = cls(
            biome_lineage=biome_lineage,
            has_analyses_from_pipeline=has_analyses_from_pipeline,
            search=search,
        )

        study_list_filters.additional_properties = d
        return study_list_filters

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
