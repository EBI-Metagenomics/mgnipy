from __future__ import annotations

from collections.abc import Mapping
from typing import (
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

T = TypeVar("T", bound="Publication")


@_attrs_define
class Publication:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            url (str):
            pub_title (str): Publication title
            studies_count (int):
            samples_count (int):
            studies (str):
            samples (str):
            pubmed_id (int | None | Unset): Pubmed ID
            pubmed_central_id (int | None | Unset): Pubmed Central Identifier
            pub_abstract (None | str | Unset): Publication abstract
            authors (None | str | Unset): Publication authors
            doi (None | str | Unset): DOI
            isbn (None | str | Unset): ISBN
            published_year (int | None | Unset): Published year
            pub_type (None | str | Unset):
            issue (None | str | Unset): Publication issue
            volume (None | str | Unset): Publication volume
            raw_pages (None | str | Unset):
            iso_journal (None | str | Unset): ISO journal
            medline_journal (None | str | Unset):
            pub_url (None | str | Unset): Publication url
    """

    url: str
    pub_title: str
    studies_count: int
    samples_count: int
    studies: str
    samples: str
    pubmed_id: int | None | Unset = UNSET
    pubmed_central_id: int | None | Unset = UNSET
    pub_abstract: None | str | Unset = UNSET
    authors: None | str | Unset = UNSET
    doi: None | str | Unset = UNSET
    isbn: None | str | Unset = UNSET
    published_year: int | None | Unset = UNSET
    pub_type: None | str | Unset = UNSET
    issue: None | str | Unset = UNSET
    volume: None | str | Unset = UNSET
    raw_pages: None | str | Unset = UNSET
    iso_journal: None | str | Unset = UNSET
    medline_journal: None | str | Unset = UNSET
    pub_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        pub_title = self.pub_title

        studies_count = self.studies_count

        samples_count = self.samples_count

        studies = self.studies

        samples = self.samples

        pubmed_id: int | None | Unset
        if isinstance(self.pubmed_id, Unset):
            pubmed_id = UNSET
        else:
            pubmed_id = self.pubmed_id

        pubmed_central_id: int | None | Unset
        if isinstance(self.pubmed_central_id, Unset):
            pubmed_central_id = UNSET
        else:
            pubmed_central_id = self.pubmed_central_id

        pub_abstract: None | str | Unset
        if isinstance(self.pub_abstract, Unset):
            pub_abstract = UNSET
        else:
            pub_abstract = self.pub_abstract

        authors: None | str | Unset
        if isinstance(self.authors, Unset):
            authors = UNSET
        else:
            authors = self.authors

        doi: None | str | Unset
        if isinstance(self.doi, Unset):
            doi = UNSET
        else:
            doi = self.doi

        isbn: None | str | Unset
        if isinstance(self.isbn, Unset):
            isbn = UNSET
        else:
            isbn = self.isbn

        published_year: int | None | Unset
        if isinstance(self.published_year, Unset):
            published_year = UNSET
        else:
            published_year = self.published_year

        pub_type: None | str | Unset
        if isinstance(self.pub_type, Unset):
            pub_type = UNSET
        else:
            pub_type = self.pub_type

        issue: None | str | Unset
        if isinstance(self.issue, Unset):
            issue = UNSET
        else:
            issue = self.issue

        volume: None | str | Unset
        if isinstance(self.volume, Unset):
            volume = UNSET
        else:
            volume = self.volume

        raw_pages: None | str | Unset
        if isinstance(self.raw_pages, Unset):
            raw_pages = UNSET
        else:
            raw_pages = self.raw_pages

        iso_journal: None | str | Unset
        if isinstance(self.iso_journal, Unset):
            iso_journal = UNSET
        else:
            iso_journal = self.iso_journal

        medline_journal: None | str | Unset
        if isinstance(self.medline_journal, Unset):
            medline_journal = UNSET
        else:
            medline_journal = self.medline_journal

        pub_url: None | str | Unset
        if isinstance(self.pub_url, Unset):
            pub_url = UNSET
        else:
            pub_url = self.pub_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "pub_title": pub_title,
                "studies_count": studies_count,
                "samples_count": samples_count,
                "studies": studies,
                "samples": samples,
            }
        )
        if pubmed_id is not UNSET:
            field_dict["pubmed_id"] = pubmed_id
        if pubmed_central_id is not UNSET:
            field_dict["pubmed_central_id"] = pubmed_central_id
        if pub_abstract is not UNSET:
            field_dict["pub_abstract"] = pub_abstract
        if authors is not UNSET:
            field_dict["authors"] = authors
        if doi is not UNSET:
            field_dict["doi"] = doi
        if isbn is not UNSET:
            field_dict["isbn"] = isbn
        if published_year is not UNSET:
            field_dict["published_year"] = published_year
        if pub_type is not UNSET:
            field_dict["pub_type"] = pub_type
        if issue is not UNSET:
            field_dict["issue"] = issue
        if volume is not UNSET:
            field_dict["volume"] = volume
        if raw_pages is not UNSET:
            field_dict["raw_pages"] = raw_pages
        if iso_journal is not UNSET:
            field_dict["iso_journal"] = iso_journal
        if medline_journal is not UNSET:
            field_dict["medline_journal"] = medline_journal
        if pub_url is not UNSET:
            field_dict["pub_url"] = pub_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        pub_title = d.pop("pub_title")

        studies_count = d.pop("studies_count")

        samples_count = d.pop("samples_count")

        studies = d.pop("studies")

        samples = d.pop("samples")

        def _parse_pubmed_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pubmed_id = _parse_pubmed_id(d.pop("pubmed_id", UNSET))

        def _parse_pubmed_central_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pubmed_central_id = _parse_pubmed_central_id(d.pop("pubmed_central_id", UNSET))

        def _parse_pub_abstract(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pub_abstract = _parse_pub_abstract(d.pop("pub_abstract", UNSET))

        def _parse_authors(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        authors = _parse_authors(d.pop("authors", UNSET))

        def _parse_doi(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        doi = _parse_doi(d.pop("doi", UNSET))

        def _parse_isbn(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        isbn = _parse_isbn(d.pop("isbn", UNSET))

        def _parse_published_year(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        published_year = _parse_published_year(d.pop("published_year", UNSET))

        def _parse_pub_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pub_type = _parse_pub_type(d.pop("pub_type", UNSET))

        def _parse_issue(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        issue = _parse_issue(d.pop("issue", UNSET))

        def _parse_volume(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        volume = _parse_volume(d.pop("volume", UNSET))

        def _parse_raw_pages(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        raw_pages = _parse_raw_pages(d.pop("raw_pages", UNSET))

        def _parse_iso_journal(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        iso_journal = _parse_iso_journal(d.pop("iso_journal", UNSET))

        def _parse_medline_journal(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        medline_journal = _parse_medline_journal(d.pop("medline_journal", UNSET))

        def _parse_pub_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pub_url = _parse_pub_url(d.pop("pub_url", UNSET))

        publication = cls(
            url=url,
            pub_title=pub_title,
            studies_count=studies_count,
            samples_count=samples_count,
            studies=studies,
            samples=samples,
            pubmed_id=pubmed_id,
            pubmed_central_id=pubmed_central_id,
            pub_abstract=pub_abstract,
            authors=authors,
            doi=doi,
            isbn=isbn,
            published_year=published_year,
            pub_type=pub_type,
            issue=issue,
            volume=volume,
            raw_pages=raw_pages,
            iso_journal=iso_journal,
            medline_journal=medline_journal,
            pub_url=pub_url,
        )

        publication.additional_properties = d
        return publication

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
