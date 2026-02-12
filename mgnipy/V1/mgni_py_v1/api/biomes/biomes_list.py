from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.biomes_list_format import BiomesListFormat
from ...models.paginated_biome_list import PaginatedBiomeList
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    *,
    filterbiome_id: str | Unset = UNSET,
    filterbiome_name: str | Unset = UNSET,
    filterdepth: str | Unset = UNSET,
    filterlineage: str | Unset = UNSET,
    format_: BiomesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["filter[biome_id]"] = filterbiome_id

    params["filter[biome_name]"] = filterbiome_name

    params["filter[depth]"] = filterdepth

    params["filter[lineage]"] = filterlineage

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/biomes",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedBiomeList | None:
    if response.status_code == 200:
        response_200 = PaginatedBiomeList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedBiomeList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    filterbiome_id: str | Unset = UNSET,
    filterbiome_name: str | Unset = UNSET,
    filterdepth: str | Unset = UNSET,
    filterlineage: str | Unset = UNSET,
    format_: BiomesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> Response[PaginatedBiomeList]:
    """Retrieves top level Biome nodes
    Example:
    ---
    `/biomes`

    Args:
        filterbiome_id (str | Unset):
        filterbiome_name (str | Unset):
        filterdepth (str | Unset):
        filterlineage (str | Unset):
        format_ (BiomesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedBiomeList]
    """

    kwargs = _get_kwargs(
        filterbiome_id=filterbiome_id,
        filterbiome_name=filterbiome_name,
        filterdepth=filterdepth,
        filterlineage=filterlineage,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    filterbiome_id: str | Unset = UNSET,
    filterbiome_name: str | Unset = UNSET,
    filterdepth: str | Unset = UNSET,
    filterlineage: str | Unset = UNSET,
    format_: BiomesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> PaginatedBiomeList | None:
    """Retrieves top level Biome nodes
    Example:
    ---
    `/biomes`

    Args:
        filterbiome_id (str | Unset):
        filterbiome_name (str | Unset):
        filterdepth (str | Unset):
        filterlineage (str | Unset):
        format_ (BiomesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedBiomeList
    """

    return sync_detailed(
        client=client,
        filterbiome_id=filterbiome_id,
        filterbiome_name=filterbiome_name,
        filterdepth=filterdepth,
        filterlineage=filterlineage,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    filterbiome_id: str | Unset = UNSET,
    filterbiome_name: str | Unset = UNSET,
    filterdepth: str | Unset = UNSET,
    filterlineage: str | Unset = UNSET,
    format_: BiomesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> Response[PaginatedBiomeList]:
    """Retrieves top level Biome nodes
    Example:
    ---
    `/biomes`

    Args:
        filterbiome_id (str | Unset):
        filterbiome_name (str | Unset):
        filterdepth (str | Unset):
        filterlineage (str | Unset):
        format_ (BiomesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedBiomeList]
    """

    kwargs = _get_kwargs(
        filterbiome_id=filterbiome_id,
        filterbiome_name=filterbiome_name,
        filterdepth=filterdepth,
        filterlineage=filterlineage,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    filterbiome_id: str | Unset = UNSET,
    filterbiome_name: str | Unset = UNSET,
    filterdepth: str | Unset = UNSET,
    filterlineage: str | Unset = UNSET,
    format_: BiomesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> PaginatedBiomeList | None:
    """Retrieves top level Biome nodes
    Example:
    ---
    `/biomes`

    Args:
        filterbiome_id (str | Unset):
        filterbiome_name (str | Unset):
        filterdepth (str | Unset):
        filterlineage (str | Unset):
        format_ (BiomesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedBiomeList
    """

    return (
        await asyncio_detailed(
            client=client,
            filterbiome_id=filterbiome_id,
            filterbiome_name=filterbiome_name,
            filterdepth=filterdepth,
            filterlineage=filterlineage,
            format_=format_,
            ordering=ordering,
            page=page,
            page_size=page_size,
            search=search,
        )
    ).parsed
