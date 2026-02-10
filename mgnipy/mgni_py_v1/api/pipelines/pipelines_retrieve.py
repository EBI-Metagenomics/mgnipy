from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.pipeline import Pipeline
from ...models.pipelines_retrieve_format import PipelinesRetrieveFormat
from ...types import UNSET, Response, Unset


def _get_kwargs(
    release_version: str,
    *,
    format_: PipelinesRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/pipelines/{release_version}".format(
            release_version=quote(str(release_version), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Pipeline | None:
    if response.status_code == 200:
        response_200 = Pipeline.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Pipeline]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    release_version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelinesRetrieveFormat | Unset = UNSET,
) -> Response[Pipeline]:
    """Retrieves pipeline for the given version
    Example:
    ---
    `/pipelines/3.0`

    `/pipelines/3.0?include=tools` with tools

    Args:
        release_version (str):
        format_ (PipelinesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Pipeline]
    """

    kwargs = _get_kwargs(
        release_version=release_version,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    release_version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelinesRetrieveFormat | Unset = UNSET,
) -> Pipeline | None:
    """Retrieves pipeline for the given version
    Example:
    ---
    `/pipelines/3.0`

    `/pipelines/3.0?include=tools` with tools

    Args:
        release_version (str):
        format_ (PipelinesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Pipeline
    """

    return sync_detailed(
        release_version=release_version,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    release_version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelinesRetrieveFormat | Unset = UNSET,
) -> Response[Pipeline]:
    """Retrieves pipeline for the given version
    Example:
    ---
    `/pipelines/3.0`

    `/pipelines/3.0?include=tools` with tools

    Args:
        release_version (str):
        format_ (PipelinesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Pipeline]
    """

    kwargs = _get_kwargs(
        release_version=release_version,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    release_version: str,
    *,
    client: AuthenticatedClient,
    format_: PipelinesRetrieveFormat | Unset = UNSET,
) -> Pipeline | None:
    """Retrieves pipeline for the given version
    Example:
    ---
    `/pipelines/3.0`

    `/pipelines/3.0?include=tools` with tools

    Args:
        release_version (str):
        format_ (PipelinesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Pipeline
    """

    return (
        await asyncio_detailed(
            release_version=release_version,
            client=client,
            format_=format_,
        )
    ).parsed
