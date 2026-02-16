from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ....client import (
    AuthenticatedClient,
    Client,
)
from ...models.list_mgnify_publications_order_type_0 import (
    ListMgnifyPublicationsOrderType0,
)
from ...models.ninja_pagination_response_schema_m_gnify_publication import (
    NinjaPaginationResponseSchemaMGnifyPublication,
)
from ...._models_v2.types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    *,
    order: ListMgnifyPublicationsOrderType0 | None | Unset = UNSET,
    published_after: int | None | Unset = UNSET,
    published_before: int | None | Unset = UNSET,
    title: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_order: None | str | Unset
    if isinstance(order, Unset):
        json_order = UNSET
    elif isinstance(order, ListMgnifyPublicationsOrderType0):
        json_order = order.value
    else:
        json_order = order
    params["order"] = json_order

    json_published_after: int | None | Unset
    if isinstance(published_after, Unset):
        json_published_after = UNSET
    else:
        json_published_after = published_after
    params["published_after"] = json_published_after

    json_published_before: int | None | Unset
    if isinstance(published_before, Unset):
        json_published_before = UNSET
    else:
        json_published_before = published_before
    params["published_before"] = json_published_before

    json_title: None | str | Unset
    if isinstance(title, Unset):
        json_title = UNSET
    else:
        json_title = title
    params["title"] = json_title

    params["page"] = page

    json_page_size: int | None | Unset
    if isinstance(page_size, Unset):
        json_page_size = UNSET
    else:
        json_page_size = page_size
    params["page_size"] = json_page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/metagenomics/api/v2/publications/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> NinjaPaginationResponseSchemaMGnifyPublication | None:
    if response.status_code == 200:
        response_200 = NinjaPaginationResponseSchemaMGnifyPublication.from_dict(
            response.json()
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[NinjaPaginationResponseSchemaMGnifyPublication]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    order: ListMgnifyPublicationsOrderType0 | None | Unset = UNSET,
    published_after: int | None | Unset = UNSET,
    published_before: int | None | Unset = UNSET,
    title: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaMGnifyPublication]:
    """List all publications

     List all publications in the MGnify database.

    Args:
        order (ListMgnifyPublicationsOrderType0 | None | Unset):
        published_after (int | None | Unset): Filter by minimum publication year
        published_before (int | None | Unset): Filter by maximum publication year
        title (None | str | Unset): Search within publication titles
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifyPublication]
    """

    kwargs = _get_kwargs(
        order=order,
        published_after=published_after,
        published_before=published_before,
        title=title,
        page=page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    order: ListMgnifyPublicationsOrderType0 | None | Unset = UNSET,
    published_after: int | None | Unset = UNSET,
    published_before: int | None | Unset = UNSET,
    title: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaMGnifyPublication | None:
    """List all publications

     List all publications in the MGnify database.

    Args:
        order (ListMgnifyPublicationsOrderType0 | None | Unset):
        published_after (int | None | Unset): Filter by minimum publication year
        published_before (int | None | Unset): Filter by maximum publication year
        title (None | str | Unset): Search within publication titles
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifyPublication
    """

    return sync_detailed(
        client=client,
        order=order,
        published_after=published_after,
        published_before=published_before,
        title=title,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    order: ListMgnifyPublicationsOrderType0 | None | Unset = UNSET,
    published_after: int | None | Unset = UNSET,
    published_before: int | None | Unset = UNSET,
    title: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaMGnifyPublication]:
    """List all publications

     List all publications in the MGnify database.

    Args:
        order (ListMgnifyPublicationsOrderType0 | None | Unset):
        published_after (int | None | Unset): Filter by minimum publication year
        published_before (int | None | Unset): Filter by maximum publication year
        title (None | str | Unset): Search within publication titles
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifyPublication]
    """

    kwargs = _get_kwargs(
        order=order,
        published_after=published_after,
        published_before=published_before,
        title=title,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    order: ListMgnifyPublicationsOrderType0 | None | Unset = UNSET,
    published_after: int | None | Unset = UNSET,
    published_before: int | None | Unset = UNSET,
    title: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaMGnifyPublication | None:
    """List all publications

     List all publications in the MGnify database.

    Args:
        order (ListMgnifyPublicationsOrderType0 | None | Unset):
        published_after (int | None | Unset): Filter by minimum publication year
        published_before (int | None | Unset): Filter by maximum publication year
        title (None | str | Unset): Search within publication titles
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifyPublication
    """

    return (
        await asyncio_detailed(
            client=client,
            order=order,
            published_after=published_after,
            published_before=published_before,
            title=title,
            page=page,
            page_size=page_size,
        )
    ).parsed
