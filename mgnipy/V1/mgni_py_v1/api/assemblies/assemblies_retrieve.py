from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.assemblies_retrieve_format import AssembliesRetrieveFormat
from ...models.assembly import Assembly
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    accession: str,
    *,
    format_: AssembliesRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/assemblies/{accession}".format(
            accession=quote(str(accession), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Assembly | None:
    if response.status_code == 200:
        response_200 = Assembly.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Assembly]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AssembliesRetrieveFormat | Unset = UNSET,
) -> Response[Assembly]:
    """Retrieves run for the given accession
    Example:
    ---
    `/assembly/ERZ477576`

    Args:
        accession (str):
        format_ (AssembliesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Assembly]
    """

    kwargs = _get_kwargs(
        accession=accession,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AssembliesRetrieveFormat | Unset = UNSET,
) -> Assembly | None:
    """Retrieves run for the given accession
    Example:
    ---
    `/assembly/ERZ477576`

    Args:
        accession (str):
        format_ (AssembliesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Assembly
    """

    return sync_detailed(
        accession=accession,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AssembliesRetrieveFormat | Unset = UNSET,
) -> Response[Assembly]:
    """Retrieves run for the given accession
    Example:
    ---
    `/assembly/ERZ477576`

    Args:
        accession (str):
        format_ (AssembliesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Assembly]
    """

    kwargs = _get_kwargs(
        accession=accession,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AssembliesRetrieveFormat | Unset = UNSET,
) -> Assembly | None:
    """Retrieves run for the given accession
    Example:
    ---
    `/assembly/ERZ477576`

    Args:
        accession (str):
        format_ (AssembliesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Assembly
    """

    return (
        await asyncio_detailed(
            accession=accession,
            client=client,
            format_=format_,
        )
    ).parsed
