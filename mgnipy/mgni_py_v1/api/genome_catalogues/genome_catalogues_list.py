import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.genome_catalogues_list_format import GenomeCataloguesListFormat
from ...models.paginated_genome_catalogue_list import PaginatedGenomeCatalogueList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    biome_biome_name: str | Unset = UNSET,
    biome_biome_name_icontains: str | Unset = UNSET,
    catalogue_id: str | Unset = UNSET,
    description: str | Unset = UNSET,
    description_icontains: str | Unset = UNSET,
    format_: GenomeCataloguesListFormat | Unset = UNSET,
    last_update: datetime.datetime | Unset = UNSET,
    last_update_gt: datetime.datetime | Unset = UNSET,
    last_update_lt: datetime.datetime | Unset = UNSET,
    lineage: str | Unset = UNSET,
    name: str | Unset = UNSET,
    name_icontains: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["biome__biome_name"] = biome_biome_name

    params["biome__biome_name__icontains"] = biome_biome_name_icontains

    params["catalogue_id"] = catalogue_id

    params["description"] = description

    params["description__icontains"] = description_icontains

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    json_last_update: str | Unset = UNSET
    if not isinstance(last_update, Unset):
        json_last_update = last_update.isoformat()
    params["last_update"] = json_last_update

    json_last_update_gt: str | Unset = UNSET
    if not isinstance(last_update_gt, Unset):
        json_last_update_gt = last_update_gt.isoformat()
    params["last_update__gt"] = json_last_update_gt

    json_last_update_lt: str | Unset = UNSET
    if not isinstance(last_update_lt, Unset):
        json_last_update_lt = last_update_lt.isoformat()
    params["last_update__lt"] = json_last_update_lt

    params["lineage"] = lineage

    params["name"] = name

    params["name__icontains"] = name_icontains

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/genome-catalogues",
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
    *,
    client: AuthenticatedClient,
    biome_biome_name: str | Unset = UNSET,
    biome_biome_name_icontains: str | Unset = UNSET,
    catalogue_id: str | Unset = UNSET,
    description: str | Unset = UNSET,
    description_icontains: str | Unset = UNSET,
    format_: GenomeCataloguesListFormat | Unset = UNSET,
    last_update: datetime.datetime | Unset = UNSET,
    last_update_gt: datetime.datetime | Unset = UNSET,
    last_update_lt: datetime.datetime | Unset = UNSET,
    lineage: str | Unset = UNSET,
    name: str | Unset = UNSET,
    name_icontains: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> Response[PaginatedGenomeCatalogueList]:
    """Retrieves list of genome catalogues
    Example:
    ---
    `/genome-catalogues` retrieves list of all genome catalogues

    `/genome-catalogues?ordering=last_update` ordered by age of catalogue

    Filter by:
    ---
    `/genome-catalogues?last_update__gt=2021-01-01`

    Biome lineage:
    `/genome-catalogues?lineage=root:Environmental:Aquatic:Marine`

    Case-insensitive search of biome name:
    `/genome-catalogues?biome__biome_name__icontains=marine`

    `/genome-catalogues?description__icontains=arctic`

    Search for:
    ---
    name, description, biome name, etc.

    `/genome-catalogues?search=intestine`

    Args:
        biome_biome_name (str | Unset):
        biome_biome_name_icontains (str | Unset):
        catalogue_id (str | Unset):
        description (str | Unset):
        description_icontains (str | Unset):
        format_ (GenomeCataloguesListFormat | Unset):
        last_update (datetime.datetime | Unset):
        last_update_gt (datetime.datetime | Unset):
        last_update_lt (datetime.datetime | Unset):
        lineage (str | Unset):
        name (str | Unset):
        name_icontains (str | Unset):
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
        biome_biome_name=biome_biome_name,
        biome_biome_name_icontains=biome_biome_name_icontains,
        catalogue_id=catalogue_id,
        description=description,
        description_icontains=description_icontains,
        format_=format_,
        last_update=last_update,
        last_update_gt=last_update_gt,
        last_update_lt=last_update_lt,
        lineage=lineage,
        name=name,
        name_icontains=name_icontains,
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
    biome_biome_name: str | Unset = UNSET,
    biome_biome_name_icontains: str | Unset = UNSET,
    catalogue_id: str | Unset = UNSET,
    description: str | Unset = UNSET,
    description_icontains: str | Unset = UNSET,
    format_: GenomeCataloguesListFormat | Unset = UNSET,
    last_update: datetime.datetime | Unset = UNSET,
    last_update_gt: datetime.datetime | Unset = UNSET,
    last_update_lt: datetime.datetime | Unset = UNSET,
    lineage: str | Unset = UNSET,
    name: str | Unset = UNSET,
    name_icontains: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> PaginatedGenomeCatalogueList | None:
    """Retrieves list of genome catalogues
    Example:
    ---
    `/genome-catalogues` retrieves list of all genome catalogues

    `/genome-catalogues?ordering=last_update` ordered by age of catalogue

    Filter by:
    ---
    `/genome-catalogues?last_update__gt=2021-01-01`

    Biome lineage:
    `/genome-catalogues?lineage=root:Environmental:Aquatic:Marine`

    Case-insensitive search of biome name:
    `/genome-catalogues?biome__biome_name__icontains=marine`

    `/genome-catalogues?description__icontains=arctic`

    Search for:
    ---
    name, description, biome name, etc.

    `/genome-catalogues?search=intestine`

    Args:
        biome_biome_name (str | Unset):
        biome_biome_name_icontains (str | Unset):
        catalogue_id (str | Unset):
        description (str | Unset):
        description_icontains (str | Unset):
        format_ (GenomeCataloguesListFormat | Unset):
        last_update (datetime.datetime | Unset):
        last_update_gt (datetime.datetime | Unset):
        last_update_lt (datetime.datetime | Unset):
        lineage (str | Unset):
        name (str | Unset):
        name_icontains (str | Unset):
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
        client=client,
        biome_biome_name=biome_biome_name,
        biome_biome_name_icontains=biome_biome_name_icontains,
        catalogue_id=catalogue_id,
        description=description,
        description_icontains=description_icontains,
        format_=format_,
        last_update=last_update,
        last_update_gt=last_update_gt,
        last_update_lt=last_update_lt,
        lineage=lineage,
        name=name,
        name_icontains=name_icontains,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    biome_biome_name: str | Unset = UNSET,
    biome_biome_name_icontains: str | Unset = UNSET,
    catalogue_id: str | Unset = UNSET,
    description: str | Unset = UNSET,
    description_icontains: str | Unset = UNSET,
    format_: GenomeCataloguesListFormat | Unset = UNSET,
    last_update: datetime.datetime | Unset = UNSET,
    last_update_gt: datetime.datetime | Unset = UNSET,
    last_update_lt: datetime.datetime | Unset = UNSET,
    lineage: str | Unset = UNSET,
    name: str | Unset = UNSET,
    name_icontains: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> Response[PaginatedGenomeCatalogueList]:
    """Retrieves list of genome catalogues
    Example:
    ---
    `/genome-catalogues` retrieves list of all genome catalogues

    `/genome-catalogues?ordering=last_update` ordered by age of catalogue

    Filter by:
    ---
    `/genome-catalogues?last_update__gt=2021-01-01`

    Biome lineage:
    `/genome-catalogues?lineage=root:Environmental:Aquatic:Marine`

    Case-insensitive search of biome name:
    `/genome-catalogues?biome__biome_name__icontains=marine`

    `/genome-catalogues?description__icontains=arctic`

    Search for:
    ---
    name, description, biome name, etc.

    `/genome-catalogues?search=intestine`

    Args:
        biome_biome_name (str | Unset):
        biome_biome_name_icontains (str | Unset):
        catalogue_id (str | Unset):
        description (str | Unset):
        description_icontains (str | Unset):
        format_ (GenomeCataloguesListFormat | Unset):
        last_update (datetime.datetime | Unset):
        last_update_gt (datetime.datetime | Unset):
        last_update_lt (datetime.datetime | Unset):
        lineage (str | Unset):
        name (str | Unset):
        name_icontains (str | Unset):
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
        biome_biome_name=biome_biome_name,
        biome_biome_name_icontains=biome_biome_name_icontains,
        catalogue_id=catalogue_id,
        description=description,
        description_icontains=description_icontains,
        format_=format_,
        last_update=last_update,
        last_update_gt=last_update_gt,
        last_update_lt=last_update_lt,
        lineage=lineage,
        name=name,
        name_icontains=name_icontains,
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
    biome_biome_name: str | Unset = UNSET,
    biome_biome_name_icontains: str | Unset = UNSET,
    catalogue_id: str | Unset = UNSET,
    description: str | Unset = UNSET,
    description_icontains: str | Unset = UNSET,
    format_: GenomeCataloguesListFormat | Unset = UNSET,
    last_update: datetime.datetime | Unset = UNSET,
    last_update_gt: datetime.datetime | Unset = UNSET,
    last_update_lt: datetime.datetime | Unset = UNSET,
    lineage: str | Unset = UNSET,
    name: str | Unset = UNSET,
    name_icontains: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> PaginatedGenomeCatalogueList | None:
    """Retrieves list of genome catalogues
    Example:
    ---
    `/genome-catalogues` retrieves list of all genome catalogues

    `/genome-catalogues?ordering=last_update` ordered by age of catalogue

    Filter by:
    ---
    `/genome-catalogues?last_update__gt=2021-01-01`

    Biome lineage:
    `/genome-catalogues?lineage=root:Environmental:Aquatic:Marine`

    Case-insensitive search of biome name:
    `/genome-catalogues?biome__biome_name__icontains=marine`

    `/genome-catalogues?description__icontains=arctic`

    Search for:
    ---
    name, description, biome name, etc.

    `/genome-catalogues?search=intestine`

    Args:
        biome_biome_name (str | Unset):
        biome_biome_name_icontains (str | Unset):
        catalogue_id (str | Unset):
        description (str | Unset):
        description_icontains (str | Unset):
        format_ (GenomeCataloguesListFormat | Unset):
        last_update (datetime.datetime | Unset):
        last_update_gt (datetime.datetime | Unset):
        last_update_lt (datetime.datetime | Unset):
        lineage (str | Unset):
        name (str | Unset):
        name_icontains (str | Unset):
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
            client=client,
            biome_biome_name=biome_biome_name,
            biome_biome_name_icontains=biome_biome_name_icontains,
            catalogue_id=catalogue_id,
            description=description,
            description_icontains=description_icontains,
            format_=format_,
            last_update=last_update,
            last_update_gt=last_update_gt,
            last_update_lt=last_update_lt,
            lineage=lineage,
            name=name,
            name_icontains=name_icontains,
            ordering=ordering,
            page=page,
            page_size=page_size,
            search=search,
        )
    ).parsed
