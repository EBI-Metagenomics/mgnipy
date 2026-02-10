from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AntiSmashGeneClusterRetrieve")


@_attrs_define
class AntiSmashGeneClusterRetrieve:
    """Serializer for DynamicDocuments.

    Maps all undefined fields to :class:`fields.DynamicField`.

        Attributes:
            accession (str):
            url (str):
            count (int):
            description (str):
    """

    accession: str
    url: str
    count: int
    description: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accession = self.accession

        url = self.url

        count = self.count

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accession": accession,
                "url": url,
                "count": count,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        accession = d.pop("accession")

        url = d.pop("url")

        count = d.pop("count")

        description = d.pop("description")

        anti_smash_gene_cluster_retrieve = cls(
            accession=accession,
            url=url,
            count=count,
            description=description,
        )

        anti_smash_gene_cluster_retrieve.additional_properties = d
        return anti_smash_gene_cluster_retrieve

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
