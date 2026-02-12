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
    from ..models.m_gnify_publication_detail_metadata import (
        MGnifyPublicationDetailMetadata,
    )
    from ..models.m_gnify_study import MGnifyStudy


T = TypeVar("T", bound="MGnifyPublicationDetail")


@_attrs_define
class MGnifyPublicationDetail:
    """
    Attributes:
        title (str):
        metadata (MGnifyPublicationDetailMetadata):
        studies (list[MGnifyStudy]):
        pubmed_id (int | Unset):
        published_year (int | None | Unset):
    """

    title: str
    metadata: MGnifyPublicationDetailMetadata
    studies: list[MGnifyStudy]
    pubmed_id: int | Unset = UNSET
    published_year: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        metadata = self.metadata.to_dict()

        studies = []
        for studies_item_data in self.studies:
            studies_item = studies_item_data.to_dict()
            studies.append(studies_item)

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
                "studies": studies,
            }
        )
        if pubmed_id is not UNSET:
            field_dict["pubmed_id"] = pubmed_id
        if published_year is not UNSET:
            field_dict["published_year"] = published_year

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.m_gnify_publication_detail_metadata import (
            MGnifyPublicationDetailMetadata,
        )
        from ..models.m_gnify_study import MGnifyStudy

        d = dict(src_dict)
        title = d.pop("title")

        metadata = MGnifyPublicationDetailMetadata.from_dict(d.pop("metadata"))

        studies = []
        _studies = d.pop("studies")
        for studies_item_data in _studies:
            studies_item = MGnifyStudy.from_dict(studies_item_data)

            studies.append(studies_item)

        pubmed_id = d.pop("pubmed_id", UNSET)

        def _parse_published_year(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        published_year = _parse_published_year(d.pop("published_year", UNSET))

        m_gnify_publication_detail = cls(
            title=title,
            metadata=metadata,
            studies=studies,
            pubmed_id=pubmed_id,
            published_year=published_year,
        )

        m_gnify_publication_detail.additional_properties = d
        return m_gnify_publication_detail

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
