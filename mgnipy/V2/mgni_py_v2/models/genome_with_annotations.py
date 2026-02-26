from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.genome_with_annotations_annotations import GenomeWithAnnotationsAnnotations





T = TypeVar("T", bound="GenomeWithAnnotations")



@_attrs_define
class GenomeWithAnnotations:
    """ 
        Attributes:
            accession (str):
            annotations (GenomeWithAnnotationsAnnotations):
     """

    accession: str
    annotations: GenomeWithAnnotationsAnnotations
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.genome_with_annotations_annotations import GenomeWithAnnotationsAnnotations
        accession = self.accession

        annotations = self.annotations.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "accession": accession,
            "annotations": annotations,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.genome_with_annotations_annotations import GenomeWithAnnotationsAnnotations
        d = dict(src_dict)
        accession = d.pop("accession")

        annotations = GenomeWithAnnotationsAnnotations.from_dict(d.pop("annotations"))




        genome_with_annotations = cls(
            accession=accession,
            annotations=annotations,
        )


        genome_with_annotations.additional_properties = d
        return genome_with_annotations

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
