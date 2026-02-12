from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.publication import Publication
from ...models.publications_retrieve_format import PublicationsRetrieveFormat
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    pubmed_id: str,
    *,
    format_: PublicationsRetrieveFormat | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/publications/{pubmed_id}".format(
            pubmed_id=quote(str(pubmed_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Publication | None:
    if response.status_code == 200:
        response_200 = Publication.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Publication]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pubmed_id: str,
    *,
    client: AuthenticatedClient,
    format_: PublicationsRetrieveFormat | Unset = UNSET,
) -> Response[Publication]:
    """Retrieves publication for the given Pubmed ID
    Example:
    ---
    `/publications/{pubmed}`

    `/publications/{pubmed}?include=studies` with studies

    Args:
        pubmed_id (str):
        format_ (PublicationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Publication]
    """

    kwargs = _get_kwargs(
        pubmed_id=pubmed_id,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pubmed_id: str,
    *,
    client: AuthenticatedClient,
    format_: PublicationsRetrieveFormat | Unset = UNSET,
) -> Publication | None:
    """Retrieves publication for the given Pubmed ID
    Example:
    ---
    `/publications/{pubmed}`

    `/publications/{pubmed}?include=studies` with studies

    Args:
        pubmed_id (str):
        format_ (PublicationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Publication
    """

    return sync_detailed(
        pubmed_id=pubmed_id,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    pubmed_id: str,
    *,
    client: AuthenticatedClient,
    format_: PublicationsRetrieveFormat | Unset = UNSET,
) -> Response[Publication]:
    """Retrieves publication for the given Pubmed ID
    Example:
    ---
    `/publications/{pubmed}`

    `/publications/{pubmed}?include=studies` with studies

    Args:
        pubmed_id (str):
        format_ (PublicationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Publication]
    """

    kwargs = _get_kwargs(
        pubmed_id=pubmed_id,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pubmed_id: str,
    *,
    client: AuthenticatedClient,
    format_: PublicationsRetrieveFormat | Unset = UNSET,
) -> Publication | None:
    """Retrieves publication for the given Pubmed ID
    Example:
    ---
    `/publications/{pubmed}`

    `/publications/{pubmed}?include=studies` with studies

    Args:
        pubmed_id (str):
        format_ (PublicationsRetrieveFormat | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Publication
    """

    return (
        await asyncio_detailed(
            pubmed_id=pubmed_id,
            client=client,
            format_=format_,
        )
    ).parsed
