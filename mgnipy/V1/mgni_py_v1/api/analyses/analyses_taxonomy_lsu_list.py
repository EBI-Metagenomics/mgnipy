from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.analyses_taxonomy_lsu_list_format import AnalysesTaxonomyLsuListFormat
from ...models.paginated_organism_retrive_list import PaginatedOrganismRetriveList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    accession: str,
    *,
    format_: AnalysesTaxonomyLsuListFormat | Unset = UNSET,
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
        "url": "/v1/analyses/{accession}/taxonomy/lsu".format(
            accession=quote(str(accession), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedOrganismRetriveList | None:
    if response.status_code == 200:
        response_200 = PaginatedOrganismRetriveList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedOrganismRetriveList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AnalysesTaxonomyLsuListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedOrganismRetriveList]:
    """Retrieves LSU Taxonomic analysis for the given accession
    Example:
    ---
    `/analyses/MGYA00102827/taxonomy/lsu`
    ---

    Args:
        accession (str):
        format_ (AnalysesTaxonomyLsuListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedOrganismRetriveList]
    """

    kwargs = _get_kwargs(
        accession=accession,
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
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AnalysesTaxonomyLsuListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedOrganismRetriveList | None:
    """Retrieves LSU Taxonomic analysis for the given accession
    Example:
    ---
    `/analyses/MGYA00102827/taxonomy/lsu`
    ---

    Args:
        accession (str):
        format_ (AnalysesTaxonomyLsuListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedOrganismRetriveList
    """

    return sync_detailed(
        accession=accession,
        client=client,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AnalysesTaxonomyLsuListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedOrganismRetriveList]:
    """Retrieves LSU Taxonomic analysis for the given accession
    Example:
    ---
    `/analyses/MGYA00102827/taxonomy/lsu`
    ---

    Args:
        accession (str):
        format_ (AnalysesTaxonomyLsuListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedOrganismRetriveList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        format_=format_,
        ordering=ordering,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AnalysesTaxonomyLsuListFormat | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedOrganismRetriveList | None:
    """Retrieves LSU Taxonomic analysis for the given accession
    Example:
    ---
    `/analyses/MGYA00102827/taxonomy/lsu`
    ---

    Args:
        accession (str):
        format_ (AnalysesTaxonomyLsuListFormat | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedOrganismRetriveList
    """

    return (
        await asyncio_detailed(
            accession=accession,
            client=client,
            format_=format_,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )
    ).parsed
