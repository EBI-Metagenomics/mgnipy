from http import HTTPStatus
from typing import Any

import httpx

from mgnipy._shared_helpers import errors
from mgnipy.V2 import (
    AuthenticatedClient,
    Client,
)
from mgnipy.V2.mgni_py_v2.models.list_mgnify_studies_order_type_0 import ListMgnifyStudiesOrderType0
from mgnipy.V2.mgni_py_v2.models.ninja_pagination_response_schema_m_gnify_study import (
    NinjaPaginationResponseSchemaMGnifyStudy,
)
from mgnipy.V2.mgni_py_v2.models.pipeline_versions import PipelineVersions
from mgnipy.V2._mgnipy_models.types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    *,
    order: ListMgnifyStudiesOrderType0 | None | Unset = UNSET,
    biome_lineage: None | str | Unset = UNSET,
    has_analyses_from_pipeline: None | PipelineVersions | Unset = UNSET,
    search: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_order: None | str | Unset
    if isinstance(order, Unset):
        json_order = UNSET
    elif isinstance(order, ListMgnifyStudiesOrderType0):
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

    json_has_analyses_from_pipeline: None | str | Unset
    if isinstance(has_analyses_from_pipeline, Unset):
        json_has_analyses_from_pipeline = UNSET
    elif isinstance(has_analyses_from_pipeline, PipelineVersions):
        json_has_analyses_from_pipeline = has_analyses_from_pipeline.value
    else:
        json_has_analyses_from_pipeline = has_analyses_from_pipeline
    params["has_analyses_from_pipeline"] = json_has_analyses_from_pipeline

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
        "url": "/metagenomics/api/v2/studies/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> NinjaPaginationResponseSchemaMGnifyStudy | None:
    if response.status_code == 200:
        response_200 = NinjaPaginationResponseSchemaMGnifyStudy.from_dict(
            response.json()
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[NinjaPaginationResponseSchemaMGnifyStudy]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    order: ListMgnifyStudiesOrderType0 | None | Unset = UNSET,
    biome_lineage: None | str | Unset = UNSET,
    has_analyses_from_pipeline: None | PipelineVersions | Unset = UNSET,
    search: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaMGnifyStudy]:
    """List all studies analysed by MGnify

     MGnify studies inherit directly from studies (or projects) in ENA.

    Args:
        order (ListMgnifyStudiesOrderType0 | None | Unset):
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        has_analyses_from_pipeline (None | PipelineVersions | Unset): If set, will only show
            studies with analyses from the specified MGnify pipeline version
        search (None | str | Unset): Search within study titles and accessions
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifyStudy]
    """

    kwargs = _get_kwargs(
        order=order,
        biome_lineage=biome_lineage,
        has_analyses_from_pipeline=has_analyses_from_pipeline,
        search=search,
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
    order: ListMgnifyStudiesOrderType0 | None | Unset = UNSET,
    biome_lineage: None | str | Unset = UNSET,
    has_analyses_from_pipeline: None | PipelineVersions | Unset = UNSET,
    search: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaMGnifyStudy | None:
    """List all studies analysed by MGnify

     MGnify studies inherit directly from studies (or projects) in ENA.

    Args:
        order (ListMgnifyStudiesOrderType0 | None | Unset):
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        has_analyses_from_pipeline (None | PipelineVersions | Unset): If set, will only show
            studies with analyses from the specified MGnify pipeline version
        search (None | str | Unset): Search within study titles and accessions
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifyStudy
    """

    return sync_detailed(
        client=client,
        order=order,
        biome_lineage=biome_lineage,
        has_analyses_from_pipeline=has_analyses_from_pipeline,
        search=search,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    order: ListMgnifyStudiesOrderType0 | None | Unset = UNSET,
    biome_lineage: None | str | Unset = UNSET,
    has_analyses_from_pipeline: None | PipelineVersions | Unset = UNSET,
    search: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> Response[NinjaPaginationResponseSchemaMGnifyStudy]:
    """List all studies analysed by MGnify

     MGnify studies inherit directly from studies (or projects) in ENA.

    Args:
        order (ListMgnifyStudiesOrderType0 | None | Unset):
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        has_analyses_from_pipeline (None | PipelineVersions | Unset): If set, will only show
            studies with analyses from the specified MGnify pipeline version
        search (None | str | Unset): Search within study titles and accessions
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NinjaPaginationResponseSchemaMGnifyStudy]
    """

    kwargs = _get_kwargs(
        order=order,
        biome_lineage=biome_lineage,
        has_analyses_from_pipeline=has_analyses_from_pipeline,
        search=search,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    order: ListMgnifyStudiesOrderType0 | None | Unset = UNSET,
    biome_lineage: None | str | Unset = UNSET,
    has_analyses_from_pipeline: None | PipelineVersions | Unset = UNSET,
    search: None | str | Unset = UNSET,
    page: int | Unset = 1,
    page_size: int | None | Unset = UNSET,
) -> NinjaPaginationResponseSchemaMGnifyStudy | None:
    """List all studies analysed by MGnify

     MGnify studies inherit directly from studies (or projects) in ENA.

    Args:
        order (ListMgnifyStudiesOrderType0 | None | Unset):
        biome_lineage (None | str | Unset): The lineage to match, including all descendant biomes
        has_analyses_from_pipeline (None | PipelineVersions | Unset): If set, will only show
            studies with analyses from the specified MGnify pipeline version
        search (None | str | Unset): Search within study titles and accessions
        page (int | Unset):  Default: 1.
        page_size (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NinjaPaginationResponseSchemaMGnifyStudy
    """

    return (
        await asyncio_detailed(
            client=client,
            order=order,
            biome_lineage=biome_lineage,
            has_analyses_from_pipeline=has_analyses_from_pipeline,
            search=search,
            page=page,
            page_size=page_size,
        )
    ).parsed
