from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sourmash_task_result import SourmashTaskResult


T = TypeVar("T", bound="SourmashGatherSignatureStatus")


@_attrs_define
class SourmashGatherSignatureStatus:
    """
    Attributes:
        job_id (str):
        status (str):
        filename (None | str | Unset):
        result (None | SourmashTaskResult | Unset):
        results_url (None | str | Unset):
        catalogue (None | str | Unset):
        reason (None | str | Unset):
        position_in_queue (int | None | Unset):
    """

    job_id: str
    status: str
    filename: None | str | Unset = UNSET
    result: None | SourmashTaskResult | Unset = UNSET
    results_url: None | str | Unset = UNSET
    catalogue: None | str | Unset = UNSET
    reason: None | str | Unset = UNSET
    position_in_queue: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.sourmash_task_result import SourmashTaskResult

        job_id = self.job_id

        status = self.status

        filename: None | str | Unset
        if isinstance(self.filename, Unset):
            filename = UNSET
        else:
            filename = self.filename

        result: dict[str, Any] | None | Unset
        if isinstance(self.result, Unset):
            result = UNSET
        elif isinstance(self.result, SourmashTaskResult):
            result = self.result.to_dict()
        else:
            result = self.result

        results_url: None | str | Unset
        if isinstance(self.results_url, Unset):
            results_url = UNSET
        else:
            results_url = self.results_url

        catalogue: None | str | Unset
        if isinstance(self.catalogue, Unset):
            catalogue = UNSET
        else:
            catalogue = self.catalogue

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        position_in_queue: int | None | Unset
        if isinstance(self.position_in_queue, Unset):
            position_in_queue = UNSET
        else:
            position_in_queue = self.position_in_queue

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job_id": job_id,
                "status": status,
            }
        )
        if filename is not UNSET:
            field_dict["filename"] = filename
        if result is not UNSET:
            field_dict["result"] = result
        if results_url is not UNSET:
            field_dict["results_url"] = results_url
        if catalogue is not UNSET:
            field_dict["catalogue"] = catalogue
        if reason is not UNSET:
            field_dict["reason"] = reason
        if position_in_queue is not UNSET:
            field_dict["position_in_queue"] = position_in_queue

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sourmash_task_result import SourmashTaskResult

        d = dict(src_dict)
        job_id = d.pop("job_id")

        status = d.pop("status")

        def _parse_filename(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        filename = _parse_filename(d.pop("filename", UNSET))

        def _parse_result(data: object) -> None | SourmashTaskResult | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_type_0 = SourmashTaskResult.from_dict(data)

                return result_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SourmashTaskResult | Unset, data)

        result = _parse_result(d.pop("result", UNSET))

        def _parse_results_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        results_url = _parse_results_url(d.pop("results_url", UNSET))

        def _parse_catalogue(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        catalogue = _parse_catalogue(d.pop("catalogue", UNSET))

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        def _parse_position_in_queue(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        position_in_queue = _parse_position_in_queue(d.pop("position_in_queue", UNSET))

        sourmash_gather_signature_status = cls(
            job_id=job_id,
            status=status,
            filename=filename,
            result=result,
            results_url=results_url,
            catalogue=catalogue,
            reason=reason,
            position_in_queue=position_in_queue,
        )

        sourmash_gather_signature_status.additional_properties = d
        return sourmash_gather_signature_status

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
