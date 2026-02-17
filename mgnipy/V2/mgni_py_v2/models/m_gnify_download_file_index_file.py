from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..._mgnipy_models.types import (
    UNSET,
    Unset,
)
from ..models.m_gnify_download_file_index_file_index_type import (
    MGnifyDownloadFileIndexFileIndexType,
)

T = TypeVar("T", bound="MGnifyDownloadFileIndexFile")


@_attrs_define
class MGnifyDownloadFileIndexFile:
    """
    Attributes:
        index_type (MGnifyDownloadFileIndexFileIndexType):
        path (str):
        relative_url (str | Unset): URL of the index file, relative to the DownloadFile it relates to.
    """

    index_type: MGnifyDownloadFileIndexFileIndexType
    path: str
    relative_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        index_type = self.index_type.value

        path = self.path

        relative_url = self.relative_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "index_type": index_type,
                "path": path,
            }
        )
        if relative_url is not UNSET:
            field_dict["relative_url"] = relative_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        index_type = MGnifyDownloadFileIndexFileIndexType(d.pop("index_type"))

        path = d.pop("path")

        relative_url = d.pop("relative_url", UNSET)

        m_gnify_download_file_index_file = cls(
            index_type=index_type,
            path=path,
            relative_url=relative_url,
        )

        m_gnify_download_file_index_file.additional_properties = d
        return m_gnify_download_file_index_file

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
