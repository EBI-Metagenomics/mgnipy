from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.m_gnify_publication_detail import MGnifyPublicationDetail
from typing import cast



def _get_kwargs(
    pubmed_id: int,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/metagenomics/api/v2/publications/{pubmed_id}".format(pubmed_id=quote(str(pubmed_id), safe=""),),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> MGnifyPublicationDetail | None:
    if response.status_code == 200:
        response_200 = MGnifyPublicationDetail.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[MGnifyPublicationDetail]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pubmed_id: int,
    *,
    client: AuthenticatedClient | Client,

) -> Response[MGnifyPublicationDetail]:
    """ Get the detail of a single publication

     Get detailed information about a publication, including associated studies.

    Args:
        pubmed_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MGnifyPublicationDetail]
     """


    kwargs = _get_kwargs(
        pubmed_id=pubmed_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    pubmed_id: int,
    *,
    client: AuthenticatedClient | Client,

) -> MGnifyPublicationDetail | None:
    """ Get the detail of a single publication

     Get detailed information about a publication, including associated studies.

    Args:
        pubmed_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MGnifyPublicationDetail
     """


    return sync_detailed(
        pubmed_id=pubmed_id,
client=client,

    ).parsed

async def asyncio_detailed(
    pubmed_id: int,
    *,
    client: AuthenticatedClient | Client,

) -> Response[MGnifyPublicationDetail]:
    """ Get the detail of a single publication

     Get detailed information about a publication, including associated studies.

    Args:
        pubmed_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MGnifyPublicationDetail]
     """


    kwargs = _get_kwargs(
        pubmed_id=pubmed_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    pubmed_id: int,
    *,
    client: AuthenticatedClient | Client,

) -> MGnifyPublicationDetail | None:
    """ Get the detail of a single publication

     Get detailed information about a publication, including associated studies.

    Args:
        pubmed_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MGnifyPublicationDetail
     """


    return (await asyncio_detailed(
        pubmed_id=pubmed_id,
client=client,

    )).parsed
