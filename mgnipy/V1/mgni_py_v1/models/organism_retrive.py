from __future__ import annotations

from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.organism_retrive_hierarchy import OrganismRetriveHierarchy


T = TypeVar("T", bound="OrganismRetrive")


@_attrs_define
class OrganismRetrive:
    """Serializer for DynamicDocuments.

    Maps all undefined fields to :class:`fields.DynamicField`.

        Attributes:
            url (str):
            lineage (str):
            pipeline_version (str):
            count (int | Unset):
            hierarchy (OrganismRetriveHierarchy | Unset):
            domain (str | Unset):
            name (str | Unset):
            parent (str | Unset):
            rank (str | Unset):
    """

    url: str
    lineage: str
    pipeline_version: str
    count: int | Unset = UNSET
    hierarchy: OrganismRetriveHierarchy | Unset = UNSET
    domain: str | Unset = UNSET
    name: str | Unset = UNSET
    parent: str | Unset = UNSET
    rank: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        lineage = self.lineage

        pipeline_version = self.pipeline_version

        count = self.count

        hierarchy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.hierarchy, Unset):
            hierarchy = self.hierarchy.to_dict()

        domain = self.domain

        name = self.name

        parent = self.parent

        rank = self.rank

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "lineage": lineage,
                "pipeline_version": pipeline_version,
            }
        )
        if count is not UNSET:
            field_dict["count"] = count
        if hierarchy is not UNSET:
            field_dict["hierarchy"] = hierarchy
        if domain is not UNSET:
            field_dict["domain"] = domain
        if name is not UNSET:
            field_dict["name"] = name
        if parent is not UNSET:
            field_dict["parent"] = parent
        if rank is not UNSET:
            field_dict["rank"] = rank

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.organism_retrive_hierarchy import OrganismRetriveHierarchy

        d = dict(src_dict)
        url = d.pop("url")

        lineage = d.pop("lineage")

        pipeline_version = d.pop("pipeline_version")

        count = d.pop("count", UNSET)

        _hierarchy = d.pop("hierarchy", UNSET)
        hierarchy: OrganismRetriveHierarchy | Unset
        if isinstance(_hierarchy, Unset):
            hierarchy = UNSET
        else:
            hierarchy = OrganismRetriveHierarchy.from_dict(_hierarchy)

        domain = d.pop("domain", UNSET)

        name = d.pop("name", UNSET)

        parent = d.pop("parent", UNSET)

        rank = d.pop("rank", UNSET)

        organism_retrive = cls(
            url=url,
            lineage=lineage,
            pipeline_version=pipeline_version,
            count=count,
            hierarchy=hierarchy,
            domain=domain,
            name=name,
            parent=parent,
            rank=rank,
        )

        organism_retrive.additional_properties = d
        return organism_retrive

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
