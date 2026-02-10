from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.genome_catalogue_list import GenomeCatalogueList
    from ..models.m_gnify_study import MGnifyStudy


T = TypeVar("T", bound="SuperStudyDetail")


@_attrs_define
class SuperStudyDetail:
    """
    Attributes:
        slug (str):
        title (str):
        flagship_studies (list[MGnifyStudy]):
        related_studies (list[MGnifyStudy]):
        genome_catalogues (list[GenomeCatalogueList]):
        description (None | str | Unset):
        logo_url (None | str | Unset):
    """

    slug: str
    title: str
    flagship_studies: list[MGnifyStudy]
    related_studies: list[MGnifyStudy]
    genome_catalogues: list[GenomeCatalogueList]
    description: None | str | Unset = UNSET
    logo_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        slug = self.slug

        title = self.title

        flagship_studies = []
        for flagship_studies_item_data in self.flagship_studies:
            flagship_studies_item = flagship_studies_item_data.to_dict()
            flagship_studies.append(flagship_studies_item)

        related_studies = []
        for related_studies_item_data in self.related_studies:
            related_studies_item = related_studies_item_data.to_dict()
            related_studies.append(related_studies_item)

        genome_catalogues = []
        for genome_catalogues_item_data in self.genome_catalogues:
            genome_catalogues_item = genome_catalogues_item_data.to_dict()
            genome_catalogues.append(genome_catalogues_item)

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        logo_url: None | str | Unset
        if isinstance(self.logo_url, Unset):
            logo_url = UNSET
        else:
            logo_url = self.logo_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "slug": slug,
                "title": title,
                "flagship_studies": flagship_studies,
                "related_studies": related_studies,
                "genome_catalogues": genome_catalogues,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if logo_url is not UNSET:
            field_dict["logo_url"] = logo_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.genome_catalogue_list import GenomeCatalogueList
        from ..models.m_gnify_study import MGnifyStudy

        d = dict(src_dict)
        slug = d.pop("slug")

        title = d.pop("title")

        flagship_studies = []
        _flagship_studies = d.pop("flagship_studies")
        for flagship_studies_item_data in _flagship_studies:
            flagship_studies_item = MGnifyStudy.from_dict(flagship_studies_item_data)

            flagship_studies.append(flagship_studies_item)

        related_studies = []
        _related_studies = d.pop("related_studies")
        for related_studies_item_data in _related_studies:
            related_studies_item = MGnifyStudy.from_dict(related_studies_item_data)

            related_studies.append(related_studies_item)

        genome_catalogues = []
        _genome_catalogues = d.pop("genome_catalogues")
        for genome_catalogues_item_data in _genome_catalogues:
            genome_catalogues_item = GenomeCatalogueList.from_dict(genome_catalogues_item_data)

            genome_catalogues.append(genome_catalogues_item)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_logo_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        logo_url = _parse_logo_url(d.pop("logo_url", UNSET))

        super_study_detail = cls(
            slug=slug,
            title=title,
            flagship_studies=flagship_studies,
            related_studies=related_studies,
            genome_catalogues=genome_catalogues,
            description=description,
            logo_url=logo_url,
        )

        super_study_detail.additional_properties = d
        return super_study_detail

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
