from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.genomes_list_format import GenomesListFormat
from ...models.genomes_list_mag_type import GenomesListMagType
from ...models.paginated_genome_list import PaginatedGenomeList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    accession: list[str] | Unset = UNSET,
    completeness_gte: float | Unset = UNSET,
    completeness_lte: float | Unset = UNSET,
    contamination_gte: float | Unset = UNSET,
    contamination_lte: float | Unset = UNSET,
    format_: GenomesListFormat | Unset = UNSET,
    gc_content_gte: float | Unset = UNSET,
    gc_content_lte: float | Unset = UNSET,
    geo_origin: list[str] | Unset = UNSET,
    length_gte: int | Unset = UNSET,
    length_lte: int | Unset = UNSET,
    mag_type: GenomesListMagType | Unset = UNSET,
    n_50_gte: int | Unset = UNSET,
    n_50_lte: int | Unset = UNSET,
    num_contigs_gte: int | Unset = UNSET,
    num_contigs_lte: int | Unset = UNSET,
    num_genomes_total_gte: int | Unset = UNSET,
    num_genomes_total_lte: int | Unset = UNSET,
    num_proteins_gte: int | Unset = UNSET,
    num_proteins_lte: int | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    pangenome_accessory_size_gte: int | Unset = UNSET,
    pangenome_accessory_size_lte: int | Unset = UNSET,
    pangenome_core_lte: int | Unset = UNSET,
    pangenome_core_size_gte: int | Unset = UNSET,
    pangenome_geographic_range: list[str] | Unset = UNSET,
    pangenome_size_gte: int | Unset = UNSET,
    pangenome_size_lte: int | Unset = UNSET,
    search: str | Unset = UNSET,
    taxon_lineage: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_accession: list[str] | Unset = UNSET
    if not isinstance(accession, Unset):
        json_accession = accession

    params["accession"] = json_accession

    params["completeness__gte"] = completeness_gte

    params["completeness__lte"] = completeness_lte

    params["contamination__gte"] = contamination_gte

    params["contamination__lte"] = contamination_lte

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["gc_content__gte"] = gc_content_gte

    params["gc_content__lte"] = gc_content_lte

    json_geo_origin: list[str] | Unset = UNSET
    if not isinstance(geo_origin, Unset):
        json_geo_origin = geo_origin

    params["geo_origin"] = json_geo_origin

    params["length__gte"] = length_gte

    params["length__lte"] = length_lte

    json_mag_type: str | Unset = UNSET
    if not isinstance(mag_type, Unset):
        json_mag_type = mag_type.value

    params["mag_type"] = json_mag_type

    params["n_50__gte"] = n_50_gte

    params["n_50__lte"] = n_50_lte

    params["num_contigs__gte"] = num_contigs_gte

    params["num_contigs__lte"] = num_contigs_lte

    params["num_genomes_total__gte"] = num_genomes_total_gte

    params["num_genomes_total__lte"] = num_genomes_total_lte

    params["num_proteins__gte"] = num_proteins_gte

    params["num_proteins__lte"] = num_proteins_lte

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params["pangenome_accessory_size__gte"] = pangenome_accessory_size_gte

    params["pangenome_accessory_size__lte"] = pangenome_accessory_size_lte

    params["pangenome_core___lte"] = pangenome_core_lte

    params["pangenome_core_size__gte"] = pangenome_core_size_gte

    json_pangenome_geographic_range: list[str] | Unset = UNSET
    if not isinstance(pangenome_geographic_range, Unset):
        json_pangenome_geographic_range = pangenome_geographic_range

    params["pangenome_geographic_range"] = json_pangenome_geographic_range

    params["pangenome_size__gte"] = pangenome_size_gte

    params["pangenome_size__lte"] = pangenome_size_lte

    params["search"] = search

    params["taxon_lineage"] = taxon_lineage

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/genomes",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> PaginatedGenomeList | None:
    if response.status_code == 200:
        response_200 = PaginatedGenomeList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[PaginatedGenomeList]:
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
    completeness_gte: float | Unset = UNSET,
    completeness_lte: float | Unset = UNSET,
    contamination_gte: float | Unset = UNSET,
    contamination_lte: float | Unset = UNSET,
    format_: GenomesListFormat | Unset = UNSET,
    gc_content_gte: float | Unset = UNSET,
    gc_content_lte: float | Unset = UNSET,
    geo_origin: list[str] | Unset = UNSET,
    length_gte: int | Unset = UNSET,
    length_lte: int | Unset = UNSET,
    mag_type: GenomesListMagType | Unset = UNSET,
    n_50_gte: int | Unset = UNSET,
    n_50_lte: int | Unset = UNSET,
    num_contigs_gte: int | Unset = UNSET,
    num_contigs_lte: int | Unset = UNSET,
    num_genomes_total_gte: int | Unset = UNSET,
    num_genomes_total_lte: int | Unset = UNSET,
    num_proteins_gte: int | Unset = UNSET,
    num_proteins_lte: int | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    pangenome_accessory_size_gte: int | Unset = UNSET,
    pangenome_accessory_size_lte: int | Unset = UNSET,
    pangenome_core_lte: int | Unset = UNSET,
    pangenome_core_size_gte: int | Unset = UNSET,
    pangenome_geographic_range: list[str] | Unset = UNSET,
    pangenome_size_gte: int | Unset = UNSET,
    pangenome_size_lte: int | Unset = UNSET,
    search: str | Unset = UNSET,
    taxon_lineage: str | Unset = UNSET,
) -> Response[PaginatedGenomeList]:
    """
    Args:
        accession (list[str] | Unset):
        completeness_gte (float | Unset):
        completeness_lte (float | Unset):
        contamination_gte (float | Unset):
        contamination_lte (float | Unset):
        format_ (GenomesListFormat | Unset):
        gc_content_gte (float | Unset):
        gc_content_lte (float | Unset):
        geo_origin (list[str] | Unset):
        length_gte (int | Unset):
        length_lte (int | Unset):
        mag_type (GenomesListMagType | Unset):
        n_50_gte (int | Unset):
        n_50_lte (int | Unset):
        num_contigs_gte (int | Unset):
        num_contigs_lte (int | Unset):
        num_genomes_total_gte (int | Unset):
        num_genomes_total_lte (int | Unset):
        num_proteins_gte (int | Unset):
        num_proteins_lte (int | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        pangenome_accessory_size_gte (int | Unset):
        pangenome_accessory_size_lte (int | Unset):
        pangenome_core_lte (int | Unset):
        pangenome_core_size_gte (int | Unset):
        pangenome_geographic_range (list[str] | Unset):
        pangenome_size_gte (int | Unset):
        pangenome_size_lte (int | Unset):
        search (str | Unset):
        taxon_lineage (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedGenomeList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        completeness_gte=completeness_gte,
        completeness_lte=completeness_lte,
        contamination_gte=contamination_gte,
        contamination_lte=contamination_lte,
        format_=format_,
        gc_content_gte=gc_content_gte,
        gc_content_lte=gc_content_lte,
        geo_origin=geo_origin,
        length_gte=length_gte,
        length_lte=length_lte,
        mag_type=mag_type,
        n_50_gte=n_50_gte,
        n_50_lte=n_50_lte,
        num_contigs_gte=num_contigs_gte,
        num_contigs_lte=num_contigs_lte,
        num_genomes_total_gte=num_genomes_total_gte,
        num_genomes_total_lte=num_genomes_total_lte,
        num_proteins_gte=num_proteins_gte,
        num_proteins_lte=num_proteins_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        pangenome_accessory_size_gte=pangenome_accessory_size_gte,
        pangenome_accessory_size_lte=pangenome_accessory_size_lte,
        pangenome_core_lte=pangenome_core_lte,
        pangenome_core_size_gte=pangenome_core_size_gte,
        pangenome_geographic_range=pangenome_geographic_range,
        pangenome_size_gte=pangenome_size_gte,
        pangenome_size_lte=pangenome_size_lte,
        search=search,
        taxon_lineage=taxon_lineage,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    accession: list[str] | Unset = UNSET,
    completeness_gte: float | Unset = UNSET,
    completeness_lte: float | Unset = UNSET,
    contamination_gte: float | Unset = UNSET,
    contamination_lte: float | Unset = UNSET,
    format_: GenomesListFormat | Unset = UNSET,
    gc_content_gte: float | Unset = UNSET,
    gc_content_lte: float | Unset = UNSET,
    geo_origin: list[str] | Unset = UNSET,
    length_gte: int | Unset = UNSET,
    length_lte: int | Unset = UNSET,
    mag_type: GenomesListMagType | Unset = UNSET,
    n_50_gte: int | Unset = UNSET,
    n_50_lte: int | Unset = UNSET,
    num_contigs_gte: int | Unset = UNSET,
    num_contigs_lte: int | Unset = UNSET,
    num_genomes_total_gte: int | Unset = UNSET,
    num_genomes_total_lte: int | Unset = UNSET,
    num_proteins_gte: int | Unset = UNSET,
    num_proteins_lte: int | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    pangenome_accessory_size_gte: int | Unset = UNSET,
    pangenome_accessory_size_lte: int | Unset = UNSET,
    pangenome_core_lte: int | Unset = UNSET,
    pangenome_core_size_gte: int | Unset = UNSET,
    pangenome_geographic_range: list[str] | Unset = UNSET,
    pangenome_size_gte: int | Unset = UNSET,
    pangenome_size_lte: int | Unset = UNSET,
    search: str | Unset = UNSET,
    taxon_lineage: str | Unset = UNSET,
) -> PaginatedGenomeList | None:
    """
    Args:
        accession (list[str] | Unset):
        completeness_gte (float | Unset):
        completeness_lte (float | Unset):
        contamination_gte (float | Unset):
        contamination_lte (float | Unset):
        format_ (GenomesListFormat | Unset):
        gc_content_gte (float | Unset):
        gc_content_lte (float | Unset):
        geo_origin (list[str] | Unset):
        length_gte (int | Unset):
        length_lte (int | Unset):
        mag_type (GenomesListMagType | Unset):
        n_50_gte (int | Unset):
        n_50_lte (int | Unset):
        num_contigs_gte (int | Unset):
        num_contigs_lte (int | Unset):
        num_genomes_total_gte (int | Unset):
        num_genomes_total_lte (int | Unset):
        num_proteins_gte (int | Unset):
        num_proteins_lte (int | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        pangenome_accessory_size_gte (int | Unset):
        pangenome_accessory_size_lte (int | Unset):
        pangenome_core_lte (int | Unset):
        pangenome_core_size_gte (int | Unset):
        pangenome_geographic_range (list[str] | Unset):
        pangenome_size_gte (int | Unset):
        pangenome_size_lte (int | Unset):
        search (str | Unset):
        taxon_lineage (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedGenomeList
    """

    return sync_detailed(
        client=client,
        accession=accession,
        completeness_gte=completeness_gte,
        completeness_lte=completeness_lte,
        contamination_gte=contamination_gte,
        contamination_lte=contamination_lte,
        format_=format_,
        gc_content_gte=gc_content_gte,
        gc_content_lte=gc_content_lte,
        geo_origin=geo_origin,
        length_gte=length_gte,
        length_lte=length_lte,
        mag_type=mag_type,
        n_50_gte=n_50_gte,
        n_50_lte=n_50_lte,
        num_contigs_gte=num_contigs_gte,
        num_contigs_lte=num_contigs_lte,
        num_genomes_total_gte=num_genomes_total_gte,
        num_genomes_total_lte=num_genomes_total_lte,
        num_proteins_gte=num_proteins_gte,
        num_proteins_lte=num_proteins_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        pangenome_accessory_size_gte=pangenome_accessory_size_gte,
        pangenome_accessory_size_lte=pangenome_accessory_size_lte,
        pangenome_core_lte=pangenome_core_lte,
        pangenome_core_size_gte=pangenome_core_size_gte,
        pangenome_geographic_range=pangenome_geographic_range,
        pangenome_size_gte=pangenome_size_gte,
        pangenome_size_lte=pangenome_size_lte,
        search=search,
        taxon_lineage=taxon_lineage,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    accession: list[str] | Unset = UNSET,
    completeness_gte: float | Unset = UNSET,
    completeness_lte: float | Unset = UNSET,
    contamination_gte: float | Unset = UNSET,
    contamination_lte: float | Unset = UNSET,
    format_: GenomesListFormat | Unset = UNSET,
    gc_content_gte: float | Unset = UNSET,
    gc_content_lte: float | Unset = UNSET,
    geo_origin: list[str] | Unset = UNSET,
    length_gte: int | Unset = UNSET,
    length_lte: int | Unset = UNSET,
    mag_type: GenomesListMagType | Unset = UNSET,
    n_50_gte: int | Unset = UNSET,
    n_50_lte: int | Unset = UNSET,
    num_contigs_gte: int | Unset = UNSET,
    num_contigs_lte: int | Unset = UNSET,
    num_genomes_total_gte: int | Unset = UNSET,
    num_genomes_total_lte: int | Unset = UNSET,
    num_proteins_gte: int | Unset = UNSET,
    num_proteins_lte: int | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    pangenome_accessory_size_gte: int | Unset = UNSET,
    pangenome_accessory_size_lte: int | Unset = UNSET,
    pangenome_core_lte: int | Unset = UNSET,
    pangenome_core_size_gte: int | Unset = UNSET,
    pangenome_geographic_range: list[str] | Unset = UNSET,
    pangenome_size_gte: int | Unset = UNSET,
    pangenome_size_lte: int | Unset = UNSET,
    search: str | Unset = UNSET,
    taxon_lineage: str | Unset = UNSET,
) -> Response[PaginatedGenomeList]:
    """
    Args:
        accession (list[str] | Unset):
        completeness_gte (float | Unset):
        completeness_lte (float | Unset):
        contamination_gte (float | Unset):
        contamination_lte (float | Unset):
        format_ (GenomesListFormat | Unset):
        gc_content_gte (float | Unset):
        gc_content_lte (float | Unset):
        geo_origin (list[str] | Unset):
        length_gte (int | Unset):
        length_lte (int | Unset):
        mag_type (GenomesListMagType | Unset):
        n_50_gte (int | Unset):
        n_50_lte (int | Unset):
        num_contigs_gte (int | Unset):
        num_contigs_lte (int | Unset):
        num_genomes_total_gte (int | Unset):
        num_genomes_total_lte (int | Unset):
        num_proteins_gte (int | Unset):
        num_proteins_lte (int | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        pangenome_accessory_size_gte (int | Unset):
        pangenome_accessory_size_lte (int | Unset):
        pangenome_core_lte (int | Unset):
        pangenome_core_size_gte (int | Unset):
        pangenome_geographic_range (list[str] | Unset):
        pangenome_size_gte (int | Unset):
        pangenome_size_lte (int | Unset):
        search (str | Unset):
        taxon_lineage (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedGenomeList]
    """

    kwargs = _get_kwargs(
        accession=accession,
        completeness_gte=completeness_gte,
        completeness_lte=completeness_lte,
        contamination_gte=contamination_gte,
        contamination_lte=contamination_lte,
        format_=format_,
        gc_content_gte=gc_content_gte,
        gc_content_lte=gc_content_lte,
        geo_origin=geo_origin,
        length_gte=length_gte,
        length_lte=length_lte,
        mag_type=mag_type,
        n_50_gte=n_50_gte,
        n_50_lte=n_50_lte,
        num_contigs_gte=num_contigs_gte,
        num_contigs_lte=num_contigs_lte,
        num_genomes_total_gte=num_genomes_total_gte,
        num_genomes_total_lte=num_genomes_total_lte,
        num_proteins_gte=num_proteins_gte,
        num_proteins_lte=num_proteins_lte,
        ordering=ordering,
        page=page,
        page_size=page_size,
        pangenome_accessory_size_gte=pangenome_accessory_size_gte,
        pangenome_accessory_size_lte=pangenome_accessory_size_lte,
        pangenome_core_lte=pangenome_core_lte,
        pangenome_core_size_gte=pangenome_core_size_gte,
        pangenome_geographic_range=pangenome_geographic_range,
        pangenome_size_gte=pangenome_size_gte,
        pangenome_size_lte=pangenome_size_lte,
        search=search,
        taxon_lineage=taxon_lineage,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    accession: list[str] | Unset = UNSET,
    completeness_gte: float | Unset = UNSET,
    completeness_lte: float | Unset = UNSET,
    contamination_gte: float | Unset = UNSET,
    contamination_lte: float | Unset = UNSET,
    format_: GenomesListFormat | Unset = UNSET,
    gc_content_gte: float | Unset = UNSET,
    gc_content_lte: float | Unset = UNSET,
    geo_origin: list[str] | Unset = UNSET,
    length_gte: int | Unset = UNSET,
    length_lte: int | Unset = UNSET,
    mag_type: GenomesListMagType | Unset = UNSET,
    n_50_gte: int | Unset = UNSET,
    n_50_lte: int | Unset = UNSET,
    num_contigs_gte: int | Unset = UNSET,
    num_contigs_lte: int | Unset = UNSET,
    num_genomes_total_gte: int | Unset = UNSET,
    num_genomes_total_lte: int | Unset = UNSET,
    num_proteins_gte: int | Unset = UNSET,
    num_proteins_lte: int | Unset = UNSET,
    ordering: str | Unset = UNSET,
    page: int | Unset = UNSET,
    page_size: int | Unset = UNSET,
    pangenome_accessory_size_gte: int | Unset = UNSET,
    pangenome_accessory_size_lte: int | Unset = UNSET,
    pangenome_core_lte: int | Unset = UNSET,
    pangenome_core_size_gte: int | Unset = UNSET,
    pangenome_geographic_range: list[str] | Unset = UNSET,
    pangenome_size_gte: int | Unset = UNSET,
    pangenome_size_lte: int | Unset = UNSET,
    search: str | Unset = UNSET,
    taxon_lineage: str | Unset = UNSET,
) -> PaginatedGenomeList | None:
    """
    Args:
        accession (list[str] | Unset):
        completeness_gte (float | Unset):
        completeness_lte (float | Unset):
        contamination_gte (float | Unset):
        contamination_lte (float | Unset):
        format_ (GenomesListFormat | Unset):
        gc_content_gte (float | Unset):
        gc_content_lte (float | Unset):
        geo_origin (list[str] | Unset):
        length_gte (int | Unset):
        length_lte (int | Unset):
        mag_type (GenomesListMagType | Unset):
        n_50_gte (int | Unset):
        n_50_lte (int | Unset):
        num_contigs_gte (int | Unset):
        num_contigs_lte (int | Unset):
        num_genomes_total_gte (int | Unset):
        num_genomes_total_lte (int | Unset):
        num_proteins_gte (int | Unset):
        num_proteins_lte (int | Unset):
        ordering (str | Unset):
        page (int | Unset):
        page_size (int | Unset):
        pangenome_accessory_size_gte (int | Unset):
        pangenome_accessory_size_lte (int | Unset):
        pangenome_core_lte (int | Unset):
        pangenome_core_size_gte (int | Unset):
        pangenome_geographic_range (list[str] | Unset):
        pangenome_size_gte (int | Unset):
        pangenome_size_lte (int | Unset):
        search (str | Unset):
        taxon_lineage (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedGenomeList
    """

    return (
        await asyncio_detailed(
            client=client,
            accession=accession,
            completeness_gte=completeness_gte,
            completeness_lte=completeness_lte,
            contamination_gte=contamination_gte,
            contamination_lte=contamination_lte,
            format_=format_,
            gc_content_gte=gc_content_gte,
            gc_content_lte=gc_content_lte,
            geo_origin=geo_origin,
            length_gte=length_gte,
            length_lte=length_lte,
            mag_type=mag_type,
            n_50_gte=n_50_gte,
            n_50_lte=n_50_lte,
            num_contigs_gte=num_contigs_gte,
            num_contigs_lte=num_contigs_lte,
            num_genomes_total_gte=num_genomes_total_gte,
            num_genomes_total_lte=num_genomes_total_lte,
            num_proteins_gte=num_proteins_gte,
            num_proteins_lte=num_proteins_lte,
            ordering=ordering,
            page=page,
            page_size=page_size,
            pangenome_accessory_size_gte=pangenome_accessory_size_gte,
            pangenome_accessory_size_lte=pangenome_accessory_size_lte,
            pangenome_core_lte=pangenome_core_lte,
            pangenome_core_size_gte=pangenome_core_size_gte,
            pangenome_geographic_range=pangenome_geographic_range,
            pangenome_size_gte=pangenome_size_gte,
            pangenome_size_lte=pangenome_size_lte,
            search=search,
            taxon_lineage=taxon_lineage,
        )
    ).parsed
