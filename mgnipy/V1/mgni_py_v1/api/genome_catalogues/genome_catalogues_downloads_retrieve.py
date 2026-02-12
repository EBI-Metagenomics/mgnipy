from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.genome_catalogue_download import GenomeCatalogueDownload
from ...models.genome_catalogues_downloads_retrieve_format import (
    GenomeCataloguesDownloadsRetrieveFormat,
)
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    catalogue_id: str,
    alias: str,
    *,
    format_: GenomeCataloguesDownloadsRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/genome-catalogues/{catalogue_id}/downloads/{alias}".format(
            catalogue_id=quote(str(catalogue_id), safe=""),
            alias=quote(str(alias), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GenomeCatalogueDownload | None:
    if response.status_code == 200:
        response_200 = GenomeCatalogueDownload.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GenomeCatalogueDownload]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    catalogue_id: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesDownloadsRetrieveFormat | Unset = UNSET,
) -> Response[GenomeCatalogueDownload]:
    """Retrieves a downloadable file for the genome catalogue
    Example:
    ---
    `
    /genome-catalogues/hgut-v1-0/downloads/phylo_tree.json`

    Args:
        catalogue_id (str):
        alias (str):
        format_ (GenomeCataloguesDownloadsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeCatalogueDownload]
    """

    kwargs = _get_kwargs(
        catalogue_id=catalogue_id,
        alias=alias,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    catalogue_id: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesDownloadsRetrieveFormat | Unset = UNSET,
) -> GenomeCatalogueDownload | None:
    """Retrieves a downloadable file for the genome catalogue
    Example:
    ---
    `
    /genome-catalogues/hgut-v1-0/downloads/phylo_tree.json`

    Args:
        catalogue_id (str):
        alias (str):
        format_ (GenomeCataloguesDownloadsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeCatalogueDownload
    """

    return sync_detailed(
        catalogue_id=catalogue_id,
        alias=alias,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    catalogue_id: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesDownloadsRetrieveFormat | Unset = UNSET,
) -> Response[GenomeCatalogueDownload]:
    """Retrieves a downloadable file for the genome catalogue
    Example:
    ---
    `
    /genome-catalogues/hgut-v1-0/downloads/phylo_tree.json`

    Args:
        catalogue_id (str):
        alias (str):
        format_ (GenomeCataloguesDownloadsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeCatalogueDownload]
    """

    kwargs = _get_kwargs(
        catalogue_id=catalogue_id,
        alias=alias,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    catalogue_id: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesDownloadsRetrieveFormat | Unset = UNSET,
) -> GenomeCatalogueDownload | None:
    """Retrieves a downloadable file for the genome catalogue
    Example:
    ---
    `
    /genome-catalogues/hgut-v1-0/downloads/phylo_tree.json`

    Args:
        catalogue_id (str):
        alias (str):
        format_ (GenomeCataloguesDownloadsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeCatalogueDownload
    """

    return (
        await asyncio_detailed(
            catalogue_id=catalogue_id,
            alias=alias,
            client=client,
            format_=format_,
        )
    ).parsed
