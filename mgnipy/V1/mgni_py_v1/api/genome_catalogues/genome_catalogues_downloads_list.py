from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.genome_catalogues_downloads_list_format import (
    GenomeCataloguesDownloadsListFormat,
)
from ...models.paginated_genome_catalogue_download_list import (
    PaginatedGenomeCatalogueDownloadList,
)
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    catalogue_id: str,
    *,
    format_: GenomeCataloguesDownloadsListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/genome-catalogues/{catalogue_id}/downloads".format(
            catalogue_id=quote(str(catalogue_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedGenomeCatalogueDownloadList | None:
    if response.status_code == 200:
        response_200 = PaginatedGenomeCatalogueDownloadList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedGenomeCatalogueDownloadList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    catalogue_id: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesDownloadsListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedGenomeCatalogueDownloadList]:
    """List a queryset.

    Args:
        catalogue_id (str):
        format_ (GenomeCataloguesDownloadsListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedGenomeCatalogueDownloadList]
    """

    kwargs = _get_kwargs(
        catalogue_id=catalogue_id,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    catalogue_id: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesDownloadsListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedGenomeCatalogueDownloadList | None:
    """List a queryset.

    Args:
        catalogue_id (str):
        format_ (GenomeCataloguesDownloadsListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedGenomeCatalogueDownloadList
    """

    return sync_detailed(
        catalogue_id=catalogue_id,
        client=client,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    catalogue_id: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesDownloadsListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedGenomeCatalogueDownloadList]:
    """List a queryset.

    Args:
        catalogue_id (str):
        format_ (GenomeCataloguesDownloadsListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedGenomeCatalogueDownloadList]
    """

    kwargs = _get_kwargs(
        catalogue_id=catalogue_id,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    catalogue_id: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesDownloadsListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedGenomeCatalogueDownloadList | None:
    """List a queryset.

    Args:
        catalogue_id (str):
        format_ (GenomeCataloguesDownloadsListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedGenomeCatalogueDownloadList
    """

    return (
        await asyncio_detailed(
            catalogue_id=catalogue_id,
            client=client,
            format_=format_,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )
    ).parsed
