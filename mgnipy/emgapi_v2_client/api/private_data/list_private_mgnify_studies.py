from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.ninja_pagination_response_schema_m_gnify_study import NinjaPaginationResponseSchemaMGnifyStudy
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

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
        "url": "/metagenomics/api/v2/my-data/studies/",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> NinjaPaginationResponseSchemaMGnifyStudy | None:
    if response.status_code == 200:
        response_200 = NinjaPaginationResponseSchemaMGnifyStudy.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[NinjaPaginationResponseSchemaMGnifyStudy]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> Response[NinjaPaginationResponseSchemaMGnifyStudy]:
    """ List all private studies available from MGnify

    Args:
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifyStudy]
     """


    kwargs = _get_kwargs(
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
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> NinjaPaginationResponseSchemaMGnifyStudy | None:
    """ List all private studies available from MGnify

    Args:
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifyStudy
     """


    return sync_detailed(
        client=client,
page=page,
page_size=page_size,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> Response[NinjaPaginationResponseSchemaMGnifyStudy]:
    """ List all private studies available from MGnify

    Args:
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifyStudy]
     """


    kwargs = _get_kwargs(
        page=page,
page_size=page_size,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> NinjaPaginationResponseSchemaMGnifyStudy | None:
    """ List all private studies available from MGnify

    Args:
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifyStudy
     """


    return (await asyncio_detailed(
        client=client,
page=page,
page_size=page_size,

    )).parsed
