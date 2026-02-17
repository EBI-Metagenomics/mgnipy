from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from mgnipy._shared_helpers import errors
from mgnipy.V2 import (
    AuthenticatedClient,
    Client,
)
from mgnipy.V2._mgnipy_models.types import Response
from mgnipy.V2.mgni_py_v2.models.genome_catalogue_detail import GenomeCatalogueDetail


def _get_kwargs(
    catalogue_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/metagenomics/api/v2/genomes/catalogues/{catalogue_id}".format(
            catalogue_id=quote(str(catalogue_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GenomeCatalogueDetail | None:
    if response.status_code == 200:
        response_200 = GenomeCatalogueDetail.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GenomeCatalogueDetail]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    catalogue_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[GenomeCatalogueDetail]:
    """Get genome catalogue by ID

    Args:
        catalogue_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeCatalogueDetail]
    """

    kwargs = _get_kwargs(
        catalogue_id=catalogue_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    catalogue_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> GenomeCatalogueDetail | None:
    """Get genome catalogue by ID

    Args:
        catalogue_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeCatalogueDetail
    """

    return sync_detailed(
        catalogue_id=catalogue_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    catalogue_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[GenomeCatalogueDetail]:
    """Get genome catalogue by ID

    Args:
        catalogue_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeCatalogueDetail]
    """

    kwargs = _get_kwargs(
        catalogue_id=catalogue_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    catalogue_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> GenomeCatalogueDetail | None:
    """Get genome catalogue by ID

    Args:
        catalogue_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeCatalogueDetail
    """

    return (
        await asyncio_detailed(
            catalogue_id=catalogue_id,
            client=client,
        )
    ).parsed
