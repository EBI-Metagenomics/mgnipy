from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.studies_recent_retrieve_format import StudiesRecentRetrieveFormat
from ...models.study import Study
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    *,
    format_: StudiesRecentRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/studies/recent",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Study | None:
    if response.status_code == 200:
        response_200 = Study.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Study]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    format_: StudiesRecentRetrieveFormat | Unset = UNSET,
) -> Response[Study]:
    """Retrieve 20 most recent studies
    Example:
    ---
    `/studies/recent`

    Args:
        format_ (StudiesRecentRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Study]
    """

    kwargs = _get_kwargs(
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    format_: StudiesRecentRetrieveFormat | Unset = UNSET,
) -> Study | None:
    """Retrieve 20 most recent studies
    Example:
    ---
    `/studies/recent`

    Args:
        format_ (StudiesRecentRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Study
    """

    return sync_detailed(
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    format_: StudiesRecentRetrieveFormat | Unset = UNSET,
) -> Response[Study]:
    """Retrieve 20 most recent studies
    Example:
    ---
    `/studies/recent`

    Args:
        format_ (StudiesRecentRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Study]
    """

    kwargs = _get_kwargs(
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    format_: StudiesRecentRetrieveFormat | Unset = UNSET,
) -> Study | None:
    """Retrieve 20 most recent studies
    Example:
    ---
    `/studies/recent`

    Args:
        format_ (StudiesRecentRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Study
    """

    return (
        await asyncio_detailed(
            client=client,
            format_=format_,
        )
    ).parsed
