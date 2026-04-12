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
    from ..models.m_gnify_publication_metadata import MGnifyPublicationMetadata


T = TypeVar("T", bound="MGnifyPublication")


@_attrs_define
class MGnifyPublication:
    """
    Attributes:
        title (str):
        metadata (MGnifyPublicationMetadata):
        pubmed_id (int | Unset):
        published_year (int | None | Unset):
    """

    title: str
    metadata: MGnifyPublicationMetadata
    pubmed_id: int | Unset = UNSET
    published_year: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        metadata = self.metadata.to_dict()

        pubmed_id = self.pubmed_id

        published_year: int | None | Unset
        if isinstance(self.published_year, Unset):
            published_year = UNSET
        else:
            published_year = self.published_year

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "metadata": metadata,
            }
        )
        if pubmed_id is not UNSET:
            field_dict["pubmed_id"] = pubmed_id
        if published_year is not UNSET:
            field_dict["published_year"] = published_year

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.m_gnify_publication_metadata import MGnifyPublicationMetadata

        d = dict(src_dict)
        title = d.pop("title")

        metadata = MGnifyPublicationMetadata.from_dict(d.pop("metadata"))

        pubmed_id = d.pop("pubmed_id", UNSET)

        def _parse_published_year(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        published_year = _parse_published_year(d.pop("published_year", UNSET))

        m_gnify_publication = cls(
            title=title,
            metadata=metadata,
            pubmed_id=pubmed_id,
            published_year=published_year,
        )

        m_gnify_publication.additional_properties = d
        return m_gnify_publication

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
