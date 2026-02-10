from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.paginated_sample_list import PaginatedSampleList
from ...models.samples_list_format import SamplesListFormat
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    accession: list[str] | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    environment_feature: str | Unset = UNSET,
    environment_material: str | Unset = UNSET,
    experiment_type: list[str] | Unset = UNSET,
    format_: SamplesListFormat | Unset = UNSET,
    geo_loc_name: str | Unset = UNSET,
    include: str | Unset = UNSET,
    instrument_model: str | Unset = UNSET,
    instrument_platform: str | Unset = UNSET,
    latitude_gte: float | Unset = UNSET,
    latitude_lte: float | Unset = UNSET,
    lineage: str | Unset = UNSET,
    longitude_gte: float | Unset = UNSET,
    longitude_lte: float | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
    study_accession: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_accession: list[str] | Unset = UNSET
    if not isinstance(accession, Unset):
        json_accession = accession

    params["accession"] = json_accession

    params["biome_name"] = biome_name

    params["environment_feature"] = environment_feature

    params["environment_material"] = environment_material

    json_experiment_type: list[str] | Unset = UNSET
    if not isinstance(experiment_type, Unset):
        json_experiment_type = experiment_type

    params["experiment_type"] = json_experiment_type

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["geo_loc_name"] = geo_loc_name

    params["include"] = include

    params["instrument_model"] = instrument_model

    params["instrument_platform"] = instrument_platform

    params["latitude_gte"] = latitude_gte

    params["latitude_lte"] = latitude_lte

    params["lineage"] = lineage

    params["longitude_gte"] = longitude_gte

    params["longitude_lte"] = longitude_lte

    params["metadata_key"] = metadata_key

    params["metadata_value"] = metadata_value

    params["metadata_value_gte"] = metadata_value_gte

    params["metadata_value_lte"] = metadata_value_lte

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params["search"] = search

    params["species"] = species

    params["study_accession"] = study_accession

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/samples",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> PaginatedSampleList | None:
    if response.status_code == 200:
        response_200 = PaginatedSampleList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[PaginatedSampleList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    accession: list[str] | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    environment_feature: str | Unset = UNSET,
    environment_material: str | Unset = UNSET,
    experiment_type: list[str] | Unset = UNSET,
    format_: SamplesListFormat | Unset = UNSET,
    geo_loc_name: str | Unset = UNSET,
    include: str | Unset = UNSET,
    instrument_model: str | Unset = UNSET,
    instrument_platform: str | Unset = UNSET,
    latitude_gte: float | Unset = UNSET,
    latitude_lte: float | Unset = UNSET,
    lineage: str | Unset = UNSET,
    longitude_gte: float | Unset = UNSET,
    longitude_lte: float | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
    study_accession: str | Unset = UNSET,
) -> Response[PaginatedSampleList]:
    """Retrieves list of samples
    Example:
    ---
    `/samples` retrieves list of samples

    `/samples?fields[samples]=accession,runs_count,biome`
    retrieve only selected fields

    `/samples?include=runs` with related runs

    `/samples?ordering=accession` ordered by accession

    Filter by:
    ---
    `/samples?experiment_type=metagenomic`

    `/samples?species=sapiens`

    `/samples?biome=root:Environmental:Aquatic:Marine`

    Search for:
    ---
    name, descriptions, metadata, species, environment feature and material

    `/samples?search=continuous%20culture`

    Args:
        accession (list[str] | Unset):
        biome_name (str | Unset):
        environment_feature (str | Unset):
        environment_material (str | Unset):
        experiment_type (list[str] | Unset):
        format_ (SamplesListFormat | Unset):
        geo_loc_name (str | Unset):
        include (str | Unset):
        instrument_model (str | Unset):
        instrument_platform (str | Unset):
        latitude_gte (float | Unset):
        latitude_lte (float | Unset):
        lineage (str | Unset):
        longitude_gte (float | Unset):
        longitude_lte (float | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):
        species (str | Unset):
        study_accession (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedSampleList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        biome_name=biome_name,
        environment_feature=environment_feature,
        environment_material=environment_material,
        experiment_type=experiment_type,
        format_=format_,
        geo_loc_name=geo_loc_name,
        include=include,
        instrument_model=instrument_model,
        instrument_platform=instrument_platform,
        latitude_gte=latitude_gte,
        latitude_lte=latitude_lte,
        lineage=lineage,
        longitude_gte=longitude_gte,
        longitude_lte=longitude_lte,
        metadata_key=metadata_key,
        metadata_value=metadata_value,
        metadata_value_gte=metadata_value_gte,
        metadata_value_lte=metadata_value_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        species=species,
        study_accession=study_accession,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    accession: list[str] | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    environment_feature: str | Unset = UNSET,
    environment_material: str | Unset = UNSET,
    experiment_type: list[str] | Unset = UNSET,
    format_: SamplesListFormat | Unset = UNSET,
    geo_loc_name: str | Unset = UNSET,
    include: str | Unset = UNSET,
    instrument_model: str | Unset = UNSET,
    instrument_platform: str | Unset = UNSET,
    latitude_gte: float | Unset = UNSET,
    latitude_lte: float | Unset = UNSET,
    lineage: str | Unset = UNSET,
    longitude_gte: float | Unset = UNSET,
    longitude_lte: float | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
    study_accession: str | Unset = UNSET,
) -> PaginatedSampleList | None:
    """Retrieves list of samples
    Example:
    ---
    `/samples` retrieves list of samples

    `/samples?fields[samples]=accession,runs_count,biome`
    retrieve only selected fields

    `/samples?include=runs` with related runs

    `/samples?ordering=accession` ordered by accession

    Filter by:
    ---
    `/samples?experiment_type=metagenomic`

    `/samples?species=sapiens`

    `/samples?biome=root:Environmental:Aquatic:Marine`

    Search for:
    ---
    name, descriptions, metadata, species, environment feature and material

    `/samples?search=continuous%20culture`

    Args:
        accession (list[str] | Unset):
        biome_name (str | Unset):
        environment_feature (str | Unset):
        environment_material (str | Unset):
        experiment_type (list[str] | Unset):
        format_ (SamplesListFormat | Unset):
        geo_loc_name (str | Unset):
        include (str | Unset):
        instrument_model (str | Unset):
        instrument_platform (str | Unset):
        latitude_gte (float | Unset):
        latitude_lte (float | Unset):
        lineage (str | Unset):
        longitude_gte (float | Unset):
        longitude_lte (float | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):
        species (str | Unset):
        study_accession (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedSampleList
    """

    return sync_detailed(
        client=client,
        accession=accession,
        biome_name=biome_name,
        environment_feature=environment_feature,
        environment_material=environment_material,
        experiment_type=experiment_type,
        format_=format_,
        geo_loc_name=geo_loc_name,
        include=include,
        instrument_model=instrument_model,
        instrument_platform=instrument_platform,
        latitude_gte=latitude_gte,
        latitude_lte=latitude_lte,
        lineage=lineage,
        longitude_gte=longitude_gte,
        longitude_lte=longitude_lte,
        metadata_key=metadata_key,
        metadata_value=metadata_value,
        metadata_value_gte=metadata_value_gte,
        metadata_value_lte=metadata_value_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        species=species,
        study_accession=study_accession,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    accession: list[str] | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    environment_feature: str | Unset = UNSET,
    environment_material: str | Unset = UNSET,
    experiment_type: list[str] | Unset = UNSET,
    format_: SamplesListFormat | Unset = UNSET,
    geo_loc_name: str | Unset = UNSET,
    include: str | Unset = UNSET,
    instrument_model: str | Unset = UNSET,
    instrument_platform: str | Unset = UNSET,
    latitude_gte: float | Unset = UNSET,
    latitude_lte: float | Unset = UNSET,
    lineage: str | Unset = UNSET,
    longitude_gte: float | Unset = UNSET,
    longitude_lte: float | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
    study_accession: str | Unset = UNSET,
) -> Response[PaginatedSampleList]:
    """Retrieves list of samples
    Example:
    ---
    `/samples` retrieves list of samples

    `/samples?fields[samples]=accession,runs_count,biome`
    retrieve only selected fields

    `/samples?include=runs` with related runs

    `/samples?ordering=accession` ordered by accession

    Filter by:
    ---
    `/samples?experiment_type=metagenomic`

    `/samples?species=sapiens`

    `/samples?biome=root:Environmental:Aquatic:Marine`

    Search for:
    ---
    name, descriptions, metadata, species, environment feature and material

    `/samples?search=continuous%20culture`

    Args:
        accession (list[str] | Unset):
        biome_name (str | Unset):
        environment_feature (str | Unset):
        environment_material (str | Unset):
        experiment_type (list[str] | Unset):
        format_ (SamplesListFormat | Unset):
        geo_loc_name (str | Unset):
        include (str | Unset):
        instrument_model (str | Unset):
        instrument_platform (str | Unset):
        latitude_gte (float | Unset):
        latitude_lte (float | Unset):
        lineage (str | Unset):
        longitude_gte (float | Unset):
        longitude_lte (float | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):
        species (str | Unset):
        study_accession (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedSampleList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        biome_name=biome_name,
        environment_feature=environment_feature,
        environment_material=environment_material,
        experiment_type=experiment_type,
        format_=format_,
        geo_loc_name=geo_loc_name,
        include=include,
        instrument_model=instrument_model,
        instrument_platform=instrument_platform,
        latitude_gte=latitude_gte,
        latitude_lte=latitude_lte,
        lineage=lineage,
        longitude_gte=longitude_gte,
        longitude_lte=longitude_lte,
        metadata_key=metadata_key,
        metadata_value=metadata_value,
        metadata_value_gte=metadata_value_gte,
        metadata_value_lte=metadata_value_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        species=species,
        study_accession=study_accession,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    accession: list[str] | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    environment_feature: str | Unset = UNSET,
    environment_material: str | Unset = UNSET,
    experiment_type: list[str] | Unset = UNSET,
    format_: SamplesListFormat | Unset = UNSET,
    geo_loc_name: str | Unset = UNSET,
    include: str | Unset = UNSET,
    instrument_model: str | Unset = UNSET,
    instrument_platform: str | Unset = UNSET,
    latitude_gte: float | Unset = UNSET,
    latitude_lte: float | Unset = UNSET,
    lineage: str | Unset = UNSET,
    longitude_gte: float | Unset = UNSET,
    longitude_lte: float | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
    study_accession: str | Unset = UNSET,
) -> PaginatedSampleList | None:
    """Retrieves list of samples
    Example:
    ---
    `/samples` retrieves list of samples

    `/samples?fields[samples]=accession,runs_count,biome`
    retrieve only selected fields

    `/samples?include=runs` with related runs

    `/samples?ordering=accession` ordered by accession

    Filter by:
    ---
    `/samples?experiment_type=metagenomic`

    `/samples?species=sapiens`

    `/samples?biome=root:Environmental:Aquatic:Marine`

    Search for:
    ---
    name, descriptions, metadata, species, environment feature and material

    `/samples?search=continuous%20culture`

    Args:
        accession (list[str] | Unset):
        biome_name (str | Unset):
        environment_feature (str | Unset):
        environment_material (str | Unset):
        experiment_type (list[str] | Unset):
        format_ (SamplesListFormat | Unset):
        geo_loc_name (str | Unset):
        include (str | Unset):
        instrument_model (str | Unset):
        instrument_platform (str | Unset):
        latitude_gte (float | Unset):
        latitude_lte (float | Unset):
        lineage (str | Unset):
        longitude_gte (float | Unset):
        longitude_lte (float | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        search (str | Unset):
        species (str | Unset):
        study_accession (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedSampleList
    """

    return (
        await asyncio_detailed(
            client=client,
            accession=accession,
            biome_name=biome_name,
            environment_feature=environment_feature,
            environment_material=environment_material,
            experiment_type=experiment_type,
            format_=format_,
            geo_loc_name=geo_loc_name,
            include=include,
            instrument_model=instrument_model,
            instrument_platform=instrument_platform,
            latitude_gte=latitude_gte,
            latitude_lte=latitude_lte,
            lineage=lineage,
            longitude_gte=longitude_gte,
            longitude_lte=longitude_lte,
            metadata_key=metadata_key,
            metadata_value=metadata_value,
            metadata_value_gte=metadata_value_gte,
            metadata_value_lte=metadata_value_lte,
            ordering=ordering,
            page=page,
            page_size=page_size,
            search=search,
            species=species,
            study_accession=study_accession,
        )
    ).parsed
