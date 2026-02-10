from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.biome import Biome


T = TypeVar("T", bound="MGnifyStudy")


@_attrs_define
class MGnifyStudy:
    """
    Attributes:
        accession (str):
        ena_accessions (list[str]):
        title (str):
        biome (Biome | None):
        updated_at (datetime.datetime):
    """

    accession: str
    ena_accessions: list[str]
    title: str
    biome: Biome | None
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.biome import Biome

        accession = self.accession

        ena_accessions = self.ena_accessions

        title = self.title

        biome: dict[str, Any] | None
        if isinstance(self.biome, Biome):
            biome = self.biome.to_dict()
        else:
            biome = self.biome

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accession": accession,
                "ena_accessions": ena_accessions,
                "title": title,
                "biome": biome,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.biome import Biome

        d = dict(src_dict)
        accession = d.pop("accession")

        ena_accessions = cast(list[str], d.pop("ena_accessions"))

        title = d.pop("title")

        def _parse_biome(data: object) -> Biome | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                biome_type_0 = Biome.from_dict(data)

                return biome_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Biome | None, data)

        biome = _parse_biome(d.pop("biome"))

        updated_at = isoparse(d.pop("updated_at"))

        m_gnify_study = cls(
            accession=accession,
            ena_accessions=ena_accessions,
            title=title,
            biome=biome,
            updated_at=updated_at,
        )

        m_gnify_study.additional_properties = d
        return m_gnify_study

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
