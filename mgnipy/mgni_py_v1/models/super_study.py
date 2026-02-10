from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SuperStudy")


@_attrs_define
class SuperStudy:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            super_study_id (int):
            title (str):
            url_slug (str):
            url (str):
            image_url (str):
            biomes (str):
            biomes_count (int):
            flagship_studies (str):
            related_studies (str):
            related_genome_catalogues (str):
            description (None | str | Unset): Use <a href="https://commonmark.org/help/" target="_newtab">markdown</a> for
                links and rich text.
    """

    super_study_id: int
    title: str
    url_slug: str
    url: str
    image_url: str
    biomes: str
    biomes_count: int
    flagship_studies: str
    related_studies: str
    related_genome_catalogues: str
    description: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        super_study_id = self.super_study_id

        title = self.title

        url_slug = self.url_slug

        url = self.url

        image_url = self.image_url

        biomes = self.biomes

        biomes_count = self.biomes_count

        flagship_studies = self.flagship_studies

        related_studies = self.related_studies

        related_genome_catalogues = self.related_genome_catalogues

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "super_study_id": super_study_id,
                "title": title,
                "url_slug": url_slug,
                "url": url,
                "image_url": image_url,
                "biomes": biomes,
                "biomes_count": biomes_count,
                "flagship_studies": flagship_studies,
                "related_studies": related_studies,
                "related_genome_catalogues": related_genome_catalogues,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        super_study_id = d.pop("super_study_id")

        title = d.pop("title")

        url_slug = d.pop("url_slug")

        url = d.pop("url")

        image_url = d.pop("image_url")

        biomes = d.pop("biomes")

        biomes_count = d.pop("biomes_count")

        flagship_studies = d.pop("flagship_studies")

        related_studies = d.pop("related_studies")

        related_genome_catalogues = d.pop("related_genome_catalogues")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        super_study = cls(
            super_study_id=super_study_id,
            title=title,
            url_slug=url_slug,
            url=url,
            image_url=image_url,
            biomes=biomes,
            biomes_count=biomes_count,
            flagship_studies=flagship_studies,
            related_studies=related_studies,
            related_genome_catalogues=related_genome_catalogues,
            description=description,
        )

        super_study.additional_properties = d
        return super_study

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
