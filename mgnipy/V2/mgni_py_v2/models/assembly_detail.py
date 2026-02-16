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

from ..._mgnipy_models.types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.assembly_detail_metadata_type_0 import AssemblyDetailMetadataType0
    from ..models.assembly_detail_status_type_0 import AssemblyDetailStatusType0


T = TypeVar("T", bound="AssemblyDetail")


@_attrs_define
class AssemblyDetail:
    """
    Attributes:
        updated_at (datetime.datetime):
        accession (None | str | Unset):
        run_accession (None | str | Unset):
        sample_accession (None | str | Unset):
        reads_study_accession (None | str | Unset):
        assembly_study_accession (None | str | Unset):
        assembler_name (None | str | Unset):
        assembler_version (None | str | Unset):
        metadata (AssemblyDetailMetadataType0 | None | Unset): Additional metadata associated with the assembly
        status (AssemblyDetailStatusType0 | None | Unset): Status information for the assembly
    """

    updated_at: datetime.datetime
    accession: None | str | Unset = UNSET
    run_accession: None | str | Unset = UNSET
    sample_accession: None | str | Unset = UNSET
    reads_study_accession: None | str | Unset = UNSET
    assembly_study_accession: None | str | Unset = UNSET
    assembler_name: None | str | Unset = UNSET
    assembler_version: None | str | Unset = UNSET
    metadata: AssemblyDetailMetadataType0 | None | Unset = UNSET
    status: AssemblyDetailStatusType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.assembly_detail_metadata_type_0 import AssemblyDetailMetadataType0
        from ..models.assembly_detail_status_type_0 import AssemblyDetailStatusType0

        updated_at = self.updated_at.isoformat()

        accession: None | str | Unset
        if isinstance(self.accession, Unset):
            accession = UNSET
        else:
            accession = self.accession

        run_accession: None | str | Unset
        if isinstance(self.run_accession, Unset):
            run_accession = UNSET
        else:
            run_accession = self.run_accession

        sample_accession: None | str | Unset
        if isinstance(self.sample_accession, Unset):
            sample_accession = UNSET
        else:
            sample_accession = self.sample_accession

        reads_study_accession: None | str | Unset
        if isinstance(self.reads_study_accession, Unset):
            reads_study_accession = UNSET
        else:
            reads_study_accession = self.reads_study_accession

        assembly_study_accession: None | str | Unset
        if isinstance(self.assembly_study_accession, Unset):
            assembly_study_accession = UNSET
        else:
            assembly_study_accession = self.assembly_study_accession

        assembler_name: None | str | Unset
        if isinstance(self.assembler_name, Unset):
            assembler_name = UNSET
        else:
            assembler_name = self.assembler_name

        assembler_version: None | str | Unset
        if isinstance(self.assembler_version, Unset):
            assembler_version = UNSET
        else:
            assembler_version = self.assembler_version

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, AssemblyDetailMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        status: dict[str, Any] | None | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, AssemblyDetailStatusType0):
            status = self.status.to_dict()
        else:
            status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "updated_at": updated_at,
            }
        )
        if accession is not UNSET:
            field_dict["accession"] = accession
        if run_accession is not UNSET:
            field_dict["run_accession"] = run_accession
        if sample_accession is not UNSET:
            field_dict["sample_accession"] = sample_accession
        if reads_study_accession is not UNSET:
            field_dict["reads_study_accession"] = reads_study_accession
        if assembly_study_accession is not UNSET:
            field_dict["assembly_study_accession"] = assembly_study_accession
        if assembler_name is not UNSET:
            field_dict["assembler_name"] = assembler_name
        if assembler_version is not UNSET:
            field_dict["assembler_version"] = assembler_version
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.assembly_detail_metadata_type_0 import AssemblyDetailMetadataType0
        from ..models.assembly_detail_status_type_0 import AssemblyDetailStatusType0

        d = dict(src_dict)
        updated_at = isoparse(d.pop("updated_at"))

        def _parse_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        accession = _parse_accession(d.pop("accession", UNSET))

        def _parse_run_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        run_accession = _parse_run_accession(d.pop("run_accession", UNSET))

        def _parse_sample_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sample_accession = _parse_sample_accession(d.pop("sample_accession", UNSET))

        def _parse_reads_study_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reads_study_accession = _parse_reads_study_accession(
            d.pop("reads_study_accession", UNSET)
        )

        def _parse_assembly_study_accession(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        assembly_study_accession = _parse_assembly_study_accession(
            d.pop("assembly_study_accession", UNSET)
        )

        def _parse_assembler_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        assembler_name = _parse_assembler_name(d.pop("assembler_name", UNSET))

        def _parse_assembler_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        assembler_version = _parse_assembler_version(d.pop("assembler_version", UNSET))

        def _parse_metadata(data: object) -> AssemblyDetailMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = AssemblyDetailMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AssemblyDetailMetadataType0 | None | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        def _parse_status(data: object) -> AssemblyDetailStatusType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                status_type_0 = AssemblyDetailStatusType0.from_dict(data)

                return status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AssemblyDetailStatusType0 | None | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        assembly_detail = cls(
            updated_at=updated_at,
            accession=accession,
            run_accession=run_accession,
            sample_accession=sample_accession,
            reads_study_accession=reads_study_accession,
            assembly_study_accession=assembly_study_accession,
            assembler_name=assembler_name,
            assembler_version=assembler_version,
            metadata=metadata,
            status=status,
        )

        assembly_detail.additional_properties = d
        return assembly_detail

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
