from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.europe_pmc_annotation import EuropePmcAnnotation


T = TypeVar("T", bound="EuropePmcAnnotationGroup")


@_attrs_define
class EuropePmcAnnotationGroup:
    """
    Attributes:
        annotation_type (str): Type (i.e. the concept) of the annotation
        title (str): Explanatory version of the annotation type
        description (str): Detailed description of the annotation type
        annotations (list[EuropePmcAnnotation]): List of annotations of the given type
    """

    annotation_type: str
    title: str
    description: str
    annotations: list[EuropePmcAnnotation]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        annotation_type = self.annotation_type

        title = self.title

        description = self.description

        annotations = []
        for annotations_item_data in self.annotations:
            annotations_item = annotations_item_data.to_dict()
            annotations.append(annotations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_type": annotation_type,
                "title": title,
                "description": description,
                "annotations": annotations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.europe_pmc_annotation import EuropePmcAnnotation

        d = dict(src_dict)
        annotation_type = d.pop("annotation_type")

        title = d.pop("title")

        description = d.pop("description")

        annotations = []
        _annotations = d.pop("annotations")
        for annotations_item_data in _annotations:
            annotations_item = EuropePmcAnnotation.from_dict(annotations_item_data)

            annotations.append(annotations_item)

        europe_pmc_annotation_group = cls(
            annotation_type=annotation_type,
            title=title,
            description=description,
            annotations=annotations,
        )

        europe_pmc_annotation_group.additional_properties = d
        return europe_pmc_annotation_group

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
