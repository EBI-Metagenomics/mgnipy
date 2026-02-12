from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.paginated_publication_list import PaginatedPublicationList
from ...models.publications_list_format import PublicationsListFormat
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    *,
    doi: str | Unset = UNSET,
    format_: PublicationsListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    isbn: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    published_year: int | None | Unset = UNSET,
    search: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["doi"] = doi

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["include"] = include

    params["isbn"] = isbn

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    json_published_year: int | None | Unset
    if isinstance(published_year, Unset):
        json_published_year = UNSET
    else:
        json_published_year = published_year
    params["published_year"] = json_published_year

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/publications",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedPublicationList | None:
    if response.status_code == 200:
        response_200 = PaginatedPublicationList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedPublicationList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    doi: str | Unset = UNSET,
    format_: PublicationsListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    isbn: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    published_year: int | None | Unset = UNSET,
    search: str | Unset = UNSET,
) -> Response[PaginatedPublicationList]:
    """Retrieves list of publications
    Example:
    ---
    `/publications` retrieves list of publications

    `/publications?include=studies` with studies

    `/publications?ordering=published_year` ordered by year

    Search for:
    ---
    title, abstract, authors, etc.

    `/publications?search=text`

    Args:
        doi (str | Unset):
        format_ (PublicationsListFormat | Unset):
        include (str | Unset):
        isbn (str | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        published_year (int | None | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedPublicationList]
    """

    kwargs = _get_kwargs(
        doi=doi,
        format_=format_,
        include=include,
        isbn=isbn,
        ordering=ordering,
        page=page,
        page_size=page_size,
        published_year=published_year,
        search=search,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    doi: str | Unset = UNSET,
    format_: PublicationsListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    isbn: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    published_year: int | None | Unset = UNSET,
    search: str | Unset = UNSET,
) -> PaginatedPublicationList | None:
    """Retrieves list of publications
    Example:
    ---
    `/publications` retrieves list of publications

    `/publications?include=studies` with studies

    `/publications?ordering=published_year` ordered by year

    Search for:
    ---
    title, abstract, authors, etc.

    `/publications?search=text`

    Args:
        doi (str | Unset):
        format_ (PublicationsListFormat | Unset):
        include (str | Unset):
        isbn (str | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        published_year (int | None | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedPublicationList
    """

    return sync_detailed(
        client=client,
        doi=doi,
        format_=format_,
        include=include,
        isbn=isbn,
        ordering=ordering,
        page=page,
        page_size=page_size,
        published_year=published_year,
        search=search,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    doi: str | Unset = UNSET,
    format_: PublicationsListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    isbn: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    published_year: int | None | Unset = UNSET,
    search: str | Unset = UNSET,
) -> Response[PaginatedPublicationList]:
    """Retrieves list of publications
    Example:
    ---
    `/publications` retrieves list of publications

    `/publications?include=studies` with studies

    `/publications?ordering=published_year` ordered by year

    Search for:
    ---
    title, abstract, authors, etc.

    `/publications?search=text`

    Args:
        doi (str | Unset):
        format_ (PublicationsListFormat | Unset):
        include (str | Unset):
        isbn (str | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        published_year (int | None | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedPublicationList]
    """

    kwargs = _get_kwargs(
        doi=doi,
        format_=format_,
        include=include,
        isbn=isbn,
        ordering=ordering,
        page=page,
        page_size=page_size,
        published_year=published_year,
        search=search,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    doi: str | Unset = UNSET,
    format_: PublicationsListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    isbn: str | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    published_year: int | None | Unset = UNSET,
    search: str | Unset = UNSET,
) -> PaginatedPublicationList | None:
    """Retrieves list of publications
    Example:
    ---
    `/publications` retrieves list of publications

    `/publications?include=studies` with studies

    `/publications?ordering=published_year` ordered by year

    Search for:
    ---
    title, abstract, authors, etc.

    `/publications?search=text`

    Args:
        doi (str | Unset):
        format_ (PublicationsListFormat | Unset):
        include (str | Unset):
        isbn (str | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        published_year (int | None | Unset):
        search (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedPublicationList
    """

    return (
        await asyncio_detailed(
            client=client,
            doi=doi,
            format_=format_,
            include=include,
            isbn=isbn,
            ordering=ordering,
            page=page,
            page_size=page_size,
            published_year=published_year,
            search=search,
        )
    ).parsed
