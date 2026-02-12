from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.genome_download import GenomeDownload
from ...models.genomes_downloads_retrieve_format import GenomesDownloadsRetrieveFormat
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    accession: str,
    alias: str,
    *,
    format_: GenomesDownloadsRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/genomes/{accession}/downloads/{alias}".format(
            accession=quote(str(accession), safe=""),
            alias=quote(str(alias), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GenomeDownload | None:
    if response.status_code == 200:
        response_200 = GenomeDownload.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GenomeDownload]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    accession: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: GenomesDownloadsRetrieveFormat | Unset = UNSET,
) -> Response[GenomeDownload]:
    """List a queryset.

    Args:
        accession (str):
        alias (str):
        format_ (GenomesDownloadsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeDownload]
    """

    kwargs = _get_kwargs(
        accession=accession,
        alias=alias,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    accession: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: GenomesDownloadsRetrieveFormat | Unset = UNSET,
) -> GenomeDownload | None:
    """List a queryset.

    Args:
        accession (str):
        alias (str):
        format_ (GenomesDownloadsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeDownload
    """

    return sync_detailed(
        accession=accession,
        alias=alias,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    accession: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: GenomesDownloadsRetrieveFormat | Unset = UNSET,
) -> Response[GenomeDownload]:
    """List a queryset.

    Args:
        accession (str):
        alias (str):
        format_ (GenomesDownloadsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeDownload]
    """

    kwargs = _get_kwargs(
        accession=accession,
        alias=alias,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: GenomesDownloadsRetrieveFormat | Unset = UNSET,
) -> GenomeDownload | None:
    """List a queryset.

    Args:
        accession (str):
        alias (str):
        format_ (GenomesDownloadsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeDownload
    """

    return (
        await asyncio_detailed(
            accession=accession,
            alias=alias,
            client=client,
            format_=format_,
        )
    ).parsed
