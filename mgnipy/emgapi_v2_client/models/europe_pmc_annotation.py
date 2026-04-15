from __future__ import annotations

from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.europe_pmc_annotation_mention import EuropePmcAnnotationMention


T = TypeVar("T", bound="EuropePmcAnnotation")


@_attrs_define
class EuropePmcAnnotation:
    """
    Attributes:
        annotation_text (str): Text of the annotation
        mentions (list[EuropePmcAnnotationMention]): List of occurrence where the annotation is mentioned in the
            publication
    """

    annotation_text: str
    mentions: list[EuropePmcAnnotationMention]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        annotation_text = self.annotation_text

        mentions = []
        for mentions_item_data in self.mentions:
            mentions_item = mentions_item_data.to_dict()
            mentions.append(mentions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_text": annotation_text,
                "mentions": mentions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.europe_pmc_annotation_mention import EuropePmcAnnotationMention

        d = dict(src_dict)
        annotation_text = d.pop("annotation_text")

        mentions = []
        _mentions = d.pop("mentions")
        for mentions_item_data in _mentions:
            mentions_item = EuropePmcAnnotationMention.from_dict(mentions_item_data)

            mentions.append(mentions_item)

        europe_pmc_annotation = cls(
            annotation_text=annotation_text,
            mentions=mentions,
        )

        europe_pmc_annotation.additional_properties = d
        return europe_pmc_annotation

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
