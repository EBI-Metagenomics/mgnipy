from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.analyses_list_format import AnalysesListFormat
from ...models.paginated_analysis_list import PaginatedAnalysisList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    accession: str | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    experiment_type: list[str] | Unset = UNSET,
    format_: AnalysesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    instrument_model: str | Unset = UNSET,
    instrument_platform: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    pipeline_version: str | Unset = UNSET,
    sample_accession: str | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
    study_accession: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["accession"] = accession

    params["biome_name"] = biome_name

    json_experiment_type: list[str] | Unset = UNSET
    if not isinstance(experiment_type, Unset):
        json_experiment_type = experiment_type

    params["experiment_type"] = json_experiment_type

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["include"] = include

    params["instrument_model"] = instrument_model

    params["instrument_platform"] = instrument_platform

    params["lineage"] = lineage

    params["metadata_key"] = metadata_key

    params["metadata_value"] = metadata_value

    params["metadata_value_gte"] = metadata_value_gte

    params["metadata_value_lte"] = metadata_value_lte

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params["pipeline_version"] = pipeline_version

    params["sample_accession"] = sample_accession

    params["search"] = search

    params["species"] = species

    params["study_accession"] = study_accession

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/analyses",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> PaginatedAnalysisList | None:
    if response.status_code == 200:
        response_200 = PaginatedAnalysisList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedAnalysisList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    accession: str | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    experiment_type: list[str] | Unset = UNSET,
    format_: AnalysesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    instrument_model: str | Unset = UNSET,
    instrument_platform: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    pipeline_version: str | Unset = UNSET,
    sample_accession: str | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
    study_accession: str | Unset = UNSET,
) -> Response[PaginatedAnalysisList]:
    """Retrieves analysis results for the given accession
    Example:
    ---
    `/analyses`

    Args:
        accession (str | Unset):
        biome_name (str | Unset):
        experiment_type (list[str] | Unset):
        format_ (AnalysesListFormat | Unset):
        include (str | Unset):
        instrument_model (str | Unset):
        instrument_platform (str | Unset):
        lineage (str | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        pipeline_version (str | Unset):
        sample_accession (str | Unset):
        search (str | Unset):
        species (str | Unset):
        study_accession (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedAnalysisList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        biome_name=biome_name,
        experiment_type=experiment_type,
        format_=format_,
        include=include,
        instrument_model=instrument_model,
        instrument_platform=instrument_platform,
        lineage=lineage,
        metadata_key=metadata_key,
        metadata_value=metadata_value,
        metadata_value_gte=metadata_value_gte,
        metadata_value_lte=metadata_value_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        pipeline_version=pipeline_version,
        sample_accession=sample_accession,
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
    accession: str | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    experiment_type: list[str] | Unset = UNSET,
    format_: AnalysesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    instrument_model: str | Unset = UNSET,
    instrument_platform: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    pipeline_version: str | Unset = UNSET,
    sample_accession: str | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
    study_accession: str | Unset = UNSET,
) -> PaginatedAnalysisList | None:
    """Retrieves analysis results for the given accession
    Example:
    ---
    `/analyses`

    Args:
        accession (str | Unset):
        biome_name (str | Unset):
        experiment_type (list[str] | Unset):
        format_ (AnalysesListFormat | Unset):
        include (str | Unset):
        instrument_model (str | Unset):
        instrument_platform (str | Unset):
        lineage (str | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        pipeline_version (str | Unset):
        sample_accession (str | Unset):
        search (str | Unset):
        species (str | Unset):
        study_accession (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedAnalysisList
    """

    return sync_detailed(
        client=client,
        accession=accession,
        biome_name=biome_name,
        experiment_type=experiment_type,
        format_=format_,
        include=include,
        instrument_model=instrument_model,
        instrument_platform=instrument_platform,
        lineage=lineage,
        metadata_key=metadata_key,
        metadata_value=metadata_value,
        metadata_value_gte=metadata_value_gte,
        metadata_value_lte=metadata_value_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        pipeline_version=pipeline_version,
        sample_accession=sample_accession,
        search=search,
        species=species,
        study_accession=study_accession,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    accession: str | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    experiment_type: list[str] | Unset = UNSET,
    format_: AnalysesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    instrument_model: str | Unset = UNSET,
    instrument_platform: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    pipeline_version: str | Unset = UNSET,
    sample_accession: str | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
    study_accession: str | Unset = UNSET,
) -> Response[PaginatedAnalysisList]:
    """Retrieves analysis results for the given accession
    Example:
    ---
    `/analyses`

    Args:
        accession (str | Unset):
        biome_name (str | Unset):
        experiment_type (list[str] | Unset):
        format_ (AnalysesListFormat | Unset):
        include (str | Unset):
        instrument_model (str | Unset):
        instrument_platform (str | Unset):
        lineage (str | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        pipeline_version (str | Unset):
        sample_accession (str | Unset):
        search (str | Unset):
        species (str | Unset):
        study_accession (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedAnalysisList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        biome_name=biome_name,
        experiment_type=experiment_type,
        format_=format_,
        include=include,
        instrument_model=instrument_model,
        instrument_platform=instrument_platform,
        lineage=lineage,
        metadata_key=metadata_key,
        metadata_value=metadata_value,
        metadata_value_gte=metadata_value_gte,
        metadata_value_lte=metadata_value_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        pipeline_version=pipeline_version,
        sample_accession=sample_accession,
        search=search,
        species=species,
        study_accession=study_accession,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    accession: str | Unset = UNSET,
    biome_name: str | Unset = UNSET,
    experiment_type: list[str] | Unset = UNSET,
    format_: AnalysesListFormat | Unset = UNSET,
    include: str | Unset = UNSET,
    instrument_model: str | Unset = UNSET,
    instrument_platform: str | Unset = UNSET,
    lineage: str | Unset = UNSET,
    metadata_key: str | Unset = UNSET,
    metadata_value: str | Unset = UNSET,
    metadata_value_gte: float | Unset = UNSET,
    metadata_value_lte: float | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    pipeline_version: str | Unset = UNSET,
    sample_accession: str | Unset = UNSET,
    search: str | Unset = UNSET,
    species: str | Unset = UNSET,
    study_accession: str | Unset = UNSET,
) -> PaginatedAnalysisList | None:
    """Retrieves analysis results for the given accession
    Example:
    ---
    `/analyses`

    Args:
        accession (str | Unset):
        biome_name (str | Unset):
        experiment_type (list[str] | Unset):
        format_ (AnalysesListFormat | Unset):
        include (str | Unset):
        instrument_model (str | Unset):
        instrument_platform (str | Unset):
        lineage (str | Unset):
        metadata_key (str | Unset):
        metadata_value (str | Unset):
        metadata_value_gte (float | Unset):
        metadata_value_lte (float | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        pipeline_version (str | Unset):
        sample_accession (str | Unset):
        search (str | Unset):
        species (str | Unset):
        study_accession (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedAnalysisList
    """

    return (
        await asyncio_detailed(
            client=client,
            accession=accession,
            biome_name=biome_name,
            experiment_type=experiment_type,
            format_=format_,
            include=include,
            instrument_model=instrument_model,
            instrument_platform=instrument_platform,
            lineage=lineage,
            metadata_key=metadata_key,
            metadata_value=metadata_value,
            metadata_value_gte=metadata_value_gte,
            metadata_value_lte=metadata_value_lte,
            ordering=ordering,
            page=page,
            page_size=page_size,
            pipeline_version=pipeline_version,
            sample_accession=sample_accession,
            search=search,
            species=species,
            study_accession=study_accession,
        )
    ).parsed
