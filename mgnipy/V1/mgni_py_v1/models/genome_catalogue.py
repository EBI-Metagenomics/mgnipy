from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.catalogue_type_enum import CatalogueTypeEnum
from ..types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.genome_catalogue_other_stats_type_0 import (
        GenomeCatalogueOtherStatsType0,
    )


T = TypeVar("T", bound="GenomeCatalogue")


@_attrs_define
class GenomeCatalogue:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            url (str):
            name (str):
            biome (str):
            genomes (str):
            downloads (str):
            genome_count (int):
            version (str):
            catalogue_type (CatalogueTypeEnum): * `prokaryotes` - prokaryotes
                * `eukaryotes` - eukaryotes
                * `viruses` - viruses
            catalogue_biome_label (str): The biome label for the catalogue (and any others that share the same practical
                biome). Need not be a GOLD biome, e.g. may include host species.
            description (None | str | Unset): Use <a href="https://commonmark.org/help/" target="_newtab">markdown</a> for
                links and rich text.
            protein_catalogue_name (None | str | Unset):
            protein_catalogue_description (None | str | Unset): Use <a href="https://commonmark.org/help/"
                target="_newtab">markdown</a> for links and rich text.
            unclustered_genome_count (int | None | Unset): Total number of genomes in the catalogue (including cluster reps
                and members)
            last_update (datetime.datetime | Unset):
            pipeline_version_tag (str | Unset):
            ftp_url (str | Unset):
            other_stats (GenomeCatalogueOtherStatsType0 | None | Unset):
    """

    url: str
    name: str
    biome: str
    genomes: str
    downloads: str
    genome_count: int
    version: str
    catalogue_type: CatalogueTypeEnum
    catalogue_biome_label: str
    description: None | str | Unset = UNSET
    protein_catalogue_name: None | str | Unset = UNSET
    protein_catalogue_description: None | str | Unset = UNSET
    unclustered_genome_count: int | None | Unset = UNSET
    last_update: datetime.datetime | Unset = UNSET
    pipeline_version_tag: str | Unset = UNSET
    ftp_url: str | Unset = UNSET
    other_stats: GenomeCatalogueOtherStatsType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.genome_catalogue_other_stats_type_0 import (
            GenomeCatalogueOtherStatsType0,
        )

        url = self.url

        name = self.name

        biome = self.biome

        genomes = self.genomes

        downloads = self.downloads

        genome_count = self.genome_count

        version = self.version

        catalogue_type = self.catalogue_type.value

        catalogue_biome_label = self.catalogue_biome_label

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        protein_catalogue_name: None | str | Unset
        if isinstance(self.protein_catalogue_name, Unset):
            protein_catalogue_name = UNSET
        else:
            protein_catalogue_name = self.protein_catalogue_name

        protein_catalogue_description: None | str | Unset
        if isinstance(self.protein_catalogue_description, Unset):
            protein_catalogue_description = UNSET
        else:
            protein_catalogue_description = self.protein_catalogue_description

        unclustered_genome_count: int | None | Unset
        if isinstance(self.unclustered_genome_count, Unset):
            unclustered_genome_count = UNSET
        else:
            unclustered_genome_count = self.unclustered_genome_count

        last_update: str | Unset = UNSET
        if not isinstance(self.last_update, Unset):
            last_update = self.last_update.isoformat()

        pipeline_version_tag = self.pipeline_version_tag

        ftp_url = self.ftp_url

        other_stats: dict[str, Any] | None | Unset
        if isinstance(self.other_stats, Unset):
            other_stats = UNSET
        elif isinstance(self.other_stats, GenomeCatalogueOtherStatsType0):
            other_stats = self.other_stats.to_dict()
        else:
            other_stats = self.other_stats

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "name": name,
                "biome": biome,
                "genomes": genomes,
                "downloads": downloads,
                "genome_count": genome_count,
                "version": version,
                "catalogue_type": catalogue_type,
                "catalogue_biome_label": catalogue_biome_label,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if protein_catalogue_name is not UNSET:
            field_dict["protein_catalogue_name"] = protein_catalogue_name
        if protein_catalogue_description is not UNSET:
            field_dict["protein_catalogue_description"] = protein_catalogue_description
        if unclustered_genome_count is not UNSET:
            field_dict["unclustered_genome_count"] = unclustered_genome_count
        if last_update is not UNSET:
            field_dict["last_update"] = last_update
        if pipeline_version_tag is not UNSET:
            field_dict["pipeline_version_tag"] = pipeline_version_tag
        if ftp_url is not UNSET:
            field_dict["ftp_url"] = ftp_url
        if other_stats is not UNSET:
            field_dict["other_stats"] = other_stats

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.genome_catalogue_other_stats_type_0 import (
            GenomeCatalogueOtherStatsType0,
        )

        d = dict(src_dict)
        url = d.pop("url")

        name = d.pop("name")

        biome = d.pop("biome")

        genomes = d.pop("genomes")

        downloads = d.pop("downloads")

        genome_count = d.pop("genome_count")

        version = d.pop("version")

        catalogue_type = CatalogueTypeEnum(d.pop("catalogue_type"))

        catalogue_biome_label = d.pop("catalogue_biome_label")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_protein_catalogue_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        protein_catalogue_name = _parse_protein_catalogue_name(
            d.pop("protein_catalogue_name", UNSET)
        )

        def _parse_protein_catalogue_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        protein_catalogue_description = _parse_protein_catalogue_description(
            d.pop("protein_catalogue_description", UNSET)
        )

        def _parse_unclustered_genome_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        unclustered_genome_count = _parse_unclustered_genome_count(
            d.pop("unclustered_genome_count", UNSET)
        )

        _last_update = d.pop("last_update", UNSET)
        last_update: datetime.datetime | Unset
        if isinstance(_last_update, Unset):
            last_update = UNSET
        else:
            last_update = isoparse(_last_update)

        pipeline_version_tag = d.pop("pipeline_version_tag", UNSET)

        ftp_url = d.pop("ftp_url", UNSET)

        def _parse_other_stats(
            data: object,
        ) -> GenomeCatalogueOtherStatsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                other_stats_type_0 = GenomeCatalogueOtherStatsType0.from_dict(data)

                return other_stats_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GenomeCatalogueOtherStatsType0 | None | Unset, data)

        other_stats = _parse_other_stats(d.pop("other_stats", UNSET))

        genome_catalogue = cls(
            url=url,
            name=name,
            biome=biome,
            genomes=genomes,
            downloads=downloads,
            genome_count=genome_count,
            version=version,
            catalogue_type=catalogue_type,
            catalogue_biome_label=catalogue_biome_label,
            description=description,
            protein_catalogue_name=protein_catalogue_name,
            protein_catalogue_description=protein_catalogue_description,
            unclustered_genome_count=unclustered_genome_count,
            last_update=last_update,
            pipeline_version_tag=pipeline_version_tag,
            ftp_url=ftp_url,
            other_stats=other_stats,
        )

        genome_catalogue.additional_properties = d
        return genome_catalogue

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
