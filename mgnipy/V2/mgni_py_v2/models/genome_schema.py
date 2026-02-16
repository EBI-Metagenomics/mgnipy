from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..._mgnipy_models.types import (
    UNSET,
    Unset,
)

T = TypeVar("T", bound="GenomeSchema")


@_attrs_define
class GenomeSchema:
    """Simple schema for a Genome model.

    Attributes:
        accession (str):
        catalogue_id (None | str):
        taxon_lineage (None | str):
        ena_genome_accession (None | str):
        catalogue_version (None | str | Unset): Version of the genome catalogue
    """

    accession: str
    catalogue_id: None | str
    taxon_lineage: None | str
    ena_genome_accession: None | str
    catalogue_version: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accession = self.accession

        catalogue_id: None | str
        catalogue_id = self.catalogue_id

        taxon_lineage: None | str
        taxon_lineage = self.taxon_lineage

        ena_genome_accession: None | str
        ena_genome_accession = self.ena_genome_accession

        catalogue_version: None | str | Unset
        if isinstance(self.catalogue_version, Unset):
            catalogue_version = UNSET
        else:
            catalogue_version = self.catalogue_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accession": accession,
                "catalogue_id": catalogue_id,
                "taxon_lineage": taxon_lineage,
                "ena_genome_accession": ena_genome_accession,
            }
        )
        if catalogue_version is not UNSET:
            field_dict["catalogue_version"] = catalogue_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        accession = d.pop("accession")

        def _parse_catalogue_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        catalogue_id = _parse_catalogue_id(d.pop("catalogue_id"))

        def _parse_taxon_lineage(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        taxon_lineage = _parse_taxon_lineage(d.pop("taxon_lineage"))

        def _parse_ena_genome_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        ena_genome_accession = _parse_ena_genome_accession(
            d.pop("ena_genome_accession")
        )

        def _parse_catalogue_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        catalogue_version = _parse_catalogue_version(d.pop("catalogue_version", UNSET))

        genome_schema = cls(
            accession=accession,
            catalogue_id=catalogue_id,
            taxon_lineage=taxon_lineage,
            ena_genome_accession=ena_genome_accession,
            catalogue_version=catalogue_version,
        )

        genome_schema.additional_properties = d
        return genome_schema

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
