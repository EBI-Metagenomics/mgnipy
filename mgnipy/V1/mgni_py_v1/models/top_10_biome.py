from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Top10Biome")


@_attrs_define
class Top10Biome:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            url (str):
            samples_count (int):
            samples (str):
            studies (str):
            genomes (str):
            children (str):
            biome_name (str): Biome name
            lineage (str): Biome lineage
    """

    url: str
    samples_count: int
    samples: str
    studies: str
    genomes: str
    children: str
    biome_name: str
    lineage: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        samples_count = self.samples_count

        samples = self.samples

        studies = self.studies

        genomes = self.genomes

        children = self.children

        biome_name = self.biome_name

        lineage = self.lineage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "samples_count": samples_count,
                "samples": samples,
                "studies": studies,
                "genomes": genomes,
                "children": children,
                "biome_name": biome_name,
                "lineage": lineage,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        samples_count = d.pop("samples_count")

        samples = d.pop("samples")

        studies = d.pop("studies")

        genomes = d.pop("genomes")

        children = d.pop("children")

        biome_name = d.pop("biome_name")

        lineage = d.pop("lineage")

        top_10_biome = cls(
            url=url,
            samples_count=samples_count,
            samples=samples,
            studies=studies,
            genomes=genomes,
            children=children,
            biome_name=biome_name,
            lineage=lineage,
        )

        top_10_biome.additional_properties = d
        return top_10_biome

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
