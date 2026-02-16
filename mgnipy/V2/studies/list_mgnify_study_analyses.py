from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from mgnipy._shared_helpers import errors
from mgnipy.V2 import (
    AuthenticatedClient,
    Client,
)
from mgnipy.V2.mgni_py_v2.models.ninja_pagination_response_schema_m_gnify_analysis import (
    NinjaPaginationResponseSchemaMGnifyAnalysis,
)
from mgnipy.V2._mgnipy_models.types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    accession: str,
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
        "url": "/metagenomics/api/v2/studies/{accession}/analyses/".format(
            accession=quote(str(accession), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> NinjaPaginationResponseSchemaMGnifyAnalysis | None:
    if response.status_code == 200:
        response_200 = NinjaPaginationResponseSchemaMGnifyAnalysis.from_dict(
            response.json()
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[NinjaPaginationResponseSchemaMGnifyAnalysis]:
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
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaMGnifyAnalysis]:
    """List MGnify Analyses associated with this Study

     MGnify analyses correspond to an individual Run or Assembly within this study,analysed by a MGnify
    Pipelione.

    Args:
        accession (str):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifyAnalysis]
    """

    kwargs = _get_kwargs(
        accession=accession,
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
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaMGnifyAnalysis | None:
    """List MGnify Analyses associated with this Study

     MGnify analyses correspond to an individual Run or Assembly within this study,analysed by a MGnify
    Pipelione.

    Args:
        accession (str):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifyAnalysis
    """

    return sync_detailed(
        accession=accession,
        client=client,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaMGnifyAnalysis]:
    """List MGnify Analyses associated with this Study

     MGnify analyses correspond to an individual Run or Assembly within this study,analysed by a MGnify
    Pipelione.

    Args:
        accession (str):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifyAnalysis]
    """

    kwargs = _get_kwargs(
        accession=accession,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    *,
    client: AuthenticatedClient,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaMGnifyAnalysis | None:
    """List MGnify Analyses associated with this Study

     MGnify analyses correspond to an individual Run or Assembly within this study,analysed by a MGnify
    Pipelione.

    Args:
        accession (str):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifyAnalysis
    """

    return (
        await asyncio_detailed(
            accession=accession,
            client=client,
            page=page,
            page_size=page_size,
        )
    ).parsed
