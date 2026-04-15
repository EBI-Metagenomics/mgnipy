from __future__ import annotations

from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.download_file_type import DownloadFileType
from ..models.download_type import DownloadType
from ..types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.download_file_index_file import DownloadFileIndexFile
    from ..models.m_gnify_download_file_index_file import MGnifyDownloadFileIndexFile


T = TypeVar("T", bound="MGnifyStudyDownloadFile")


@_attrs_define
class MGnifyStudyDownloadFile:
    """
    Attributes:
        file_type (DownloadFileType):
        download_type (DownloadType):
        short_description (str): Brief description of the file
        long_description (str): Detailed description of the file
        alias (str):
        download_group (None | str | Unset): Group identifier for the download
        path (str | Unset):
        file_size_bytes (int | None | Unset):
        index_file (DownloadFileIndexFile | list[DownloadFileIndexFile] | None | Unset):
        parent_identifier (int | str | Unset):
        parent_is_private (bool | None | Unset):
        parent_results_dir (None | str | Unset):
        index_files (list[MGnifyDownloadFileIndexFile] | None | Unset):
        url (None | str | Unset):
    """

    file_type: DownloadFileType
    download_type: DownloadType
    short_description: str
    long_description: str
    alias: str
    download_group: None | str | Unset = UNSET
    path: str | Unset = UNSET
    file_size_bytes: int | None | Unset = UNSET
    index_file: DownloadFileIndexFile | list[DownloadFileIndexFile] | None | Unset = (
        UNSET
    )
    parent_identifier: int | str | Unset = UNSET
    parent_is_private: bool | None | Unset = UNSET
    parent_results_dir: None | str | Unset = UNSET
    index_files: list[MGnifyDownloadFileIndexFile] | None | Unset = UNSET
    url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.download_file_index_file import DownloadFileIndexFile

        file_type = self.file_type.value

        download_type = self.download_type.value

        short_description = self.short_description

        long_description = self.long_description

        alias = self.alias

        download_group: None | str | Unset
        if isinstance(self.download_group, Unset):
            download_group = UNSET
        else:
            download_group = self.download_group

        path = self.path

        file_size_bytes: int | None | Unset
        if isinstance(self.file_size_bytes, Unset):
            file_size_bytes = UNSET
        else:
            file_size_bytes = self.file_size_bytes

        index_file: dict[str, Any] | list[dict[str, Any]] | None | Unset
        if isinstance(self.index_file, Unset):
            index_file = UNSET
        elif isinstance(self.index_file, DownloadFileIndexFile):
            index_file = self.index_file.to_dict()
        elif isinstance(self.index_file, list):
            index_file = []
            for index_file_type_1_item_data in self.index_file:
                index_file_type_1_item = index_file_type_1_item_data.to_dict()
                index_file.append(index_file_type_1_item)

        else:
            index_file = self.index_file

        parent_identifier: int | str | Unset
        if isinstance(self.parent_identifier, Unset):
            parent_identifier = UNSET
        else:
            parent_identifier = self.parent_identifier

        parent_is_private: bool | None | Unset
        if isinstance(self.parent_is_private, Unset):
            parent_is_private = UNSET
        else:
            parent_is_private = self.parent_is_private

        parent_results_dir: None | str | Unset
        if isinstance(self.parent_results_dir, Unset):
            parent_results_dir = UNSET
        else:
            parent_results_dir = self.parent_results_dir

        index_files: list[dict[str, Any]] | None | Unset
        if isinstance(self.index_files, Unset):
            index_files = UNSET
        elif isinstance(self.index_files, list):
            index_files = []
            for index_files_type_0_item_data in self.index_files:
                index_files_type_0_item = index_files_type_0_item_data.to_dict()
                index_files.append(index_files_type_0_item)

        else:
            index_files = self.index_files

        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file_type": file_type,
                "download_type": download_type,
                "short_description": short_description,
                "long_description": long_description,
                "alias": alias,
            }
        )
        if download_group is not UNSET:
            field_dict["download_group"] = download_group
        if path is not UNSET:
            field_dict["path"] = path
        if file_size_bytes is not UNSET:
            field_dict["file_size_bytes"] = file_size_bytes
        if index_file is not UNSET:
            field_dict["index_file"] = index_file
        if parent_identifier is not UNSET:
            field_dict["parent_identifier"] = parent_identifier
        if parent_is_private is not UNSET:
            field_dict["parent_is_private"] = parent_is_private
        if parent_results_dir is not UNSET:
            field_dict["parent_results_dir"] = parent_results_dir
        if index_files is not UNSET:
            field_dict["index_files"] = index_files
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.download_file_index_file import DownloadFileIndexFile
        from ..models.m_gnify_download_file_index_file import (
            MGnifyDownloadFileIndexFile,
        )

        d = dict(src_dict)
        file_type = DownloadFileType(d.pop("file_type"))

        download_type = DownloadType(d.pop("download_type"))

        short_description = d.pop("short_description")

        long_description = d.pop("long_description")

        alias = d.pop("alias")

        def _parse_download_group(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        download_group = _parse_download_group(d.pop("download_group", UNSET))

        path = d.pop("path", UNSET)

        def _parse_file_size_bytes(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        file_size_bytes = _parse_file_size_bytes(d.pop("file_size_bytes", UNSET))

        def _parse_index_file(
            data: object,
        ) -> DownloadFileIndexFile | list[DownloadFileIndexFile] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                index_file_type_0 = DownloadFileIndexFile.from_dict(data)

                return index_file_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, list):
                    raise TypeError()
                index_file_type_1 = []
                _index_file_type_1 = data
                for index_file_type_1_item_data in _index_file_type_1:
                    index_file_type_1_item = DownloadFileIndexFile.from_dict(
                        index_file_type_1_item_data
                    )

                    index_file_type_1.append(index_file_type_1_item)

                return index_file_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                DownloadFileIndexFile | list[DownloadFileIndexFile] | None | Unset, data
            )

        index_file = _parse_index_file(d.pop("index_file", UNSET))

        def _parse_parent_identifier(data: object) -> int | str | Unset:
            if isinstance(data, Unset):
                return data
            return cast(int | str | Unset, data)

        parent_identifier = _parse_parent_identifier(d.pop("parent_identifier", UNSET))

        def _parse_parent_is_private(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        parent_is_private = _parse_parent_is_private(d.pop("parent_is_private", UNSET))

        def _parse_parent_results_dir(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_results_dir = _parse_parent_results_dir(
            d.pop("parent_results_dir", UNSET)
        )

        def _parse_index_files(
            data: object,
        ) -> list[MGnifyDownloadFileIndexFile] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                index_files_type_0 = []
                _index_files_type_0 = data
                for index_files_type_0_item_data in _index_files_type_0:
                    index_files_type_0_item = MGnifyDownloadFileIndexFile.from_dict(
                        index_files_type_0_item_data
                    )

                    index_files_type_0.append(index_files_type_0_item)

                return index_files_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[MGnifyDownloadFileIndexFile] | None | Unset, data)

        index_files = _parse_index_files(d.pop("index_files", UNSET))

        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))

        m_gnify_study_download_file = cls(
            file_type=file_type,
            download_type=download_type,
            short_description=short_description,
            long_description=long_description,
            alias=alias,
            download_group=download_group,
            path=path,
            file_size_bytes=file_size_bytes,
            index_file=index_file,
            parent_identifier=parent_identifier,
            parent_is_private=parent_is_private,
            parent_results_dir=parent_results_dir,
            index_files=index_files,
            url=url,
        )

        m_gnify_study_download_file.additional_properties = d
        return m_gnify_study_download_file

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
