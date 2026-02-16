from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ....._shared_helpers import errors
from ....client import (
    AuthenticatedClient,
    Client,
)
from ...models.publication_annotations import PublicationAnnotations
from ...._models_v2.types import Response


def _get_kwargs(
    pubmed_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/metagenomics/api/v2/publications/{pubmed_id}/annotations".format(
            pubmed_id=quote(str(pubmed_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PublicationAnnotations | None:
    if response.status_code == 200:
        response_200 = PublicationAnnotations.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PublicationAnnotations]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pubmed_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[PublicationAnnotations]:
    """Get any full-text annotations associated with the publication

     Full-text annotations are retrieved from Europe PMC, text mined for relevant metagenomic metadata
    terms

    Args:
        pubmed_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PublicationAnnotations]
    """

    kwargs = _get_kwargs(
        pubmed_id=pubmed_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pubmed_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> PublicationAnnotations | None:
    """Get any full-text annotations associated with the publication

     Full-text annotations are retrieved from Europe PMC, text mined for relevant metagenomic metadata
    terms

    Args:
        pubmed_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PublicationAnnotations
    """

    return sync_detailed(
        pubmed_id=pubmed_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    pubmed_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[PublicationAnnotations]:
    """Get any full-text annotations associated with the publication

     Full-text annotations are retrieved from Europe PMC, text mined for relevant metagenomic metadata
    terms

    Args:
        pubmed_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PublicationAnnotations]
    """

    kwargs = _get_kwargs(
        pubmed_id=pubmed_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pubmed_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> PublicationAnnotations | None:
    """Get any full-text annotations associated with the publication

     Full-text annotations are retrieved from Europe PMC, text mined for relevant metagenomic metadata
    terms

    Args:
        pubmed_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PublicationAnnotations
    """

    return (
        await asyncio_detailed(
            pubmed_id=pubmed_id,
            client=client,
        )
    ).parsed
