from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.experiment_type import ExperimentType
from ...models.experiment_types_retrieve_format import ExperimentTypesRetrieveFormat
from ...types import UNSET, Response, Unset


def _get_kwargs(
    experiment_type: str,
    *,
    format_: ExperimentTypesRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/experiment-types/{experiment_type}".format(
            experiment_type=quote(str(experiment_type), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ExperimentType | None:
    if response.status_code == 200:
        response_200 = ExperimentType.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ExperimentType]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    experiment_type: str,
    *,
    client: AuthenticatedClient,
    format_: ExperimentTypesRetrieveFormat | Unset = UNSET,
) -> Response[ExperimentType]:
    """Retrieves experiment type for the given id

    Args:
        experiment_type (str):
        format_ (ExperimentTypesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ExperimentType]
    """

    kwargs = _get_kwargs(
        experiment_type=experiment_type,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    experiment_type: str,
    *,
    client: AuthenticatedClient,
    format_: ExperimentTypesRetrieveFormat | Unset = UNSET,
) -> ExperimentType | None:
    """Retrieves experiment type for the given id

    Args:
        experiment_type (str):
        format_ (ExperimentTypesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ExperimentType
    """

    return sync_detailed(
        experiment_type=experiment_type,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    experiment_type: str,
    *,
    client: AuthenticatedClient,
    format_: ExperimentTypesRetrieveFormat | Unset = UNSET,
) -> Response[ExperimentType]:
    """Retrieves experiment type for the given id

    Args:
        experiment_type (str):
        format_ (ExperimentTypesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ExperimentType]
    """

    kwargs = _get_kwargs(
        experiment_type=experiment_type,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    experiment_type: str,
    *,
    client: AuthenticatedClient,
    format_: ExperimentTypesRetrieveFormat | Unset = UNSET,
) -> ExperimentType | None:
    """Retrieves experiment type for the given id

    Args:
        experiment_type (str):
        format_ (ExperimentTypesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ExperimentType
    """

    return (
        await asyncio_detailed(
            experiment_type=experiment_type,
            client=client,
            format_=format_,
        )
    ).parsed
