from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.genome_catalogue import GenomeCatalogue
from ...models.genome_catalogues_retrieve_format import GenomeCataloguesRetrieveFormat
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    catalogue_id: str,
    *,
    format_: GenomeCataloguesRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/genome-catalogues/{catalogue_id}".format(
            catalogue_id=quote(str(catalogue_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GenomeCatalogue | None:
    if response.status_code == 200:
        response_200 = GenomeCatalogue.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GenomeCatalogue]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    catalogue_id: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesRetrieveFormat | Unset = UNSET,
) -> Response[GenomeCatalogue]:
    """Retrieves Genome Catalogues for the given Catalogue ID
    Example:
    ---
    `/genome-catalogues/{catalogue_id}`

    Args:
        catalogue_id (str):
        format_ (GenomeCataloguesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeCatalogue]
    """

    kwargs = _get_kwargs(
        catalogue_id=catalogue_id,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    catalogue_id: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesRetrieveFormat | Unset = UNSET,
) -> GenomeCatalogue | None:
    """Retrieves Genome Catalogues for the given Catalogue ID
    Example:
    ---
    `/genome-catalogues/{catalogue_id}`

    Args:
        catalogue_id (str):
        format_ (GenomeCataloguesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeCatalogue
    """

    return sync_detailed(
        catalogue_id=catalogue_id,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    catalogue_id: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesRetrieveFormat | Unset = UNSET,
) -> Response[GenomeCatalogue]:
    """Retrieves Genome Catalogues for the given Catalogue ID
    Example:
    ---
    `/genome-catalogues/{catalogue_id}`

    Args:
        catalogue_id (str):
        format_ (GenomeCataloguesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeCatalogue]
    """

    kwargs = _get_kwargs(
        catalogue_id=catalogue_id,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    catalogue_id: str,
    *,
    client: AuthenticatedClient,
    format_: GenomeCataloguesRetrieveFormat | Unset = UNSET,
) -> GenomeCatalogue | None:
    """Retrieves Genome Catalogues for the given Catalogue ID
    Example:
    ---
    `/genome-catalogues/{catalogue_id}`

    Args:
        catalogue_id (str):
        format_ (GenomeCataloguesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeCatalogue
    """

    return (
        await asyncio_detailed(
            catalogue_id=catalogue_id,
            client=client,
            format_=format_,
        )
    ).parsed
