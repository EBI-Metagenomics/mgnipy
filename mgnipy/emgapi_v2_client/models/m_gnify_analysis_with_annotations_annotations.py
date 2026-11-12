from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.m_gnify_analysis_typed_annotation import MGnifyAnalysisTypedAnnotation
  from ..models.m_gnify_analysis_with_annotations_annotations_additional_property_type_1 import MGnifyAnalysisWithAnnotationsAnnotationsAdditionalPropertyType1





T = TypeVar("T", bound="MGnifyAnalysisWithAnnotationsAnnotations")



@_attrs_define
class MGnifyAnalysisWithAnnotationsAnnotations:
    """ 
     """

    additional_properties: dict[str, list[MGnifyAnalysisTypedAnnotation] | MGnifyAnalysisWithAnnotationsAnnotationsAdditionalPropertyType1] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.m_gnify_analysis_with_annotations_annotations_additional_property_type_1 import MGnifyAnalysisWithAnnotationsAnnotationsAdditionalPropertyType1
        from ..models.m_gnify_analysis_typed_annotation import MGnifyAnalysisTypedAnnotation
        
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            
            if isinstance(prop, list):
                field_dict[prop_name] = []
                for additional_property_type_0_item_data in prop:
                    additional_property_type_0_item = additional_property_type_0_item_data.to_dict()
                    field_dict[prop_name].append(additional_property_type_0_item)


            else:
                field_dict[prop_name] = prop.to_dict()



        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.m_gnify_analysis_typed_annotation import MGnifyAnalysisTypedAnnotation
        from ..models.m_gnify_analysis_with_annotations_annotations_additional_property_type_1 import MGnifyAnalysisWithAnnotationsAnnotationsAdditionalPropertyType1
        d = dict(src_dict)
        m_gnify_analysis_with_annotations_annotations = cls(
        )


        additional_properties = {}
        for prop_name, prop_dict in d.items():
            def _parse_additional_property(data: object) -> list[MGnifyAnalysisTypedAnnotation] | MGnifyAnalysisWithAnnotationsAnnotationsAdditionalPropertyType1:
                try:
                    if not isinstance(data, list):
                        raise TypeError()
                    additional_property_type_0 = []
                    _additional_property_type_0 = data
                    for additional_property_type_0_item_data in (_additional_property_type_0):
                        additional_property_type_0_item = MGnifyAnalysisTypedAnnotation.from_dict(additional_property_type_0_item_data)



                        additional_property_type_0.append(additional_property_type_0_item)

                    return additional_property_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                additional_property_type_1 = MGnifyAnalysisWithAnnotationsAnnotationsAdditionalPropertyType1.from_dict(data)



                return additional_property_type_1

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        m_gnify_analysis_with_annotations_annotations.additional_properties = additional_properties
        return m_gnify_analysis_with_annotations_annotations

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> list[MGnifyAnalysisTypedAnnotation] | MGnifyAnalysisWithAnnotationsAnnotationsAdditionalPropertyType1:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: list[MGnifyAnalysisTypedAnnotation] | MGnifyAnalysisWithAnnotationsAnnotationsAdditionalPropertyType1) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
