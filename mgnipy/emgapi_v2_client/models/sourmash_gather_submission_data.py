from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.sourmash_gather_submission_data_children_ids import SourmashGatherSubmissionDataChildrenIds





T = TypeVar("T", bound="SourmashGatherSubmissionData")



@_attrs_define
class SourmashGatherSubmissionData:
    """ 
        Attributes:
            message (str):
            job_id (str):
            status (str):
            children_ids (SourmashGatherSubmissionDataChildrenIds):
            signatures_received (list[str]):
            requested_catalogues (list[str]):
            status_url (str):
     """

    message: str
    job_id: str
    status: str
    children_ids: SourmashGatherSubmissionDataChildrenIds
    signatures_received: list[str]
    requested_catalogues: list[str]
    status_url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.sourmash_gather_submission_data_children_ids import SourmashGatherSubmissionDataChildrenIds
        message = self.message

        job_id = self.job_id

        status = self.status

        children_ids = self.children_ids.to_dict()

        signatures_received = self.signatures_received



        requested_catalogues = self.requested_catalogues



        status_url = self.status_url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "message": message,
            "job_id": job_id,
            "status": status,
            "children_ids": children_ids,
            "signatures_received": signatures_received,
            "requested_catalogues": requested_catalogues,
            "status_url": status_url,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sourmash_gather_submission_data_children_ids import SourmashGatherSubmissionDataChildrenIds
        d = dict(src_dict)
        message = d.pop("message")

        job_id = d.pop("job_id")

        status = d.pop("status")

        children_ids = SourmashGatherSubmissionDataChildrenIds.from_dict(d.pop("children_ids"))




        signatures_received = cast(list[str], d.pop("signatures_received"))


        requested_catalogues = cast(list[str], d.pop("requested_catalogues"))


        status_url = d.pop("status_url")

        sourmash_gather_submission_data = cls(
            message=message,
            job_id=job_id,
            status=status,
            children_ids=children_ids,
            signatures_received=signatures_received,
            requested_catalogues=requested_catalogues,
            status_url=status_url,
        )


        sourmash_gather_submission_data.additional_properties = d
        return sourmash_gather_submission_data

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
