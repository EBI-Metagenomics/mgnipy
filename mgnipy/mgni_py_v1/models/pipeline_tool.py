from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PipelineTool")


@_attrs_define
class PipelineTool:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            id (str):
            url (str):
            tool_name (None | str):
            version (None | str):
            pipelines (str):
            description (None | str | Unset):
            web_link (None | str | Unset):
            exe_command (None | str | Unset):
            configuration_file (None | str | Unset):
            notes (None | str | Unset):
    """

    id: str
    url: str
    tool_name: None | str
    version: None | str
    pipelines: str
    description: None | str | Unset = UNSET
    web_link: None | str | Unset = UNSET
    exe_command: None | str | Unset = UNSET
    configuration_file: None | str | Unset = UNSET
    notes: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        url = self.url

        tool_name: None | str
        tool_name = self.tool_name

        version: None | str
        version = self.version

        pipelines = self.pipelines

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        web_link: None | str | Unset
        if isinstance(self.web_link, Unset):
            web_link = UNSET
        else:
            web_link = self.web_link

        exe_command: None | str | Unset
        if isinstance(self.exe_command, Unset):
            exe_command = UNSET
        else:
            exe_command = self.exe_command

        configuration_file: None | str | Unset
        if isinstance(self.configuration_file, Unset):
            configuration_file = UNSET
        else:
            configuration_file = self.configuration_file

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "url": url,
                "tool_name": tool_name,
                "version": version,
                "pipelines": pipelines,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if web_link is not UNSET:
            field_dict["web_link"] = web_link
        if exe_command is not UNSET:
            field_dict["exe_command"] = exe_command
        if configuration_file is not UNSET:
            field_dict["configuration_file"] = configuration_file
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        url = d.pop("url")

        def _parse_tool_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        tool_name = _parse_tool_name(d.pop("tool_name"))

        def _parse_version(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        version = _parse_version(d.pop("version"))

        pipelines = d.pop("pipelines")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_web_link(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        web_link = _parse_web_link(d.pop("web_link", UNSET))

        def _parse_exe_command(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        exe_command = _parse_exe_command(d.pop("exe_command", UNSET))

        def _parse_configuration_file(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        configuration_file = _parse_configuration_file(d.pop("configuration_file", UNSET))

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        pipeline_tool = cls(
            id=id,
            url=url,
            tool_name=tool_name,
            version=version,
            pipelines=pipelines,
            description=description,
            web_link=web_link,
            exe_command=exe_command,
            configuration_file=configuration_file,
            notes=notes,
        )

        pipeline_tool.additional_properties = d
        return pipeline_tool

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
