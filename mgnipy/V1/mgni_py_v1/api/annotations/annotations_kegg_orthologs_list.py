from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.annotations_kegg_orthologs_list_format import (
    AnnotationsKeggOrthologsListFormat,
)
from ...models.paginated_kegg_ortholog_list import PaginatedKeggOrthologList
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    *,
    format_: AnnotationsKeggOrthologsListFormat | Unset = UNSET,
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
        "url": "/v1/annotations/kegg-orthologs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedKeggOrthologList | None:
    if response.status_code == 200:
        response_200 = PaginatedKeggOrthologList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedKeggOrthologList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    format_: AnnotationsKeggOrthologsListFormat | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedKeggOrthologList]:
    """Retrieves list of KO
    Example:
    ---
    `/annotations/ko`

    Args:
        format_ (AnnotationsKeggOrthologsListFormat | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedKeggOrthologList]
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
    format_: AnnotationsKeggOrthologsListFormat | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedKeggOrthologList | None:
    """Retrieves list of KO
    Example:
    ---
    `/annotations/ko`

    Args:
        format_ (AnnotationsKeggOrthologsListFormat | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedKeggOrthologList
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
    format_: AnnotationsKeggOrthologsListFormat | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> Response[PaginatedKeggOrthologList]:
    """Retrieves list of KO
    Example:
    ---
    `/annotations/ko`

    Args:
        format_ (AnnotationsKeggOrthologsListFormat | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedKeggOrthologList]
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
    format_: AnnotationsKeggOrthologsListFormat | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
) -> PaginatedKeggOrthologList | None:
    """Retrieves list of KO
    Example:
    ---
    `/annotations/ko`

    Args:
        format_ (AnnotationsKeggOrthologsListFormat | Unset):
        page (int | Unset):
        page_size (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedKeggOrthologList
    """

    return (
        await asyncio_detailed(
            client=client,
            format_=format_,
            page=page,
            page_size=page_size,
        )
    ).parsed
