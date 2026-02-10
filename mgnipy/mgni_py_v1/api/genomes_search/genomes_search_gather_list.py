from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.genomes_search_gather_list_format import GenomesSearchGatherListFormat
from ...models.paginated_genome_upload_search_list import (
    PaginatedGenomeUploadSearchList,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    format_: GenomesSearchGatherListFormat | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["page"] = page

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/genomes-search/gather",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedGenomeUploadSearchList | None:
    if response.status_code == 200:
        response_200 = PaginatedGenomeUploadSearchList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedGenomeUploadSearchList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    format_: GenomesSearchGatherListFormat | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedGenomeUploadSearchList]:
    """
    Args:
        format_ (GenomesSearchGatherListFormat | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedGenomeUploadSearchList]
    """

    kwargs = _get_kwargs(
        format_=format_,
        page=page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    format_: GenomesSearchGatherListFormat | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedGenomeUploadSearchList | None:
    """
    Args:
        format_ (GenomesSearchGatherListFormat | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedGenomeUploadSearchList
    """

    return sync_detailed(
        client=client,
        format_=format_,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    format_: GenomesSearchGatherListFormat | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedGenomeUploadSearchList]:
    """
    Args:
        format_ (GenomesSearchGatherListFormat | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedGenomeUploadSearchList]
    """

    kwargs = _get_kwargs(
        format_=format_,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    format_: GenomesSearchGatherListFormat | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedGenomeUploadSearchList | None:
    """
    Args:
        format_ (GenomesSearchGatherListFormat | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedGenomeUploadSearchList
    """

    return (
        await asyncio_detailed(
            client=client,
            format_=format_,
            page=page,
            page_size=page_size,
        )
    ).parsed
