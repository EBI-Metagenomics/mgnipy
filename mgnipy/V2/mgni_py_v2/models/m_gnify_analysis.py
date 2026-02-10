from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.pipeline_versions import PipelineVersions

if TYPE_CHECKING:
    from ..models.analysed_run import AnalysedRun
    from ..models.assembly import Assembly
    from ..models.m_gnify_sample import MGnifySample


T = TypeVar("T", bound="MGnifyAnalysis")


@_attrs_define
class MGnifyAnalysis:
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
    """

    study_accession: str
    accession: str
    experiment_type: str
    run: AnalysedRun | None
    sample: MGnifySample | None
    assembly: Assembly | None
    pipeline_version: None | PipelineVersions
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.analysed_run import AnalysedRun
        from ..models.assembly import Assembly
        from ..models.m_gnify_sample import MGnifySample

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "study_accession": study_accession,
                "accession": accession,
                "experiment_type": experiment_type,
                "run": run,
                "sample": sample,
                "assembly": assembly,
                "pipeline_version": pipeline_version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.analysed_run import AnalysedRun
        from ..models.assembly import Assembly
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

        m_gnify_analysis = cls(
            study_accession=study_accession,
            accession=accession,
            experiment_type=experiment_type,
            run=run,
            sample=sample,
            assembly=assembly,
            pipeline_version=pipeline_version,
        )

        m_gnify_analysis.additional_properties = d
        return m_gnify_analysis

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
