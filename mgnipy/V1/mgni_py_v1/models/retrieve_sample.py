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

T = TypeVar("T", bound="RetrieveSample")


@_attrs_define
class RetrieveSample:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            url (str):
            biome (str):
            biosample (str):
            longitude (float):
            sample_metadata (list[Any]):
            studies (str):
            latitude (float):
            runs (str):
            accession (str): Secondary accession
            last_update (datetime.datetime):
            analysis_completed (datetime.date | None | Unset):
            collection_date (datetime.date | None | Unset): Collection date
            geo_loc_name (None | str | Unset): Name of geographical location
            sample_desc (None | str | Unset): Sample description
            environment_biome (None | str | Unset): Environment biome
            environment_feature (None | str | Unset): Environment feature
            environment_material (None | str | Unset): Environment material
            sample_name (None | str | Unset): Sample name
            sample_alias (None | str | Unset): Sample alias
            host_tax_id (int | None | Unset): Sample host tax id
            species (None | str | Unset): Species
    """

    url: str
    biome: str
    biosample: str
    longitude: float
    sample_metadata: list[Any]
    studies: str
    latitude: float
    runs: str
    accession: str
    last_update: datetime.datetime
    analysis_completed: datetime.date | None | Unset = UNSET
    collection_date: datetime.date | None | Unset = UNSET
    geo_loc_name: None | str | Unset = UNSET
    sample_desc: None | str | Unset = UNSET
    environment_biome: None | str | Unset = UNSET
    environment_feature: None | str | Unset = UNSET
    environment_material: None | str | Unset = UNSET
    sample_name: None | str | Unset = UNSET
    sample_alias: None | str | Unset = UNSET
    host_tax_id: int | None | Unset = UNSET
    species: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        biome = self.biome

        biosample = self.biosample

        longitude = self.longitude

        sample_metadata = self.sample_metadata

        studies = self.studies

        latitude = self.latitude

        runs = self.runs

        accession = self.accession

        last_update = self.last_update.isoformat()

        analysis_completed: None | str | Unset
        if isinstance(self.analysis_completed, Unset):
            analysis_completed = UNSET
        elif isinstance(self.analysis_completed, datetime.date):
            analysis_completed = self.analysis_completed.isoformat()
        else:
            analysis_completed = self.analysis_completed

        collection_date: None | str | Unset
        if isinstance(self.collection_date, Unset):
            collection_date = UNSET
        elif isinstance(self.collection_date, datetime.date):
            collection_date = self.collection_date.isoformat()
        else:
            collection_date = self.collection_date

        geo_loc_name: None | str | Unset
        if isinstance(self.geo_loc_name, Unset):
            geo_loc_name = UNSET
        else:
            geo_loc_name = self.geo_loc_name

        sample_desc: None | str | Unset
        if isinstance(self.sample_desc, Unset):
            sample_desc = UNSET
        else:
            sample_desc = self.sample_desc

        environment_biome: None | str | Unset
        if isinstance(self.environment_biome, Unset):
            environment_biome = UNSET
        else:
            environment_biome = self.environment_biome

        environment_feature: None | str | Unset
        if isinstance(self.environment_feature, Unset):
            environment_feature = UNSET
        else:
            environment_feature = self.environment_feature

        environment_material: None | str | Unset
        if isinstance(self.environment_material, Unset):
            environment_material = UNSET
        else:
            environment_material = self.environment_material

        sample_name: None | str | Unset
        if isinstance(self.sample_name, Unset):
            sample_name = UNSET
        else:
            sample_name = self.sample_name

        sample_alias: None | str | Unset
        if isinstance(self.sample_alias, Unset):
            sample_alias = UNSET
        else:
            sample_alias = self.sample_alias

        host_tax_id: int | None | Unset
        if isinstance(self.host_tax_id, Unset):
            host_tax_id = UNSET
        else:
            host_tax_id = self.host_tax_id

        species: None | str | Unset
        if isinstance(self.species, Unset):
            species = UNSET
        else:
            species = self.species

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "biome": biome,
                "biosample": biosample,
                "longitude": longitude,
                "sample_metadata": sample_metadata,
                "studies": studies,
                "latitude": latitude,
                "runs": runs,
                "accession": accession,
                "last_update": last_update,
            }
        )
        if analysis_completed is not UNSET:
            field_dict["analysis_completed"] = analysis_completed
        if collection_date is not UNSET:
            field_dict["collection_date"] = collection_date
        if geo_loc_name is not UNSET:
            field_dict["geo_loc_name"] = geo_loc_name
        if sample_desc is not UNSET:
            field_dict["sample_desc"] = sample_desc
        if environment_biome is not UNSET:
            field_dict["environment_biome"] = environment_biome
        if environment_feature is not UNSET:
            field_dict["environment_feature"] = environment_feature
        if environment_material is not UNSET:
            field_dict["environment_material"] = environment_material
        if sample_name is not UNSET:
            field_dict["sample_name"] = sample_name
        if sample_alias is not UNSET:
            field_dict["sample_alias"] = sample_alias
        if host_tax_id is not UNSET:
            field_dict["host_tax_id"] = host_tax_id
        if species is not UNSET:
            field_dict["species"] = species

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        biome = d.pop("biome")

        biosample = d.pop("biosample")

        longitude = d.pop("longitude")

        sample_metadata = cast(list[Any], d.pop("sample_metadata"))

        studies = d.pop("studies")

        latitude = d.pop("latitude")

        runs = d.pop("runs")

        accession = d.pop("accession")

        last_update = isoparse(d.pop("last_update"))

        def _parse_analysis_completed(data: object) -> datetime.date | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                analysis_completed_type_0 = isoparse(data).date()

                return analysis_completed_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.date | None | Unset, data)

        analysis_completed = _parse_analysis_completed(
            d.pop("analysis_completed", UNSET)
        )

        def _parse_collection_date(data: object) -> datetime.date | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                collection_date_type_0 = isoparse(data).date()

                return collection_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.date | None | Unset, data)

        collection_date = _parse_collection_date(d.pop("collection_date", UNSET))

        def _parse_geo_loc_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        geo_loc_name = _parse_geo_loc_name(d.pop("geo_loc_name", UNSET))

        def _parse_sample_desc(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sample_desc = _parse_sample_desc(d.pop("sample_desc", UNSET))

        def _parse_environment_biome(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        environment_biome = _parse_environment_biome(d.pop("environment_biome", UNSET))

        def _parse_environment_feature(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        environment_feature = _parse_environment_feature(
            d.pop("environment_feature", UNSET)
        )

        def _parse_environment_material(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        environment_material = _parse_environment_material(
            d.pop("environment_material", UNSET)
        )

        def _parse_sample_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sample_name = _parse_sample_name(d.pop("sample_name", UNSET))

        def _parse_sample_alias(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sample_alias = _parse_sample_alias(d.pop("sample_alias", UNSET))

        def _parse_host_tax_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        host_tax_id = _parse_host_tax_id(d.pop("host_tax_id", UNSET))

        def _parse_species(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        species = _parse_species(d.pop("species", UNSET))

        retrieve_sample = cls(
            url=url,
            biome=biome,
            biosample=biosample,
            longitude=longitude,
            sample_metadata=sample_metadata,
            studies=studies,
            latitude=latitude,
            runs=runs,
            accession=accession,
            last_update=last_update,
            analysis_completed=analysis_completed,
            collection_date=collection_date,
            geo_loc_name=geo_loc_name,
            sample_desc=sample_desc,
            environment_biome=environment_biome,
            environment_feature=environment_feature,
            environment_material=environment_material,
            sample_name=sample_name,
            sample_alias=sample_alias,
            host_tax_id=host_tax_id,
            species=species,
        )

        retrieve_sample.additional_properties = d
        return retrieve_sample

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
