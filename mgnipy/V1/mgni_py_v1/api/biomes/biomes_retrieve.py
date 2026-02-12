from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.biome import Biome
from ...models.biomes_retrieve_format import BiomesRetrieveFormat
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    lineage: str,
    *,
    format_: BiomesRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/biomes/{lineage}".format(
            lineage=quote(str(lineage), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Biome | None:
    if response.status_code == 200:
        response_200 = Biome.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Biome]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    lineage: str,
    *,
    client: AuthenticatedClient,
    format_: BiomesRetrieveFormat | Unset = UNSET,
) -> Response[Biome]:
    """Retrieves children for the given lineage
    Example:
    ---
    `/biomes/root:Environmental:Aquatic:Freshwater`

    Args:
        lineage (str):
        format_ (BiomesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Biome]
    """

    kwargs = _get_kwargs(
        lineage=lineage,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    lineage: str,
    *,
    client: AuthenticatedClient,
    format_: BiomesRetrieveFormat | Unset = UNSET,
) -> Biome | None:
    """Retrieves children for the given lineage
    Example:
    ---
    `/biomes/root:Environmental:Aquatic:Freshwater`

    Args:
        lineage (str):
        format_ (BiomesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Biome
    """

    return sync_detailed(
        lineage=lineage,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    lineage: str,
    *,
    client: AuthenticatedClient,
    format_: BiomesRetrieveFormat | Unset = UNSET,
) -> Response[Biome]:
    """Retrieves children for the given lineage
    Example:
    ---
    `/biomes/root:Environmental:Aquatic:Freshwater`

    Args:
        lineage (str):
        format_ (BiomesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Biome]
    """

    kwargs = _get_kwargs(
        lineage=lineage,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    lineage: str,
    *,
    client: AuthenticatedClient,
    format_: BiomesRetrieveFormat | Unset = UNSET,
) -> Biome | None:
    """Retrieves children for the given lineage
    Example:
    ---
    `/biomes/root:Environmental:Aquatic:Freshwater`

    Args:
        lineage (str):
        format_ (BiomesRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Biome
    """

    return (
        await asyncio_detailed(
            lineage=lineage,
            client=client,
            format_=format_,
        )
    ).parsed
