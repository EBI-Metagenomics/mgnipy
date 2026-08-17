from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.genome_type import GenomeType
from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
    from ..models.biome import Biome
    from ..models.genome_catalogue_base import GenomeCatalogueBase
    from ..models.m_gnify_genome_download_file import MGnifyGenomeDownloadFile


T = TypeVar("T", bound="GenomeDetail")


@_attrs_define
class GenomeDetail:
    """
    Attributes:
        accession (str):
        ena_genome_accession (None | str):
        ena_sample_accession (None | str):
        ena_study_accession (None | str):
        ncbi_genome_accession (None | str):
        ncbi_study_accession (None | str):
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
        taxon_lineage (str):
        updated_at (datetime.datetime):
        geographic_origin (None | str):
        downloads (list[MGnifyGenomeDownloadFile]):
        num_genomes_total (int | None | Unset):
        geographic_range (list[str] | None | Unset):
        biome (Biome | None | Unset):
        rna_5s (float | None | Unset):
        rna_5_8s (float | None | Unset):
        rna_16s (float | None | Unset):
        rna_18s (float | None | Unset):
        rna_23s (float | None | Unset):
        rna_28s (float | None | Unset):
        trnas (float | None | Unset):
        nc_rnas (float | None | Unset):
        eggnog_coverage (float | None | Unset):
        ipr_coverage (float | None | Unset):
        num_proteins (int | None | Unset):
        pangenome_size (int | None | Unset):
        pangenome_core_size (int | None | Unset):
        pangenome_accessory_size (int | None | Unset):
        catalogue (GenomeCatalogueBase | None | Unset):
    """

    accession: str
    ena_genome_accession: None | str
    ena_sample_accession: None | str
    ena_study_accession: None | str
    ncbi_genome_accession: None | str
    ncbi_study_accession: None | str
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
    taxon_lineage: str
    updated_at: datetime.datetime
    geographic_origin: None | str
    downloads: list[MGnifyGenomeDownloadFile]
    num_genomes_total: int | None | Unset = UNSET
    geographic_range: list[str] | None | Unset = UNSET
    biome: Biome | None | Unset = UNSET
    rna_5s: float | None | Unset = UNSET
    rna_5_8s: float | None | Unset = UNSET
    rna_16s: float | None | Unset = UNSET
    rna_18s: float | None | Unset = UNSET
    rna_23s: float | None | Unset = UNSET
    rna_28s: float | None | Unset = UNSET
    trnas: float | None | Unset = UNSET
    nc_rnas: float | None | Unset = UNSET
    eggnog_coverage: float | None | Unset = UNSET
    ipr_coverage: float | None | Unset = UNSET
    num_proteins: int | None | Unset = UNSET
    pangenome_size: int | None | Unset = UNSET
    pangenome_core_size: int | None | Unset = UNSET
    pangenome_accessory_size: int | None | Unset = UNSET
    catalogue: GenomeCatalogueBase | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.genome_catalogue_base import GenomeCatalogueBase
        from ..models.biome import Biome

        accession = self.accession

        ena_genome_accession: None | str
        ena_genome_accession = self.ena_genome_accession

        ena_sample_accession: None | str
        ena_sample_accession = self.ena_sample_accession

        ena_study_accession: None | str
        ena_study_accession = self.ena_study_accession

        ncbi_genome_accession: None | str
        ncbi_genome_accession = self.ncbi_genome_accession

        ncbi_study_accession: None | str
        ncbi_study_accession = self.ncbi_study_accession

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

        taxon_lineage = self.taxon_lineage

        updated_at = self.updated_at.isoformat()

        geographic_origin: None | str
        geographic_origin = self.geographic_origin

        downloads = []
        for downloads_item_data in self.downloads:
            downloads_item = downloads_item_data.to_dict()
            downloads.append(downloads_item)

        num_genomes_total: int | None | Unset
        if isinstance(self.num_genomes_total, Unset):
            num_genomes_total = UNSET
        else:
            num_genomes_total = self.num_genomes_total

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

        rna_5s: float | None | Unset
        if isinstance(self.rna_5s, Unset):
            rna_5s = UNSET
        else:
            rna_5s = self.rna_5s

        rna_5_8s: float | None | Unset
        if isinstance(self.rna_5_8s, Unset):
            rna_5_8s = UNSET
        else:
            rna_5_8s = self.rna_5_8s

        rna_16s: float | None | Unset
        if isinstance(self.rna_16s, Unset):
            rna_16s = UNSET
        else:
            rna_16s = self.rna_16s

        rna_18s: float | None | Unset
        if isinstance(self.rna_18s, Unset):
            rna_18s = UNSET
        else:
            rna_18s = self.rna_18s

        rna_23s: float | None | Unset
        if isinstance(self.rna_23s, Unset):
            rna_23s = UNSET
        else:
            rna_23s = self.rna_23s

        rna_28s: float | None | Unset
        if isinstance(self.rna_28s, Unset):
            rna_28s = UNSET
        else:
            rna_28s = self.rna_28s

        trnas: float | None | Unset
        if isinstance(self.trnas, Unset):
            trnas = UNSET
        else:
            trnas = self.trnas

        nc_rnas: float | None | Unset
        if isinstance(self.nc_rnas, Unset):
            nc_rnas = UNSET
        else:
            nc_rnas = self.nc_rnas

        eggnog_coverage: float | None | Unset
        if isinstance(self.eggnog_coverage, Unset):
            eggnog_coverage = UNSET
        else:
            eggnog_coverage = self.eggnog_coverage

        ipr_coverage: float | None | Unset
        if isinstance(self.ipr_coverage, Unset):
            ipr_coverage = UNSET
        else:
            ipr_coverage = self.ipr_coverage

        num_proteins: int | None | Unset
        if isinstance(self.num_proteins, Unset):
            num_proteins = UNSET
        else:
            num_proteins = self.num_proteins

        pangenome_size: int | None | Unset
        if isinstance(self.pangenome_size, Unset):
            pangenome_size = UNSET
        else:
            pangenome_size = self.pangenome_size

        pangenome_core_size: int | None | Unset
        if isinstance(self.pangenome_core_size, Unset):
            pangenome_core_size = UNSET
        else:
            pangenome_core_size = self.pangenome_core_size

        pangenome_accessory_size: int | None | Unset
        if isinstance(self.pangenome_accessory_size, Unset):
            pangenome_accessory_size = UNSET
        else:
            pangenome_accessory_size = self.pangenome_accessory_size

        catalogue: dict[str, Any] | None | Unset
        if isinstance(self.catalogue, Unset):
            catalogue = UNSET
        elif isinstance(self.catalogue, GenomeCatalogueBase):
            catalogue = self.catalogue.to_dict()
        else:
            catalogue = self.catalogue

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accession": accession,
                "ena_genome_accession": ena_genome_accession,
                "ena_sample_accession": ena_sample_accession,
                "ena_study_accession": ena_study_accession,
                "ncbi_genome_accession": ncbi_genome_accession,
                "ncbi_study_accession": ncbi_study_accession,
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
                "taxon_lineage": taxon_lineage,
                "updated_at": updated_at,
                "geographic_origin": geographic_origin,
                "downloads": downloads,
            }
        )
        if num_genomes_total is not UNSET:
            field_dict["num_genomes_total"] = num_genomes_total
        if geographic_range is not UNSET:
            field_dict["geographic_range"] = geographic_range
        if biome is not UNSET:
            field_dict["biome"] = biome
        if rna_5s is not UNSET:
            field_dict["rna_5s"] = rna_5s
        if rna_5_8s is not UNSET:
            field_dict["rna_5_8s"] = rna_5_8s
        if rna_16s is not UNSET:
            field_dict["rna_16s"] = rna_16s
        if rna_18s is not UNSET:
            field_dict["rna_18s"] = rna_18s
        if rna_23s is not UNSET:
            field_dict["rna_23s"] = rna_23s
        if rna_28s is not UNSET:
            field_dict["rna_28s"] = rna_28s
        if trnas is not UNSET:
            field_dict["trnas"] = trnas
        if nc_rnas is not UNSET:
            field_dict["nc_rnas"] = nc_rnas
        if eggnog_coverage is not UNSET:
            field_dict["eggnog_coverage"] = eggnog_coverage
        if ipr_coverage is not UNSET:
            field_dict["ipr_coverage"] = ipr_coverage
        if num_proteins is not UNSET:
            field_dict["num_proteins"] = num_proteins
        if pangenome_size is not UNSET:
            field_dict["pangenome_size"] = pangenome_size
        if pangenome_core_size is not UNSET:
            field_dict["pangenome_core_size"] = pangenome_core_size
        if pangenome_accessory_size is not UNSET:
            field_dict["pangenome_accessory_size"] = pangenome_accessory_size
        if catalogue is not UNSET:
            field_dict["catalogue"] = catalogue

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.biome import Biome
        from ..models.genome_catalogue_base import GenomeCatalogueBase
        from ..models.m_gnify_genome_download_file import MGnifyGenomeDownloadFile

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

        def _parse_ena_study_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        ena_study_accession = _parse_ena_study_accession(d.pop("ena_study_accession"))

        def _parse_ncbi_genome_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        ncbi_genome_accession = _parse_ncbi_genome_accession(
            d.pop("ncbi_genome_accession")
        )

        def _parse_ncbi_study_accession(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        ncbi_study_accession = _parse_ncbi_study_accession(
            d.pop("ncbi_study_accession")
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

        taxon_lineage = d.pop("taxon_lineage")

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_geographic_origin(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        geographic_origin = _parse_geographic_origin(d.pop("geographic_origin"))

        downloads = []
        _downloads = d.pop("downloads")
        for downloads_item_data in _downloads:
            downloads_item = MGnifyGenomeDownloadFile.from_dict(downloads_item_data)

            downloads.append(downloads_item)

        def _parse_num_genomes_total(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        num_genomes_total = _parse_num_genomes_total(d.pop("num_genomes_total", UNSET))

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

        def _parse_rna_5s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_5s = _parse_rna_5s(d.pop("rna_5s", UNSET))

        def _parse_rna_5_8s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_5_8s = _parse_rna_5_8s(d.pop("rna_5_8s", UNSET))

        def _parse_rna_16s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_16s = _parse_rna_16s(d.pop("rna_16s", UNSET))

        def _parse_rna_18s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_18s = _parse_rna_18s(d.pop("rna_18s", UNSET))

        def _parse_rna_23s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_23s = _parse_rna_23s(d.pop("rna_23s", UNSET))

        def _parse_rna_28s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_28s = _parse_rna_28s(d.pop("rna_28s", UNSET))

        def _parse_trnas(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        trnas = _parse_trnas(d.pop("trnas", UNSET))

        def _parse_nc_rnas(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        nc_rnas = _parse_nc_rnas(d.pop("nc_rnas", UNSET))

        def _parse_eggnog_coverage(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        eggnog_coverage = _parse_eggnog_coverage(d.pop("eggnog_coverage", UNSET))

        def _parse_ipr_coverage(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ipr_coverage = _parse_ipr_coverage(d.pop("ipr_coverage", UNSET))

        def _parse_num_proteins(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        num_proteins = _parse_num_proteins(d.pop("num_proteins", UNSET))

        def _parse_pangenome_size(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pangenome_size = _parse_pangenome_size(d.pop("pangenome_size", UNSET))

        def _parse_pangenome_core_size(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pangenome_core_size = _parse_pangenome_core_size(
            d.pop("pangenome_core_size", UNSET)
        )

        def _parse_pangenome_accessory_size(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pangenome_accessory_size = _parse_pangenome_accessory_size(
            d.pop("pangenome_accessory_size", UNSET)
        )

        def _parse_catalogue(data: object) -> GenomeCatalogueBase | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                catalogue_type_0 = GenomeCatalogueBase.from_dict(data)

                return catalogue_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GenomeCatalogueBase | None | Unset, data)

        catalogue = _parse_catalogue(d.pop("catalogue", UNSET))

        genome_detail = cls(
            accession=accession,
            ena_genome_accession=ena_genome_accession,
            ena_sample_accession=ena_sample_accession,
            ena_study_accession=ena_study_accession,
            ncbi_genome_accession=ncbi_genome_accession,
            ncbi_study_accession=ncbi_study_accession,
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
            taxon_lineage=taxon_lineage,
            updated_at=updated_at,
            geographic_origin=geographic_origin,
            downloads=downloads,
            num_genomes_total=num_genomes_total,
            geographic_range=geographic_range,
            biome=biome,
            rna_5s=rna_5s,
            rna_5_8s=rna_5_8s,
            rna_16s=rna_16s,
            rna_18s=rna_18s,
            rna_23s=rna_23s,
            rna_28s=rna_28s,
            trnas=trnas,
            nc_rnas=nc_rnas,
            eggnog_coverage=eggnog_coverage,
            ipr_coverage=ipr_coverage,
            num_proteins=num_proteins,
            pangenome_size=pangenome_size,
            pangenome_core_size=pangenome_core_size,
            pangenome_accessory_size=pangenome_accessory_size,
            catalogue=catalogue,
        )

        genome_detail.additional_properties = d
        return genome_detail

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
