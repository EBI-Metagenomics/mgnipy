from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

T = TypeVar("T", bound="SourmashTaskResult")


@_attrs_define
class SourmashTaskResult:
    """
    Attributes:
        overlap (None | str | Unset):
        p_query (None | str | Unset):
        p_match (None | str | Unset):
        match (None | str | Unset):
        catalog (None | str | Unset):
        query_filename (None | str | Unset):
        md5_name (None | str | Unset):
        matches (int | None | Unset):
        status (None | str | Unset):
    """

    overlap: None | str | Unset = UNSET
    p_query: None | str | Unset = UNSET
    p_match: None | str | Unset = UNSET
    match: None | str | Unset = UNSET
    catalog: None | str | Unset = UNSET
    query_filename: None | str | Unset = UNSET
    md5_name: None | str | Unset = UNSET
    matches: int | None | Unset = UNSET
    status: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        overlap: None | str | Unset
        if isinstance(self.overlap, Unset):
            overlap = UNSET
        else:
            overlap = self.overlap

        p_query: None | str | Unset
        if isinstance(self.p_query, Unset):
            p_query = UNSET
        else:
            p_query = self.p_query

        p_match: None | str | Unset
        if isinstance(self.p_match, Unset):
            p_match = UNSET
        else:
            p_match = self.p_match

        match: None | str | Unset
        if isinstance(self.match, Unset):
            match = UNSET
        else:
            match = self.match

        catalog: None | str | Unset
        if isinstance(self.catalog, Unset):
            catalog = UNSET
        else:
            catalog = self.catalog

        query_filename: None | str | Unset
        if isinstance(self.query_filename, Unset):
            query_filename = UNSET
        else:
            query_filename = self.query_filename

        md5_name: None | str | Unset
        if isinstance(self.md5_name, Unset):
            md5_name = UNSET
        else:
            md5_name = self.md5_name

        matches: int | None | Unset
        if isinstance(self.matches, Unset):
            matches = UNSET
        else:
            matches = self.matches

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if overlap is not UNSET:
            field_dict["overlap"] = overlap
        if p_query is not UNSET:
            field_dict["p_query"] = p_query
        if p_match is not UNSET:
            field_dict["p_match"] = p_match
        if match is not UNSET:
            field_dict["match"] = match
        if catalog is not UNSET:
            field_dict["catalog"] = catalog
        if query_filename is not UNSET:
            field_dict["query_filename"] = query_filename
        if md5_name is not UNSET:
            field_dict["md5_name"] = md5_name
        if matches is not UNSET:
            field_dict["matches"] = matches
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_overlap(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        overlap = _parse_overlap(d.pop("overlap", UNSET))

        def _parse_p_query(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        p_query = _parse_p_query(d.pop("p_query", UNSET))

        def _parse_p_match(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        p_match = _parse_p_match(d.pop("p_match", UNSET))

        def _parse_match(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        match = _parse_match(d.pop("match", UNSET))

        def _parse_catalog(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        catalog = _parse_catalog(d.pop("catalog", UNSET))

        def _parse_query_filename(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        query_filename = _parse_query_filename(d.pop("query_filename", UNSET))

        def _parse_md5_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        md5_name = _parse_md5_name(d.pop("md5_name", UNSET))

        def _parse_matches(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        matches = _parse_matches(d.pop("matches", UNSET))

        def _parse_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        sourmash_task_result = cls(
            overlap=overlap,
            p_query=p_query,
            p_match=p_match,
            match=match,
            catalog=catalog,
            query_filename=query_filename,
            md5_name=md5_name,
            matches=matches,
            status=status,
        )

        sourmash_task_result.additional_properties = d
        return sourmash_task_result

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
