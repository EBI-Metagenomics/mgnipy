from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.download_file_index_file_index_type import DownloadFileIndexFileIndexType

T = TypeVar("T", bound="DownloadFileIndexFile")


@_attrs_define
class DownloadFileIndexFile:
    """An index file (e.g., a .fai for a FASTA file of .gzi for a bgzip file) of a DownloadFile.

    Attributes:
        index_type (DownloadFileIndexFileIndexType):
        path (str):
    """

    index_type: DownloadFileIndexFileIndexType
    path: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        index_type = self.index_type.value

        path: str
        path = self.path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "index_type": index_type,
                "path": path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        index_type = DownloadFileIndexFileIndexType(d.pop("index_type"))

        def _parse_path(data: object) -> str:
            return cast(str, data)

        path = _parse_path(d.pop("path"))

        download_file_index_file = cls(
            index_type=index_type,
            path=path,
        )

        download_file_index_file.additional_properties = d
        return download_file_index_file

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
