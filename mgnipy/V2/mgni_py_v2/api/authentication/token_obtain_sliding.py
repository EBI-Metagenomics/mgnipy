from http import HTTPStatus
from typing import Any

import httpx

from ....._shared_helpers import errors
from ...._mgnipy_models.types import Response
from ....client import (
    AuthenticatedClient,
    Client,
)
from ...models.webin_token_request import WebinTokenRequest
from ...models.webin_token_response import WebinTokenResponse


def _get_kwargs(
    *,
    body: WebinTokenRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/metagenomics/api/v2/auth/sliding",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> WebinTokenResponse | None:
    if response.status_code == 200:
        response_200 = WebinTokenResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[WebinTokenResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: WebinTokenRequest,
) -> Response[WebinTokenResponse]:
    """Obtain an authentication token using Webin credentials.

     Obtain an authentication JWT token using Webin credentials. This token is sliding, i.e. it can be
    used both to access private data endpoints and to refresh itself after expiry.

    Args:
        body (WebinTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebinTokenResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: WebinTokenRequest,
) -> WebinTokenResponse | None:
    """Obtain an authentication token using Webin credentials.

     Obtain an authentication JWT token using Webin credentials. This token is sliding, i.e. it can be
    used both to access private data endpoints and to refresh itself after expiry.

    Args:
        body (WebinTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebinTokenResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: WebinTokenRequest,
) -> Response[WebinTokenResponse]:
    """Obtain an authentication token using Webin credentials.

     Obtain an authentication JWT token using Webin credentials. This token is sliding, i.e. it can be
    used both to access private data endpoints and to refresh itself after expiry.

    Args:
        body (WebinTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebinTokenResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: WebinTokenRequest,
) -> WebinTokenResponse | None:
    """Obtain an authentication token using Webin credentials.

     Obtain an authentication JWT token using Webin credentials. This token is sliding, i.e. it can be
    used both to access private data endpoints and to refresh itself after expiry.

    Args:
        body (WebinTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebinTokenResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
