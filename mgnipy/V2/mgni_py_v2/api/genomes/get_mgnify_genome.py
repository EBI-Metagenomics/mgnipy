from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.genome_detail import GenomeDetail
from ...types import Response


def _get_kwargs(
    accession: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/metagenomics/api/v2/genomes/{accession}".format(
            accession=quote(str(accession), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GenomeDetail | None:
    if response.status_code == 200:
        response_200 = GenomeDetail.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GenomeDetail]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    accession: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[GenomeDetail]:
    """Get the detail of a single MGnify Genome

     MGnify Genomes are either isolates, or MAGs derived from binned metagenomes.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeDetail]
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
    client: AuthenticatedClient | Client,
) -> GenomeDetail | None:
    """Get the detail of a single MGnify Genome

     MGnify Genomes are either isolates, or MAGs derived from binned metagenomes.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeDetail
    """

    return sync_detailed(
        accession=accession,
        client=client,
    ).parsed


async def asyncio_detailed(
    accession: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[GenomeDetail]:
    """Get the detail of a single MGnify Genome

     MGnify Genomes are either isolates, or MAGs derived from binned metagenomes.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeDetail]
    """

    kwargs = _get_kwargs(
        accession=accession,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    *,
    client: AuthenticatedClient | Client,
) -> GenomeDetail | None:
    """Get the detail of a single MGnify Genome

     MGnify Genomes are either isolates, or MAGs derived from binned metagenomes.

    Args:
        accession (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeDetail
    """

    return (
        await asyncio_detailed(
            accession=accession,
            client=client,
        )
    ).parsed
