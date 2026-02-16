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

from ..models.genome_catalogue_base_catalogue_type import (
    GenomeCatalogueBaseCatalogueType,
)
from ..._models_v2.types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.biome import Biome
    from ..models.genome_catalogue_base_other_stats_type_0 import (
        GenomeCatalogueBaseOtherStatsType0,
    )


T = TypeVar("T", bound="GenomeCatalogueBase")


@_attrs_define
class GenomeCatalogueBase:
    """
    Attributes:
        catalogue_id (str):
        version (str):
        name (str):
        description (None | str):
        protein_catalogue_description (None | str):
        updated_at (datetime.datetime):
        result_directory (None | str):
        unclustered_genome_count (int | None): Total number of genomes in the catalogue, including non-cluster-
            representatives not available via this API.
        ftp_url (str):
        pipeline_version_tag (str):
        catalogue_biome_label (str):
        catalogue_type (GenomeCatalogueBaseCatalogueType):
        other_stats (GenomeCatalogueBaseOtherStatsType0 | None):
        protein_catalogue_name (None | str | Unset):
        genome_count (int | None | Unset):
        biome (Biome | None | Unset):
    """

    catalogue_id: str
    version: str
    name: str
    description: None | str
    protein_catalogue_description: None | str
    updated_at: datetime.datetime
    result_directory: None | str
    unclustered_genome_count: int | None
    ftp_url: str
    pipeline_version_tag: str
    catalogue_biome_label: str
    catalogue_type: GenomeCatalogueBaseCatalogueType
    other_stats: GenomeCatalogueBaseOtherStatsType0 | None
    protein_catalogue_name: None | str | Unset = UNSET
    genome_count: int | None | Unset = UNSET
    biome: Biome | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.biome import Biome
        from ..models.genome_catalogue_base_other_stats_type_0 import (
            GenomeCatalogueBaseOtherStatsType0,
        )

        catalogue_id = self.catalogue_id

        version = self.version

        name = self.name

        description: None | str
        description = self.description

        protein_catalogue_description: None | str
        protein_catalogue_description = self.protein_catalogue_description

        updated_at = self.updated_at.isoformat()

        result_directory: None | str
        result_directory = self.result_directory

        unclustered_genome_count: int | None
        unclustered_genome_count = self.unclustered_genome_count

        ftp_url = self.ftp_url

        pipeline_version_tag = self.pipeline_version_tag

        catalogue_biome_label = self.catalogue_biome_label

        catalogue_type = self.catalogue_type.value

        other_stats: dict[str, Any] | None
        if isinstance(self.other_stats, GenomeCatalogueBaseOtherStatsType0):
            other_stats = self.other_stats.to_dict()
        else:
            other_stats = self.other_stats

        protein_catalogue_name: None | str | Unset
        if isinstance(self.protein_catalogue_name, Unset):
            protein_catalogue_name = UNSET
        else:
            protein_catalogue_name = self.protein_catalogue_name

        genome_count: int | None | Unset
        if isinstance(self.genome_count, Unset):
            genome_count = UNSET
        else:
            genome_count = self.genome_count

        biome: dict[str, Any] | None | Unset
        if isinstance(self.biome, Unset):
            biome = UNSET
        elif isinstance(self.biome, Biome):
            biome = self.biome.to_dict()
        else:
            biome = self.biome

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "catalogue_id": catalogue_id,
                "version": version,
                "name": name,
                "description": description,
                "protein_catalogue_description": protein_catalogue_description,
                "updated_at": updated_at,
                "result_directory": result_directory,
                "unclustered_genome_count": unclustered_genome_count,
                "ftp_url": ftp_url,
                "pipeline_version_tag": pipeline_version_tag,
                "catalogue_biome_label": catalogue_biome_label,
                "catalogue_type": catalogue_type,
                "other_stats": other_stats,
            }
        )
        if protein_catalogue_name is not UNSET:
            field_dict["protein_catalogue_name"] = protein_catalogue_name
        if genome_count is not UNSET:
            field_dict["genome_count"] = genome_count
        if biome is not UNSET:
            field_dict["biome"] = biome

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.biome import Biome
        from ..models.genome_catalogue_base_other_stats_type_0 import (
            GenomeCatalogueBaseOtherStatsType0,
        )

        d = dict(src_dict)
        catalogue_id = d.pop("catalogue_id")

        version = d.pop("version")

        name = d.pop("name")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        def _parse_protein_catalogue_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        protein_catalogue_description = _parse_protein_catalogue_description(
            d.pop("protein_catalogue_description")
        )

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_result_directory(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        result_directory = _parse_result_directory(d.pop("result_directory"))

        def _parse_unclustered_genome_count(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        unclustered_genome_count = _parse_unclustered_genome_count(
            d.pop("unclustered_genome_count")
        )

        ftp_url = d.pop("ftp_url")

        pipeline_version_tag = d.pop("pipeline_version_tag")

        catalogue_biome_label = d.pop("catalogue_biome_label")

        catalogue_type = GenomeCatalogueBaseCatalogueType(d.pop("catalogue_type"))

        def _parse_other_stats(
            data: object,
        ) -> GenomeCatalogueBaseOtherStatsType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                other_stats_type_0 = GenomeCatalogueBaseOtherStatsType0.from_dict(data)

                return other_stats_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GenomeCatalogueBaseOtherStatsType0 | None, data)

        other_stats = _parse_other_stats(d.pop("other_stats"))

        def _parse_protein_catalogue_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        protein_catalogue_name = _parse_protein_catalogue_name(
            d.pop("protein_catalogue_name", UNSET)
        )

        def _parse_genome_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        genome_count = _parse_genome_count(d.pop("genome_count", UNSET))

        def _parse_biome(data: object) -> Biome | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                biome_type_0 = Biome.from_dict(data)

                return biome_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Biome | None | Unset, data)

        biome = _parse_biome(d.pop("biome", UNSET))

        genome_catalogue_base = cls(
            catalogue_id=catalogue_id,
            version=version,
            name=name,
            description=description,
            protein_catalogue_description=protein_catalogue_description,
            updated_at=updated_at,
            result_directory=result_directory,
            unclustered_genome_count=unclustered_genome_count,
            ftp_url=ftp_url,
            pipeline_version_tag=pipeline_version_tag,
            catalogue_biome_label=catalogue_biome_label,
            catalogue_type=catalogue_type,
            other_stats=other_stats,
            protein_catalogue_name=protein_catalogue_name,
            genome_count=genome_count,
            biome=biome,
        )

        genome_catalogue_base.additional_properties = d
        return genome_catalogue_base

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
