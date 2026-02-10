from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Analysis")


@_attrs_define
class Analysis:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            url (str):
            assembly (str):
            taxonomy_itsunite (str):
            antismash_gene_clusters (str):
            experiment_type (str):
            genome_properties (str):
            analysis_status (str):
            downloads (str):
            taxonomy_itsonedb (str):
            pipeline_version (str):
            run (str):
            go_terms (str):
            taxonomy_ssu (str):
            interpro_identifiers (str):
            sample (str):
            study (str):
            analysis_summary (list[Any]):
            accession (str):
            taxonomy (str):
            taxonomy_lsu (str):
            go_slim (str):
            last_update (datetime.datetime):
            is_private (bool | Unset):
            mgx_accession (None | str | Unset): The Metagenomics Exchange accession.
            complete_time (datetime.datetime | None | Unset):
            instrument_platform (None | str | Unset):
            instrument_model (None | str | Unset):
    """

    url: str
    assembly: str
    taxonomy_itsunite: str
    antismash_gene_clusters: str
    experiment_type: str
    genome_properties: str
    analysis_status: str
    downloads: str
    taxonomy_itsonedb: str
    pipeline_version: str
    run: str
    go_terms: str
    taxonomy_ssu: str
    interpro_identifiers: str
    sample: str
    study: str
    analysis_summary: list[Any]
    accession: str
    taxonomy: str
    taxonomy_lsu: str
    go_slim: str
    last_update: datetime.datetime
    is_private: bool | Unset = UNSET
    mgx_accession: None | str | Unset = UNSET
    complete_time: datetime.datetime | None | Unset = UNSET
    instrument_platform: None | str | Unset = UNSET
    instrument_model: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        assembly = self.assembly

        taxonomy_itsunite = self.taxonomy_itsunite

        antismash_gene_clusters = self.antismash_gene_clusters

        experiment_type = self.experiment_type

        genome_properties = self.genome_properties

        analysis_status = self.analysis_status

        downloads = self.downloads

        taxonomy_itsonedb = self.taxonomy_itsonedb

        pipeline_version = self.pipeline_version

        run = self.run

        go_terms = self.go_terms

        taxonomy_ssu = self.taxonomy_ssu

        interpro_identifiers = self.interpro_identifiers

        sample = self.sample

        study = self.study

        analysis_summary = self.analysis_summary

        accession = self.accession

        taxonomy = self.taxonomy

        taxonomy_lsu = self.taxonomy_lsu

        go_slim = self.go_slim

        last_update = self.last_update.isoformat()

        is_private = self.is_private

        mgx_accession: None | str | Unset
        if isinstance(self.mgx_accession, Unset):
            mgx_accession = UNSET
        else:
            mgx_accession = self.mgx_accession

        complete_time: None | str | Unset
        if isinstance(self.complete_time, Unset):
            complete_time = UNSET
        elif isinstance(self.complete_time, datetime.datetime):
            complete_time = self.complete_time.isoformat()
        else:
            complete_time = self.complete_time

        instrument_platform: None | str | Unset
        if isinstance(self.instrument_platform, Unset):
            instrument_platform = UNSET
        else:
            instrument_platform = self.instrument_platform

        instrument_model: None | str | Unset
        if isinstance(self.instrument_model, Unset):
            instrument_model = UNSET
        else:
            instrument_model = self.instrument_model

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "assembly": assembly,
                "taxonomy_itsunite": taxonomy_itsunite,
                "antismash_gene_clusters": antismash_gene_clusters,
                "experiment_type": experiment_type,
                "genome_properties": genome_properties,
                "analysis_status": analysis_status,
                "downloads": downloads,
                "taxonomy_itsonedb": taxonomy_itsonedb,
                "pipeline_version": pipeline_version,
                "run": run,
                "go_terms": go_terms,
                "taxonomy_ssu": taxonomy_ssu,
                "interpro_identifiers": interpro_identifiers,
                "sample": sample,
                "study": study,
                "analysis_summary": analysis_summary,
                "accession": accession,
                "taxonomy": taxonomy,
                "taxonomy_lsu": taxonomy_lsu,
                "go_slim": go_slim,
                "last_update": last_update,
            }
        )
        if is_private is not UNSET:
            field_dict["is_private"] = is_private
        if mgx_accession is not UNSET:
            field_dict["mgx_accession"] = mgx_accession
        if complete_time is not UNSET:
            field_dict["complete_time"] = complete_time
        if instrument_platform is not UNSET:
            field_dict["instrument_platform"] = instrument_platform
        if instrument_model is not UNSET:
            field_dict["instrument_model"] = instrument_model

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        assembly = d.pop("assembly")

        taxonomy_itsunite = d.pop("taxonomy_itsunite")

        antismash_gene_clusters = d.pop("antismash_gene_clusters")

        experiment_type = d.pop("experiment_type")

        genome_properties = d.pop("genome_properties")

        analysis_status = d.pop("analysis_status")

        downloads = d.pop("downloads")

        taxonomy_itsonedb = d.pop("taxonomy_itsonedb")

        pipeline_version = d.pop("pipeline_version")

        run = d.pop("run")

        go_terms = d.pop("go_terms")

        taxonomy_ssu = d.pop("taxonomy_ssu")

        interpro_identifiers = d.pop("interpro_identifiers")

        sample = d.pop("sample")

        study = d.pop("study")

        analysis_summary = cast(list[Any], d.pop("analysis_summary"))

        accession = d.pop("accession")

        taxonomy = d.pop("taxonomy")

        taxonomy_lsu = d.pop("taxonomy_lsu")

        go_slim = d.pop("go_slim")

        last_update = isoparse(d.pop("last_update"))

        is_private = d.pop("is_private", UNSET)

        def _parse_mgx_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mgx_accession = _parse_mgx_accession(d.pop("mgx_accession", UNSET))

        def _parse_complete_time(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                complete_time_type_0 = isoparse(data)

                return complete_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        complete_time = _parse_complete_time(d.pop("complete_time", UNSET))

        def _parse_instrument_platform(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        instrument_platform = _parse_instrument_platform(d.pop("instrument_platform", UNSET))

        def _parse_instrument_model(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        instrument_model = _parse_instrument_model(d.pop("instrument_model", UNSET))

        analysis = cls(
            url=url,
            assembly=assembly,
            taxonomy_itsunite=taxonomy_itsunite,
            antismash_gene_clusters=antismash_gene_clusters,
            experiment_type=experiment_type,
            genome_properties=genome_properties,
            analysis_status=analysis_status,
            downloads=downloads,
            taxonomy_itsonedb=taxonomy_itsonedb,
            pipeline_version=pipeline_version,
            run=run,
            go_terms=go_terms,
            taxonomy_ssu=taxonomy_ssu,
            interpro_identifiers=interpro_identifiers,
            sample=sample,
            study=study,
            analysis_summary=analysis_summary,
            accession=accession,
            taxonomy=taxonomy,
            taxonomy_lsu=taxonomy_lsu,
            go_slim=go_slim,
            last_update=last_update,
            is_private=is_private,
            mgx_accession=mgx_accession,
            complete_time=complete_time,
            instrument_platform=instrument_platform,
            instrument_model=instrument_model,
        )

        analysis.additional_properties = d
        return analysis

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
