from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.list_mgnify_samples_order_type_0 import ListMgnifySamplesOrderType0
from ...models.ninja_pagination_response_schema_m_gnify_sample import NinjaPaginationResponseSchemaMGnifySample
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    biome_lineage: None | str | Unset = UNSET,
    search: None | str | Unset = UNSET,
    order: ListMgnifySamplesOrderType0 | None | Unset = UNSET,
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

    json_search: None | str | Unset
    if isinstance(search, Unset):
        json_search = UNSET
    else:
        json_search = search
    params["search"] = json_search

    json_order: None | str | Unset
    if isinstance(order, Unset):
        json_order = UNSET
    elif isinstance(order, ListMgnifySamplesOrderType0):
        json_order = order.value
    else:
        json_order = order
    params["order"] = json_order

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
        "url": "/metagenomics/api/v2/samples/",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> NinjaPaginationResponseSchemaMGnifySample | None:
    if response.status_code == 200:
        response_200 = NinjaPaginationResponseSchemaMGnifySample.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[NinjaPaginationResponseSchemaMGnifySample]:
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
    search: None | str | Unset = UNSET,
    order: ListMgnifySamplesOrderType0 | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> Response[NinjaPaginationResponseSchemaMGnifySample]:
    """ List all samples analysed by MGnify

     MGnify samples inherit directly from samples (or BioSamples) in ENA.

    Args:
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        search (None | str | Unset): Search within sample titles and accessions
        order (ListMgnifySamplesOrderType0 | None | Unset):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifySample]
     """


    kwargs = _get_kwargs(
        biome_lineage=biome_lineage,
search=search,
order=order,
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
    search: None | str | Unset = UNSET,
    order: ListMgnifySamplesOrderType0 | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> NinjaPaginationResponseSchemaMGnifySample | None:
    """ List all samples analysed by MGnify

     MGnify samples inherit directly from samples (or BioSamples) in ENA.

    Args:
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        search (None | str | Unset): Search within sample titles and accessions
        order (ListMgnifySamplesOrderType0 | None | Unset):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifySample
     """


    return sync_detailed(
        client=client,
biome_lineage=biome_lineage,
search=search,
order=order,
page=page,
page_size=page_size,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    biome_lineage: None | str | Unset = UNSET,
    search: None | str | Unset = UNSET,
    order: ListMgnifySamplesOrderType0 | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> Response[NinjaPaginationResponseSchemaMGnifySample]:
    """ List all samples analysed by MGnify

     MGnify samples inherit directly from samples (or BioSamples) in ENA.

    Args:
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        search (None | str | Unset): Search within sample titles and accessions
        order (ListMgnifySamplesOrderType0 | None | Unset):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifySample]
     """


    kwargs = _get_kwargs(
        biome_lineage=biome_lineage,
search=search,
order=order,
page=page,
page_size=page_size,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    biome_lineage: None | str | Unset = UNSET,
    search: None | str | Unset = UNSET,
    order: ListMgnifySamplesOrderType0 | None | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,

) -> NinjaPaginationResponseSchemaMGnifySample | None:
    """ List all samples analysed by MGnify

     MGnify samples inherit directly from samples (or BioSamples) in ENA.

    Args:
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        search (None | str | Unset): Search within sample titles and accessions
        order (ListMgnifySamplesOrderType0 | None | Unset):
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifySample
     """


    return (await asyncio_detailed(
        client=client,
biome_lineage=biome_lineage,
search=search,
order=order,
page=page,
page_size=page_size,

    )).parsed
