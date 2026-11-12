from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.m_gnify_analysis_detail import MGnifyAnalysisDetail
from typing import cast



def _get_kwargs(
    accession: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/metagenomics/api/v2/analyses/{accession}".format(accession=quote(str(accession), safe=""),),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> MGnifyAnalysisDetail | None:
    if response.status_code == 200:
        response_200 = MGnifyAnalysisDetail.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[MGnifyAnalysisDetail]:
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

) -> Response[MGnifyAnalysisDetail]:
    """ Get MGnify analysis by accession

     MGnify analyses are accessioned with an MYGA-prefixed identifier and correspond to an individual Run
    or Assembly analysed by a Pipeline.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MGnifyAnalysisDetail]
     """


    kwargs = _get_kwargs(
        accession=accession,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    accession: str,
    *,
    client: AuthenticatedClient,

) -> MGnifyAnalysisDetail | None:
    """ Get MGnify analysis by accession

     MGnify analyses are accessioned with an MYGA-prefixed identifier and correspond to an individual Run
    or Assembly analysed by a Pipeline.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MGnifyAnalysisDetail
     """


    return sync_detailed(
        accession=accession,
client=client,

    ).parsed

async def asyncio_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,

) -> Response[MGnifyAnalysisDetail]:
    """ Get MGnify analysis by accession

     MGnify analyses are accessioned with an MYGA-prefixed identifier and correspond to an individual Run
    or Assembly analysed by a Pipeline.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MGnifyAnalysisDetail]
     """


    kwargs = _get_kwargs(
        accession=accession,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    accession: str,
    *,
    client: AuthenticatedClient,

) -> MGnifyAnalysisDetail | None:
    """ Get MGnify analysis by accession

     MGnify analyses are accessioned with an MYGA-prefixed identifier and correspond to an individual Run
    or Assembly analysed by a Pipeline.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MGnifyAnalysisDetail
     """


    return (await asyncio_detailed(
        accession=accession,
client=client,

    )).parsed
