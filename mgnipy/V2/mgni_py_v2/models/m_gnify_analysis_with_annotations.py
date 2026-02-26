from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.pipeline_versions import PipelineVersions
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.analysed_run import AnalysedRun
  from ..models.assembly import Assembly
  from ..models.m_gnify_analysis_download_file import MGnifyAnalysisDownloadFile
  from ..models.m_gnify_analysis_with_annotations_annotations import MGnifyAnalysisWithAnnotationsAnnotations
  from ..models.m_gnify_analysis_with_annotations_metadata_type_0 import MGnifyAnalysisWithAnnotationsMetadataType0
  from ..models.m_gnify_analysis_with_annotations_quality_control_summary_type_0 import MGnifyAnalysisWithAnnotationsQualityControlSummaryType0
  from ..models.m_gnify_sample import MGnifySample





T = TypeVar("T", bound="MGnifyAnalysisWithAnnotations")



@_attrs_define
class MGnifyAnalysisWithAnnotations:
    """ 
        Attributes:
            study_accession (str):
            accession (str):
            experiment_type (str): Experiment type refers to the type of sequencing data that was analysed, e.g. amplicon
                reads or a metagenome assembly
            run (AnalysedRun | None):
            sample (MGnifySample | None):
            assembly (Assembly | None):
            pipeline_version (None | PipelineVersions):
            downloads (list[MGnifyAnalysisDownloadFile]):
            read_run (AnalysedRun | None): Metadata associated with the original read run this analysis is based on, whether
                or not those reads were assembled.
            quality_control_summary (MGnifyAnalysisWithAnnotationsQualityControlSummaryType0 | None):
            annotations (MGnifyAnalysisWithAnnotationsAnnotations):
            results_dir (None | str | Unset): Directory path where analysis results are stored
            metadata (MGnifyAnalysisWithAnnotationsMetadataType0 | None | Unset): Additional metadata associated with the
                analysis
     """

    study_accession: str
    accession: str
    experiment_type: str
    run: AnalysedRun | None
    sample: MGnifySample | None
    assembly: Assembly | None
    pipeline_version: None | PipelineVersions
    downloads: list[MGnifyAnalysisDownloadFile]
    read_run: AnalysedRun | None
    quality_control_summary: MGnifyAnalysisWithAnnotationsQualityControlSummaryType0 | None
    annotations: MGnifyAnalysisWithAnnotationsAnnotations
    results_dir: None | str | Unset = UNSET
    metadata: MGnifyAnalysisWithAnnotationsMetadataType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.m_gnify_sample import MGnifySample
        from ..models.m_gnify_analysis_with_annotations_metadata_type_0 import MGnifyAnalysisWithAnnotationsMetadataType0
        from ..models.m_gnify_analysis_download_file import MGnifyAnalysisDownloadFile
        from ..models.m_gnify_analysis_with_annotations_quality_control_summary_type_0 import MGnifyAnalysisWithAnnotationsQualityControlSummaryType0
        from ..models.assembly import Assembly
        from ..models.analysed_run import AnalysedRun
        from ..models.m_gnify_analysis_with_annotations_annotations import MGnifyAnalysisWithAnnotationsAnnotations
        study_accession = self.study_accession

        accession = self.accession

        experiment_type = self.experiment_type

        run: dict[str, Any] | None
        if isinstance(self.run, AnalysedRun):
            run = self.run.to_dict()
        else:
            run = self.run

        sample: dict[str, Any] | None
        if isinstance(self.sample, MGnifySample):
            sample = self.sample.to_dict()
        else:
            sample = self.sample

        assembly: dict[str, Any] | None
        if isinstance(self.assembly, Assembly):
            assembly = self.assembly.to_dict()
        else:
            assembly = self.assembly

        pipeline_version: None | str
        if isinstance(self.pipeline_version, PipelineVersions):
            pipeline_version = self.pipeline_version.value
        else:
            pipeline_version = self.pipeline_version

        downloads = []
        for downloads_item_data in self.downloads:
            downloads_item = downloads_item_data.to_dict()
            downloads.append(downloads_item)



        read_run: dict[str, Any] | None
        if isinstance(self.read_run, AnalysedRun):
            read_run = self.read_run.to_dict()
        else:
            read_run = self.read_run

        quality_control_summary: dict[str, Any] | None
        if isinstance(self.quality_control_summary, MGnifyAnalysisWithAnnotationsQualityControlSummaryType0):
            quality_control_summary = self.quality_control_summary.to_dict()
        else:
            quality_control_summary = self.quality_control_summary

        annotations = self.annotations.to_dict()

        results_dir: None | str | Unset
        if isinstance(self.results_dir, Unset):
            results_dir = UNSET
        else:
            results_dir = self.results_dir

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, MGnifyAnalysisWithAnnotationsMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "study_accession": study_accession,
            "accession": accession,
            "experiment_type": experiment_type,
            "run": run,
            "sample": sample,
            "assembly": assembly,
            "pipeline_version": pipeline_version,
            "downloads": downloads,
            "read_run": read_run,
            "quality_control_summary": quality_control_summary,
            "annotations": annotations,
        })
        if results_dir is not UNSET:
            field_dict["results_dir"] = results_dir
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.analysed_run import AnalysedRun
        from ..models.assembly import Assembly
        from ..models.m_gnify_analysis_download_file import MGnifyAnalysisDownloadFile
        from ..models.m_gnify_analysis_with_annotations_annotations import MGnifyAnalysisWithAnnotationsAnnotations
        from ..models.m_gnify_analysis_with_annotations_metadata_type_0 import MGnifyAnalysisWithAnnotationsMetadataType0
        from ..models.m_gnify_analysis_with_annotations_quality_control_summary_type_0 import MGnifyAnalysisWithAnnotationsQualityControlSummaryType0
        from ..models.m_gnify_sample import MGnifySample
        d = dict(src_dict)
        study_accession = d.pop("study_accession")

        accession = d.pop("accession")

        experiment_type = d.pop("experiment_type")

        def _parse_run(data: object) -> AnalysedRun | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                run_type_0 = AnalysedRun.from_dict(data)



                return run_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AnalysedRun | None, data)

        run = _parse_run(d.pop("run"))


        def _parse_sample(data: object) -> MGnifySample | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                sample_type_0 = MGnifySample.from_dict(data)



                return sample_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MGnifySample | None, data)

        sample = _parse_sample(d.pop("sample"))


        def _parse_assembly(data: object) -> Assembly | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                assembly_type_0 = Assembly.from_dict(data)



                return assembly_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Assembly | None, data)

        assembly = _parse_assembly(d.pop("assembly"))


        def _parse_pipeline_version(data: object) -> None | PipelineVersions:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                pipeline_version_type_0 = PipelineVersions(data)



                return pipeline_version_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PipelineVersions, data)

        pipeline_version = _parse_pipeline_version(d.pop("pipeline_version"))


        downloads = []
        _downloads = d.pop("downloads")
        for downloads_item_data in (_downloads):
            downloads_item = MGnifyAnalysisDownloadFile.from_dict(downloads_item_data)



            downloads.append(downloads_item)


        def _parse_read_run(data: object) -> AnalysedRun | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                read_run_type_0 = AnalysedRun.from_dict(data)



                return read_run_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AnalysedRun | None, data)

        read_run = _parse_read_run(d.pop("read_run"))


        def _parse_quality_control_summary(data: object) -> MGnifyAnalysisWithAnnotationsQualityControlSummaryType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                quality_control_summary_type_0 = MGnifyAnalysisWithAnnotationsQualityControlSummaryType0.from_dict(data)



                return quality_control_summary_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MGnifyAnalysisWithAnnotationsQualityControlSummaryType0 | None, data)

        quality_control_summary = _parse_quality_control_summary(d.pop("quality_control_summary"))


        annotations = MGnifyAnalysisWithAnnotationsAnnotations.from_dict(d.pop("annotations"))




        def _parse_results_dir(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        results_dir = _parse_results_dir(d.pop("results_dir", UNSET))


        def _parse_metadata(data: object) -> MGnifyAnalysisWithAnnotationsMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = MGnifyAnalysisWithAnnotationsMetadataType0.from_dict(data)



                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MGnifyAnalysisWithAnnotationsMetadataType0 | None | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))


        m_gnify_analysis_with_annotations = cls(
            study_accession=study_accession,
            accession=accession,
            experiment_type=experiment_type,
            run=run,
            sample=sample,
            assembly=assembly,
            pipeline_version=pipeline_version,
            downloads=downloads,
            read_run=read_run,
            quality_control_summary=quality_control_summary,
            annotations=annotations,
            results_dir=results_dir,
            metadata=metadata,
        )


        m_gnify_analysis_with_annotations.additional_properties = d
        return m_gnify_analysis_with_annotations

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
