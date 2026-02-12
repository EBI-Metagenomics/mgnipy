from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AnalysisJobDownload")


@_attrs_define
class AnalysisJobDownload:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            id (str):
            url (str):
            alias (str):
            file_format (str):
            description (str):
            group_type (str):
            pipeline (str):
            file_checksum (str):
    """

    id: str
    url: str
    alias: str
    file_format: str
    description: str
    group_type: str
    pipeline: str
    file_checksum: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        url = self.url

        alias = self.alias

        file_format = self.file_format

        description = self.description

        group_type = self.group_type

        pipeline = self.pipeline

        file_checksum = self.file_checksum

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "url": url,
                "alias": alias,
                "file_format": file_format,
                "description": description,
                "group_type": group_type,
                "pipeline": pipeline,
                "file_checksum": file_checksum,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        url = d.pop("url")

        alias = d.pop("alias")

        file_format = d.pop("file_format")

        description = d.pop("description")

        group_type = d.pop("group_type")

        pipeline = d.pop("pipeline")

        file_checksum = d.pop("file_checksum")

        analysis_job_download = cls(
            id=id,
            url=url,
            alias=alias,
            file_format=file_format,
            description=description,
            group_type=group_type,
            pipeline=pipeline,
            file_checksum=file_checksum,
        )

        analysis_job_download.additional_properties = d
        return analysis_job_download

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
