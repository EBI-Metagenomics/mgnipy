from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.paginated_super_study_list import PaginatedSuperStudyList
from ...models.super_studies_list_format import SuperStudiesListFormat
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    *,
    biome_name: str | Unset = UNSET,
    description: str | Unset = UNSET,
    format_: SuperStudiesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
    super_study_id: int | Unset = UNSET,
    title: str | Unset = UNSET,
    url_slug: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["biome_name"] = biome_name

    params["description"] = description

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params["search"] = search

    params["super_study_id"] = super_study_id

    params["title"] = title

    params["url_slug"] = url_slug

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/super-studies",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedSuperStudyList | None:
    if response.status_code == 200:
        response_200 = PaginatedSuperStudyList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedSuperStudyList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    biome_name: str | Unset = UNSET,
    description: str | Unset = UNSET,
    format_: SuperStudiesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
    super_study_id: int | Unset = UNSET,
    title: str | Unset = UNSET,
    url_slug: str | Unset = UNSET,
) -> Response[PaginatedSuperStudyList]:
    """Retrieves list of super studies
    Example:
    `/super-studies`

    `/super-studies?fields[super-studies]=super_study_id,title`
    retrieve only selected fields

    `/super-studies?include=biomes` with biomes

    Filter by:
    ---
    `/super-studies?lineage=root:Environmental:Terrestrial:Soil`

    `/studies?title=Human`

    Search for:
    ---
    title, description etc.

    `/super-studies?search=%20micriobiome`
    ---

    Args:
        biome_name (str | Unset):
        description (str | Unset):
        format_ (SuperStudiesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):
        super_study_id (int | Unset):
        title (str | Unset):
        url_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedSuperStudyList]
    """

    kwargs = _get_kwargs(
        biome_name=biome_name,
        description=description,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        super_study_id=super_study_id,
        title=title,
        url_slug=url_slug,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    biome_name: str | Unset = UNSET,
    description: str | Unset = UNSET,
    format_: SuperStudiesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
    super_study_id: int | Unset = UNSET,
    title: str | Unset = UNSET,
    url_slug: str | Unset = UNSET,
) -> PaginatedSuperStudyList | None:
    """Retrieves list of super studies
    Example:
    `/super-studies`

    `/super-studies?fields[super-studies]=super_study_id,title`
    retrieve only selected fields

    `/super-studies?include=biomes` with biomes

    Filter by:
    ---
    `/super-studies?lineage=root:Environmental:Terrestrial:Soil`

    `/studies?title=Human`

    Search for:
    ---
    title, description etc.

    `/super-studies?search=%20micriobiome`
    ---

    Args:
        biome_name (str | Unset):
        description (str | Unset):
        format_ (SuperStudiesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):
        super_study_id (int | Unset):
        title (str | Unset):
        url_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedSuperStudyList
    """

    return sync_detailed(
        client=client,
        biome_name=biome_name,
        description=description,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        super_study_id=super_study_id,
        title=title,
        url_slug=url_slug,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    biome_name: str | Unset = UNSET,
    description: str | Unset = UNSET,
    format_: SuperStudiesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
    super_study_id: int | Unset = UNSET,
    title: str | Unset = UNSET,
    url_slug: str | Unset = UNSET,
) -> Response[PaginatedSuperStudyList]:
    """Retrieves list of super studies
    Example:
    `/super-studies`

    `/super-studies?fields[super-studies]=super_study_id,title`
    retrieve only selected fields

    `/super-studies?include=biomes` with biomes

    Filter by:
    ---
    `/super-studies?lineage=root:Environmental:Terrestrial:Soil`

    `/studies?title=Human`

    Search for:
    ---
    title, description etc.

    `/super-studies?search=%20micriobiome`
    ---

    Args:
        biome_name (str | Unset):
        description (str | Unset):
        format_ (SuperStudiesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):
        super_study_id (int | Unset):
        title (str | Unset):
        url_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedSuperStudyList]
    """

    kwargs = _get_kwargs(
        biome_name=biome_name,
        description=description,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        super_study_id=super_study_id,
        title=title,
        url_slug=url_slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    biome_name: str | Unset = UNSET,
    description: str | Unset = UNSET,
    format_: SuperStudiesListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
    super_study_id: int | Unset = UNSET,
    title: str | Unset = UNSET,
    url_slug: str | Unset = UNSET,
) -> PaginatedSuperStudyList | None:
    """Retrieves list of super studies
    Example:
    `/super-studies`

    `/super-studies?fields[super-studies]=super_study_id,title`
    retrieve only selected fields

    `/super-studies?include=biomes` with biomes

    Filter by:
    ---
    `/super-studies?lineage=root:Environmental:Terrestrial:Soil`

    `/studies?title=Human`

    Search for:
    ---
    title, description etc.

    `/super-studies?search=%20micriobiome`
    ---

    Args:
        biome_name (str | Unset):
        description (str | Unset):
        format_ (SuperStudiesListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):
        super_study_id (int | Unset):
        title (str | Unset):
        url_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedSuperStudyList
    """

    return (
        await asyncio_detailed(
            client=client,
            biome_name=biome_name,
            description=description,
            format_=format_,
            ordering=ordering,
            page=page,
            page_size=page_size,
            search=search,
            super_study_id=super_study_id,
            title=title,
            url_slug=url_slug,
        )
    ).parsed
