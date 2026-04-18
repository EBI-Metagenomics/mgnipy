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

from ..types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.genome_schema import GenomeSchema


T = TypeVar("T", bound="GenomeAssemblyLinkSchema")


@_attrs_define
class GenomeAssemblyLinkSchema:
    """
    Attributes:
        genome (GenomeSchema): Simple schema for a Genome model.
        updated_at (datetime.datetime | None):
        species_rep (None | str | Unset): Deposition database accession for species representative
        mag_accession (None | str | Unset): Deposition database for MAG
    """

    genome: GenomeSchema
    updated_at: datetime.datetime | None
    species_rep: None | str | Unset = UNSET
    mag_accession: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        genome = self.genome.to_dict()

        updated_at: None | str
        if isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        species_rep: None | str | Unset
        if isinstance(self.species_rep, Unset):
            species_rep = UNSET
        else:
            species_rep = self.species_rep

        mag_accession: None | str | Unset
        if isinstance(self.mag_accession, Unset):
            mag_accession = UNSET
        else:
            mag_accession = self.mag_accession

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "genome": genome,
                "updated_at": updated_at,
            }
        )
        if species_rep is not UNSET:
            field_dict["species_rep"] = species_rep
        if mag_accession is not UNSET:
            field_dict["mag_accession"] = mag_accession

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.genome_schema import GenomeSchema

        d = dict(src_dict)
        genome = GenomeSchema.from_dict(d.pop("genome"))

        def _parse_updated_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        updated_at = _parse_updated_at(d.pop("updated_at"))

        def _parse_species_rep(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        species_rep = _parse_species_rep(d.pop("species_rep", UNSET))

        def _parse_mag_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mag_accession = _parse_mag_accession(d.pop("mag_accession", UNSET))

        genome_assembly_link_schema = cls(
            genome=genome,
            updated_at=updated_at,
            species_rep=species_rep,
            mag_accession=mag_accession,
        )

        genome_assembly_link_schema.additional_properties = d
        return genome_assembly_link_schema

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
