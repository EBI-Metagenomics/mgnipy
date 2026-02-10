from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.europe_pmc_annotation_tag import EuropePmcAnnotationTag


T = TypeVar("T", bound="EuropePmcAnnotationMention")


@_attrs_define
class EuropePmcAnnotationMention:
    """
    Attributes:
        exact (str): The exact text of the annotation in the text
        type_ (str): The type of the annotation
        tags (list[EuropePmcAnnotationTag]): A list of tags that associate the annotation with an ontology term
        id (None | str | Unset):
        postfix (None | str | Unset): The text immediately following the annotation
        prefix (None | str | Unset): The text immediately preceding the annotation
        provider (str | Unset): The provider of the annotation Default: 'Metagenomic'.
        section (None | str | Unset): The section of the text where the annotation occurs
    """

    exact: str
    type_: str
    tags: list[EuropePmcAnnotationTag]
    id: None | str | Unset = UNSET
    postfix: None | str | Unset = UNSET
    prefix: None | str | Unset = UNSET
    provider: str | Unset = "Metagenomic"
    section: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        exact = self.exact

        type_ = self.type_

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        postfix: None | str | Unset
        if isinstance(self.postfix, Unset):
            postfix = UNSET
        else:
            postfix = self.postfix

        prefix: None | str | Unset
        if isinstance(self.prefix, Unset):
            prefix = UNSET
        else:
            prefix = self.prefix

        provider = self.provider

        section: None | str | Unset
        if isinstance(self.section, Unset):
            section = UNSET
        else:
            section = self.section

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "exact": exact,
                "type": type_,
                "tags": tags,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if postfix is not UNSET:
            field_dict["postfix"] = postfix
        if prefix is not UNSET:
            field_dict["prefix"] = prefix
        if provider is not UNSET:
            field_dict["provider"] = provider
        if section is not UNSET:
            field_dict["section"] = section

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.europe_pmc_annotation_tag import EuropePmcAnnotationTag

        d = dict(src_dict)
        exact = d.pop("exact")

        type_ = d.pop("type")

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = EuropePmcAnnotationTag.from_dict(tags_item_data)

            tags.append(tags_item)

        def _parse_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_postfix(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        postfix = _parse_postfix(d.pop("postfix", UNSET))

        def _parse_prefix(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        prefix = _parse_prefix(d.pop("prefix", UNSET))

        provider = d.pop("provider", UNSET)

        def _parse_section(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        section = _parse_section(d.pop("section", UNSET))

        europe_pmc_annotation_mention = cls(
            exact=exact,
            type_=type_,
            tags=tags,
            id=id,
            postfix=postfix,
            prefix=prefix,
            provider=provider,
            section=section,
        )

        europe_pmc_annotation_mention.additional_properties = d
        return europe_pmc_annotation_mention

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
