from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.assemblies_list_format import AssembliesListFormat
from ...models.paginated_assembly_list import PaginatedAssemblyList
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    *,
    accession: list[None | str] | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    format_: AssembliesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    run_accession: str | Unset = UNSET,
    sample_accession: str | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_accession: list[None | str] | Unset = UNSET
    if not isinstance(accession, Unset):
        json_accession = []
        for accession_item_data in accession:
            accession_item: None | str
            accession_item = accession_item_data
            json_accession.append(accession_item)

    params["accession"] = json_accession

    params["biome_name"] = biome_name

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["include"] = include

    params["lineage"] = lineage

    params["metadata_key"] = metadata_key

    params["metadata_value"] = metadata_value

    params["metadata_value_gte"] = metadata_value_gte

    params["metadata_value_lte"] = metadata_value_lte

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params["run_accession"] = run_accession

    params["sample_accession"] = sample_accession

    params["search"] = search

    params["species"] = species

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/assemblies",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedAssemblyList | None:
    if response.status_code == 200:
        response_200 = PaginatedAssemblyList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedAssemblyList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    accession: list[None | str] | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    format_: AssembliesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    run_accession: str | Unset = UNSET,
    sample_accession: str | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
) -> Response[PaginatedAssemblyList]:
    """Retrieves list of runs
    Example:
    ---
    `/assembly`

    `/assembly?fields[assembly]=accession` retrieve only
    selected fields

    Filter by:
    ---
    `/assembly?biome=root:Environmental:Aquatic:Marine`

    Args:
        accession (list[None | str] | Unset):
        biome_name (str | Unset):
        format_ (AssembliesListFormat | Unset):
        include (str | Unset):
        lineage (str | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        run_accession (str | Unset):
        sample_accession (str | Unset):
        search (str | Unset):
        species (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedAssemblyList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        biome_name=biome_name,
        format_=format_,
        include=include,
        lineage=lineage,
        metadata_key=metadata_key,
        metadata_value=metadata_value,
        metadata_value_gte=metadata_value_gte,
        metadata_value_lte=metadata_value_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        run_accession=run_accession,
        sample_accession=sample_accession,
        search=search,
        species=species,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    accession: list[None | str] | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    format_: AssembliesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    run_accession: str | Unset = UNSET,
    sample_accession: str | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
) -> PaginatedAssemblyList | None:
    """Retrieves list of runs
    Example:
    ---
    `/assembly`

    `/assembly?fields[assembly]=accession` retrieve only
    selected fields

    Filter by:
    ---
    `/assembly?biome=root:Environmental:Aquatic:Marine`

    Args:
        accession (list[None | str] | Unset):
        biome_name (str | Unset):
        format_ (AssembliesListFormat | Unset):
        include (str | Unset):
        lineage (str | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        run_accession (str | Unset):
        sample_accession (str | Unset):
        search (str | Unset):
        species (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedAssemblyList
    """

    return sync_detailed(
        client=client,
        accession=accession,
        biome_name=biome_name,
        format_=format_,
        include=include,
        lineage=lineage,
        metadata_key=metadata_key,
        metadata_value=metadata_value,
        metadata_value_gte=metadata_value_gte,
        metadata_value_lte=metadata_value_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        run_accession=run_accession,
        sample_accession=sample_accession,
        search=search,
        species=species,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    accession: list[None | str] | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    format_: AssembliesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    run_accession: str | Unset = UNSET,
    sample_accession: str | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
) -> Response[PaginatedAssemblyList]:
    """Retrieves list of runs
    Example:
    ---
    `/assembly`

    `/assembly?fields[assembly]=accession` retrieve only
    selected fields

    Filter by:
    ---
    `/assembly?biome=root:Environmental:Aquatic:Marine`

    Args:
        accession (list[None | str] | Unset):
        biome_name (str | Unset):
        format_ (AssembliesListFormat | Unset):
        include (str | Unset):
        lineage (str | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        run_accession (str | Unset):
        sample_accession (str | Unset):
        search (str | Unset):
        species (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedAssemblyList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        biome_name=biome_name,
        format_=format_,
        include=include,
        lineage=lineage,
        metadata_key=metadata_key,
        metadata_value=metadata_value,
        metadata_value_gte=metadata_value_gte,
        metadata_value_lte=metadata_value_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        run_accession=run_accession,
        sample_accession=sample_accession,
        search=search,
        species=species,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    accession: list[None | str] | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    format_: AssembliesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    run_accession: str | Unset = UNSET,
    sample_accession: str | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
) -> PaginatedAssemblyList | None:
    """Retrieves list of runs
    Example:
    ---
    `/assembly`

    `/assembly?fields[assembly]=accession` retrieve only
    selected fields

    Filter by:
    ---
    `/assembly?biome=root:Environmental:Aquatic:Marine`

    Args:
        accession (list[None | str] | Unset):
        biome_name (str | Unset):
        format_ (AssembliesListFormat | Unset):
        include (str | Unset):
        lineage (str | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        run_accession (str | Unset):
        sample_accession (str | Unset):
        search (str | Unset):
        species (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedAssemblyList
    """

    return (
        await asyncio_detailed(
            client=client,
            accession=accession,
            biome_name=biome_name,
            format_=format_,
            include=include,
            lineage=lineage,
            metadata_key=metadata_key,
            metadata_value=metadata_value,
            metadata_value_gte=metadata_value_gte,
            metadata_value_lte=metadata_value_lte,
            ordering=ordering,
            page=page,
            page_size=page_size,
            run_accession=run_accession,
            sample_accession=sample_accession,
            search=search,
            species=species,
        )
    ).parsed
