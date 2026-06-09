from http import HTTPStatus
from typing import Any

import httpx

from mgnipy.emgapi_v2_client import errors
from mgnipy.emgapi_v2_client.client import (
    AuthenticatedClient,
    Client,
)
from mgnipy.emgapi_v2_client.types import Response


def _get_kwargs(
    url: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": url,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> bytes | None:
    if response.is_success:
        return response.content

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[bytes]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    url: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[bytes]:
    """
    Download raw content from a custom absolute URL.

    Parameters
    ----------
    url : str
        Fully-qualified URL (e.g. https://ftp.ebi.ac.uk/...fasta.gz).

    Returns
    -------
        Response[bytes]

    Raises
    ------
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    kwargs = _get_kwargs(
        url=url,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    url: str,
    *,
    client: AuthenticatedClient | Client,
) -> bytes | None:
    """
    Custom Endpoint

    Download raw content from a custom absolute URL.

    Parameters
    ----------
    url : str
        Fully-qualified URL (e.g. https://ftp.ebi.ac.uk/...fasta.gz).

    Returns
    -------
        Response[bytes]

    Raises
    ------
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    return sync_detailed(
        url=url,
        client=client,
    ).parsed


async def asyncio_detailed(
    url: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[bytes]:
    """
    Download raw content asynchronously from a custom absolute URL.

    Parameters
    ----------
    url : str
        Fully-qualified URL (e.g. https://ftp.ebi.ac.uk/...fasta.gz).

    Returns
    -------
        Response[bytes]

    Raises
    ------
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    kwargs = _get_kwargs(
        url=url,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    url: str,
    *,
    client: AuthenticatedClient | Client,
) -> bytes | None:
    """
    Download raw content asynchronously from a custom absolute URL.

    Parameters
    ----------
    url : str
        Fully-qualified URL (e.g. https://ftp.ebi.ac.uk/...fasta.gz).

    Returns
    -------
        Response[bytes]

    Raises
    ------
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    return (
        await asyncio_detailed(
            url=url,
            client=client,
        )
    ).parsed
