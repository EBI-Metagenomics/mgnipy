from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.europe_pmc_annotation_group import EuropePmcAnnotationGroup





T = TypeVar("T", bound="PublicationAnnotations")



@_attrs_define
class PublicationAnnotations:
    """ 
        Attributes:
            sample_processing (list[EuropePmcAnnotationGroup]): List of sample processing annotations
            other (list[EuropePmcAnnotationGroup]): List of other annotations
     """

    sample_processing: list[EuropePmcAnnotationGroup]
    other: list[EuropePmcAnnotationGroup]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.europe_pmc_annotation_group import EuropePmcAnnotationGroup
        sample_processing = []
        for sample_processing_item_data in self.sample_processing:
            sample_processing_item = sample_processing_item_data.to_dict()
            sample_processing.append(sample_processing_item)



        other = []
        for other_item_data in self.other:
            other_item = other_item_data.to_dict()
            other.append(other_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "sample_processing": sample_processing,
            "other": other,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.europe_pmc_annotation_group import EuropePmcAnnotationGroup
        d = dict(src_dict)
        sample_processing = []
        _sample_processing = d.pop("sample_processing")
        for sample_processing_item_data in (_sample_processing):
            sample_processing_item = EuropePmcAnnotationGroup.from_dict(sample_processing_item_data)



            sample_processing.append(sample_processing_item)


        other = []
        _other = d.pop("other")
        for other_item_data in (_other):
            other_item = EuropePmcAnnotationGroup.from_dict(other_item_data)



            other.append(other_item)


        publication_annotations = cls(
            sample_processing=sample_processing,
            other=other,
        )


        publication_annotations.additional_properties = d
        return publication_annotations

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
