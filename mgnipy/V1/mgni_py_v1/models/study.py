from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import (
    UNSET,
    Unset,
)

T = TypeVar("T", bound="Study")


@_attrs_define
class Study:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            url (str):
            bioproject (str):
            samples_count (int):
            downloads (str):
            publications (str):
            geocoordinates (str):
            analyses (str):
            samples (str):
            accession (str):
            biomes (str):
            last_update (datetime.datetime):
            secondary_accession (str):
            is_private (bool | Unset):
            centre_name (None | str | Unset):
            public_release_date (datetime.date | None | Unset):
            study_abstract (None | str | Unset):
            study_name (None | str | Unset):
            data_origination (None | str | Unset):
    """

    url: str
    bioproject: str
    samples_count: int
    downloads: str
    publications: str
    geocoordinates: str
    analyses: str
    samples: str
    accession: str
    biomes: str
    last_update: datetime.datetime
    secondary_accession: str
    is_private: bool | Unset = UNSET
    centre_name: None | str | Unset = UNSET
    public_release_date: datetime.date | None | Unset = UNSET
    study_abstract: None | str | Unset = UNSET
    study_name: None | str | Unset = UNSET
    data_origination: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        bioproject = self.bioproject

        samples_count = self.samples_count

        downloads = self.downloads

        publications = self.publications

        geocoordinates = self.geocoordinates

        analyses = self.analyses

        samples = self.samples

        accession = self.accession

        biomes = self.biomes

        last_update = self.last_update.isoformat()

        secondary_accession = self.secondary_accession

        is_private = self.is_private

        centre_name: None | str | Unset
        if isinstance(self.centre_name, Unset):
            centre_name = UNSET
        else:
            centre_name = self.centre_name

        public_release_date: None | str | Unset
        if isinstance(self.public_release_date, Unset):
            public_release_date = UNSET
        elif isinstance(self.public_release_date, datetime.date):
            public_release_date = self.public_release_date.isoformat()
        else:
            public_release_date = self.public_release_date

        study_abstract: None | str | Unset
        if isinstance(self.study_abstract, Unset):
            study_abstract = UNSET
        else:
            study_abstract = self.study_abstract

        study_name: None | str | Unset
        if isinstance(self.study_name, Unset):
            study_name = UNSET
        else:
            study_name = self.study_name

        data_origination: None | str | Unset
        if isinstance(self.data_origination, Unset):
            data_origination = UNSET
        else:
            data_origination = self.data_origination

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "bioproject": bioproject,
                "samples_count": samples_count,
                "downloads": downloads,
                "publications": publications,
                "geocoordinates": geocoordinates,
                "analyses": analyses,
                "samples": samples,
                "accession": accession,
                "biomes": biomes,
                "last_update": last_update,
                "secondary_accession": secondary_accession,
            }
        )
        if is_private is not UNSET:
            field_dict["is_private"] = is_private
        if centre_name is not UNSET:
            field_dict["centre_name"] = centre_name
        if public_release_date is not UNSET:
            field_dict["public_release_date"] = public_release_date
        if study_abstract is not UNSET:
            field_dict["study_abstract"] = study_abstract
        if study_name is not UNSET:
            field_dict["study_name"] = study_name
        if data_origination is not UNSET:
            field_dict["data_origination"] = data_origination

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        bioproject = d.pop("bioproject")

        samples_count = d.pop("samples_count")

        downloads = d.pop("downloads")

        publications = d.pop("publications")

        geocoordinates = d.pop("geocoordinates")

        analyses = d.pop("analyses")

        samples = d.pop("samples")

        accession = d.pop("accession")

        biomes = d.pop("biomes")

        last_update = isoparse(d.pop("last_update"))

        secondary_accession = d.pop("secondary_accession")

        is_private = d.pop("is_private", UNSET)

        def _parse_centre_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        centre_name = _parse_centre_name(d.pop("centre_name", UNSET))

        def _parse_public_release_date(data: object) -> datetime.date | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                public_release_date_type_0 = isoparse(data).date()

                return public_release_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.date | None | Unset, data)

        public_release_date = _parse_public_release_date(
            d.pop("public_release_date", UNSET)
        )

        def _parse_study_abstract(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        study_abstract = _parse_study_abstract(d.pop("study_abstract", UNSET))

        def _parse_study_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        study_name = _parse_study_name(d.pop("study_name", UNSET))

        def _parse_data_origination(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        data_origination = _parse_data_origination(d.pop("data_origination", UNSET))

        study = cls(
            url=url,
            bioproject=bioproject,
            samples_count=samples_count,
            downloads=downloads,
            publications=publications,
            geocoordinates=geocoordinates,
            analyses=analyses,
            samples=samples,
            accession=accession,
            biomes=biomes,
            last_update=last_update,
            secondary_accession=secondary_accession,
            is_private=is_private,
            centre_name=centre_name,
            public_release_date=public_release_date,
            study_abstract=study_abstract,
            study_name=study_name,
            data_origination=data_origination,
        )

        study.additional_properties = d
        return study

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
