from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.annotations_antismash_gene_clusters_retrieve_format import (
    AnnotationsAntismashGeneClustersRetrieveFormat,
)
from ...models.anti_smash_gene_cluster import AntiSmashGeneCluster
from ...types import UNSET, Response, Unset


def _get_kwargs(
    accession: str,
    *,
    format_: AnnotationsAntismashGeneClustersRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/annotations/antismash-gene-clusters/{accession}".format(
            accession=quote(str(accession), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> AntiSmashGeneCluster | None:
    if response.status_code == 200:
        response_200 = AntiSmashGeneCluster.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AntiSmashGeneCluster]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AnnotationsAntismashGeneClustersRetrieveFormat | Unset = UNSET,
) -> Response[AntiSmashGeneCluster]:
    """Retrieves an antiSMASH gene cluster
    Example:
    ---
    `/annotations/antismash-gene-clusters/terpene`

    Args:
        accession (str):
        format_ (AnnotationsAntismashGeneClustersRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AntiSmashGeneCluster]
    """

    kwargs = _get_kwargs(
        accession=accession,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AnnotationsAntismashGeneClustersRetrieveFormat | Unset = UNSET,
) -> AntiSmashGeneCluster | None:
    """Retrieves an antiSMASH gene cluster
    Example:
    ---
    `/annotations/antismash-gene-clusters/terpene`

    Args:
        accession (str):
        format_ (AnnotationsAntismashGeneClustersRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AntiSmashGeneCluster
    """

    return sync_detailed(
        accession=accession,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AnnotationsAntismashGeneClustersRetrieveFormat | Unset = UNSET,
) -> Response[AntiSmashGeneCluster]:
    """Retrieves an antiSMASH gene cluster
    Example:
    ---
    `/annotations/antismash-gene-clusters/terpene`

    Args:
        accession (str):
        format_ (AnnotationsAntismashGeneClustersRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AntiSmashGeneCluster]
    """

    kwargs = _get_kwargs(
        accession=accession,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    accession: str,
    *,
    client: AuthenticatedClient,
    format_: AnnotationsAntismashGeneClustersRetrieveFormat | Unset = UNSET,
) -> AntiSmashGeneCluster | None:
    """Retrieves an antiSMASH gene cluster
    Example:
    ---
    `/annotations/antismash-gene-clusters/terpene`

    Args:
        accession (str):
        format_ (AnnotationsAntismashGeneClustersRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AntiSmashGeneCluster
    """

    return (
        await asyncio_detailed(
            accession=accession,
            client=client,
            format_=format_,
        )
    ).parsed
