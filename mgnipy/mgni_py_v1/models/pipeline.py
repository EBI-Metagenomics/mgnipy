from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Pipeline")


@_attrs_define
class Pipeline:
    """Retrieve object with explicit fields. This is compatible with `include`
    although relationship has to be present in `fields`.

        Attributes:
            url (str):
            samples_count (int):
            analyses_count (int):
            analyses (str):
            samples (str):
            tools (str):
            changes (str):
            release_version (str):
            release_date (datetime.date):
            description (None | str | Unset):
    """

    url: str
    samples_count: int
    analyses_count: int
    analyses: str
    samples: str
    tools: str
    changes: str
    release_version: str
    release_date: datetime.date
    description: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        samples_count = self.samples_count

        analyses_count = self.analyses_count

        analyses = self.analyses

        samples = self.samples

        tools = self.tools

        changes = self.changes

        release_version = self.release_version

        release_date = self.release_date.isoformat()

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "samples_count": samples_count,
                "analyses_count": analyses_count,
                "analyses": analyses,
                "samples": samples,
                "tools": tools,
                "changes": changes,
                "release_version": release_version,
                "release_date": release_date,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        samples_count = d.pop("samples_count")

        analyses_count = d.pop("analyses_count")

        analyses = d.pop("analyses")

        samples = d.pop("samples")

        tools = d.pop("tools")

        changes = d.pop("changes")

        release_version = d.pop("release_version")

        release_date = isoparse(d.pop("release_date")).date()

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        pipeline = cls(
            url=url,
            samples_count=samples_count,
            analyses_count=analyses_count,
            analyses=analyses,
            samples=samples,
            tools=tools,
            changes=changes,
            release_version=release_version,
            release_date=release_date,
            description=description,
        )

        pipeline.additional_properties = d
        return pipeline

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
