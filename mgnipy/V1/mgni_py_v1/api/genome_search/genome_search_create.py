from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.genome_fragment_search import GenomeFragmentSearch
from ...models.genome_search_create_format import GenomeSearchCreateFormat
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: GenomeFragmentSearch | GenomeFragmentSearch | Unset = UNSET,
    format_: GenomeSearchCreateFormat | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_format_: str | Unset = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/genome-search",
        "params": params,
    }

    if isinstance(body, GenomeFragmentSearch):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, GenomeFragmentSearch):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GenomeFragmentSearch | None:
    if response.status_code == 201:
        response_201 = GenomeFragmentSearch.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GenomeFragmentSearch]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: GenomeFragmentSearch | GenomeFragmentSearch | Unset = UNSET,
    format_: GenomeSearchCreateFormat | Unset = UNSET,
) -> Response[GenomeFragmentSearch]:
    """
    Args:
        format_ (GenomeSearchCreateFormat | Unset):
        body (GenomeFragmentSearch):
        body (GenomeFragmentSearch):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeFragmentSearch]
    """

    kwargs = _get_kwargs(
        body=body,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: GenomeFragmentSearch | GenomeFragmentSearch | Unset = UNSET,
    format_: GenomeSearchCreateFormat | Unset = UNSET,
) -> GenomeFragmentSearch | None:
    """
    Args:
        format_ (GenomeSearchCreateFormat | Unset):
        body (GenomeFragmentSearch):
        body (GenomeFragmentSearch):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeFragmentSearch
    """

    return sync_detailed(
        client=client,
        body=body,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: GenomeFragmentSearch | GenomeFragmentSearch | Unset = UNSET,
    format_: GenomeSearchCreateFormat | Unset = UNSET,
) -> Response[GenomeFragmentSearch]:
    """
    Args:
        format_ (GenomeSearchCreateFormat | Unset):
        body (GenomeFragmentSearch):
        body (GenomeFragmentSearch):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GenomeFragmentSearch]
    """

    kwargs = _get_kwargs(
        body=body,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: GenomeFragmentSearch | GenomeFragmentSearch | Unset = UNSET,
    format_: GenomeSearchCreateFormat | Unset = UNSET,
) -> GenomeFragmentSearch | None:
    """
    Args:
        format_ (GenomeSearchCreateFormat | Unset):
        body (GenomeFragmentSearch):
        body (GenomeFragmentSearch):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GenomeFragmentSearch
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            format_=format_,
        )
    ).parsed
