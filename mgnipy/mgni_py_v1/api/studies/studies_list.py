from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.paginated_study_list import PaginatedStudyList
from ...models.studies_list_format import StudiesListFormat
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    accession: str | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    centre_name: str | Unset = UNSET,
    format_: StudiesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["accession"] = accession

    params["biome_name"] = biome_name

    params["centre_name"] = centre_name

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["include"] = include

    params["lineage"] = lineage

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/studies",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> PaginatedStudyList | None:
    if response.status_code == 200:
        response_200 = PaginatedStudyList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[PaginatedStudyList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    accession: str | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    centre_name: str | Unset = UNSET,
    format_: StudiesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> Response[PaginatedStudyList]:
    """Retrieves list of studies
    Example:
    ---
    `/studies`

    `/studies?fields[studies]=accession,study_name,samples_count,biomes`
    retrieve only selected fields

    `/studies?include=biomes` with biomes

    Filter by:
    ---
    `/studies?lineage=root:Environmental:Terrestrial:Soil`

    `/studies?centre_name=BioProject`

    Search for:
    ---
    name, abstract, author and centre name etc.

    `/studies?search=microbial%20fuel%20cells`

    Args:
        accession (str | Unset):
        biome_name (str | Unset):
        centre_name (str | Unset):
        format_ (StudiesListFormat | Unset):
        include (str | Unset):
        lineage (str | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedStudyList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        biome_name=biome_name,
        centre_name=centre_name,
        format_=format_,
        include=include,
        lineage=lineage,
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
    accession: str | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    centre_name: str | Unset = UNSET,
    format_: StudiesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> PaginatedStudyList | None:
    """Retrieves list of studies
    Example:
    ---
    `/studies`

    `/studies?fields[studies]=accession,study_name,samples_count,biomes`
    retrieve only selected fields

    `/studies?include=biomes` with biomes

    Filter by:
    ---
    `/studies?lineage=root:Environmental:Terrestrial:Soil`

    `/studies?centre_name=BioProject`

    Search for:
    ---
    name, abstract, author and centre name etc.

    `/studies?search=microbial%20fuel%20cells`

    Args:
        accession (str | Unset):
        biome_name (str | Unset):
        centre_name (str | Unset):
        format_ (StudiesListFormat | Unset):
        include (str | Unset):
        lineage (str | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedStudyList
    """

    return sync_detailed(
        client=client,
        accession=accession,
        biome_name=biome_name,
        centre_name=centre_name,
        format_=format_,
        include=include,
        lineage=lineage,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    accession: str | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    centre_name: str | Unset = UNSET,
    format_: StudiesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> Response[PaginatedStudyList]:
    """Retrieves list of studies
    Example:
    ---
    `/studies`

    `/studies?fields[studies]=accession,study_name,samples_count,biomes`
    retrieve only selected fields

    `/studies?include=biomes` with biomes

    Filter by:
    ---
    `/studies?lineage=root:Environmental:Terrestrial:Soil`

    `/studies?centre_name=BioProject`

    Search for:
    ---
    name, abstract, author and centre name etc.

    `/studies?search=microbial%20fuel%20cells`

    Args:
        accession (str | Unset):
        biome_name (str | Unset):
        centre_name (str | Unset):
        format_ (StudiesListFormat | Unset):
        include (str | Unset):
        lineage (str | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedStudyList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        biome_name=biome_name,
        centre_name=centre_name,
        format_=format_,
        include=include,
        lineage=lineage,
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
    accession: str | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    centre_name: str | Unset = UNSET,
    format_: StudiesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
) -> PaginatedStudyList | None:
    """Retrieves list of studies
    Example:
    ---
    `/studies`

    `/studies?fields[studies]=accession,study_name,samples_count,biomes`
    retrieve only selected fields

    `/studies?include=biomes` with biomes

    Filter by:
    ---
    `/studies?lineage=root:Environmental:Terrestrial:Soil`

    `/studies?centre_name=BioProject`

    Search for:
    ---
    name, abstract, author and centre name etc.

    `/studies?search=microbial%20fuel%20cells`

    Args:
        accession (str | Unset):
        biome_name (str | Unset):
        centre_name (str | Unset):
        format_ (StudiesListFormat | Unset):
        include (str | Unset):
        lineage (str | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedStudyList
    """

    return (
        await asyncio_detailed(
            client=client,
            accession=accession,
            biome_name=biome_name,
            centre_name=centre_name,
            format_=format_,
            include=include,
            lineage=lineage,
            ordering=ordering,
            page=page,
            page_size=page_size,
            search=search,
        )
    ).parsed
