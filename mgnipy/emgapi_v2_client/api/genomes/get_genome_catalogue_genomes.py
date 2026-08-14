from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_genome_catalogue_genomes_order_type_0 import GetGenomeCatalogueGenomesOrderType0
from ...models.ninja_pagination_response_schema_genome_list import NinjaPaginationResponseSchemaGenomeList
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    catalogue_id: str,
    *,
    order: GetGenomeCatalogueGenomesOrderType0 | None | Unset = UNSET,
    biome_lineage: None | str | Unset = UNSET,
    search: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    json_order: None | str | Unset
    if isinstance(order, Unset):
        json_order = UNSET
    elif isinstance(order, GetGenomeCatalogueGenomesOrderType0):
        json_order = order.value
    else:
        json_order = order
    params["order"] = json_order

    json_biome_lineage: None | str | Unset
    if isinstance(biome_lineage, Unset):
        json_biome_lineage = UNSET
    else:
        json_biome_lineage = biome_lineage
    params["biome_lineage"] = json_biome_lineage

    json_search: None | str | Unset
    if isinstance(search, Unset):
        json_search = UNSET
    else:
        json_search = search
    params["search"] = json_search

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
        "url": "/metagenomics/api/v2/genomes/catalogues/{catalogue_id}/genomes/".format(catalogue_id=quote(str(catalogue_id), safe=""),),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> NinjaPaginationResponseSchemaGenomeList | None:
    if response.status_code == 200:
        response_200 = NinjaPaginationResponseSchemaGenomeList.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[NinjaPaginationResponseSchemaGenomeList]:
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
    order: GetGenomeCatalogueGenomesOrderType0 | None | Unset = UNSET,
    biome_lineage: None | str | Unset = UNSET,
    search: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> Response[NinjaPaginationResponseSchemaGenomeList]:
    """ Get genomes within the genome catalogue

    Args:
        catalogue_id (str):
        order (GetGenomeCatalogueGenomesOrderType0 | None | Unset):
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        search (None | str | Unset): Search with genome taxonomies and accessions
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaGenomeList]
     """


    kwargs = _get_kwargs(
        catalogue_id=catalogue_id,
order=order,
biome_lineage=biome_lineage,
search=search,
page=page,
page_size=page_size,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    catalogue_id: str,
    *,
    client: AuthenticatedClient,
    order: GetGenomeCatalogueGenomesOrderType0 | None | Unset = UNSET,
    biome_lineage: None | str | Unset = UNSET,
    search: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> NinjaPaginationResponseSchemaGenomeList | None:
    """ Get genomes within the genome catalogue

    Args:
        catalogue_id (str):
        order (GetGenomeCatalogueGenomesOrderType0 | None | Unset):
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        search (None | str | Unset): Search with genome taxonomies and accessions
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaGenomeList
     """


    return sync_detailed(
        catalogue_id=catalogue_id,
client=client,
order=order,
biome_lineage=biome_lineage,
search=search,
page=page,
page_size=page_size,

    ).parsed

async def asyncio_detailed(
    catalogue_id: str,
    *,
    client: AuthenticatedClient,
    order: GetGenomeCatalogueGenomesOrderType0 | None | Unset = UNSET,
    biome_lineage: None | str | Unset = UNSET,
    search: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> Response[NinjaPaginationResponseSchemaGenomeList]:
    """ Get genomes within the genome catalogue

    Args:
        catalogue_id (str):
        order (GetGenomeCatalogueGenomesOrderType0 | None | Unset):
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        search (None | str | Unset): Search with genome taxonomies and accessions
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaGenomeList]
     """


    kwargs = _get_kwargs(
        catalogue_id=catalogue_id,
order=order,
biome_lineage=biome_lineage,
search=search,
page=page,
page_size=page_size,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    catalogue_id: str,
    *,
    client: AuthenticatedClient,
    order: GetGenomeCatalogueGenomesOrderType0 | None | Unset = UNSET,
    biome_lineage: None | str | Unset = UNSET,
    search: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> NinjaPaginationResponseSchemaGenomeList | None:
    """ Get genomes within the genome catalogue

    Args:
        catalogue_id (str):
        order (GetGenomeCatalogueGenomesOrderType0 | None | Unset):
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        search (None | str | Unset): Search with genome taxonomies and accessions
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaGenomeList
     """


    return (await asyncio_detailed(
        catalogue_id=catalogue_id,
client=client,
order=order,
biome_lineage=biome_lineage,
search=search,
page=page,
page_size=page_size,

    )).parsed
