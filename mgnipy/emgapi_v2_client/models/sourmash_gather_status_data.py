from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sourmash_gather_signature_status import SourmashGatherSignatureStatus


T = TypeVar("T", bound="SourmashGatherStatusData")


@_attrs_define
class SourmashGatherStatusData:
    """
    Attributes:
        group_id (str):
        status (str):
        signatures (list[SourmashGatherSignatureStatus]):
        worker_status (str):
        results_url (None | str | Unset):
    """

    group_id: str
    status: str
    signatures: list[SourmashGatherSignatureStatus]
    worker_status: str
    results_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group_id = self.group_id

        status = self.status

        signatures = []
        for signatures_item_data in self.signatures:
            signatures_item = signatures_item_data.to_dict()
            signatures.append(signatures_item)

        worker_status = self.worker_status

        results_url: None | str | Unset
        if isinstance(self.results_url, Unset):
            results_url = UNSET
        else:
            results_url = self.results_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "group_id": group_id,
                "status": status,
                "signatures": signatures,
                "worker_status": worker_status,
            }
        )
        if results_url is not UNSET:
            field_dict["results_url"] = results_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sourmash_gather_signature_status import (
            SourmashGatherSignatureStatus,
        )

        d = dict(src_dict)
        group_id = d.pop("group_id")

        status = d.pop("status")

        signatures = []
        _signatures = d.pop("signatures")
        for signatures_item_data in _signatures:
            signatures_item = SourmashGatherSignatureStatus.from_dict(
                signatures_item_data
            )

            signatures.append(signatures_item)

        worker_status = d.pop("worker_status")

        def _parse_results_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        results_url = _parse_results_url(d.pop("results_url", UNSET))

        sourmash_gather_status_data = cls(
            group_id=group_id,
            status=status,
            signatures=signatures,
            worker_status=worker_status,
            results_url=results_url,
        )

        sourmash_gather_status_data.additional_properties = d
        return sourmash_gather_status_data

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
