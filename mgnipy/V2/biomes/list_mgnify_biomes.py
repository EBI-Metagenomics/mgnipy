from http import HTTPStatus
from typing import Any

import httpx

from mgnipy._shared_helpers import errors
from mgnipy.V2 import (
    AuthenticatedClient,
    Client,
)
from mgnipy.V2._mgnipy_models.types import (
    UNSET,
    Response,
    Unset,
)
from mgnipy.V2.mgni_py_v2.models.ninja_pagination_response_schema_biome import (
    NinjaPaginationResponseSchemaBiome,
)


def _get_kwargs(
    *,
    biome_lineage: None | str | Unset = UNSET,
    max_depth: int | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_biome_lineage: None | str | Unset
    if isinstance(biome_lineage, Unset):
        json_biome_lineage = UNSET
    else:
        json_biome_lineage = biome_lineage
    params["biome_lineage"] = json_biome_lineage

    json_max_depth: int | None | Unset
    if isinstance(max_depth, Unset):
        json_max_depth = UNSET
    else:
        json_max_depth = max_depth
    params["max_depth"] = json_max_depth

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
        "url": "/metagenomics/api/v2/biomes/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> NinjaPaginationResponseSchemaBiome | None:
    if response.status_code == 200:
        response_200 = NinjaPaginationResponseSchemaBiome.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[NinjaPaginationResponseSchemaBiome]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    biome_lineage: None | str | Unset = UNSET,
    max_depth: int | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaBiome]:
    """List all biomes

     List all biomes in the MGnify database.

    Args:
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        max_depth (int | None | Unset): Maximum depth of the biome lineage to include, e.g. `root`
            is 1 and `root:Host-Associated:Human` is level 3
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaBiome]
    """

    kwargs = _get_kwargs(
        biome_lineage=biome_lineage,
        max_depth=max_depth,
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
    biome_lineage: None | str | Unset = UNSET,
    max_depth: int | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaBiome | None:
    """List all biomes

     List all biomes in the MGnify database.

    Args:
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        max_depth (int | None | Unset): Maximum depth of the biome lineage to include, e.g. `root`
            is 1 and `root:Host-Associated:Human` is level 3
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaBiome
    """

    return sync_detailed(
        client=client,
        biome_lineage=biome_lineage,
        max_depth=max_depth,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    biome_lineage: None | str | Unset = UNSET,
    max_depth: int | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaBiome]:
    """List all biomes

     List all biomes in the MGnify database.

    Args:
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        max_depth (int | None | Unset): Maximum depth of the biome lineage to include, e.g. `root`
            is 1 and `root:Host-Associated:Human` is level 3
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaBiome]
    """

    kwargs = _get_kwargs(
        biome_lineage=biome_lineage,
        max_depth=max_depth,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    biome_lineage: None | str | Unset = UNSET,
    max_depth: int | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaBiome | None:
    """List all biomes

     List all biomes in the MGnify database.

    Args:
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        max_depth (int | None | Unset): Maximum depth of the biome lineage to include, e.g. `root`
            is 1 and `root:Host-Associated:Human` is level 3
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaBiome
    """

    return (
        await asyncio_detailed(
            client=client,
            biome_lineage=biome_lineage,
            max_depth=max_depth,
            page=page,
            page_size=page_size,
        )
    ).parsed
