from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.biomes_genome_catalogues_list_format import (
    BiomesGenomeCataloguesListFormat,
)
from ...models.paginated_genome_catalogue_list import PaginatedGenomeCatalogueList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    lineage: str,
    *,
    format_: BiomesGenomeCataloguesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

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
        "url": "/v1/biomes/{lineage}/genome-catalogues".format(
            lineage=quote(str(lineage), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedGenomeCatalogueList | None:
    if response.status_code == 200:
        response_200 = PaginatedGenomeCatalogueList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedGenomeCatalogueList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    lineage: str,
    *,
    client: AuthenticatedClient,
    format_: BiomesGenomeCataloguesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> Response[PaginatedGenomeCatalogueList]:
    """Retrieves list of genome catalogues for the given biome
    Example:
    ---
    `/biomes/root:Environmental:Aquatic/genome-catalogues` retrieve genome
    catalogues for the aquatic biome

    Filter by:
    ---
    `/biomes/root:Environmental:Aquatic/genome-catalogues?name=fishes`
    filtered by catalogue name

    Args:
        lineage (str):
        format_ (BiomesGenomeCataloguesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedGenomeCatalogueList]
    """

    kwargs = _get_kwargs(
        lineage=lineage,
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
    lineage: str,
    *,
    client: AuthenticatedClient,
    format_: BiomesGenomeCataloguesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> PaginatedGenomeCatalogueList | None:
    """Retrieves list of genome catalogues for the given biome
    Example:
    ---
    `/biomes/root:Environmental:Aquatic/genome-catalogues` retrieve genome
    catalogues for the aquatic biome

    Filter by:
    ---
    `/biomes/root:Environmental:Aquatic/genome-catalogues?name=fishes`
    filtered by catalogue name

    Args:
        lineage (str):
        format_ (BiomesGenomeCataloguesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedGenomeCatalogueList
    """

    return sync_detailed(
        lineage=lineage,
        client=client,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
    ).parsed


async def asyncio_detailed(
    lineage: str,
    *,
    client: AuthenticatedClient,
    format_: BiomesGenomeCataloguesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> Response[PaginatedGenomeCatalogueList]:
    """Retrieves list of genome catalogues for the given biome
    Example:
    ---
    `/biomes/root:Environmental:Aquatic/genome-catalogues` retrieve genome
    catalogues for the aquatic biome

    Filter by:
    ---
    `/biomes/root:Environmental:Aquatic/genome-catalogues?name=fishes`
    filtered by catalogue name

    Args:
        lineage (str):
        format_ (BiomesGenomeCataloguesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedGenomeCatalogueList]
    """

    kwargs = _get_kwargs(
        lineage=lineage,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    lineage: str,
    *,
    client: AuthenticatedClient,
    format_: BiomesGenomeCataloguesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> PaginatedGenomeCatalogueList | None:
    """Retrieves list of genome catalogues for the given biome
    Example:
    ---
    `/biomes/root:Environmental:Aquatic/genome-catalogues` retrieve genome
    catalogues for the aquatic biome

    Filter by:
    ---
    `/biomes/root:Environmental:Aquatic/genome-catalogues?name=fishes`
    filtered by catalogue name

    Args:
        lineage (str):
        format_ (BiomesGenomeCataloguesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedGenomeCatalogueList
    """

    return (
        await asyncio_detailed(
            lineage=lineage,
            client=client,
            format_=format_,
            ordering=ordering,
            page=page,
            page_size=page_size,
            search=search,
        )
    ).parsed
