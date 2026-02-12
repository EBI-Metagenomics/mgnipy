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

from ..models.type_enum import TypeEnum
from ..types import (
    UNSET,
    Unset,
)

T = TypeVar("T", bound="Genome")


@_attrs_define
class Genome:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            genome_id (int):
            cog_matches (str):
            biome (str):
            geographic_origin (str):
            kegg_class_matches (str):
            antismash_geneclusters (str):
            geographic_range (list[Any]):
            kegg_modules_matches (str):
            catalogue (str):
            url (str):
            downloads (str):
            accession (str):
            length (int):
            num_contigs (int):
            n_50 (int):
            gc_content (float):
            type_ (TypeEnum): * `mag` - MAG
                * `isolate` - Isolate
            completeness (float):
            contamination (float):
            trnas (float):
            nc_rnas (int):
            num_proteins (int):
            eggnog_coverage (float):
            ipr_coverage (float):
            taxon_lineage (str):
            last_update (datetime.datetime):
            first_created (datetime.datetime):
            ena_genome_accession (None | str | Unset):
            ena_sample_accession (None | str | Unset):
            ena_study_accession (None | str | Unset):
            ncbi_genome_accession (None | str | Unset):
            ncbi_sample_accession (None | str | Unset):
            ncbi_study_accession (None | str | Unset):
            img_genome_accession (None | str | Unset):
            patric_genome_accession (None | str | Unset):
            busco_completeness (float | None | Unset):
            rna_5s (float | None | Unset):
            rna_16s (float | None | Unset):
            rna_23s (float | None | Unset):
            rna_5_8s (float | None | Unset):
            rna_18s (float | None | Unset):
            rna_28s (float | None | Unset):
            num_genomes_total (int | None | Unset):
            pangenome_size (int | None | Unset):
            pangenome_core_size (int | None | Unset):
            pangenome_accessory_size (int | None | Unset):
    """

    genome_id: int
    cog_matches: str
    biome: str
    geographic_origin: str
    kegg_class_matches: str
    antismash_geneclusters: str
    geographic_range: list[Any]
    kegg_modules_matches: str
    catalogue: str
    url: str
    downloads: str
    accession: str
    length: int
    num_contigs: int
    n_50: int
    gc_content: float
    type_: TypeEnum
    completeness: float
    contamination: float
    trnas: float
    nc_rnas: int
    num_proteins: int
    eggnog_coverage: float
    ipr_coverage: float
    taxon_lineage: str
    last_update: datetime.datetime
    first_created: datetime.datetime
    ena_genome_accession: None | str | Unset = UNSET
    ena_sample_accession: None | str | Unset = UNSET
    ena_study_accession: None | str | Unset = UNSET
    ncbi_genome_accession: None | str | Unset = UNSET
    ncbi_sample_accession: None | str | Unset = UNSET
    ncbi_study_accession: None | str | Unset = UNSET
    img_genome_accession: None | str | Unset = UNSET
    patric_genome_accession: None | str | Unset = UNSET
    busco_completeness: float | None | Unset = UNSET
    rna_5s: float | None | Unset = UNSET
    rna_16s: float | None | Unset = UNSET
    rna_23s: float | None | Unset = UNSET
    rna_5_8s: float | None | Unset = UNSET
    rna_18s: float | None | Unset = UNSET
    rna_28s: float | None | Unset = UNSET
    num_genomes_total: int | None | Unset = UNSET
    pangenome_size: int | None | Unset = UNSET
    pangenome_core_size: int | None | Unset = UNSET
    pangenome_accessory_size: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        genome_id = self.genome_id

        cog_matches = self.cog_matches

        biome = self.biome

        geographic_origin = self.geographic_origin

        kegg_class_matches = self.kegg_class_matches

        antismash_geneclusters = self.antismash_geneclusters

        geographic_range = self.geographic_range

        kegg_modules_matches = self.kegg_modules_matches

        catalogue = self.catalogue

        url = self.url

        downloads = self.downloads

        accession = self.accession

        length = self.length

        num_contigs = self.num_contigs

        n_50 = self.n_50

        gc_content = self.gc_content

        type_ = self.type_.value

        completeness = self.completeness

        contamination = self.contamination

        trnas = self.trnas

        nc_rnas = self.nc_rnas

        num_proteins = self.num_proteins

        eggnog_coverage = self.eggnog_coverage

        ipr_coverage = self.ipr_coverage

        taxon_lineage = self.taxon_lineage

        last_update = self.last_update.isoformat()

        first_created = self.first_created.isoformat()

        ena_genome_accession: None | str | Unset
        if isinstance(self.ena_genome_accession, Unset):
            ena_genome_accession = UNSET
        else:
            ena_genome_accession = self.ena_genome_accession

        ena_sample_accession: None | str | Unset
        if isinstance(self.ena_sample_accession, Unset):
            ena_sample_accession = UNSET
        else:
            ena_sample_accession = self.ena_sample_accession

        ena_study_accession: None | str | Unset
        if isinstance(self.ena_study_accession, Unset):
            ena_study_accession = UNSET
        else:
            ena_study_accession = self.ena_study_accession

        ncbi_genome_accession: None | str | Unset
        if isinstance(self.ncbi_genome_accession, Unset):
            ncbi_genome_accession = UNSET
        else:
            ncbi_genome_accession = self.ncbi_genome_accession

        ncbi_sample_accession: None | str | Unset
        if isinstance(self.ncbi_sample_accession, Unset):
            ncbi_sample_accession = UNSET
        else:
            ncbi_sample_accession = self.ncbi_sample_accession

        ncbi_study_accession: None | str | Unset
        if isinstance(self.ncbi_study_accession, Unset):
            ncbi_study_accession = UNSET
        else:
            ncbi_study_accession = self.ncbi_study_accession

        img_genome_accession: None | str | Unset
        if isinstance(self.img_genome_accession, Unset):
            img_genome_accession = UNSET
        else:
            img_genome_accession = self.img_genome_accession

        patric_genome_accession: None | str | Unset
        if isinstance(self.patric_genome_accession, Unset):
            patric_genome_accession = UNSET
        else:
            patric_genome_accession = self.patric_genome_accession

        busco_completeness: float | None | Unset
        if isinstance(self.busco_completeness, Unset):
            busco_completeness = UNSET
        else:
            busco_completeness = self.busco_completeness

        rna_5s: float | None | Unset
        if isinstance(self.rna_5s, Unset):
            rna_5s = UNSET
        else:
            rna_5s = self.rna_5s

        rna_16s: float | None | Unset
        if isinstance(self.rna_16s, Unset):
            rna_16s = UNSET
        else:
            rna_16s = self.rna_16s

        rna_23s: float | None | Unset
        if isinstance(self.rna_23s, Unset):
            rna_23s = UNSET
        else:
            rna_23s = self.rna_23s

        rna_5_8s: float | None | Unset
        if isinstance(self.rna_5_8s, Unset):
            rna_5_8s = UNSET
        else:
            rna_5_8s = self.rna_5_8s

        rna_18s: float | None | Unset
        if isinstance(self.rna_18s, Unset):
            rna_18s = UNSET
        else:
            rna_18s = self.rna_18s

        rna_28s: float | None | Unset
        if isinstance(self.rna_28s, Unset):
            rna_28s = UNSET
        else:
            rna_28s = self.rna_28s

        num_genomes_total: int | None | Unset
        if isinstance(self.num_genomes_total, Unset):
            num_genomes_total = UNSET
        else:
            num_genomes_total = self.num_genomes_total

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "genome_id": genome_id,
                "cog_matches": cog_matches,
                "biome": biome,
                "geographic_origin": geographic_origin,
                "kegg_class_matches": kegg_class_matches,
                "antismash_geneclusters": antismash_geneclusters,
                "geographic_range": geographic_range,
                "kegg_modules_matches": kegg_modules_matches,
                "catalogue": catalogue,
                "url": url,
                "downloads": downloads,
                "accession": accession,
                "length": length,
                "num_contigs": num_contigs,
                "n_50": n_50,
                "gc_content": gc_content,
                "type": type_,
                "completeness": completeness,
                "contamination": contamination,
                "trnas": trnas,
                "nc_rnas": nc_rnas,
                "num_proteins": num_proteins,
                "eggnog_coverage": eggnog_coverage,
                "ipr_coverage": ipr_coverage,
                "taxon_lineage": taxon_lineage,
                "last_update": last_update,
                "first_created": first_created,
            }
        )
        if ena_genome_accession is not UNSET:
            field_dict["ena_genome_accession"] = ena_genome_accession
        if ena_sample_accession is not UNSET:
            field_dict["ena_sample_accession"] = ena_sample_accession
        if ena_study_accession is not UNSET:
            field_dict["ena_study_accession"] = ena_study_accession
        if ncbi_genome_accession is not UNSET:
            field_dict["ncbi_genome_accession"] = ncbi_genome_accession
        if ncbi_sample_accession is not UNSET:
            field_dict["ncbi_sample_accession"] = ncbi_sample_accession
        if ncbi_study_accession is not UNSET:
            field_dict["ncbi_study_accession"] = ncbi_study_accession
        if img_genome_accession is not UNSET:
            field_dict["img_genome_accession"] = img_genome_accession
        if patric_genome_accession is not UNSET:
            field_dict["patric_genome_accession"] = patric_genome_accession
        if busco_completeness is not UNSET:
            field_dict["busco_completeness"] = busco_completeness
        if rna_5s is not UNSET:
            field_dict["rna_5s"] = rna_5s
        if rna_16s is not UNSET:
            field_dict["rna_16s"] = rna_16s
        if rna_23s is not UNSET:
            field_dict["rna_23s"] = rna_23s
        if rna_5_8s is not UNSET:
            field_dict["rna_5_8s"] = rna_5_8s
        if rna_18s is not UNSET:
            field_dict["rna_18s"] = rna_18s
        if rna_28s is not UNSET:
            field_dict["rna_28s"] = rna_28s
        if num_genomes_total is not UNSET:
            field_dict["num_genomes_total"] = num_genomes_total
        if pangenome_size is not UNSET:
            field_dict["pangenome_size"] = pangenome_size
        if pangenome_core_size is not UNSET:
            field_dict["pangenome_core_size"] = pangenome_core_size
        if pangenome_accessory_size is not UNSET:
            field_dict["pangenome_accessory_size"] = pangenome_accessory_size

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        genome_id = d.pop("genome_id")

        cog_matches = d.pop("cog_matches")

        biome = d.pop("biome")

        geographic_origin = d.pop("geographic_origin")

        kegg_class_matches = d.pop("kegg_class_matches")

        antismash_geneclusters = d.pop("antismash_geneclusters")

        geographic_range = cast(list[Any], d.pop("geographic_range"))

        kegg_modules_matches = d.pop("kegg_modules_matches")

        catalogue = d.pop("catalogue")

        url = d.pop("url")

        downloads = d.pop("downloads")

        accession = d.pop("accession")

        length = d.pop("length")

        num_contigs = d.pop("num_contigs")

        n_50 = d.pop("n_50")

        gc_content = d.pop("gc_content")

        type_ = TypeEnum(d.pop("type"))

        completeness = d.pop("completeness")

        contamination = d.pop("contamination")

        trnas = d.pop("trnas")

        nc_rnas = d.pop("nc_rnas")

        num_proteins = d.pop("num_proteins")

        eggnog_coverage = d.pop("eggnog_coverage")

        ipr_coverage = d.pop("ipr_coverage")

        taxon_lineage = d.pop("taxon_lineage")

        last_update = isoparse(d.pop("last_update"))

        first_created = isoparse(d.pop("first_created"))

        def _parse_ena_genome_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ena_genome_accession = _parse_ena_genome_accession(
            d.pop("ena_genome_accession", UNSET)
        )

        def _parse_ena_sample_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ena_sample_accession = _parse_ena_sample_accession(
            d.pop("ena_sample_accession", UNSET)
        )

        def _parse_ena_study_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ena_study_accession = _parse_ena_study_accession(
            d.pop("ena_study_accession", UNSET)
        )

        def _parse_ncbi_genome_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ncbi_genome_accession = _parse_ncbi_genome_accession(
            d.pop("ncbi_genome_accession", UNSET)
        )

        def _parse_ncbi_sample_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ncbi_sample_accession = _parse_ncbi_sample_accession(
            d.pop("ncbi_sample_accession", UNSET)
        )

        def _parse_ncbi_study_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ncbi_study_accession = _parse_ncbi_study_accession(
            d.pop("ncbi_study_accession", UNSET)
        )

        def _parse_img_genome_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        img_genome_accession = _parse_img_genome_accession(
            d.pop("img_genome_accession", UNSET)
        )

        def _parse_patric_genome_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        patric_genome_accession = _parse_patric_genome_accession(
            d.pop("patric_genome_accession", UNSET)
        )

        def _parse_busco_completeness(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        busco_completeness = _parse_busco_completeness(
            d.pop("busco_completeness", UNSET)
        )

        def _parse_rna_5s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_5s = _parse_rna_5s(d.pop("rna_5s", UNSET))

        def _parse_rna_16s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_16s = _parse_rna_16s(d.pop("rna_16s", UNSET))

        def _parse_rna_23s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_23s = _parse_rna_23s(d.pop("rna_23s", UNSET))

        def _parse_rna_5_8s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_5_8s = _parse_rna_5_8s(d.pop("rna_5_8s", UNSET))

        def _parse_rna_18s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_18s = _parse_rna_18s(d.pop("rna_18s", UNSET))

        def _parse_rna_28s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rna_28s = _parse_rna_28s(d.pop("rna_28s", UNSET))

        def _parse_num_genomes_total(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        num_genomes_total = _parse_num_genomes_total(d.pop("num_genomes_total", UNSET))

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

        genome = cls(
            genome_id=genome_id,
            cog_matches=cog_matches,
            biome=biome,
            geographic_origin=geographic_origin,
            kegg_class_matches=kegg_class_matches,
            antismash_geneclusters=antismash_geneclusters,
            geographic_range=geographic_range,
            kegg_modules_matches=kegg_modules_matches,
            catalogue=catalogue,
            url=url,
            downloads=downloads,
            accession=accession,
            length=length,
            num_contigs=num_contigs,
            n_50=n_50,
            gc_content=gc_content,
            type_=type_,
            completeness=completeness,
            contamination=contamination,
            trnas=trnas,
            nc_rnas=nc_rnas,
            num_proteins=num_proteins,
            eggnog_coverage=eggnog_coverage,
            ipr_coverage=ipr_coverage,
            taxon_lineage=taxon_lineage,
            last_update=last_update,
            first_created=first_created,
            ena_genome_accession=ena_genome_accession,
            ena_sample_accession=ena_sample_accession,
            ena_study_accession=ena_study_accession,
            ncbi_genome_accession=ncbi_genome_accession,
            ncbi_sample_accession=ncbi_sample_accession,
            ncbi_study_accession=ncbi_study_accession,
            img_genome_accession=img_genome_accession,
            patric_genome_accession=patric_genome_accession,
            busco_completeness=busco_completeness,
            rna_5s=rna_5s,
            rna_16s=rna_16s,
            rna_23s=rna_23s,
            rna_5_8s=rna_5_8s,
            rna_18s=rna_18s,
            rna_28s=rna_28s,
            num_genomes_total=num_genomes_total,
            pangenome_size=pangenome_size,
            pangenome_core_size=pangenome_core_size,
            pangenome_accessory_size=pangenome_accessory_size,
        )

        genome.additional_properties = d
        return genome

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
