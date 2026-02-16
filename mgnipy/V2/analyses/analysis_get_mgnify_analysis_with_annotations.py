from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from mgnipy._shared_helpers import errors
from mgnipy.V2 import (
    AuthenticatedClient,
    Client,
)
from mgnipy.V2.mgni_py_v2.models.m_gnify_analysis_with_annotations import MGnifyAnalysisWithAnnotations
from mgnipy.V2._mgnipy_models.types import Response


def _get_kwargs(
    accession: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/metagenomics/api/v2/analyses/{accession}/annotations".format(
            accession=quote(str(accession), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> MGnifyAnalysisWithAnnotations | None:
    if response.status_code == 200:
        response_200 = MGnifyAnalysisWithAnnotations.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[MGnifyAnalysisWithAnnotations]:
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
) -> Response[MGnifyAnalysisWithAnnotations]:
    """Get MGnify analysis by accession, with annotations and downloadable files

     MGnify analyses have annotations (taxonomic and functional assignments), and downloadable files
    (outputs from the pipeline execution).

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MGnifyAnalysisWithAnnotations]
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
) -> MGnifyAnalysisWithAnnotations | None:
    """Get MGnify analysis by accession, with annotations and downloadable files

     MGnify analyses have annotations (taxonomic and functional assignments), and downloadable files
    (outputs from the pipeline execution).

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MGnifyAnalysisWithAnnotations
    """

    return sync_detailed(
        accession=accession,
        client=client,
    ).parsed


async def asyncio_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,
) -> Response[MGnifyAnalysisWithAnnotations]:
    """Get MGnify analysis by accession, with annotations and downloadable files

     MGnify analyses have annotations (taxonomic and functional assignments), and downloadable files
    (outputs from the pipeline execution).

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MGnifyAnalysisWithAnnotations]
    """

    kwargs = _get_kwargs(
        accession=accession,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    *,
    client: AuthenticatedClient,
) -> MGnifyAnalysisWithAnnotations | None:
    """Get MGnify analysis by accession, with annotations and downloadable files

     MGnify analyses have annotations (taxonomic and functional assignments), and downloadable files
    (outputs from the pipeline execution).

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MGnifyAnalysisWithAnnotations
    """

    return (
        await asyncio_detailed(
            accession=accession,
            client=client,
        )
    ).parsed
