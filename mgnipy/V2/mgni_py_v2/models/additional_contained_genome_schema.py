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

from ..._models_v2.types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.genome_schema import GenomeSchema


T = TypeVar("T", bound="AdditionalContainedGenomeSchema")


@_attrs_define
class AdditionalContainedGenomeSchema:
    """
    Attributes:
        genome (GenomeSchema): Simple schema for a Genome model.
        updated_at (datetime.datetime | None):
        run_accession (None | str | Unset): ENA accession of the run that produced this assembly
        containment (float | None | Unset): Containment score for the genome within the assembly
        cani (float | None | Unset): Containment Average Nucleotide Identity (cANI)
    """

    genome: GenomeSchema
    updated_at: datetime.datetime | None
    run_accession: None | str | Unset = UNSET
    containment: float | None | Unset = UNSET
    cani: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        genome = self.genome.to_dict()

        updated_at: None | str
        if isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        run_accession: None | str | Unset
        if isinstance(self.run_accession, Unset):
            run_accession = UNSET
        else:
            run_accession = self.run_accession

        containment: float | None | Unset
        if isinstance(self.containment, Unset):
            containment = UNSET
        else:
            containment = self.containment

        cani: float | None | Unset
        if isinstance(self.cani, Unset):
            cani = UNSET
        else:
            cani = self.cani

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "genome": genome,
                "updated_at": updated_at,
            }
        )
        if run_accession is not UNSET:
            field_dict["run_accession"] = run_accession
        if containment is not UNSET:
            field_dict["containment"] = containment
        if cani is not UNSET:
            field_dict["cani"] = cani

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

        def _parse_run_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        run_accession = _parse_run_accession(d.pop("run_accession", UNSET))

        def _parse_containment(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        containment = _parse_containment(d.pop("containment", UNSET))

        def _parse_cani(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        cani = _parse_cani(d.pop("cani", UNSET))

        additional_contained_genome_schema = cls(
            genome=genome,
            updated_at=updated_at,
            run_accession=run_accession,
            containment=containment,
            cani=cani,
        )

        additional_contained_genome_schema.additional_properties = d
        return additional_contained_genome_schema

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
