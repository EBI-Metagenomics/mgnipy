from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.download_file_type import DownloadFileType
from ..models.download_type import DownloadType
from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="MGnifyGenomeDownloadFile")



@_attrs_define
class MGnifyGenomeDownloadFile:
    """ 
        Attributes:
            file_type (DownloadFileType):
            download_type (DownloadType):
            short_description (str): Brief description of the file
            long_description (str): Detailed description of the file
            path (str):
            alias (str):
            download_group (None | str | Unset): Group identifier for the download
            file_size_bytes (int | None | Unset):
            url (None | str | Unset):
     """

    file_type: DownloadFileType
    download_type: DownloadType
    short_description: str
    long_description: str
    path: str
    alias: str
    download_group: None | str | Unset = UNSET
    file_size_bytes: int | None | Unset = UNSET
    url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        file_type = self.file_type.value

        download_type = self.download_type.value

        short_description = self.short_description

        long_description = self.long_description

        path = self.path

        alias = self.alias

        download_group: None | str | Unset
        if isinstance(self.download_group, Unset):
            download_group = UNSET
        else:
            download_group = self.download_group

        file_size_bytes: int | None | Unset
        if isinstance(self.file_size_bytes, Unset):
            file_size_bytes = UNSET
        else:
            file_size_bytes = self.file_size_bytes

        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "file_type": file_type,
            "download_type": download_type,
            "short_description": short_description,
            "long_description": long_description,
            "path": path,
            "alias": alias,
        })
        if download_group is not UNSET:
            field_dict["download_group"] = download_group
        if file_size_bytes is not UNSET:
            field_dict["file_size_bytes"] = file_size_bytes
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file_type = DownloadFileType(d.pop("file_type"))




        download_type = DownloadType(d.pop("download_type"))




        short_description = d.pop("short_description")

        long_description = d.pop("long_description")

        path = d.pop("path")

        alias = d.pop("alias")

        def _parse_download_group(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        download_group = _parse_download_group(d.pop("download_group", UNSET))


        def _parse_file_size_bytes(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        file_size_bytes = _parse_file_size_bytes(d.pop("file_size_bytes", UNSET))


        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))


        m_gnify_genome_download_file = cls(
            file_type=file_type,
            download_type=download_type,
            short_description=short_description,
            long_description=long_description,
            path=path,
            alias=alias,
            download_group=download_group,
            file_size_bytes=file_size_bytes,
            url=url,
        )


        m_gnify_genome_download_file.additional_properties = d
        return m_gnify_genome_download_file

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
