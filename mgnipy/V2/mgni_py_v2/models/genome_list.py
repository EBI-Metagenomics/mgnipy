from __future__ import annotations

from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.genome_type import GenomeType
from ..._models_v2.types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.biome import Biome


T = TypeVar("T", bound="GenomeList")


@_attrs_define
class GenomeList:
    """
    Attributes:
        accession (str):
        ena_genome_accession (None | str):
        ena_sample_accession (None | str):
        ncbi_genome_accession (None | str):
        img_genome_accession (None | str):
        patric_genome_accession (None | str):
        length (int):
        num_contigs (int):
        n_50 (int):
        gc_content (float):
        type_ (GenomeType):
        completeness (float):
        contamination (float):
        catalogue_id (str):
        geographic_origin (None | str):
        geographic_range (list[str] | None | Unset):
        biome (Biome | None | Unset):
    """

    accession: str
    ena_genome_accession: None | str
    ena_sample_accession: None | str
    ncbi_genome_accession: None | str
    img_genome_accession: None | str
    patric_genome_accession: None | str
    length: int
    num_contigs: int
    n_50: int
    gc_content: float
    type_: GenomeType
    completeness: float
    contamination: float
    catalogue_id: str
    geographic_origin: None | str
    geographic_range: list[str] | None | Unset = UNSET
    biome: Biome | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.biome import Biome

        accession = self.accession

        ena_genome_accession: None | str
        ena_genome_accession = self.ena_genome_accession

        ena_sample_accession: None | str
        ena_sample_accession = self.ena_sample_accession

        ncbi_genome_accession: None | str
        ncbi_genome_accession = self.ncbi_genome_accession

        img_genome_accession: None | str
        img_genome_accession = self.img_genome_accession

        patric_genome_accession: None | str
        patric_genome_accession = self.patric_genome_accession

        length = self.length

        num_contigs = self.num_contigs

        n_50 = self.n_50

        gc_content = self.gc_content

        type_ = self.type_.value

        completeness = self.completeness

        contamination = self.contamination

        catalogue_id = self.catalogue_id

        geographic_origin: None | str
        geographic_origin = self.geographic_origin

        geographic_range: list[str] | None | Unset
        if isinstance(self.geographic_range, Unset):
            geographic_range = UNSET
        elif isinstance(self.geographic_range, list):
            geographic_range = self.geographic_range

        else:
            geographic_range = self.geographic_range

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
                "accession": accession,
                "ena_genome_accession": ena_genome_accession,
                "ena_sample_accession": ena_sample_accession,
                "ncbi_genome_accession": ncbi_genome_accession,
                "img_genome_accession": img_genome_accession,
                "patric_genome_accession": patric_genome_accession,
                "length": length,
                "num_contigs": num_contigs,
                "n_50": n_50,
                "gc_content": gc_content,
                "type": type_,
                "completeness": completeness,
                "contamination": contamination,
                "catalogue_id": catalogue_id,
                "geographic_origin": geographic_origin,
            }
        )
        if geographic_range is not UNSET:
            field_dict["geographic_range"] = geographic_range
        if biome is not UNSET:
            field_dict["biome"] = biome

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.biome import Biome

        d = dict(src_dict)
        accession = d.pop("accession")

        def _parse_ena_genome_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        ena_genome_accession = _parse_ena_genome_accession(
            d.pop("ena_genome_accession")
        )

        def _parse_ena_sample_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        ena_sample_accession = _parse_ena_sample_accession(
            d.pop("ena_sample_accession")
        )

        def _parse_ncbi_genome_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        ncbi_genome_accession = _parse_ncbi_genome_accession(
            d.pop("ncbi_genome_accession")
        )

        def _parse_img_genome_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        img_genome_accession = _parse_img_genome_accession(
            d.pop("img_genome_accession")
        )

        def _parse_patric_genome_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        patric_genome_accession = _parse_patric_genome_accession(
            d.pop("patric_genome_accession")
        )

        length = d.pop("length")

        num_contigs = d.pop("num_contigs")

        n_50 = d.pop("n_50")

        gc_content = d.pop("gc_content")

        type_ = GenomeType(d.pop("type"))

        completeness = d.pop("completeness")

        contamination = d.pop("contamination")

        catalogue_id = d.pop("catalogue_id")

        def _parse_geographic_origin(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        geographic_origin = _parse_geographic_origin(d.pop("geographic_origin"))

        def _parse_geographic_range(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                geographic_range_type_0 = cast(list[str], data)

                return geographic_range_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        geographic_range = _parse_geographic_range(d.pop("geographic_range", UNSET))

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

        genome_list = cls(
            accession=accession,
            ena_genome_accession=ena_genome_accession,
            ena_sample_accession=ena_sample_accession,
            ncbi_genome_accession=ncbi_genome_accession,
            img_genome_accession=img_genome_accession,
            patric_genome_accession=patric_genome_accession,
            length=length,
            num_contigs=num_contigs,
            n_50=n_50,
            gc_content=gc_content,
            type_=type_,
            completeness=completeness,
            contamination=contamination,
            catalogue_id=catalogue_id,
            geographic_origin=geographic_origin,
            geographic_range=geographic_range,
            biome=biome,
        )

        genome_list.additional_properties = d
        return genome_list

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
